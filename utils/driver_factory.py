"""WebDriver factory implementation for browser management."""
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
import platform
import logging
from config.config import HEADLESS, TIMEOUT


class DriverFactory:
    """Factory class for creating WebDriver instances.
    
    This class implements the Factory pattern to create different types of WebDriver
    instances based on the browser type and configuration.
    """
    
    @staticmethod
    def create_driver(browser_type: str = "chrome") -> webdriver.Remote:
        """
        Create and return a WebDriver instance based on browser type.
        
        Args:
            browser_type: Type of browser ("chrome", "firefox")
            
        Returns:
            WebDriver instance configured according to settings
            
        Raises:
            ValueError: If an unsupported browser type is specified
        """
        # config variables imported at module level
        logger = logging.getLogger(__name__)
        
        browser_type = browser_type.lower()
        logger.info(f"Creating {browser_type} driver (headless: {HEADLESS})")
        
        if browser_type == "chrome":
            return DriverFactory._create_chrome_driver()
        elif browser_type == "firefox":
            return DriverFactory._create_firefox_driver()
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")
    
    @staticmethod
    def _create_chrome_driver() -> webdriver.Chrome:
        """Create a Chrome WebDriver instance."""
        options = ChromeOptions()
        
        # Set headless mode if configured
        if HEADLESS:
            options.add_argument("--headless")
        
        # Common options for stability
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        
        # Platform-specific settings
        if platform.system() == "Linux":
            options.add_argument("--disable-dev-shm-usage")
        
        # Create and return the driver
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(TIMEOUT)
        return driver
    
    @staticmethod
    def _create_firefox_driver() -> webdriver.Firefox:
        """Create a Firefox WebDriver instance."""
        options = FirefoxOptions()
        
        # Set headless mode if configured
        if HEADLESS:
            options.add_argument("--headless")
        
        # Create and return the driver
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(TIMEOUT)
        return driver
