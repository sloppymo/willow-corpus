import pytest
import json
import tempfile
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
        }
    }

def test_data_loading(tmp_path):
    # Create a temporary file with sample data
    file_path = tmp_path / "test_data.json"
    test_data = {"test": "data"}
    with open(file_path, 'w') as f:
        json.dump(test_data, f)
    
    # Test loading data from file path
    visualizer = AnalysisVisualizer(str(file_path))
    assert visualizer.analysis == test_data
    
    # Test loading data from dict
    visualizer = AnalysisVisualizer(test_data)
    assert visualizer.analysis == test_data

def test_missing_data(sample_data):
    # Remove a key that's normally expected
    del sample_data["basic_statistics"]
    
    # Should handle missing data gracefully
    visualizer = AnalysisVisualizer(sample_data)
    visualizer.create_demographic_charts()
    
    # Should still create charts for available data
    assert len(visualizer.figures) > 0

def test_sampling_large_datasets():
    # Create a large dataset
    large_data = {
        "basic_statistics": {"total_scenarios": 1500},
        "dialogue_patterns": {
            "turn_count_distribution": {str(i): i*10 for i in range(1, 101)}
        },
        "identity_factors": {
            "race": {f"race_{i}": i*5 for i in range(1, 51)}
        }
    }
    
    visualizer = AnalysisVisualizer(large_data, sample_size=0.5)  # 50% sampling
    visualizer.create_demographic_charts()
    
    # Should have sampled data (reduced number of categories)
    fig_data = visualizer.figures[0].data[0]
    assert len(fig_data.labels) < 50  # Sampled down
    assert sum(fig_data.values) == 1500  # Total preserved

def test_invalid_data_handling():
    # Test with completely invalid data
    with pytest.raises(ValueError):
        AnalysisVisualizer(None)
    
    # Test with empty data
    with pytest.raises(ValueError):
        AnalysisVisualizer({})
    
    # Test with invalid file path
    with pytest.raises(FileNotFoundError):
        AnalysisVisualizer("nonexistent_file.json")
