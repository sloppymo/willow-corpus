"""Configuration file for pytest."""
import os
import shutil
import pytest
from pathlib import Path

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
os.environ["PYTHONPATH"] = str(PROJECT_ROOT)

# Fixture for cleaning up temporary files
@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Clean up temporary files after each test."""
    # Setup - runs before each test
    temp_dirs = []
    
    yield  # This is where the test runs
    
    # Teardown - runs after each test
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

# Fixture for sample data directory
@pytest.fixture
def sample_data_dir():
    """Return the path to the sample data directory."""
    return Path(__file__).parent / "data"

# Fixture for creating a temporary directory
@pytest.fixture
temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = Path("test_temp")
    temp_dir.mkdir(exist_ok=True)
    yield temp_dir
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

# Configure logging for tests
@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for tests."""
    import logging
    logging.basicConfig(level=logging.INFO)

# Skip browser-based tests if Chrome is not available
@pytest.fixture(autouse=True)
def skip_browser_tests(request):
    """Skip browser-based tests if Chrome is not available."""
    if "browser" in request.keywords:
        try:
            from selenium import webdriver
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            # Try to set up Chrome
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            driver.quit()
        except Exception as e:
            pytest.skip(f"Browser tests require Chrome: {str(e)}")

# Add custom markers
def pytest_configure(config):
    """Configure custom markers for pytest."""
    config.addinivalue_line(
        "markers",
        "browser: mark test as requiring a browser"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running"
    )

# Configure test timeout (10 seconds by default)
def pytest_collection_modifyitems(config, items):
    """Add a timeout to all tests."""
    if not config.getoption("--no-timeout"):
        for item in items:
            if "timeout" not in item.keywords:
                item.add_marker(pytest.mark.timeout(10))

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--no-timeout",
        action="store_true",
        default=False,
        help="disable test timeouts"
    )
