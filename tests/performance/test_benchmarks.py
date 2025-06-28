"""Performance benchmarking tests for the visualization toolkit."""
import pytest
import time
import json
from pathlib import Path
import numpy as np

# Import the visualization module
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / 'scripts'))
from visualize_analysis import AnalysisVisualizer

# Performance test markers
pytestmark = [
    pytest.mark.performance,
    pytest.mark.skipif(
        not pytest.config.getoption("--run-performance"),
        reason="Performance tests only run with --run-performance flag"
    )
]

def generate_mock_data(dataset_size):
    """Generate mock dataset for performance testing."""
    return {
        "basic_statistics": {
            "total_scenarios": dataset_size,
            "average_dialogue_turns": 3.5,
            "scenarios_by_type": {
                f"type_{i}": dataset_size // 10 for i in range(10)
            }
        },
        "identity_factors": {
            "race": {f"Race_{i}": dataset_size // 10 for i in range(10)},
            "age": {f"Age_{i}": dataset_size // 5 for i in range(5)},
            "disability_status": {"Yes": int(dataset_size * 0.15), "No": int(dataset_size * 0.85)}
        },
        "vulnerability_distribution": {
            f"Vuln_{i}": dataset_size // 20 for i in range(20)
        },
        "dialogue_metrics": {
            "average_turn_count": 3.5,
            "emotion_distribution": {
                "Positive": int(dataset_size * 0.35),
                "Neutral": int(dataset_size * 0.5),
                "Negative": int(dataset_size * 0.15)
            }
        },
        "conflict_resolution": {
            "resolved": int(dataset_size * 0.8),
            "escalated": int(dataset_size * 0.1),
            "pending": int(dataset_size * 0.1)
        }
    }

@pytest.mark.parametrize("dataset_size", [100, 1000, 5000], ids=["small", "medium", "large"])
def test_dashboard_generation_performance(dataset_size, benchmark):
    """Benchmark dashboard generation with different dataset sizes."""
    data = generate_mock_data(dataset_size)
    
    def setup():
        visualizer = AnalysisVisualizer(data)
        return (visualizer,), {}
    
    def run_benchmark(visualizer):
        visualizer.create_demographic_charts()
        visualizer.create_vulnerability_charts()
        visualizer.create_dialogue_metrics()
        visualizer.create_conflict_resolution_charts()
        
        # Generate HTML
        with open("temp_dashboard.html", "w") as f:
            visualizer.generate_html_dashboard(f.name)
    
    benchmark.pedantic(run_benchmark, setup=setup, rounds=3)
    
    # Performance assertions (adjust based on your requirements)
    mean_time = benchmark.stats["mean"]
    max_time = benchmark.stats["max"]
    
    # Log performance metrics
    print(f"\nDataset size: {dataset_size}")
    print(f"Mean time: {mean_time:.2f}s")
    print(f"Max time: {max_time:.2f}s")
    
    # Assert performance thresholds (adjust as needed)
    threshold = 0.1 * dataset_size  # 100ms per scenario
    assert mean_time < threshold, f"Performance threshold exceeded: {mean_time:.2f}s > {threshold}s"

@pytest.mark.parametrize("num_charts", [5, 20, 50], ids=["few", "medium", "many"])
def test_chart_rendering_performance(num_charts, benchmark):
    """Test performance with varying numbers of charts."""
    data = generate_mock_data(1000)
    
    def setup():
        visualizer = AnalysisVisualizer(data)
        # Generate multiple charts
        for i in range(num_charts):
            visualizer.create_demographic_charts()
        return (visualizer,), {}
    
    def run_benchmark(visualizer):
        with open("temp_dashboard.html", "w") as f:
            visualizer.generate_html_dashboard(f.name)
    
    benchmark.pedantic(run_benchmark, setup=setup, rounds=3)
    
    # Log performance metrics
    print(f"\nNumber of charts: {num_charts}")
    print(f"Mean time: {benchmark.stats['mean']:.2f}s")

@pytest.mark.parametrize("theme", ["light", "dark", "high_contrast"])
def test_theme_application_performance(theme, benchmark):
    """Test performance of different theme applications."""
    data = generate_mock_data(1000)
    
    def setup():
        visualizer = AnalysisVisualizer(data, theme=theme)
        return (visualizer,), {}
    
    def run_benchmark(visualizer):
        visualizer.create_demographic_charts()
        with open(f"temp_{theme}.html", "w") as f:
            visualizer.generate_html_dashboard(f.name)
    
    benchmark(run_benchmark)
    
    # Log performance metrics
    print(f"\nTheme: {theme}")
    print(f"Mean time: {benchmark.stats['mean']:.2f}s")

def test_memory_usage():
    """Test memory usage with large datasets."""
    import tracemalloc
    import gc
    
    # Generate a large dataset
    data = generate_mock_data(10000)
    
    # Start tracking memory
    tracemalloc.start()
    
    # Create visualizer and generate charts
    visualizer = AnalysisVisualizer(data)
    visualizer.create_demographic_charts()
    visualizer.create_vulnerability_charts()
    
    # Take snapshot and calculate memory usage
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    # Log memory usage
    print("\nMemory usage (top 5):")
    for stat in top_stats[:5]:
        print(stat)
    
    # Clean up
    del visualizer
    gc.collect()
    
    # Assert memory usage is reasonable (adjust threshold as needed)
    total_mb = sum(stat.size for stat in top_stats) / (1024 * 1024)
    print(f"Total memory used: {total_mb:.2f} MB")
    assert total_mb < 500, f"Memory usage too high: {total_mb:.2f} MB"

# Helper function to generate performance report
def pytest_benchmark_group_stats(config, benchmarks, group_by):
    """Generate performance report after benchmarks complete."""
    if not benchmarks:
        return
        
    print("\n" + "="*50)
    print("PERFORMANCE REPORT")
    print("="*50)
    
    for bench in benchmarks:
        print(f"\n{bench['name']}:")
        print(f"  Mean: {bench['stats']['mean']:.4f} ± {bench['stats']['stddev']:.4f} sec")
        print(f"  Min: {bench['stats']['min']:.4f} sec")
        print(f"  Max: {bench['stats']['max']:.4f} sec")
    
    print("\n" + "="*50 + "\n")
