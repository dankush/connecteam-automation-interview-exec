import time

import pytest
from selenium import webdriver

@pytest.mark.usefixtures("chrome_web_driver_base")
class TestSubmitCv:
    def test_submit_cv(self, chrome_web_driver_base: webdriver.Chrome):
        chrome_web_driver_base.get("https://connecteam.com/")
        time.sleep(5)
