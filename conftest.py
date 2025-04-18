import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(autouse=True)
def chrome_web_driver_base(request):
    chrome_web_driver: WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--allow-running-insecure-content")

    try:
        service = Service()
        chrome_web_driver = webdriver.Chrome(
            service=service, options=options
        )
    except Exception:
        downloaded_binary_path = ChromeDriverManager().install()
        service = Service(executable_path=downloaded_binary_path)
        chrome_web_driver = webdriver.Chrome(
            service=service, options=options
        )

    chrome_web_driver.maximize_window()
    yield chrome_web_driver
    chrome_web_driver.close()
