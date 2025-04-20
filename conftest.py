import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

def pytest_addoption(parser):
    """Add command line option for browser selection"""
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to run tests on: chrome or firefox"
    )

@pytest.fixture(scope="session")
def browser(request):
    """Get browser from command line option"""
    return request.config.getoption("--browser").lower()

@pytest.fixture(autouse=True)
def driver(browser):
    """Setup WebDriver based on browser choice"""
    if browser == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--start-maximized")
        
        try:
            service = ChromeService()
            web_driver = webdriver.Chrome(service=service, options=options)
        except Exception:
            downloaded_binary_path = ChromeDriverManager().install()
            service = ChromeService(executable_path=downloaded_binary_path)
            web_driver = webdriver.Chrome(service=service, options=options)
            
    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument("--private")
        
        try:
            service = FirefoxService()
            web_driver = webdriver.Firefox(service=service, options=options)
        except Exception:
            downloaded_binary_path = GeckoDriverManager().install()
            service = FirefoxService(executable_path=downloaded_binary_path)
            web_driver = webdriver.Firefox(service=service, options=options)
            
    else:
        raise ValueError(f"Unsupported browser: {browser}")
    
    web_driver.maximize_window()
    yield web_driver
    web_driver.quit()
