"""Configuration settings for the test automation framework."""
import os
from typing import Dict, Any, Optional, ClassVar
import logging

class Config:
    """Global configuration settings using Singleton pattern.
    
    This class manages all configuration settings for the automation framework.
    It ensures only one instance exists throughout the application.
    """
    
    _instance: ClassVar[Optional['Config']] = None
    _initialized: bool = False
    
    # Base URL
    BASE_URL: str = "https://connecteam.com/"
    CAREERS_PAGE_URL_SUFFIX: str = "careers"
    
    # Test data for job applications
    TARGET_DEPARTMENT: str = "R&D"
    FIRST_NAME: str = "Test"
    LAST_NAME: str = "Automation"
    EMAIL: str = "test.automation@example.com"
    PHONE: str = "+1234567890"
    
    # CV file path - using absolute path to example_cv.pdf in project root
    CV_FILE_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "example_cv.pdf")
    
    # Additional settings with environment variable support
    HEADLESS: bool = False
    TIMEOUT: int = 10
    SCREENSHOT_DIR: str = "screenshots"
    
    def __new__(cls) -> 'Config':
        """Create a new instance or return the existing one."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the configuration with environment variables or defaults."""
        if self._initialized:
            return
            
        # Load configuration from environment variables if available
        self.TARGET_DEPARTMENT = os.getenv("TARGET_DEPARTMENT", self.TARGET_DEPARTMENT)
        self.FIRST_NAME = os.getenv("FIRST_NAME", self.FIRST_NAME)
        self.LAST_NAME = os.getenv("LAST_NAME", self.LAST_NAME)
        self.EMAIL = os.getenv("EMAIL", self.EMAIL)
        self.PHONE = os.getenv("PHONE", self.PHONE)
        self.CV_FILE_PATH = os.getenv("CV_FILE_PATH", self.CV_FILE_PATH)
        self.HEADLESS = os.getenv("HEADLESS", str(self.HEADLESS)).lower() == "true"
        self.TIMEOUT = int(os.getenv("TIMEOUT", str(self.TIMEOUT)))
        self.SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", self.SCREENSHOT_DIR)
        
        # Create screenshot directory if it doesn't exist
        os.makedirs(self.SCREENSHOT_DIR, exist_ok=True)
        
        # Mark as initialized
        self._initialized = True


# Create a singleton instance for backward compatibility
config = Config()