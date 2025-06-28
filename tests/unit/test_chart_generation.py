import pytest
import plotly.graph_objects as go
from pathlib import Path

# Import the visualization module
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / 'scripts'))
from visualize_analysis import AnalysisVisualizer

@pytest.fixture
def sample_data():
    return {
        "basic_statistics": {"total_scenarios": 100, "average_dialogue_turns": 3.5},
        "identity_factors": {
            "race": {"White": 40, "Black": 30, "Asian": 20, "Hispanic": 10},
            "age": {"18-25": 15, "26-35": 30, "36-50": 35, "51+": 20}
        },
        "vulnerability_distribution": {
            "Vulnerable": 45,
            "Moderate": 35,
            "Low": 20
        },
        "dialogue_metrics": {
            "average_turn_count": 4.2,
            "emotion_distribution": {
                "Positive": 40, "Neutral": 45, "Negative": 15
            }
        }
    }

def test_demographic_charts(sample_data):
    visualizer = AnalysisVisualizer(sample_data)
    
    # Test generating all demographic charts
    visualizer.create_demographic_charts()
    
    # Should create charts for each demographic factor
    assert len(visualizer.figures) >= 2  # At least race and age
    
    # Verify chart types and titles
    chart_titles = [fig.layout.title.text for fig in visualizer.figures]
    assert any("Race Distribution" in title for title in chart_titles)
    assert any("Age Group Distribution" in title for title in chart_titles)
    
    # Verify data integrity
    for fig in visualizer.figures:
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

def test_vulnerability_charts(sample_data):
    visualizer = AnalysisVisualizer(sample_data)
    visualizer.create_vulnerability_charts()
    
    assert len(visualizer.figures) == 1
    fig = visualizer.figures[0]
    
    # Check chart properties
    assert "Vulnerability Distribution" in fig.layout.title.text
    assert len(fig.data[0].values) == 3  # Three categories
    assert sum(fig.data[0].values) == 100  # Should sum to 100%

def test_dialogue_metrics_charts(sample_data):
    visualizer = AnalysisVisualizer(sample_data)
    visualizer.create_dialogue_metrics()
    
    # Should create at least one chart for dialogue metrics
    assert len(visualizer.figures) >= 1
    
    # Check if emotion distribution chart is present
    emotion_figs = [f for f in visualizer.figures 
                   if hasattr(f.layout, 'title') and 'Emotion Distribution' in f.layout.title.text]
    assert len(emotion_figs) == 1

def test_chart_theme_application(sample_data):
    # Test light theme
    visualizer_light = AnalysisVisualizer(sample_data, theme="light")
    visualizer_light.create_demographic_charts()
    
    # Test dark theme
    visualizer_dark = AnalysisVisualizer(sample_data, theme="dark")
    visualizer_dark.create_demographic_charts()
    
    # Verify theme application by checking background colors
    light_bg = visualizer_light.figures[0].layout.paper_bgcolor
    dark_bg = visualizer_dark.figures[0].layout.paper_bgcolor
    
    assert light_bg != dark_bg
    assert light_bg == "#f8f9fa"  # Light theme background
    assert dark_bg == "#121212"   # Dark theme background

def test_chart_export_formats(sample_data, tmp_path):
    visualizer = AnalysisVisualizer(sample_data)
    visualizer.create_demographic_charts()
    
    # Test exporting to different formats
    export_dir = tmp_path / "exports"
    export_dir.mkdir()
    
    # Test PNG export
    png_path = export_dir / "chart.png"
    visualizer.export_chart(visualizer.figures[0], str(png_path), "png")
    assert png_path.exists()
    assert png_path.stat().st_size > 0
    
    # Test SVG export
    svg_path = export_dir / "chart.svg"
    visualizer.export_chart(visualizer.figures[0], str(svg_path), "svg")
    assert svg_path.exists()
    assert svg_path.stat().st_size > 0
    
    # Test PDF export
    pdf_path = export_dir / "chart.pdf"
    visualizer.export_chart(visualizer.figures[0], str(pdf_path), "pdf")
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
