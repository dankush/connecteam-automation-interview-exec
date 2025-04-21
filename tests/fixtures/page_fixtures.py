"""Fixtures for page objects and test environment setup."""
import pytest
import logging
from selenium.webdriver.remote.webdriver import WebDriver
from pages.home_page import HomePage
from pages.careers_page import CareersPage
from pages.position_page import PositionPage


@pytest.fixture
def home_page(driver: WebDriver):
    """Provide a configured HomePage instance.
    
    Args:
        driver: WebDriver instance from the driver fixture
        
    Returns:
        HomePage: Configured home page object
    """
    return HomePage(driver)


@pytest.fixture
def careers_page(driver: WebDriver):
    """Provide a configured CareersPage instance.
    
    Args:
        driver: WebDriver instance from the driver fixture
        
    Returns:
        CareersPage: Configured careers page object
    """
    return CareersPage(driver)


@pytest.fixture
def position_page(driver: WebDriver):
    """Provide a configured PositionPage instance.
    
    Args:
        driver: WebDriver instance from the driver fixture
        
    Returns:
        PositionPage: Configured position page object
    """
    return PositionPage(driver)


@pytest.fixture
def test_logger():
    """Provide a configured logger for test classes.
    
    Returns:
        Logger: Configured logger instance
    """
    return logging.getLogger("test_career_application")
