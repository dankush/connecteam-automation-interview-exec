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
from pages.position_page import PositionPage

class CareersPage(BasePage):
    """Page Object for the Careers Page"""

    # Element definitions with descriptions (updated for 2025 best practices)
    DEPARTMENT_FILTER_SECTION = ElementInfo(
        locator=(By.CSS_SELECTOR, "div.field.department-filter"),
        description="Department filter section"
    )
    
    DEPARTMENT_SELECT = ElementInfo(
        locator=(By.CSS_SELECTOR, "select#department-filter[data-department-filter]"),
        description="Department filter dropdown"
    )
    
    DEPARTMENT_LABEL = ElementInfo(
        locator=(By.CSS_SELECTOR, "label[for='department-filter']"),
        description="Department filter label"
    )
    
    VISIBLE_JOB_ROWS = ElementInfo(
        locator=(By.CSS_SELECTOR, "tr[role='row'][data-department='R&amp;D']"),
        description="Visible R&D job rows"
    )
    
    APPLY_LINK = ElementInfo(
        locator=(By.CSS_SELECTOR, "td.link a[href*='careers']"),
        description="Apply now link"
    )
    
    JOB_TITLE = ElementInfo(
        locator=(By.CSS_SELECTOR, "td.title"),
        description="Job title cell"
    )
    
    NO_RESULTS_MESSAGE = ElementInfo(
        locator=(By.CSS_SELECTOR, "div.no-results-message"),
        description="No results message"
    )

    def __init__(self, driver):
        super().__init__(driver)
        self.logger = logging.getLogger(__name__)
        self.position_page = PositionPage(driver)

    def select_department(self, department: str = "R&D") -> bool:
        """
        Select a department from the filter dropdown with improved validation
        Args:
            department: Department name to select (default: R&D)
        Returns:
            bool: True if department was successfully selected and jobs are visible
        """
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                # Wait for filter section to be present
                filter_section = self.wait.until(
                    EC.presence_of_element_located(self.DEPARTMENT_FILTER_SECTION.locator)
                )
                
                # Ensure dropdown is visible and interactable
                select_element = self.wait.until(
                    EC.element_to_be_clickable(self.DEPARTMENT_SELECT.locator)
                )
                
                # Get all options and find the correct one (handling HTML encoding)
                select = Select(select_element)
                options = select.options
                target_option = None
                for option in options:
                    if option.text.replace("&amp;", "&") == department:
                        target_option = option
                        break
                
                if not target_option:
                    if attempt == max_attempts - 1:
                        self.logger.error(f"Could not find department option: {department}")
                        return False
                    time.sleep(1)
                    continue
                
                # Select using the option's actual value
                select.select_by_visible_text(target_option.text)
                time.sleep(1)  # Wait for filtering
                
                # Update job rows locator to match the actual department value in HTML
                self.VISIBLE_JOB_ROWS.locator = (
                    By.CSS_SELECTOR, 
                    f'tr[role="row"][data-department="{target_option.text}"]'
                )
                
                # Verify selection worked
                visible_rows = self._find_elements(self.VISIBLE_JOB_ROWS)
                if visible_rows:
                    self.logger.info(f"Successfully selected department: {department}")
                    return True
                
                if attempt == max_attempts - 1:
                    self.logger.warning(f"No visible positions found for department: {department}")
                    return False
                    
                # If verification failed, try scrolling and checking again
                self.driver.execute_script("window.scrollBy(0, 200);")
                time.sleep(0.5)
                
            except Exception as e:
                if attempt == max_attempts - 1:
                    self.logger.error(f"Failed to select department: {str(e)}")
                    return False
                time.sleep(1)
                
        return False

    def _verify_department_selection(self, department: str) -> bool:
        """
        Verify department selection was successful using multiple checks
        Args:
            department: Department value to verify (with HTML encoding)
        Returns:
            bool: True if verification passed
        """
        try:
            # Wait for either job rows OR no results message
            self.wait.until(lambda driver: (
                len(driver.find_elements(*self.VISIBLE_JOB_ROWS.locator)) > 0 or
                len(driver.find_elements(*self.NO_RESULTS_MESSAGE.locator)) > 0
            ))
            
            # Check if jobs are visible
            visible_rows = self._find_elements(self.VISIBLE_JOB_ROWS)
            if visible_rows:
                # Verify department attribute on rows
                for row in visible_rows:
                    if row.get_attribute("data-department") != department:
                        return False
                return True
                
            # If no jobs found, verify no results message is shown
            no_results = self._find_element(self.NO_RESULTS_MESSAGE)
            if no_results and no_results.is_displayed():
                self.logger.info("No positions available for selected department")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error verifying department selection: {str(e)}")
            return False

    def _refresh_positions(self) -> List[WebElement]:
        """Get a fresh list of applyable positions to avoid stale elements"""
        try:
            # First ensure department is still selected
            if not self.select_department("R&D"):
                self.logger.error("Failed to refresh department selection")
                return []
                
            # Get visible rows
            rows = self._find_elements(self.VISIBLE_JOB_ROWS)
            positions = []
            
            for row in rows:
                try:
                    if not row.is_displayed():
                        continue
                        
                    # Check if row has an apply link
                    apply_link = row.find_element(*self.APPLY_LINK.locator)
                    if apply_link and apply_link.is_displayed() and "Apply" in apply_link.text:
                        positions.append(row)
                except Exception:
                    continue
                    
            return positions
        except Exception as e:
            self.logger.error(f"Error refreshing positions: {str(e)}")
            return []

    def get_applyable_positions(self) -> List[WebElement]:
        """Get all visible job listing rows that can be applied to"""
        positions = self._refresh_positions()
        self.logger.info(f"Found {len(positions)} applyable positions")
        return positions

    def apply_for_position(self, position: WebElement, first_name: str, last_name: str, 
                         email: str, phone: str, cv_path: str, linkedin: str = None) -> bool:
        """Apply for a specific position with improved handling of stale elements"""
        position_index = -1
        position_title = "Unknown"
        
        try:
            # First try to get position information for logging
            try:
                # Find the position in the current list and get its index
                positions = self._find_elements(self.VISIBLE_JOB_ROWS)
                for i, pos in enumerate(positions):
                    if pos == position:
                        position_index = i
                        break
                
                # Get title for logging
                title_element = position.find_element(*self.JOB_TITLE.locator)
                if title_element:
                    position_title = title_element.text.strip()
                    self.logger.info(f"Applying for position {position_index+1}: {position_title}")
            except Exception as e:
                self.logger.info(f"Applying for position (index: {position_index+1}, title extraction failed: {str(e)})")
            
            # Find and click apply link with retry mechanism
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Try to get a fresh reference to the position if we have its index
                    if position_index >= 0 and attempt > 0:
                        self.logger.info(f"Refreshing position reference (attempt {attempt+1})")
                        fresh_positions = self._refresh_positions()
                        if position_index < len(fresh_positions):
                            position = fresh_positions[position_index]
                        else:
                            raise Exception(f"Position index {position_index} out of range after refresh")
                    
                    # Find apply link
                    apply_link = position.find_element(*self.APPLY_LINK.locator)
                    
                    # Ensure element is in view
                    self._scroll_to_element(apply_link)
                    time.sleep(0.5)  # Short delay before click
                    
                    # Use JS click for reliability
                    self.driver.execute_script("arguments[0].click();", apply_link)
                    time.sleep(1)  # Wait for modal animation
                    
                    # Break out of retry loop if successful
                    break
                    
                except StaleElementReferenceException as e:
                    if attempt == max_retries - 1:
                        raise e
                    self.logger.warning(f"Stale element on attempt {attempt+1}, retrying...")
                    time.sleep(0.5)
                    
            # Use PositionPage to handle form
            result = self.position_page.fill_application_form(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                cv_path=cv_path,
                linkedin=linkedin
            )
            
            if not result:
                self.logger.error(f"Failed to fill application form for position: {position_title}")
                return False
                
            self.logger.info(f"Successfully applied to position: {position_title}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying for position {position_title}: {str(e)}")
            return False
            
        finally:
            # Always try to close the form and return to the positions list
            try:
                self.position_page.close_form()
                # Wait for form to close and page to stabilize
                time.sleep(1)
            except Exception as e:
                self.logger.warning(f"Error closing form: {str(e)}")