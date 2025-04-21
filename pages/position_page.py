from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from pages.base_page import BasePage, ElementInfo
import logging
import time
import os

class PositionPage(BasePage):
    """Page Object for handling individual position application forms"""
    
    # Application form container and iframe
    APPLICATION_FORM = ElementInfo(
        locator=(By.ID, "application-form"),
        description="Application form element"
    )
    
    GREENHOUSE_IFRAME = ElementInfo(
        locator=(By.CSS_SELECTOR, "iframe[src*='greenhouse'], iframe[id*='grnhse']"),
        description="Greenhouse iframe"
    )
    
    # Form input fields with exact selectors from HTML
    FIRST_NAME_INPUT = ElementInfo(
        locator=(By.ID, "first_name"),
        description="First name input"
    )
    
    LAST_NAME_INPUT = ElementInfo(
        locator=(By.ID, "last_name"),
        description="Last name input"
    )
    
    EMAIL_INPUT = ElementInfo(
        locator=(By.ID, "email"),
        description="Email input"
    )
    
    PHONE_INPUT = ElementInfo(
        locator=(By.ID, "phone"),
        description="Phone input"
    )
    
    # Resume upload elements
    CV_UPLOAD_BUTTON = ElementInfo(
        locator=(By.CSS_SELECTOR, ".file-upload__wrapper .btn"),
        description="CV upload button"
    )
    
    CV_UPLOAD_INPUT = ElementInfo(
        locator=(By.ID, "resume"),
        description="CV upload input field"
    )
    
    # Additional fields
    LINKEDIN_INPUT = ElementInfo(
        locator=(By.ID, "question_12434949004"),
        description="LinkedIn Profile input"
    )
    
    # Onsite work dropdown
    ONSITE_SELECT_CONTAINER = ElementInfo(
        locator=(By.CSS_SELECTOR, ".select__control"),
        description="On-site work question dropdown container"
    )
    
    ONSITE_SELECT = ElementInfo(
        locator=(By.ID, "question_12477665004"),
        description="On-site work question select input"
    )
    
    ONSITE_YES_OPTION = ElementInfo(
        locator=(By.CSS_SELECTOR, "div[id^='react-select'][id$='-option-0']"),
        description="'Yes' option for on-site work question"
    )
    
    # Submit button
    SUBMIT_BUTTON = ElementInfo(
        locator=(By.CSS_SELECTOR, ".application--submit button[type='submit']"),
        description="Submit application button"
    )
    
    # Close button for modal
    CLOSE_MODAL_BTN = ElementInfo(
        locator=(By.CSS_SELECTOR, "button[aria-label='Close']"),
        description="Close form modal button"
    )
    
    # Back to all positions link
    BACK_TO_POSITIONS_LINK = ElementInfo(
        locator=(By.CSS_SELECTOR, "a.section-careers-single-back"),
        description="Back to all open positions link"
    )

    def __init__(self, driver):
        super().__init__(driver)
        self.logger = logging.getLogger(__name__)

    def fill_application_form(self, first_name: str, last_name: str, 
                            email: str, phone: str, cv_path: str,
                            linkedin: str = None) -> bool:
        """Fill out the position application form without submitting it
        
        As per instructions, we only fill the fields and upload the CV but don't submit
        """
        try:
            # Wait for iframe to load and switch to it
            self.logger.info("Waiting for Greenhouse iframe to load")
            try:
                # Try to enter the Greenhouse iframe with scrolling
                self._enter_greenhouse_iframe(max_scrolls=8)
                self.logger.info("Successfully switched to Greenhouse iframe")
            except Exception as e:
                self.logger.warning(f"Could not switch to iframe: {str(e)}")
                self.logger.info("Proceeding with direct form interaction")
            
            # Wait for form to be present
            self.logger.info("Waiting for application form to load")
            try:
                self.wait.until(EC.presence_of_element_located(self.APPLICATION_FORM.locator))
                self.logger.info("Application form found")
            except TimeoutException:
                self.logger.warning("Application form not found by ID, continuing anyway")
            
            # Fill in the form fields with explicit waits
            self.logger.info("Starting to fill form fields")
            
            # Step 4b.1-4: Fill basic information fields
            field_data = [
                (self.FIRST_NAME_INPUT, first_name, "First name"),
                (self.LAST_NAME_INPUT, last_name, "Last name"),
                (self.EMAIL_INPUT, email, "Email"),
                (self.PHONE_INPUT, phone, "Phone")
            ]
            
            for field_info, value, field_name in field_data:
                try:
                    # Wait for field to be visible and interactable
                    field = self.wait.until(EC.element_to_be_clickable(field_info.locator))
                    
                    # Clear and fill the field
                    field.clear()
                    field.send_keys(value)
                    self.logger.info(f"Filled {field_name}: {value}")
                    time.sleep(0.3)  # Small delay between fields for stability
                except Exception as e:
                    self.logger.error(f"Failed to fill {field_name}: {str(e)}")
                    return False

            # Step 4b.5: Upload CV file
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cv_full_path = os.path.join(project_root, cv_path)
            if not os.path.exists(cv_full_path):
                self.logger.error(f"CV file not found at path: {cv_full_path}")
                return False
            try:
                # First try to find the upload button to make the input visible
                upload_button = self.wait.until(EC.element_to_be_clickable(self.CV_UPLOAD_BUTTON.locator))
                self.logger.info("Found CV upload button")
                # Don't actually click it as we'll use the hidden input directly
            except Exception:
                self.logger.warning("Could not find CV upload button, will try direct input")
            # Now find the file input and send the file path
            cv_input = self.wait.until(EC.presence_of_element_located(self.CV_UPLOAD_INPUT.locator))
            # Make sure the input is interactable (even if hidden)
            self.driver.execute_script("arguments[0].style.opacity = '1'; arguments[0].style.display = 'block';", cv_input)
            # Send the absolute path to the file input
            cv_input.send_keys(cv_full_path)
            self.logger.info(f"Uploaded CV from: {cv_full_path}")
            time.sleep(1)  # Wait for upload to process
            # Fill LinkedIn field if provided (optional)
            if linkedin:
                try:
                    linkedin_field = self.wait.until(EC.element_to_be_clickable(self.LINKEDIN_INPUT.locator))
                    linkedin_field.clear()
                    linkedin_field.send_keys(linkedin)
                    self.logger.info(f"Filled LinkedIn profile: {linkedin}")
                except Exception as e:
                    self.logger.warning(f"Could not fill LinkedIn field: {str(e)}")
                    # Continue anyway as this might be optional
            # Handle on-site work dropdown if present
            try:
                # Click the dropdown to open it
                dropdown_container = self.wait.until(EC.element_to_be_clickable(self.ONSITE_SELECT_CONTAINER.locator))
                dropdown_container.click()
                time.sleep(0.5)  # Wait for dropdown to open
                # Select 'Yes' option
                try:
                    yes_option = self.wait.until(EC.element_to_be_clickable(self.ONSITE_YES_OPTION.locator))
                    yes_option.click()
                    self.logger.info("Selected 'Yes' for on-site work question")
                except TimeoutException:
                    # If can't find the option by CSS, try JavaScript
                    self.driver.execute_script("""
                        const options = document.querySelectorAll('[id^=\"react-select\"][id$=\"-option-0\"]');
                        if (options.length > 0) options[0].click();
                    """)
                    self.logger.info("Selected on-site option via JavaScript")
                try:
                    os.makedirs("screenshots", exist_ok=True)
                    self.driver.save_screenshot(f"screenshots/form_filled_{int(time.time())}.png")
                    self.logger.info("Saved screenshot of filled form")
                except Exception as e:
                    self.logger.warning(f"Could not save screenshot: {str(e)}")
                    
                # Log form filling success
                self.logger.info(f"Successfully filled form with: {first_name} {last_name}, {email}, {phone}")
                    
                # Return success
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to upload CV: {str(e)}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error filling application form: {str(e)}")
            return False

    def _enter_greenhouse_iframe(self, max_scrolls=5):
        """Enter the Greenhouse iframe with scrolling to ensure it's loaded"""
        # First switch to default content to ensure we're not already in an iframe
        try:
            self.driver.switch_to.default_content()
        except Exception:
            pass
            
        # Try to find the iframe with scrolling if needed
        iframe = None
        for scroll_attempt in range(max_scrolls):
            try:
                # Try multiple selectors for the iframe
                selectors = [
                    (By.CSS_SELECTOR, "iframe[src*='greenhouse'], iframe[id*='grnhse']"),
                    (By.CSS_SELECTOR, "iframe[id*='application']"),
                    (By.CSS_SELECTOR, "iframe[title*='Application']"),
                    (By.CSS_SELECTOR, "iframe")
                ]
                
                for selector in selectors:
                    try:
                        iframe = self._find_element(ElementInfo(locator=selector, description="Iframe selector"), timeout=2)
                        if iframe:
                            self.logger.info(f"Found iframe using selector: {selector}")
                            break
                    except Exception:
                        continue
                        
                if iframe:
                    break
                    
                # Scroll down to try to find the iframe
                self.driver.execute_script(f"window.scrollBy(0, {300 * (scroll_attempt + 1)});")
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.debug(f"Scroll attempt {scroll_attempt+1} exception: {str(e)}")
                # Continue to next scroll attempt
        
        if not iframe:
            raise Exception("Greenhouse iframe not found after scrolling")
            
        # Switch to the iframe
        self.driver.switch_to.frame(iframe)
        
        # Wait for form to be present in iframe with multiple checks
        for field in [self.FIRST_NAME_INPUT, self.LAST_NAME_INPUT, self.EMAIL_INPUT]:
            try:
                if self._find_element(field, timeout=2):
                    return True  # Successfully found a field
            except Exception:
                continue
                
        # If we get here, we're in the iframe but couldn't find expected fields
        # This is still considered a success since we're in the iframe
        return True
        
    def _fill_input_field(self, element_info, value):
        """Fill an input field with the given value using multiple methods for reliability"""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                element = self._find_element(element_info, timeout=5)
                if not element:
                    raise Exception(f"Element {element_info.description} not found")
                    
                # Scroll element into view
                self._scroll_to_element(element)
                time.sleep(0.2)
                
                # Try multiple methods to fill the field
                methods = [
                    # Method 1: Standard WebDriver
                    lambda: {
                        "action": lambda: self._standard_input_fill(element, value),
                        "description": "Standard WebDriver"
                    },
                    # Method 2: JavaScript
                    lambda: {
                        "action": lambda: self._js_input_fill(element, value),
                        "description": "JavaScript"
                    },
                    # Method 3: Action chains
                    lambda: {
                        "action": lambda: self._action_chains_fill(element, value),
                        "description": "Action Chains"
                    }
                ]
                
                # Try each method until one succeeds
                for method in methods:
                    try:
                        method_info = method()
                        method_info["action"]()
                        self.logger.debug(f"Filled {element_info.description} using {method_info['description']}")
                        return True
                    except Exception as e:
                        self.logger.debug(f"Method {method_info['description']} failed: {str(e)}")
                        continue
                        
                # If we get here, all methods failed on this attempt
                if attempt == max_attempts - 1:
                    raise Exception(f"All input methods failed for {element_info.description}")
                    
                time.sleep(0.5)  # Wait before retry
                    
            except Exception as e:
                if attempt == max_attempts - 1:
                    self.logger.error(f"Failed to fill {element_info.description} after {max_attempts} attempts: {str(e)}")
                    return False
                self.logger.debug(f"Attempt {attempt+1} failed: {str(e)}, retrying...")
                time.sleep(0.5)
                
        return False
        
    def _standard_input_fill(self, element, value):
        """Standard WebDriver method to fill an input field (do NOT clear before filling)"""
        element.send_keys(value)

        
    def _js_input_fill(self, element, value):
        """Use JavaScript to fill an input field"""
        self.driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            element, value
        )
        
    def _action_chains_fill(self, element, value):
        """Use Action Chains to fill an input field (do NOT clear before filling)"""
        actions = ActionChains(self.driver)
        actions.click(element)
        actions.pause(0.1)
        actions.send_keys(value)
        actions.perform()

    
    def close_form(self):
        """Close the application form modal"""
        try:
            # First make sure we're back in the default content
            try:
                self.driver.switch_to.default_content()
            except Exception:
                pass
                
            # Try different methods to close the form
            methods = [
                # Method 1: Find and click the close button
                lambda: {
                    "action": lambda: self._find_element(self.CLOSE_MODAL_BTN).click(),
                    "log": "Clicked close button"
                },
                # Method 2: Use JavaScript to click the close button
                lambda: {
                    "action": lambda: self.driver.execute_script(
                        "const closeBtn = document.querySelector('button[aria-label=\"Close\"]'); "
                        "if (closeBtn) closeBtn.click();"
                    ),
                    "log": "Closed form via JavaScript"
                },
                # Method 3: Press Escape key
                lambda: {
                    "action": lambda: self.driver.execute_script(
                        "document.dispatchEvent(new KeyboardEvent('keydown', {'key': 'Escape'}))"
                    ),
                    "log": "Sent Escape key to close form"
                }
            ]
            
            for method in methods:
                try:
                    method_info = method()
                    method_info["action"]()
                    self.logger.info(method_info["log"])
                    time.sleep(0.5)  # Wait for modal to close
                    return
                except Exception:
                    continue
                    
            self.logger.warning("Could not close form with any method")
            
        except Exception as e:
            self.logger.error(f"Error closing form: {str(e)}")
    
    def return_to_all_positions(self):
        """Click on 'All open positions' link to return to the positions list"""
        try:
            # First make sure we're back in the default content
            try:
                self.driver.switch_to.default_content()
            except Exception:
                pass
            
            # Try to find and click the 'All open positions' link
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # Find the back link
                    back_link = self._find_element(self.BACK_TO_POSITIONS_LINK, timeout=5)
                    if not back_link:
                        raise Exception("Back to positions link not found")
                    
                    # Scroll to the link to ensure it's visible
                    self._scroll_to_element(back_link)
                    time.sleep(0.5)
                    
                    # Click using JavaScript for reliability
                    self.driver.execute_script("arguments[0].click();", back_link)
                    
                    # Wait for navigation to complete
                    start_time = time.time()
                    while time.time() - start_time < 10:  # 10 second timeout
                        if "careers" in self.driver.current_url.lower() and "gh_jid" not in self.driver.current_url.lower():
                            self.logger.info("Successfully returned to all positions")
                            time.sleep(1)  # Wait for page to stabilize
                            return True
                        time.sleep(0.5)
                        
                    # If we get here, navigation didn't complete
                    if attempt == max_attempts - 1:
                        raise TimeoutException("Navigation to positions page timed out")
                        
                except Exception as e:
                    if attempt == max_attempts - 1:
                        self.logger.error(f"Failed to return to positions after {max_attempts} attempts: {str(e)}")
                        return False
                    self.logger.warning(f"Return attempt {attempt+1} failed: {str(e)}, retrying...")
                    time.sleep(1)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error returning to all positions: {str(e)}")
            return False
