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
        """Navigate to home page and handle initial setup"""
        try:
            self.driver.get("https://connecteam.com/")
            self.logger.info("Navigated to Connecteam homepage")
            self._handle_cookies()
        except Exception as e:
            self.logger.error(f"Failed to navigate to homepage: {str(e)}")
            raise
    
    def _handle_cookies(self):
        """Handle cookie banner with retries and JS fallback"""
        try:
            # Wait for banner to be present
            banner = self._find_element(self.COOKIE_BANNER)
            
            if banner and banner.is_displayed():
                # Try normal click first
                try:
                    accept_btn = self._find_element(self.COOKIE_ACCEPT_BTN)
                    if accept_btn:
                        accept_btn.click()
                except:
                    # Fallback to JS click
                    self.driver.execute_script(
                        "document.querySelector('#onetrust-accept-btn-handler').click();"
                    )
                
                # Wait for banner to disappear
                try:
                    self.wait.until(EC.invisibility_of_element_located(self.COOKIE_BANNER.locator))
                except TimeoutException:
                    # Force hide banner if it's still visible
                    self.driver.execute_script(
                        "document.querySelector('#onetrust-banner-sdk').style.display='none';"
                    )
                self.logger.info("Handled cookie banner")
        except:
            # Banner might not be present, continue
            self.logger.info("Cookie banner not present or already handled")
            pass

    def scroll_to_and_click_careers(self):
        """Scroll to and click the careers link in footer"""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            try:
                # Ensure cookie banner is handled
                self._handle_cookies()
                
                # Scroll to footer
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.9);")
                time.sleep(0.5)
                
                # Find and scroll to careers link
                careers_link = self._find_element(self.CAREERS_LINK)
                if not careers_link:
                    raise Exception("Failed to find careers link")
                
                self._scroll_to_element(self.CAREERS_LINK)
                time.sleep(0.5)
                
                # Try JS click first
                self.driver.execute_script("arguments[0].click();", careers_link)
                
                # Wait for navigation
                self.wait.until(lambda driver: "careers" in driver.current_url.lower())
                self.logger.info("Successfully navigated to careers page")
                return True
                
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed to navigate to careers page: {str(e)}")
                if attempt == max_attempts - 1:
                    self._take_screenshot("careers_navigation_failed")
                    raise Exception(f"Failed to navigate to careers page after {max_attempts} attempts: {e}")
                time.sleep(1)
                continue
            
        return False