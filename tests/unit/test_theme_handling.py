import pytest
from pathlib import Path

# Import the visualization module
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / 'scripts'))
from visualize_analysis import AnalysisVisualizer, COLOR_PALETTE

def test_default_theme():
    """Test that default theme is applied correctly"""
    visualizer = AnalysisVisualizer({"basic_statistics": {"total_scenarios": 100}})
    
    # Check default theme is light
    assert visualizer.theme == "light"
    
    # Check default colors are set
    assert visualizer.colors["background"] == "#f8f9fa"
    assert visualizer.colors["text"] == "#212529"
    assert visualizer.colors["primary"] == COLOR_PALETTE[0]

def test_theme_switching():
    """Test switching between themes"""
    visualizer = AnalysisVisualizer({"basic_statistics": {"total_scenarios": 100}})
    
    # Switch to dark theme
    visualizer.theme = "dark"
    assert visualizer.theme == "dark"
    assert visualizer.colors["background"] == "#121212"
    assert visualizer.colors["text"] == "#f8f9fa"
    
    # Switch back to light theme
    visualizer.theme = "light"
    assert visualizer.theme == "light"
    assert visualizer.colors["background"] == "#f8f9fa"
    assert visualizer.colors["text"] == "#212529"

def test_custom_theme():
    """Test applying a custom theme"""
    custom_theme = {
        "background": "#000000",
        "text": "#ffffff",
        "primary": "#ff0000",
        "secondary": "#00ff00",
        "accent": "#0000ff"
    }
    
    visualizer = AnalysisVisualizer(
        {"basic_statistics": {"total_scenarios": 100}},
        theme=custom_theme
    )
    
    # Check custom theme is applied
    assert visualizer.theme == "custom"
    assert visualizer.colors["background"] == "#000000"
    assert visualizer.colors["text"] == "#ffffff"
    assert visualizer.colors["primary"] == "#ff0000"

def test_invalid_theme():
    """Test handling of invalid theme"""
    with pytest.raises(ValueError):
        AnalysisVisualizer(
            {"basic_statistics": {"total_scenarios": 100}},
            theme="invalid_theme"
        )

def test_theme_application_to_charts():
    """Test that themes are correctly applied to charts"""
    data = {
        "basic_statistics": {"total_scenarios": 100},
        "identity_factors": {
            "race": {"White": 40, "Black": 30}
        }
    }
    
    # Test light theme
    visualizer_light = AnalysisVisualizer(data, theme="light")
    visualizer_light.create_demographic_charts()
    
    # Test dark theme
    visualizer_dark = AnalysisVisualizer(data, theme="dark")
    visualizer_dark.create_demographic_charts()
    
    # Get chart layouts
    light_layout = visualizer_light.figures[0].layout
    dark_layout = visualizer_dark.figures[0].layout
    
    # Check background colors
    assert light_layout.paper_bgcolor == "#f8f9fa"
    assert dark_layout.paper_bgcolor == "#121212"
    
    # Check text colors
    assert light_layout.font.color == "#212529"
    assert dark_layout.font.color == "#f8f9fa"

def test_high_contrast_theme():
    """Test high contrast theme settings"""
    visualizer = AnalysisVisualizer(
        {"basic_statistics": {"total_scenarios": 100}},
        theme="high_contrast"
    )
    
    # Check high contrast colors
    assert visualizer.colors["background"] == "#000000"
    assert visualizer.colors["text"] == "#ffffff"
    assert visualizer.colors["primary"] == "#ffff00"  # Yellow for high visibility

def test_theme_persistence():
    """Test that theme persists when changing visualizer properties"""
    visualizer = AnalysisVisualizer(
        {"basic_statistics": {"total_scenarios": 100}},
        theme="dark"
    )
    
    # Change some properties
    visualizer.sample_size = 0.5
    visualizer.chart_types = ["demographics"]
    
    # Theme should remain the same
    assert visualizer.theme == "dark"
    assert visualizer.colors["background"] == "#121212"

def test_theme_update():
    """Test updating theme after initialization"""
    visualizer = AnalysisVisualizer({"basic_statistics": {"total_scenarios": 100}})
    
    # Initial theme is light
    assert visualizer.theme == "light"
    
    # Update to dark theme
    visualizer.update_theme("dark")
    assert visualizer.theme == "dark"
    assert visualizer.colors["background"] == "#121212"
    
    # Update to custom theme
    custom_theme = {
        "background": "#000000",
        "text": "#ffffff"
    }
    visualizer.update_theme(custom_theme)
    assert visualizer.theme == "custom"
    assert visualizer.colors["background"] == "#000000"
    assert visualizer.colors["text"] == "#ffffff"
