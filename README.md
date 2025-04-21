# Connecteam Careers QA Automation Framework

A production-ready Selenium-based QA automation framework for testing the Connecteam careers site. This suite navigates, filters, and fills job application forms for all R&D positions—without submitting—using Python, Pytest, and the Page Object Model. It is cross-platform (Windows & Linux) and built for reliability, maintainability, and CI/CD integration.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [How to Run Tests](#how-to-run-tests)
- [Fixtures and Configs](#fixtures-and-configs)
- [Design Patterns Used](#design-patterns-used)
- [CI/CD Integration](#cicd-integration)
- [Logging and Reports](#logging-and-reports)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

---

## Project Structure

```
.
├── tests/           # Test cases (Pytest)
├── pages/           # Page Object Model classes: BasePage, HomePage, CareersPage, PositionPage
├── fixtures/        # Pytest fixtures and reusable test data
├── utils/           # Helpers (custom waits, logging, etc.)
├── config/          # Config management (Config class, .env parsing)
├── requirements.txt # Python dependencies
├── conftest.py      # Global Pytest hooks and fixtures
└── README.md
```

- **tests/**: All test scenarios and assertions.
- **pages/**: Encapsulates UI locators and actions for each page.
- **fixtures/**: Shared setup, teardown, and test data.
- **utils/**: Helper modules (logging, waits, etc.).
- **config/**: Handles environment/configuration logic.

---

## Installation & Setup

1. **Clone the repo**  
   `git clone <repo-url> && cd connecteam-automation-interview-exec`

2. **Python & Tools**  
   - Python 3.9+ required  
   - [pip](https://pip.pypa.io/), [virtualenv](https://virtualenv.pypa.io/), [Ruff](https://docs.astral.sh/ruff/), [pytest](https://docs.pytest.org/)

3. **Create and activate a virtualenv**  
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies**  
   ```sh
   pip install -r requirements.txt
   ```

5. **Environment Variables**  
   - Copy `.env.example` to `.env` and fill in required values (browser, base URL, credentials, etc.)

---

## How to Run Tests

- **Run all tests:**  
  `pytest -v -s tests/`

- **Run a specific test:**  
  `pytest -v -s tests/test_career_application.py`

- **Generate Allure report:**  
  `pytest --alluredir=allure-results`  
  `allure serve allure-results`

- **CI/CD:**  
  Tests run automatically on push/pull via GitHub Actions or Jenkins (see workflows or Jenkinsfile).

---

## Fixtures and Configs

- **Fixtures:**  
  Located in `fixtures/` and `conftest.py`.  
  Provide browser setup/teardown, data loading, and reusable state.

- **Configuration:**  
  Managed via `config/` and `.env` files.  
  Supports environment-specific settings and secrets.

---

## Design Patterns Used

- **Page Object Model:** All UI actions/locators in `pages/`
- **Factory:** Browser/WebDriver instantiation.
- **Strategy:** Element finding and waiting strategies in `utils/`.

---


## Logging and Reports

- **Logging:**  
  - Test actions and errors are logged to `logs/`.
  - Screenshots of failures saved to `screenshots/`.

- **Reports:**  
  - Allure reporting supported for rich HTML reports.
  - Pytest output available in terminal and CI logs.

---

## Contributing

- **Linting:**  
  Run `ruff .` before committing.
- **Type Checking:**  
  Use `mypy` for static type checks.
- **Adding Tests/Pages:**  
  - Add new test files to `tests/`.
  - Add new page objects to `pages/` following the POM pattern.
- **Pull Requests:**  
  - Ensure all tests pass locally and in CI.
  - Follow project code style.

---

## Troubleshooting

- **WebDriver errors:**  
  - Ensure correct browser driver is installed and in PATH.
  - Check `.env` for correct browser/version.

- **Flaky tests:**  
  - Increase explicit waits in page objects.
  - Use stable selectors (avoid dynamic IDs).

- **Debugging:**  
  - Use `-s` with pytest for live logs.
  - Check `logs/` and `screenshots/` for error context.

---

For questions or issues, open a GitHub Issue or contact the project maintainer.