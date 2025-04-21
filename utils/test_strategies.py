"""Strategy pattern implementation for test execution modes."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
import logging
import time


class TestStrategy(ABC):
    """Abstract base class for test execution strategies."""
    
    @abstractmethod
    def execute(self, driver: WebDriver, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the test using the specific strategy.
        
        Args:
            driver: WebDriver instance
            test_data: Dictionary containing test data
            
        Returns:
            Dictionary with test results
        """
        pass


class StandardTestStrategy(TestStrategy):
    """Standard test execution strategy.
    
    This strategy executes the test in a linear fashion, processing all positions
    and collecting results.
    """
    
    def execute(self, driver: WebDriver, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test in standard mode."""
        logger = logging.getLogger(__name__)
        logger.info("Executing test with StandardTestStrategy")
        
        from pages.home_page import HomePage
        from pages.careers_page import CareersPage
        from pages.position_page import PositionPage
        
        results = {
            "success": True,
            "positions_processed": 0,
            "positions_failed": 0,
            "details": []
        }
        
        try:
            # Navigate to home page and then to careers page
            home_page = HomePage(driver)
            home_page.navigate_to_home()
            home_page.scroll_to_and_click_careers()
            
            # Select department and get positions
            careers_page = CareersPage(driver)
            careers_page.select_department(test_data["department"])
            positions = careers_page.get_applyable_positions()
            
            logger.info(f"Found {len(positions)} positions in {test_data['department']} department")
            
            # Process each position
            position_page = PositionPage(driver)
            processed_positions = set()  # Track which positions we've already processed
            
            # Continue until we've processed all positions or hit a maximum retry count
            max_retries = 3
            retry_count = 0
            
            while len(processed_positions) < len(positions) and retry_count < max_retries:
                # Get a fresh list of positions each time
                current_positions = careers_page.get_applyable_positions()
                if not current_positions:
                    logger.warning("No positions found, retrying...")
                    retry_count += 1
                    continue
                
                # Process each position that hasn't been processed yet
                for i, position in enumerate(current_positions):
                    # Create a position identifier (index in the list)
                    position_id = i
                    
                    # Skip if we've already processed this position
                    if position_id in processed_positions:
                        continue
                    
                    # Extract position name for logging
                    try:
                        title_element = position.find_element(By.CSS_SELECTOR, "td.title")
                        position_name = title_element.text.strip() if title_element else f"Position {i+1}"
                    except Exception:
                        position_name = f"Position {i+1}"
                    
                    logger.info(f"Processing position {i+1}/{len(current_positions)}: {position_name}")
                    
                    try:
                        # Apply for the position
                        success = careers_page.apply_for_position(
                            position,
                            test_data["first_name"],
                            test_data["last_name"],
                            test_data["email"],
                            test_data["phone"],
                            test_data["cv_path"]
                        )
                        
                        # Add to processed set regardless of success/failure
                        processed_positions.add(position_id)
                        
                        if success:
                            # Record success
                            results["positions_processed"] += 1
                            results["details"].append({
                                "position": position_name,
                                "status": "success"
                            })
                            logger.info(f"Successfully applied to position: {position_name}")
                        else:
                            # Record failure
                            results["positions_failed"] += 1
                            results["details"].append({
                                "position": position_name,
                                "status": "failed",
                                "error": "Application process failed"
                            })
                            logger.warning(f"Failed to apply to position: {position_name}")
                        
                        # Return to positions list - use the position page method
                        logger.info("Returning to positions list")
                        try:
                            if not position_page.return_to_all_positions():
                                logger.warning("Could not return to positions list via button, trying fallback")
                                # Fallback: navigate back to the careers page and reselect department
                                driver.back()
                                # Wait for page to load and reselect department
                                time.sleep(2)
                                careers_page.select_department(test_data["department"])
                        except Exception as e:
                            logger.warning(f"Error returning to positions list: {str(e)}, trying fallback")
                            # Last resort - go back to careers page
                            home_page.navigate_to_home()
                            home_page.scroll_to_and_click_careers()
                            careers_page.select_department(test_data["department"])
                        
                        # Wait for positions to load
                        time.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"Error processing position {position_name}: {str(e)}")
                        results["positions_failed"] += 1
                        results["details"].append({
                            "position": position_name,
                            "status": "failed",
                            "error": str(e)
                        })
                        processed_positions.add(position_id)  # Mark as processed even though it failed
                        
                        # Try to recover and continue
                        try:
                            # Try to close any open forms
                            position_page.close_form()
                            # Try to return to positions list
                            position_page.return_to_all_positions()
                        except Exception as recovery_error:
                            logger.error(f"Recovery failed: {str(recovery_error)}")
                            # Last resort - go back to careers page and reselect department
                            home_page.navigate_to_home()
                            home_page.scroll_to_and_click_careers()
                            careers_page.select_department(test_data["department"])
                        
                        # Wait for page to stabilize
                        time.sleep(2)
            
        except Exception as e:
            logger.error(f"Test execution failed: {str(e)}")
            results["success"] = False
            results["error"] = str(e)
        
        return results


class ParallelTestStrategy(TestStrategy):
    """Parallel test execution strategy.
    
    This strategy is designed for future implementation of parallel test execution
    using multiple browser instances.
    """
    
    def execute(self, driver: WebDriver, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test in parallel mode (placeholder for future implementation)."""
        logger = logging.getLogger(__name__)
        logger.warning("ParallelTestStrategy is not fully implemented yet, falling back to StandardTestStrategy")
        
        # For now, just use the standard strategy
        standard_strategy = StandardTestStrategy()
        return standard_strategy.execute(driver, test_data)


class TestStrategyFactory:
    """Factory for creating test execution strategy instances."""
    
    @staticmethod
    def create_strategy(strategy_type: str = "standard") -> TestStrategy:
        """
        Create and return a test strategy based on the specified type.
        
        Args:
            strategy_type: Type of strategy ("standard", "parallel")
            
        Returns:
            TestStrategy instance
            
        Raises:
            ValueError: If an unsupported strategy type is specified
        """
        strategy_type = strategy_type.lower()
        
        if strategy_type == "standard":
            return StandardTestStrategy()
        elif strategy_type == "parallel":
            return ParallelTestStrategy()
        else:
            raise ValueError(f"Unsupported test strategy type: {strategy_type}")
