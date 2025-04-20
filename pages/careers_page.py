import time
import os
import logging
from typing import List
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException,
    StaleElementReferenceException
)
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from pages.base_page import BasePage, ElementInfo

class CareersPage(BasePage):
    """Page Object for the Careers Page and Application Form"""

    # Element definitions with descriptions
    DEPARTMENT_SELECT = ElementInfo(
        locator=(By.ID, "department-filter"),
        description="Department filter dropdown"
    )
    
    VISIBLE_JOB_ROWS = ElementInfo(
        locator=(By.CSS_SELECTOR, "tr[data-department='R&D']"),
        description="Visible R&D job rows"
    )
    
    JOB_TITLE = ElementInfo(
        locator=(By.CSS_SELECTOR, "td.title"),
        description="Job title cell"
    )
    
    APPLY_LINK = ElementInfo(
        locator=(By.CSS_SELECTOR, "td.link a[href*='careers']"),
        description="Apply now link"
    )
    
    # Form elements
    FORM_CONTAINER = ElementInfo(
        locator=(By.CSS_SELECTOR, "div[data-testid='modal']"),
        description="Application form modal"
    )
    
    FIRST_NAME_INPUT = ElementInfo(
        locator=(By.NAME, "first_name"),
        description="First name input"
    )
    
    LAST_NAME_INPUT = ElementInfo(
        locator=(By.NAME, "last_name"),
        description="Last name input"
    )
    
    EMAIL_INPUT = ElementInfo(
        locator=(By.NAME, "email"),
        description="Email input"
    )
    
    PHONE_INPUT = ElementInfo(
        locator=(By.NAME, "phone"),
        description="Phone input"
    )
    
    CV_UPLOAD_INPUT = ElementInfo(
        locator=(By.NAME, "resume"),
        description="CV upload input"
    )
    
    CLOSE_MODAL_BTN = ElementInfo(
        locator=(By.CSS_SELECTOR, "button[aria-label='Close']"),
        description="Close form modal button"
    )

    def __init__(self, driver):
        super().__init__(driver)
        self.logger = logging.getLogger(__name__)

    def select_department(self, department: str = "R&D") -> bool:
        """Select a department from the filter dropdown"""
        try:
            select_element = self._find_element(self.DEPARTMENT_SELECT)
            if not select_element:
                self.logger.error("Department select element not found")
                return False
                
            Select(select_element).select_by_visible_text(department)
            time.sleep(1)  # Wait for filtering
            
            # Verify selection worked
            visible_rows = self._find_elements(self.VISIBLE_JOB_ROWS)
            if visible_rows:
                self.logger.info(f"Successfully selected department: {department}")
                return True
            else:
                self.logger.warning(f"No visible positions found for department: {department}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to select department: {str(e)}")
            return False

    def get_applyable_positions(self) -> List[WebElement]:
        """Get all visible job listing rows that can be applied to"""
        positions = []
        try:
            rows = self._find_elements(self.VISIBLE_JOB_ROWS)
            
            for row in rows:
                try:
                    if not row.is_displayed():
                        continue
                        
                    # Check if row has an apply link
                    apply_link = row.find_element(*self.APPLY_LINK.locator)
                    if apply_link and "Apply" in apply_link.text:
                        positions.append(row)
                except NoSuchElementException:
                    continue
                    
            self.logger.info(f"Found {len(positions)} applyable positions")
            return positions
            
        except Exception as e:
            self.logger.error(f"Error getting applyable positions: {str(e)}")
            return []

    def apply_for_position(self, position: WebElement, first_name: str, last_name: str, 
                         email: str, phone: str, cv_path: str) -> bool:
        """Apply for a specific position"""
        try:
            # Get position title for logging
            try:
                title = position.find_element(*self.JOB_TITLE.locator).text.strip()
                self.logger.info(f"Applying for position: {title}")
            except:
                self.logger.info("Applying for position (title not found)")
            
            # Find and click apply link
            apply_link = position.find_element(*self.APPLY_LINK.locator)
            self._scroll_to_element(apply_link)
            time.sleep(0.5)
            
            # Use JS click for reliability
            self.driver.execute_script("arguments[0].click();", apply_link)
            
            # Wait for and fill form
            form = self._find_element(self.FORM_CONTAINER)
            if not form:
                self.logger.error("Application form not found")
                return False
                
            # Fill form fields
            if not all([
                self._send_keys(self.FIRST_NAME_INPUT, first_name),
                self._send_keys(self.LAST_NAME_INPUT, last_name),
                self._send_keys(self.EMAIL_INPUT, email),
                self._send_keys(self.PHONE_INPUT, phone)
            ]):
                self.logger.error("Failed to fill one or more form fields")
                return False
            
            # Handle CV upload
            if not os.path.exists(cv_path):
                self.logger.error(f"CV file not found: {cv_path}")
                return False
                
            cv_input = self._find_element(self.CV_UPLOAD_INPUT)
            if not cv_input:
                self.logger.error("CV upload input not found")
                return False
                
            cv_input.send_keys(cv_path)
            self.logger.info("Successfully filled application form")
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying for position: {str(e)}")
            return False
            
        finally:
            # Always try to close the form
            try:
                close_btn = self._find_element(self.CLOSE_MODAL_BTN)
                if close_btn:
                    self.driver.execute_script("arguments[0].click();", close_btn)
                    self.wait.until(EC.invisibility_of_element_located(self.FORM_CONTAINER.locator))
            except:
                pass