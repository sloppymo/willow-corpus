import os
import pytest
from pathlib import Path

# Import the visualization module
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / 'scripts'))
from visualize_analysis import AnalysisVisualizer

@pytest.fixture
def sample_visualizer():
    # Create a visualizer with sample data
    data = {
        "basic_statistics": {"total_scenarios": 100, "average_dialogue_turns": 3.5},
        "identity_factors": {
            "race": {"White": 40, "Black": 30, "Asian": 20, "Hispanic": 10}
        }
    }
    return AnalysisVisualizer(data)

def test_html_output(sample_visualizer, tmp_path):
    """Test basic HTML dashboard generation"""
    output_file = tmp_path / "dashboard.html"
    
    # Generate some charts first
    sample_visualizer.create_demographic_charts()
    
    # Generate the dashboard
    sample_visualizer.generate_html_dashboard(str(output_file), title="Test Dashboard")
    
    # Verify file was created and has content
    assert output_file.exists()
    assert output_file.stat().st_size > 1000  # Should have significant content
    
    # Check for key HTML elements
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    assert "<!DOCTYPE html>" in content
    assert "<title>Test Dashboard</title>" in content
    assert "Plotly.newPlot" in content  # Check for plotly.js initialization
    assert "Race Distribution" in content  # Should contain chart title

def test_custom_title(sample_visualizer, tmp_path):
    """Test dashboard with custom title"""
    output_file = tmp_path / "custom_title.html"
    custom_title = "Custom Analysis Dashboard"
    
    sample_visualizer.generate_html_dashboard(
        str(output_file), 
        title=custom_title,
        description="Test description"
    )
    
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert f"<title>{custom_title}</title>" in content
        assert f"<h1>{custom_title}</h1>" in content
        assert "Test description" in content

def test_dark_theme(sample_visualizer, tmp_path):
    """Test dashboard with dark theme"""
    output_file = tmp_path / "dark_theme.html"
    
    # Create some charts with dark theme
    sample_visualizer.theme = "dark"
    sample_visualizer.create_demographic_charts()
    
    # Generate dashboard
    sample_visualizer.generate_html_dashboard(str(output_file))
    
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check for dark theme classes and styles
    assert "bg-dark" in content
    assert "text-light" in content
    assert "#121212" in content  # Dark theme background color

def test_empty_dashboard(sample_visualizer, tmp_path):
    """Test dashboard generation with no charts"""
    output_file = tmp_path / "empty_dashboard.html"
    
    # Don't create any charts
    sample_visualizer.generate_html_dashboard(str(output_file))
    
    assert output_file.exists()
    
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "No charts to display" in content

def test_export_buttons(sample_visualizer, tmp_path):
    """Test that export buttons are included in the HTML"""
    output_file = tmp_path / "export_buttons.html"
    sample_visualizer.create_demographic_charts()
    sample_visualizer.generate_html_dashboard(str(output_file))
    
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check for export buttons
    assert "Export as PNG" in content
    assert "Export as SVG" in content
    assert "Export as PDF" in content
    
    # Check for Plotly export functionality
    assert "Plotly.download" in content
    
    # Check for export script inclusion
    assert "html2canvas" in content
    assert "jspdf" in content

def test_accessibility_features(sample_visualizer, tmp_path):
    """Test that accessibility features are included"""
    output_file = tmp_path / "accessibility.html"
    sample_visualizer.create_demographic_charts()
    sample_visualizer.generate_html_dashboard(str(output_file))
    
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check for ARIA attributes
    assert 'role="main"' in content
    assert 'aria-label=' in content
    
    # Check for skip links
    assert 'Skip to main content' in content
    
    # Check for high contrast mode toggle
    assert 'High Contrast Mode' in content
    
    # Check for proper heading structure
    assert '<h1>' in content
    assert '<h2>' in content
    
    # Check for figure captions
    assert '<figcaption>' in content
