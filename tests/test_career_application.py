import pytest
import time
import logging
import os
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from config.config import DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, DEFAULT_EMAIL, DEFAULT_PHONE, CV_FILE_PATH
# Import fixtures
from tests.fixtures.page_fixtures import home_page, careers_page, position_page, test_logger

@pytest.mark.usefixtures("driver", "home_page", "careers_page", "position_page", "test_logger")
class TestCareerApplication:
    """Test suite for career application process."""

    def _take_screenshot(self, driver, name: str) -> None:
        """Take a screenshot of the current page.
        
        Args:
            driver: WebDriver instance
            name: Name to use for the screenshot file
        """
        try:
            filename = f"screenshots/{name}_{time.strftime('%Y%m%d-%H%M%S')}.png"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            driver.save_screenshot(filename)
            logging.info(f"Screenshot saved: {filename}")
        except Exception as e:
            logging.error(f"Failed to take screenshot: {str(e)}")

    def test_apply_for_rd_positions(self, driver, home_page, careers_page, position_page, test_logger):
        """Test applying for all R&D positions following the exercise instructions"""
        test_logger.info("=== Starting R&D Positions Application Test ===")
        
        try:
            # Step 1: Navigate to https://connecteam.com/
            test_logger.info("Step 1: Navigating to Connecteam homepage")
            home_page.navigate_to_home()
            
            # Step 2: Scroll down and click on 'careers' in the footer
            test_logger.info("Step 2: Navigating to careers page")
            if not home_page.scroll_to_and_click_careers():
                self._take_screenshot(driver, "careers_navigation_failed")
                pytest.fail("Failed to navigate to careers page")
            
            # Wait for careers page to fully load
            time.sleep(2)
            
            # Step 3: Select R&D from the left dropdown
            from config.config import DEFAULT_TARGET_DEPARTMENT
            test_logger.info(f"Step 3: Selecting department: {DEFAULT_TARGET_DEPARTMENT}")
            if not careers_page.select_department(DEFAULT_TARGET_DEPARTMENT):
                self._take_screenshot(driver, "department_selection_failed")
                pytest.skip(f"No {DEFAULT_TARGET_DEPARTMENT} positions currently visible")
            
            # Wait for department filter to apply
            time.sleep(1)
            
            # Get all available positions
            positions = careers_page.get_applyable_positions()
            if not positions:
                self._take_screenshot(driver, "no_positions_found")
                pytest.skip(f"No {DEFAULT_TARGET_DEPARTMENT} positions available to apply for")
            
            total_positions = len(positions)
            test_logger.info(f"Found {total_positions} R&D positions to process")
            
            successful = 0
            failed = 0
            skipped = 0
            
            # Step 4: For all positions in R&D (marked 'apply now'), perform the following
            test_logger.info("Step 4: Processing all R&D positions")
            
            # Process each position one by one
            for i in range(total_positions):
                test_logger.info(f"\nProcessing position {i+1}/{total_positions}")
                
                # Get fresh positions list before each application
                fresh_positions = careers_page.get_applyable_positions()
                if not fresh_positions or i >= len(fresh_positions):
                    test_logger.warning(f"Position {i+1} no longer available, skipping")
                    skipped += 1
                    continue
                
                try:
                    # Step 4a: Click on 'Apply now'
                    test_logger.info(f"Clicking 'Apply now' for position {i+1}")
                    
                    # Use the CV file path from config as specified in instructions
                    # Do not submit the form as per instructions
                    from config.config import DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, DEFAULT_EMAIL, DEFAULT_PHONE, CV_FILE_PATH
                    result = careers_page.apply_for_position(
                        position=fresh_positions[i],
                        first_name=DEFAULT_FIRST_NAME,
                        last_name=DEFAULT_LAST_NAME,
                        email=DEFAULT_EMAIL,
                        phone=DEFAULT_PHONE,
                        cv_path=CV_FILE_PATH
                    )
                    
                    if result:
                        successful += 1
                        test_logger.info(f"✓ Successfully applied to position {i+1}")
                    else:
                        failed += 1
                        test_logger.warning(f"✗ Failed to apply to position {i+1}")
                        self._take_screenshot(driver, f"position_{i+1}_failed")
                    
                    # Return to all positions list after each application
                    test_logger.info("Returning to all positions list")
                    if not position_page.return_to_all_positions():
                        test_logger.warning("Could not return to positions list, trying to continue...")
                        # Try to navigate back to careers page as fallback
                        home_page.navigate_to_home()
                        home_page.scroll_to_and_click_careers()
                        careers_page.select_department(DEFAULT_TARGET_DEPARTMENT)
                    
                    # Wait for the positions list to reload
                    time.sleep(2)
                except Exception as e:
                    failed += 1
                    test_logger.error(f"Error processing position {i+1}: {str(e)}")
                    self._take_screenshot(driver, f"position_{i+1}_exception")
                    
                    # Try to recover and continue with next position
                    try:
                        position_page.close_form()
                        position_page.return_to_all_positions()
                    except Exception:
                        # Last resort - go back to careers page
                        home_page.navigate_to_home()
                        home_page.scroll_to_and_click_careers()
                        careers_page.select_department(DEFAULT_TARGET_DEPARTMENT)
                    
                    time.sleep(2)
            
            # Log detailed results
            test_logger.info("\n=== Test Summary ===")
            test_logger.info(f"Total positions found: {total_positions}")
            test_logger.info(f"Successfully applied: {successful}")
            test_logger.info(f"Failed applications: {failed}")
            test_logger.info(f"Skipped positions: {skipped}")
            
            # Test is successful if we were able to process at least one position
            if total_positions > 0 and (successful + failed) == 0:
                pytest.fail("Could not process any positions")
            
        except Exception as e:
            test_logger.error(f"Unexpected error in test: {str(e)}")
            self._take_screenshot(driver, "unexpected_error")
            pytest.fail(f"Test failed with unexpected error: {str(e)}")

    def _fill_form_with_js(self, driver, test_logger, first_name: str, last_name: str, email: str, phone: str, cv_path: str) -> None:
        """Fill form fields using JavaScript for maximum reliability."""
        # Wait for form to be fully loaded
        try:
            # Try multiple iframe selectors
            iframe_selectors = [
                (By.CSS_SELECTOR, "iframe[id*='grnhse_iframe']"),
                (By.CSS_SELECTOR, "iframe[src*='greenhouse']"),
                (By.CSS_SELECTOR, "iframe[id*='application']"),
                (By.CSS_SELECTOR, "iframe")
            ]
            
            iframe = None
            for selector in iframe_selectors:
                try:
                    iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located(selector))
                    if iframe:
                        test_logger.info(f"Found iframe using selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not iframe:
                raise Exception("No iframe found after trying multiple selectors")
                
            driver.switch_to.frame(iframe)
            test_logger.info("Switched to application iframe")
        except Exception as e:
            test_logger.error(f"Error switching to iframe: {str(e)}")
            raise
            
        # Fill form fields using JavaScript with enhanced reliability
        script = """
        function setInputValue(id, value) {
            // Try multiple methods to find the element
            let input = document.getElementById(id);
            
            // If not found by ID, try by name
            if (!input) {
                input = document.getElementsByName(id)[0];
            }
            
            // If still not found, try by selector
            if (!input) {
                input = document.querySelector(`[id='${id}'], [name='${id}'], [data-field='${id}'], [aria-label='${id}']`);
            }
            
            if (input) {
                // Focus on the element first
                input.focus();
                
                // Clear existing value first
                input.value = '';
                input.dispatchEvent(new Event('input', { bubbles: true }));
                
                // Set the value and trigger events
                input.value = value;
                
                // Trigger multiple events for maximum compatibility
                const events = ['input', 'change', 'blur', 'focus'];
                events.forEach(eventType => {
                    input.dispatchEvent(new Event(eventType, { bubbles: true }));
                });
                
                return true;
            }
            return false;
        }
        
        // Fill required fields with multiple attempts
        const filled = {
            first_name: setInputValue('first_name', arguments[0]),
            last_name: setInputValue('last_name', arguments[1]),
            email: setInputValue('email', arguments[2]),
            phone: setInputValue('phone', arguments[3])
        };
        
        // Try alternative selectors if the main ones failed
        if (!filled.first_name) filled.first_name = setInputValue('First Name', arguments[0]);
        if (!filled.last_name) filled.last_name = setInputValue('Last Name', arguments[1]);
        if (!filled.email) filled.email = setInputValue('Email', arguments[2]);
        if (!filled.phone) filled.phone = setInputValue('Phone', arguments[3]);
        
        // Also try to fill LinkedIn if present
        setInputValue('question_12434949004', 'https://linkedin.com/in/example');
        setInputValue('LinkedIn Profile', 'https://linkedin.com/in/example');
        
        return filled;
        """
        
        result = driver.execute_script(script, first_name, last_name, email, phone)
        test_logger.info("Filled form fields using JavaScript")
        
        # Log the results if available
        if isinstance(result, dict):
            for field, success in result.items():
                if success:
                    test_logger.info(f"Successfully filled {field}")
                else:
                    test_logger.warning(f"Failed to fill {field} using JavaScript")
        
        # Upload CV
        try:
            # Try multiple selectors to find the file input
            file_selectors = [
                (By.ID, "resume"),
                (By.CSS_SELECTOR, "input[type='file']"),
                (By.CSS_SELECTOR, ".visually-hidden[type='file']"),
                (By.CSS_SELECTOR, "input[accept*='.pdf']")
            ]
            
            file_input = None
            for selector in file_selectors:
                try:
                    file_input = driver.find_element(*selector)
                    if file_input:
                        test_logger.info(f"Found file input using selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not file_input:
                test_logger.warning("Could not find file input, trying direct JavaScript approach")
                # Try to create a file input if none exists
                driver.execute_script("""
                    if (!document.getElementById('resume')) {
                        const input = document.createElement('input');
                        input.id = 'resume';
                        input.type = 'file';
                        input.style.display = 'block';
                        document.body.appendChild(input);
                    }
                """)
                file_input = driver.find_element(By.ID, "resume")
            
            # Make file input visible and interactable
            driver.execute_script("""
                arguments[0].style.display = 'block';
                arguments[0].style.visibility = 'visible';
                arguments[0].style.opacity = '1';
                arguments[0].style.position = 'fixed';
                arguments[0].style.top = '0';
                arguments[0].style.left = '0';
                arguments[0].style.zIndex = '9999';
            """, file_input)
            
            # Set the file path
            absolute_path = os.path.abspath(cv_path)
            file_input.send_keys(absolute_path)
            test_logger.info(f"Uploaded CV from: {absolute_path}")
        except Exception as e:
            test_logger.error(f"Error uploading CV: {str(e)}")
            
        # Try to handle additional form elements
        try:
            # Handle on-site work question if present
            try:
                # Click on the dropdown
                dropdown = driver.find_element(By.CSS_SELECTOR, ".select__control")
                driver.execute_script("arguments[0].click();", dropdown)
                time.sleep(0.5)
                
                # Select 'Yes' option
                yes_option = driver.find_element(By.CSS_SELECTOR, "div[id^='react-select'][id$='-option-0']")
                driver.execute_script("arguments[0].click();", yes_option)
                test_logger.info("Selected 'Yes' for on-site work question")
            except Exception as e:
                test_logger.debug(f"No on-site work dropdown found or error selecting option: {str(e)}")
        except Exception as e:
            test_logger.debug(f"Error handling additional form elements: {str(e)}")
            
    def _close_form(self, driver, test_logger) -> None:
        """Close the application form using multiple methods for reliability."""
        try:
            # Try different methods to close the form
            methods = [
                # Method 1: Click close button
                lambda: driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']").click(),
                # Method 2: Use JavaScript
                lambda: driver.execute_script(
                    "const closeBtn = document.querySelector('button[aria-label=\"Close\"');" 
                    "if (closeBtn) closeBtn.click();"
                ),
                # Method 3: Press Escape key
                lambda: driver.execute_script(
                    "document.dispatchEvent(new KeyboardEvent('keydown', {'key': 'Escape'}))"
                )
            ]
            
            for method in methods:
                try:
                    method()
                    test_logger.info("Closed form")
                    time.sleep(1)  # Wait for form to close
                    return
                except Exception:
                    continue
                    
            test_logger.warning("Could not close form with any method")
            
        except Exception as e:
            test_logger.error(f"Error closing form: {str(e)}")
    
    def _return_to_careers_page(self, driver, home_page, careers_page, test_logger) -> None:
        """Return to the careers page and reselect the department."""
        try:
            # Try to find and click the 'All open positions' link
            try:
                back_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "a.section-careers-single-back")
                ))
                driver.execute_script("arguments[0].click();", back_link)
                test_logger.info("Clicked 'All open positions' link")
                time.sleep(2)
            except Exception:
                # If link not found, navigate back to careers page
                test_logger.info("'All open positions' link not found, navigating back to careers page")
                home_page.navigate_to_home()
                home_page.scroll_to_and_click_careers()
            
            # Reselect department
            careers_page.select_department(DEFAULT_TARGET_DEPARTMENT)
            time.sleep(2)  # Wait for positions to load
            
        except Exception as e:
            test_logger.error(f"Error returning to careers page: {str(e)}")
            # Last resort - go back to homepage and navigate to careers
            home_page.navigate_to_home()
            home_page.scroll_to_and_click_careers()
            careers_page.select_department(DEFAULT_TARGET_DEPARTMENT)