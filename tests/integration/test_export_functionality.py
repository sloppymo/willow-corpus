import os
import pytest
import time
from pathlib import Path

# Import the visualization module
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / 'scripts'))

# Sample analysis data for testing
SAMPLE_ANALYSIS = {
    "basic_statistics": {"total_scenarios": 100, "average_dialogue_turns": 3.5},
    "identity_factors": {
        "race": {"White": 40, "Black": 30, "Asian": 20, "Hispanic": 10},
        "age": {"18-25": 15, "26-35": 30, "36-50": 35, "51+": 20}
    },
    "vulnerability_distribution": {
        "High": 30,
        "Medium": 50,
        "Low": 20
    }
}

@pytest.fixture
def sample_analysis_file(tmp_path):
    """Create a temporary file with sample analysis data"""
    file_path = tmp_path / "sample_analysis.json"
    with open(file_path, 'w') as f:
        json.dump(SAMPLE_ANALYSIS, f)
    return str(file_path)

@pytest.fixture
def chrome_driver():
    """Set up and tear down Chrome WebDriver"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Set up the driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    yield driver
    
    # Clean up
    driver.quit()

def test_png_export(tmp_path, chrome_driver):
    """Test exporting charts as PNG"""
    # Generate the dashboard
    from scripts.visualize_analysis import AnalysisVisualizer
    
    output_file = tmp_path / "dashboard.html"
    visualizer = AnalysisVisualizer(SAMPLE_ANALYSIS)
    visualizer.create_demographic_charts()
    visualizer.generate_html_dashboard(str(output_file))
    
    # Set up Chrome in headless mode
    chrome_driver.get(f"file://{output_file.resolve()}")
    
    # Wait for page to load
    time.sleep(2)
    
    # Find and click PNG export button
    export_buttons = chrome_driver.find_elements_by_xpath("//button[contains(., 'PNG')]")
    assert len(export_buttons) > 0, "No PNG export buttons found"
    
    # Click the first export button
    export_buttons[0].click()
    
    # Wait for download to complete
    time.sleep(2)
    
    # Check if file was downloaded
    downloads = list(tmp_path.glob("*.png"))
    assert len(downloads) > 0, "No PNG file was downloaded"
    assert downloads[0].stat().st_size > 0, "Downloaded PNG file is empty"

def test_pdf_export(tmp_path, chrome_driver):
    """Test exporting the entire dashboard as PDF"""
    # Generate the dashboard
    from scripts.visualize_analysis import AnalysisVisualizer
    
    output_file = tmp_path / "dashboard.html"
    visualizer = AnalysisVisualizer(SAMPLE_ANALYSIS)
    visualizer.create_demographic_charts()
    visualizer.generate_html_dashboard(str(output_file))
    
    # Set up Chrome in headless mode
    chrome_driver.get(f"file://{output_file.resolve()}")
    
    # Wait for page to load
    time.sleep(2)
    
    # Find and click PDF export button
    export_buttons = chrome_driver.find_elements_by_xpath("//button[contains(., 'PDF')]")
    assert len(export_buttons) > 0, "No PDF export buttons found"
    
    # Click the first export button
    export_buttons[0].click()
    
    # Wait for download to complete
    time.sleep(3)  # PDF generation might take longer
    
    # Check if file was downloaded
    downloads = list(tmp_path.glob("*.pdf"))
    assert len(downloads) > 0, "No PDF file was downloaded"
    assert downloads[0].stat().st_size > 0, "Downloaded PDF file is empty"

def test_svg_export(tmp_path, chrome_driver):
    """Test exporting charts as SVG"""
    # Generate the dashboard
    from scripts.visualize_analysis import AnalysisVisualizer
    
    output_file = tmp_path / "dashboard.html"
    visualizer = AnalysisVisualizer(SAMPLE_ANALYSIS)
    visualizer.create_demographic_charts()
    visualizer.generate_html_dashboard(str(output_file))
    
    # Set up Chrome in headless mode
    chrome_driver.get(f"file://{output_file.resolve()}")
    
    # Wait for page to load
    time.sleep(2)
    
    # Find and click SVG export button
    export_buttons = chrome_driver.find_elements_by_xpath("//button[contains(., 'SVG')]")
    assert len(export_buttons) > 0, "No SVG export buttons found"
    
    # Click the first export button
    export_buttons[0].click()
    
    # Wait for download to complete
    time.sleep(2)
    
    # Check if file was downloaded
    downloads = list(tmp_path.glob("*.svg"))
    assert len(downloads) > 0, "No SVG file was downloaded"
    assert downloads[0].stat().st_size > 0, "Downloaded SVG file is empty"

def test_export_accessibility(tmp_path, chrome_driver):
    """Test that exported files maintain accessibility features"""
    from scripts.visualize_analysis import AnalysisVisualizer
    
    output_file = tmp_path / "dashboard.html"
    visualizer = AnalysisVisualizer(SAMPLE_ANALYSIS)
    visualizer.create_demographic_charts()
    visualizer.generate_html_dashboard(
        str(output_file),
        title="Accessibility Test Dashboard"
    )
    
    # Set up Chrome in headless mode
    chrome_driver.get(f"file://{output_file.resolve()}")
    
    # Wait for page to load
    time.sleep(2)
    
    # Check for accessibility features in HTML
    page_source = chrome_driver.page_source
    assert 'role="main"' in page_source
    assert 'aria-label=' in page_source
    
    # Export as PDF and check content
    pdf_button = chrome_driver.find_element_by_xpath("//button[contains(., 'PDF')]")
    pdf_button.click()
    
    # Wait for download
    time.sleep(3)
    
    # Find the downloaded PDF
    pdf_files = list(tmp_path.glob("*.pdf"))
    assert len(pdf_files) > 0
    
    # Check PDF content (basic check)
    pdf_path = pdf_files[0]
    with open(pdf_path, 'rb') as f:
        pdf_content = f.read().decode('latin-1')
        
    # Check for title in PDF
    assert 'Accessibility Test Dashboard' in pdf_content

def test_export_performance(tmp_path):
    """Test performance of export functionality"""
    from scripts.visualize_analysis import AnalysisVisualizer
    import time
    
    # Create a larger dataset
    large_data = {"basic_statistics": {"total_scenarios": 1000}}
    large_data["identity_factors"] = {
        "race": {f"race_{i}": i*10 for i in range(1, 51)}
    }
    
    visualizer = AnalysisVisualizer(large_data)
    
    # Time the chart generation
    start_time = time.time()
    visualizer.create_demographic_charts()
    generation_time = time.time() - start_time
    
    # Time the HTML generation
    output_file = tmp_path / "performance_test.html"
    start_time = time.time()
    visualizer.generate_html_dashboard(str(output_file))
    html_generation_time = time.time() - start_time
    
    # Check performance metrics
    assert generation_time < 5.0, "Chart generation took too long"
    assert html_generation_time < 10.0, "HTML generation took too long"
    
    # Verify file was created
    assert output_file.exists()
    assert output_file.stat().st_size > 0
