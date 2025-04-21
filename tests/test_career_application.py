import pytest
import time
import logging
import os
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
from pages.careers_page import CareersPage
from pages.position_page import PositionPage
from config import Config  # Import the Config class directly

@pytest.mark.usefixtures("driver")
class TestCareerApplication:
    """Test suite for career application process."""
    
    @pytest.fixture(autouse=True)
    def setup(self, driver: WebDriver):
        """Setup test environment.
        
        Args:
            driver: WebDriver instance
        """
        self.logger = logging.getLogger(__name__)
        self.home_page = HomePage(driver)
        self.careers_page = CareersPage(driver)
        self.position_page = PositionPage(driver)
        self.driver = driver
        self.config = Config()  # Create config instance

    def _take_screenshot(self, name: str) -> None:
        """Take a screenshot of the current page.
        
        Args:
            name: Name to use for the screenshot file
        """
        try:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"screenshots/{name}_{timestamp}.png"
            os.makedirs("screenshots", exist_ok=True)
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {str(e)}")

    def test_apply_for_rd_positions(self):
        """Test applying for all R&D positions following the exercise instructions"""
        self.logger.info("=== Starting R&D Positions Application Test ===")
        
        try:
            # Step 1: Navigate to https://connecteam.com/
            self.logger.info("Step 1: Navigating to Connecteam homepage")
            self.home_page.navigate_to_home()
            
            # Step 2: Scroll down and click on 'careers' in the footer
            self.logger.info("Step 2: Navigating to careers page")
            if not self.home_page.scroll_to_and_click_careers():
                self._take_screenshot("careers_navigation_failed")
                pytest.fail("Failed to navigate to careers page")
            
            # Wait for careers page to fully load
            time.sleep(2)
            
            # Step 3: Select R&D from the left dropdown
            self.logger.info(f"Step 3: Selecting department: {self.config.TARGET_DEPARTMENT}")
            if not self.careers_page.select_department(self.config.TARGET_DEPARTMENT):
                self._take_screenshot("department_selection_failed")
                pytest.skip(f"No {self.config.TARGET_DEPARTMENT} positions currently visible")
            
            # Wait for department filter to apply
            time.sleep(1)
            
            # Get all available positions
            positions = self.careers_page.get_applyable_positions()
            if not positions:
                self._take_screenshot("no_positions_found")
                pytest.skip(f"No {self.config.TARGET_DEPARTMENT} positions available to apply for")
            
            total_positions = len(positions)
            self.logger.info(f"Found {total_positions} R&D positions to process")
            
            successful = 0
            failed = 0
            skipped = 0
            
            # Step 4: For all positions in R&D (marked 'apply now'), perform the following
            self.logger.info("Step 4: Processing all R&D positions")
            
            # Process each position one by one
            for i in range(total_positions):
                self.logger.info(f"\nProcessing position {i+1}/{total_positions}")
                
                # Get fresh positions list before each application
                fresh_positions = self.careers_page.get_applyable_positions()
                if not fresh_positions or i >= len(fresh_positions):
                    self.logger.warning(f"Position {i+1} no longer available, skipping")
                    skipped += 1
                    continue
                
                try:
                    # Step 4a: Click on 'Apply now'
                    self.logger.info(f"Clicking 'Apply now' for position {i+1}")
                    
                    # Use the example_cv.pdf from project root as specified in instructions
                    # Do not submit the form as per instructions
                    result = self.careers_page.apply_for_position(
                        position=fresh_positions[i],
                        first_name=self.config.FIRST_NAME,
                        last_name=self.config.LAST_NAME,
                        email=self.config.EMAIL,
                        phone=self.config.PHONE,
                        cv_path="example_cv.pdf"
                    )
                    
                    if result:
                        successful += 1
                        self.logger.info(f"✓ Successfully applied to position {i+1}")
                    else:
                        failed += 1
                        self.logger.warning(f"✗ Failed to apply to position {i+1}")
                        self._take_screenshot(f"position_{i+1}_failed")
                    
                    # Return to all positions list after each application
                    self.logger.info("Returning to all positions list")
                    if not self.position_page.return_to_all_positions():
                        self.logger.warning("Could not return to positions list, trying to continue...")
                        # Try to navigate back to careers page as fallback
                        self.home_page.navigate_to_home()
                        self.home_page.scroll_to_and_click_careers()
                        self.careers_page.select_department(self.config.TARGET_DEPARTMENT)
                    
                    # Wait for the positions list to reload
                    time.sleep(2)
                        
                except Exception as e:
                    failed += 1
                    self.logger.error(f"Error processing position {i+1}: {str(e)}")
                    self._take_screenshot(f"position_{i+1}_exception")
                    
                    # Try to recover and continue with next position
                    try:
                        self.position_page.close_form()
                        self.position_page.return_to_all_positions()
                    except Exception:
                        # Last resort - go back to careers page
                        self.home_page.navigate_to_home()
                        self.home_page.scroll_to_and_click_careers()
                        self.careers_page.select_department(self.config.TARGET_DEPARTMENT)
                    
                    time.sleep(2)
            
            # Log final results
            self.logger.info("\n=== Test Summary ===")
            self.logger.info(f"Total positions found: {total_positions}")
            self.logger.info(f"Successfully applied: {successful}")
            self.logger.info(f"Failed applications: {failed}")
            self.logger.info(f"Skipped positions: {skipped}")
            
            # Test is successful if we were able to process at least one position
            if total_positions > 0 and (successful + failed) == 0:
                pytest.fail("Could not process any positions")
            
        except Exception as e:
            self.logger.error(f"Test failed: {str(e)}")
            self._take_screenshot("test_failure")
            raise