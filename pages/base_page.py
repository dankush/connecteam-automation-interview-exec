from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import logging
import time
from typing import Optional, List, Union, Tuple
from dataclasses import dataclass
from functools import wraps
from selenium.webdriver.common.by import By

@dataclass
class ElementInfo:
    """Data class for element information"""
    locator: Tuple[str, str]
    description: str
    timeout: int = 10

class BasePage:
    """Base class for all Page Objects with modern patterns and robust error handling"""
    
    def __init__(self, driver: WebDriver, timeout: int = 10):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(self.driver, self.timeout)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _get_locator_and_desc(self, element_info: Union[ElementInfo, Tuple]) -> Tuple[Tuple[str, str], str]:
        """Helper method to extract locator and description from either ElementInfo or tuple"""
        if isinstance(element_info, ElementInfo):
            return element_info.locator, element_info.description
        return element_info, str(element_info)
    
    def _find_element(self, element_info: Union[ElementInfo, Tuple, WebElement], timeout: int = None) -> Optional[WebElement]:
        """Find a single element with explicit wait and robust error handling. If already a WebElement, return it."""
        if hasattr(element_info, 'is_displayed') and callable(element_info.is_displayed):
            # Already a WebElement
            return element_info
        locator, desc = self._get_locator_and_desc(element_info)
        wait_time = timeout if timeout else (
            element_info.timeout if isinstance(element_info, ElementInfo) else self.timeout
        )
        try:
            element = self.wait.until(EC.presence_of_element_located(locator))
            self.logger.debug(f"Found element: {desc}")
            return element
        except TimeoutException:
            self.logger.error(f"Element not found within {wait_time}s: {desc}")
            return None
        except Exception as e:
            self.logger.error(f"Error finding element {desc}: {str(e)}")
            return None

    
    def _find_elements(self, element_info: Union[ElementInfo, Tuple, WebElement]) -> List[WebElement]:
        """Find multiple elements with explicit wait and error handling. If already a WebElement, return as single-item list."""
        if hasattr(element_info, 'is_displayed') and callable(element_info.is_displayed):
            # Already a WebElement
            return [element_info]
        locator, desc = self._get_locator_and_desc(element_info)
        try:
            elements = self.wait.until(EC.presence_of_all_elements_located(locator))
            self.logger.debug(f"Found {len(elements)} elements: {desc}")
            return elements
        except TimeoutException:
            self.logger.warning(f"No elements found: {desc}")
            return []
        except Exception as e:
            self.logger.error(f"Error finding elements {desc}: {str(e)}")
            return []

    
    def _click(self, element_info: Union[ElementInfo, Tuple]):
        """Click an element with retry mechanism"""
        locator, desc = self._get_locator_and_desc(element_info)
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                element = self.wait.until(EC.element_to_be_clickable(locator))
                element.click()
                self.logger.info(f"Successfully clicked: {desc}")
                return True
            except Exception as e:
                self.logger.warning(f"Click attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    self.logger.error(f"Failed to click after {max_retries} attempts: {desc}")
                    return False
                time.sleep(1)
    
    def _send_keys(self, element_info: Union[ElementInfo, Tuple], text: str):
        """Send keys to an element with validation"""
        locator, desc = self._get_locator_and_desc(element_info)
        try:
            element = self.wait.until(EC.visibility_of_element_located(locator))
            element.clear()
            element.send_keys(text)
            actual_value = element.get_attribute('value')
            if actual_value != text:
                self.logger.warning(f"Text verification failed for {desc}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send keys to {desc}: {str(e)}")
            return False
    
    def _get_text(self, element_info: Union[ElementInfo, Tuple]) -> Optional[str]:
        """Get text from an element with error handling"""
        locator, desc = self._get_locator_and_desc(element_info)
        try:
            element = self.wait.until(EC.visibility_of_element_located(locator))
            return element.text
        except Exception as e:
            self.logger.error(f"Failed to get text from {desc}: {str(e)}")
            return None
    
    def _is_element_present(self, element_info: Union[ElementInfo, Tuple]) -> bool:
        """Check if an element is present with logging"""
        locator, desc = self._get_locator_and_desc(element_info)
        try:
            self.wait.until(EC.presence_of_element_located(locator))
            return True
        except (TimeoutException, NoSuchElementException):
            self.logger.debug(f"Element not present: {desc}")
            return False
    
    def _scroll_to_element(self, element_info: Union[ElementInfo, Tuple]):
        """Scroll to an element with smooth behavior"""
        element = self._find_element(element_info)
        if element:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                element
            )
            time.sleep(0.5)  # Allow for smooth scroll completion
    
    def _wait_for_element_disappear(self, element_info: Union[ElementInfo, Tuple]):
        """Wait for an element to disappear"""
        locator, desc = self._get_locator_and_desc(element_info)
        try:
            self.wait.until(EC.invisibility_of_element_located(locator))
            self.logger.debug(f"Element disappeared: {desc}")
            return True
        except TimeoutException:
            self.logger.warning(f"Element did not disappear: {desc}")
            return False
    
    def _take_screenshot(self, name: str):
        """Take a screenshot for debugging"""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"screenshots/{name}_{timestamp}.png"
        self.driver.save_screenshot(filename)
        self.logger.info(f"Screenshot saved: {filename}")

    def _select_dropdown_by_visible_text(self, element_info: Union[ElementInfo, Tuple], text: str):
        """Select dropdown option by visible text"""
        from selenium.webdriver.support.ui import Select
        element = self._find_element(element_info)
        if element:
            select = Select(element)
            select.select_by_visible_text(text)
            return True
        return False
    
    def _enter_greenhouse_iframe(self, max_scrolls: int = 6):
        """
        Lazy-loads Greenhouse board by scrolling the viewport until the iframe
        is attached, then switches driver context into it.
        """
        selector = ElementInfo(
            locator=(By.CSS_SELECTOR, "iframe[src*='greenhouse'], iframe[id*='grnhse']"),
            description="Greenhouse iframe",
            timeout=1  # Short timeout since we're retrying
        )
        
        for i in range(max_scrolls):
            iframe = self._find_element(selector)
            if iframe:
                self.driver.switch_to.frame(iframe)
                self.logger.info("Switched to Greenhouse iframe")
                return
                
            self.logger.debug(f"Scrolling attempt {i+1}/{max_scrolls}")
            self.driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(1)

        raise TimeoutException("Greenhouse iframe not found after scrolling")