import pytest
import os
import logging
import time
from typing import Generator
from selenium.webdriver.remote.webdriver import WebDriver
from utils.driver_factory import DriverFactory
from utils.logger import setup_logger, LogContext
from config.config import BASE_URL, HEADLESS, TIMEOUT, SCREENSHOT_DIR


def pytest_addoption(parser) -> None:
    """Add command line options for test configuration.
    
    Args:
        parser: pytest command line parser
    """
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to run tests on: chrome or firefox"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=None,
        help="Run browser in headless mode"
    )
    parser.addoption(
        "--logging-level",
        action="store",
        default="INFO",
        help="Set logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    parser.addoption(
        "--strategy",
        action="store",
        default="standard",
        help="Test execution strategy: standard, parallel"
    )


@pytest.fixture(scope="session", autouse=True)
def setup_logging(request) -> None:
    """Set up logging for the test session.
    
    Args:
        request: pytest request object
    """
    log_level = request.config.getoption("--logging-level")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_file = f"{log_dir}/test-run-{timestamp}.log"
    
    setup_logger(log_level, log_file)
    logging.info(f"Test session started with log level {log_level}")


@pytest.fixture(scope="session")
def browser(request) -> str:
    """Get browser type from command line option.
    
    Args:
        request: pytest request object
        
    Returns:
        Browser type string
    """
    return request.config.getoption("--browser").lower()


@pytest.fixture(scope="session")
def strategy(request) -> str:
    """Get test execution strategy from command line option.
    
    Args:
        request: pytest request object
        
    Returns:
        Strategy type string
    """
    return request.config.getoption("--strategy").lower()


@pytest.fixture(scope="session")
def driver(browser) -> Generator[WebDriver, None, None]:
    """Set up and tear down WebDriver for tests.
    
    Args:
        browser: Browser type from browser fixture
        config: Config instance from config fixture
        
    Yields:
        WebDriver instance
    """
    # Create driver using factory pattern
    from config.config import HEADLESS, TIMEOUT
    with LogContext(browser=browser, headless=HEADLESS):
        logging.info(f"Creating {browser} WebDriver")
        web_driver = DriverFactory.create_driver(browser)
        
        # Set up driver
        web_driver.maximize_window()
        web_driver.set_page_load_timeout(TIMEOUT)
        
        # Provide driver to test
        yield web_driver
        
        # Clean up
        logging.info("Closing WebDriver")
        web_driver.quit()
