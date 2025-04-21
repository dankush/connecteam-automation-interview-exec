"""Configuration settings for the test automation framework."""
import os
import logging
from pathlib import Path

# Configure logging basic settings - Do this early in your app/test runner
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Framework Configuration (module-level) ---
BASE_URL = os.getenv("BASE_URL", "https://connecteam.com/")
CAREERS_PAGE_URL_SUFFIX = "careers"  # Usually static

# --- Framework Settings ---
# More robust boolean parsing for HEADLESS
_raw_headless = os.getenv("HEADLESS", "False").lower()
HEADLESS = _raw_headless in ("true", "1", "yes", "on")

_default_timeout = 10
try:
    TIMEOUT = int(os.getenv("TIMEOUT", str(_default_timeout)))
except ValueError:
    # Ensure logging is configured before this point for the warning to show up
    logging.warning(f"Invalid value for TIMEOUT env var. Using default: {_default_timeout}")
    TIMEOUT = _default_timeout

# Project root is parent of this config file's directory
try:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
except NameError:
     # Handle case where __file__ might not be defined (e.g. interactive interpreter)
     PROJECT_ROOT = Path('.').resolve()
     logging.warning(f"__file__ not defined. Assuming project root is current dir: {PROJECT_ROOT}")

SCREENSHOT_DIR_NAME = os.getenv("SCREENSHOT_DIR", "screenshots")
SCREENSHOT_DIR = PROJECT_ROOT / SCREENSHOT_DIR_NAME

# --- Default Test Data (consider moving to a separate data module/file) ---
DEFAULT_TARGET_DEPARTMENT = os.getenv("TARGET_DEPARTMENT", "R&D")
DEFAULT_FIRST_NAME = os.getenv("FIRST_NAME", "Test")
DEFAULT_LAST_NAME = os.getenv("LAST_NAME", "Automation")
DEFAULT_EMAIL = os.getenv("EMAIL", "test.automation@example.com")
DEFAULT_PHONE = os.getenv("PHONE", "+1234567890")

# CV Path - make it relative to project root
_default_cv_path = PROJECT_ROOT / "example_cv.pdf"
CV_FILE_PATH = Path(os.getenv("CV_FILE_PATH", str(_default_cv_path)))

# --- Setup Function (call from test setup/fixtures) ---
def setup_directories():
    """Creates necessary directories defined in config."""
    if not SCREENSHOT_DIR:
        logging.error("SCREENSHOT_DIR is not defined. Cannot create directory.")
        return # Or raise an error

    try:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        logging.info(f"Ensured screenshot directory exists: {SCREENSHOT_DIR}")
    except OSError as e:
        logging.error(f"Failed to create screenshot directory {SCREENSHOT_DIR}: {e}")
        raise # Re-raise: directory creation might be critical

# --- Validation (Optional) ---
def validate_config():
    """Perform basic validation checks."""
    if not CV_FILE_PATH.is_file():
        # This might be a warning or an error depending on requirements
        logging.warning(f"CV file not found at specified path: {CV_FILE_PATH}")

    if not BASE_URL.startswith(('http://', 'https://')):
         logging.warning(f"BASE_URL '{BASE_URL}' does not look like a valid URL.")

    # Add other checks as needed (e.g., TIMEOUT > 0)
    if TIMEOUT <= 0:
        logging.warning(f"TIMEOUT value ({TIMEOUT}) should likely be positive.")


# --- Example Usage (in your test setup or main script) ---
# import config
#
# def run_tests():
#     logging.basicConfig(level=logging.INFO) # Configure logging
#     config.setup_directories()
#     config.validate_config()
#     # ... proceed with test execution using config.BASE_URL etc.
#
# if __name__ == "__main__":
#      run_tests()