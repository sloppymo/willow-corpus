import os
import json
import subprocess
import tempfile
import time
from pathlib import Path
import pytest

# Import the visualization module
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / 'scripts'))

# Sample analysis data for testing
SAMPLE_ANALYSIS = {
    "basic_statistics": {
        "total_scenarios": 150,
        "average_dialogue_turns": 3.7,
        "scenarios_by_type": {
            "maintenance": 45,
            "lease": 35,
            "noise": 30,
            "accessibility": 25,
            "other": 15
        }
    },
    "identity_factors": {
        "race": {
            "White": 70,
            "Black": 40,
            "Hispanic": 25,
            "Asian": 10,
            "Other": 5
        },
        "age": {
            "18-25": 20,
            "26-35": 45,
            "36-50": 50,
            "51+": 35
        },
        "disability_status": {
            "Yes": 25,
            "No": 125
        }
    },
    "vulnerability_distribution": {
        "High": 30,
        "Medium": 65,
        "Low": 55
    },
    "dialogue_metrics": {
        "average_turn_count": 3.7,
        "emotion_distribution": {
            "Positive": 35,
            "Neutral": 80,
            "Negative": 35
        },
        "common_topics": ["maintenance", "lease", "noise", "accessibility"]
    },
    "conflict_resolution": {
        "resolved": 120,
        "escalated": 20,
        "pending": 10
    },
    "compliance_metrics": {
        "legal_requirements_met": 145,
        "potential_risks": 5,
        "accessibility_issues": 3
    },
    "sentiment_analysis": {
        "positive": 70,
        "neutral": 60,
        "negative": 20
    }
}

@pytest.fixture
def sample_analysis_file(tmp_path):
    """Create a temporary file with sample analysis data"""
    file_path = tmp_path / "sample_analysis.json"
    with open(file_path, 'w') as f:
        json.dump(SAMPLE_ANALYSIS, f)
    return str(file_path)

def test_end_to_end_workflow(tmp_path, sample_analysis_file):
    """Test the full workflow from analysis to visualization"""
    # Output file for the dashboard
    output_file = tmp_path / "dashboard.html"
    
    # Run the visualization script
    cmd = [
        sys.executable, 
        str(Path(__file__).parent.parent.parent / "scripts" / "visualize_analysis.py"),
        "-i", sample_analysis_file,
        "-o", str(output_file),
        "--title", "Integration Test Dashboard",
        "--theme", "dark"
    ]
    
    # Execute the command
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Check command execution
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"
    
    # Verify output file was created
    assert output_file.exists(), "Dashboard HTML file was not created"
    assert output_file.stat().st_size > 1000, "Dashboard file is too small"
    
    # Check content
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check for key elements
    assert "<title>Integration Test Dashboard</title>" in content
    assert "Plotly.newPlot" in content
    assert "Race Distribution" in content
    
    # Check for theme
    assert "bg-dark" in content
    
    # Check for charts
    assert "Highcharts.chart" in content or "Plotly.newPlot" in content

def test_command_line_arguments(tmp_path, sample_analysis_file):
    """Test various command line arguments"""
    output_file = tmp_path / "args_test.html"
    
    # Test with minimal arguments
    cmd = [
        sys.executable, 
        str(Path(__file__).parent.parent.parent / "scripts" / "visualize_analysis.py"),
        "-i", sample_analysis_file,
        "-o", str(output_file)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert output_file.exists()
    
    # Test with all arguments
    output_file_full = tmp_path / "full_args_test.html"
    cmd = [
        sys.executable, 
        str(Path(__file__).parent.parent.parent / "scripts" / "visualize_analysis.py"),
        "-i", sample_analysis_file,
        "-o", str(output_file_full),
        "--title", "Full Args Test",
        "--theme", "light",
        "--charts", "demographics", "vulnerability",
        "--sample-size", "0.5"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert output_file_full.exists()

def test_error_handling():
    """Test error conditions and handling"""
    # Non-existent input file
    cmd = [
        sys.executable, 
        str(Path(__file__).parent.parent.parent / "scripts" / "visualize_analysis.py"),
        "-i", "nonexistent_file.json",
        "-o", "output.html"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode != 0
    assert "not found" in result.stderr.lower()
    
    # Invalid JSON
    with tempfile.NamedTemporaryFile(suffix='.json', mode='w') as tmp:
        tmp.write("invalid json")
        tmp.flush()
        
        cmd = [
            sys.executable, 
            str(Path(__file__).parent.parent.parent / "scripts" / "visualize_analysis.py"),
            "-i", tmp.name,
            "-o", "output.html"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode != 0
        assert "invalid" in result.stderr.lower()

def test_performance_large_dataset(tmp_path):
    """Test performance with a large dataset"""
    # Create a large dataset
    large_data = {
        "basic_statistics": {"total_scenarios": 10000},
        "identity_factors": {
            "race": {f"race_{i}": i*10 for i in range(1, 101)}
        },
        "vulnerability_distribution": {
            f"category_{i}": i*5 for i in range(1, 51)
        }
    }
    
    large_file = tmp_path / "large_analysis.json"
    with open(large_file, 'w') as f:
        json.dump(large_data, f)
    
    output_file = tmp_path / "large_dashboard.html"
    
    # Run with sampling
    start_time = time.time()
    cmd = [
        sys.executable, 
        str(Path(__file__).parent.parent.parent / "scripts" / "visualize_analysis.py"),
        "-i", str(large_file),
        "-o", str(output_file),
        "--sample-size", "0.1"  # 10% sampling
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    assert result.returncode == 0
    assert output_file.exists()
    
    # Check performance (should complete in reasonable time)
    assert (end_time - start_time) < 30  # Less than 30 seconds
    
    # Check file size is reasonable
    assert output_file.stat().st_size < 10 * 1024 * 1024  # Less than 10MB
