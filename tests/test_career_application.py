import pytest
import time
import logging
from selenium.common.exceptions import TimeoutException
from pages.home_page import HomePage
from pages.careers_page import CareersPage
from config import config

@pytest.mark.usefixtures("driver")
class TestCareerApplication:
    @pytest.fixture(autouse=True)
    def setup(self, driver):
        """Setup test class with page objects and logging"""
        self.logger = logging.getLogger(__name__)
        self.home_page = HomePage(driver)
        self.careers_page = CareersPage(driver)

    def test_apply_for_rd_positions(self):
        """Test applying for all R&D positions"""
        self.logger.info("=== Starting R&D Positions Application Test ===")
        
        try:
            # Navigate to careers page and handle cookies
            self.home_page.navigate_to_home()
            
            # Scroll to and click careers link
            if not self.home_page.scroll_to_and_click_careers():
                pytest.fail("Failed to navigate to careers page")
            
            # Select R&D department
            if not self.careers_page.select_department(config.TARGET_DEPARTMENT):
                pytest.skip(f"No {config.TARGET_DEPARTMENT} positions currently visible")
            
            # Get available positions
            positions = self.careers_page.get_applyable_positions()
            if not positions:
                pytest.skip(f"No {config.TARGET_DEPARTMENT} positions available to apply for")
            
            self.logger.info(f"Found {len(positions)} R&D positions to process")
            
            successful = 0
            failed = 0
            
            # Process each position
            for i, position in enumerate(positions, 1):
                self.logger.info(f"\nProcessing position {i}/{len(positions)}")
                
                try:
                    result = self.careers_page.apply_for_position(
                        position=position,
                        first_name=config.FIRST_NAME,
                        last_name=config.LAST_NAME,
                        email=config.EMAIL,
                        phone=config.PHONE,
                        cv_path=config.CV_FILE_PATH
                    )
                    
                    if result:
                        successful += 1
                        self.logger.info(f"✓ Successfully applied to position {i}")
                    else:
                        failed += 1
                        self.logger.warning(f"✗ Failed to apply to position {i}")
                        
                except Exception as e:
                    failed += 1
                    self.logger.error(f"Error applying to position {i}: {str(e)}")
                
                time.sleep(0.5)  # Brief pause between applications
            
            # Log final results
            self.logger.info("\n=== Test Summary ===")
            self.logger.info(f"Total positions processed: {len(positions)}")
            self.logger.info(f"Successfully applied: {successful}")
            self.logger.info(f"Failed applications: {failed}")
            
            # Fail if no applications succeeded
            assert successful > 0, f"Failed to successfully apply to any of the {len(positions)} positions"
            
        except Exception as e:
            self.logger.error(f"Test failed: {str(e)}")
            raise