"""Configuration settings for the test automation framework."""
import os

class Config:
    """Global configuration settings."""
    
    # Base URL
    BASE_URL = "https://connecteam.com/"
    CAREERS_PAGE_URL_SUFFIX = "careers"
    
    # Test data for job applications
    TARGET_DEPARTMENT = "R&D"
    FIRST_NAME = "Test"
    LAST_NAME = "Automation"
    EMAIL = "test.automation@example.com"
    PHONE = "+1234567890"
    
    # CV file path - using absolute path to example_cv.pdf in project root
    CV_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "example_cv.pdf")

# Create a singleton instance
config = Config()