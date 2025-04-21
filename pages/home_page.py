from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage, ElementInfo
import logging
import time

class HomePage(BasePage):
    """Page Object for the Connecteam Home Page"""
    
    # Element definitions with descriptions
    CAREERS_LINK = ElementInfo(
        locator=(By.XPATH, "//footer//a[text()='Careers']"),
        description="Careers link in footer"
    )
    
    # Updated cookie banner selectors
    COOKIE_BANNER = ElementInfo(
        locator=(By.ID, "onetrust-banner-sdk"),
        description="Cookie consent banner"
    )
    
    COOKIE_ACCEPT_BTN = ElementInfo(
        locator=(By.ID, "onetrust-accept-btn-handler"),
        description="Accept cookies button"
    )
    
    def __init__(self, driver):
        super().__init__(driver)
        self.logger = logging.getLogger(__name__)
        self.navigate_to_home()
    
    def navigate_to_home(self):
        """Navigate to home page and handle initial setup - optimized"""
        try:
            # Set page load strategy to eager to speed up navigation
            self.driver.execute_script("window.performance.setResourceTimingBufferSize(500);")
            
            # Navigate to homepage
            self.driver.get("https://connecteam.com/")
            self.logger.info("Navigated to Connecteam homepage")
            
            # Handle cookies immediately without waiting
            self._handle_cookies()
            
            # Return success
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate to homepage: {str(e)}")
            raise
    
    def _handle_cookies(self):
        """Handle cookie banner with optimized approach"""
        # Skip waiting and immediately try to handle cookies
        try:
            # Use JavaScript to check if banner exists and handle it in one go
            cookie_handled = self.driver.execute_script("""
                // Try to find the cookie banner
                const banner = document.getElementById('onetrust-banner-sdk');
                if (!banner || !banner.offsetParent) {
                    // Banner doesn't exist or is not visible
                    return true;
                }
                
                // Try to click the accept button
                const acceptBtn = document.getElementById('onetrust-accept-btn-handler');
                if (acceptBtn) {
                    acceptBtn.click();
                    return true;
                }
                
                // If no button found, try to hide the banner
                banner.style.display = 'none';
                if (banner.parentNode) {
                    banner.parentNode.removeChild(banner);
                }
                return true;
            """)
            
            if cookie_handled:
                self.logger.info("Cookie banner handled via JavaScript")
                return True
                
            # Fallback to Selenium approach if JS method fails
            banner = self._find_element(self.COOKIE_BANNER, timeout=2)
            if not banner or not banner.is_displayed():
                self.logger.info("Cookie banner not detected")
                return True
                
            # Try direct click on button
            accept_btn = self._find_element(self.COOKIE_ACCEPT_BTN, timeout=1)
            if accept_btn and accept_btn.is_displayed():
                accept_btn.click()
                self.logger.info("Clicked cookie accept button")
                return True
                
            # Last resort - force hide via JS again
            self.driver.execute_script("""
                const elements = document.querySelectorAll('#onetrust-banner-sdk, .onetrust-pc-dark-filter');
                elements.forEach(el => {
                    if (el) {
                        el.style.display = 'none';
                        if (el.parentNode) el.parentNode.removeChild(el);
                    }
                });
            """)
            self.logger.info("Removed cookie elements from DOM")
            return True
            
        except Exception as e:
            self.logger.warning(f"Error handling cookies: {str(e)}")
            # Continue test execution even if cookie handling fails
            return True

    def scroll_to_and_click_careers(self):
        """Scroll to and click the careers link in footer - optimized version"""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                # Direct scroll to bottom of page where footer is located
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Try to find the careers link with a short timeout first
                careers_link = self._find_element(self.CAREERS_LINK, timeout=2)
                
                # If not found, try an alternative approach with direct JS selector
                if not careers_link:
                    self.logger.info("Trying alternative method to find careers link")
                    # Try to find using JavaScript
                    careers_link = self.driver.execute_script(
                        "return document.evaluate('//footer//a[text()=\"Careers\"]', document, null, "
                        "XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
                    )
                    
                    if not careers_link:
                        # Try with a more general selector as fallback
                        careers_link = self.driver.execute_script(
                            "return document.querySelector('footer a[href*=\"careers\"]');"
                        )
                
                if not careers_link:
                    if attempt < max_attempts - 1:
                        self.logger.warning(f"Careers link not found on attempt {attempt+1}, retrying...")
                        time.sleep(1)
                        continue
                    else:
                        raise Exception("Failed to find careers link after multiple attempts")
                
                # Ensure element is in view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", careers_link)
                
                # Click directly with JS for reliability
                self.driver.execute_script("arguments[0].click();", careers_link)
                
                # Wait for navigation with a more specific condition
                start_time = time.time()
                while time.time() - start_time < 10:  # 10 second timeout
                    if "careers" in self.driver.current_url.lower():
                        self.logger.info("Successfully navigated to careers page")
                        return True
                    time.sleep(0.5)
                    
                # If we get here, navigation didn't complete in time
                raise TimeoutException("Navigation to careers page timed out")
                
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed to navigate to careers page: {str(e)}")
                if attempt == max_attempts - 1:
                    self._take_screenshot("careers_navigation_failed")
                    raise Exception(f"Failed to navigate to careers page after {max_attempts} attempts: {e}")
                time.sleep(1)
            
        return False