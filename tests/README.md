# Willow Dataset Toolkit - Test Suite

This directory contains the comprehensive test suite for the Willow Dataset Toolkit, including unit tests, integration tests, performance benchmarks, security scans, and documentation coverage checks.

## Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_data_handling.py     # Tests for data loading and processing
│   ├── test_chart_generation.py  # Tests for chart generation
│   ├── test_html_generation.py   # Tests for HTML dashboard generation
│   └── test_theme_handling.py    # Tests for theme handling
├── integration/              # Integration tests
│   ├── test_full_workflow.py     # End-to-end workflow tests
│   └── test_export_functionality.py  # Tests for export features
├── performance/              # Performance benchmarks
│   ├── test_benchmarks.py       # Performance tests for visualization
│   └── test_load_handling.py    # Load testing scenarios
├── security/                 # Security tests
│   ├── test_vulnerabilities.py  # Security vulnerability scans
│   └── test_injection.py       # Injection attack tests
├── documentation/            # Documentation tests
│   ├── test_doc_coverage.py    # Docstring coverage checks
│   └── test_examples.py        # Example code validation
├── data/                     # Test data files
│   ├── sample_analysis_small.json
│   ├── sample_analysis_large.json
│   └── sample_analysis_edge_cases.json
├── conftest.py               # Pytest configuration and fixtures
└── pytest.ini               # Pytest configuration
```

## Running the Tests

### Prerequisites

1. Install the test and development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

2. For browser-based tests, ensure you have Chrome installed.

### Running All Tests

```bash
# Run all tests (unit, integration, documentation, security, performance)
pytest

# Run with coverage report
pytest --cov=scripts --cov-report=html
```

### Running Specific Test Categories

- **Unit Tests**:
  ```bash
  pytest tests/unit/
  ```

- **Integration Tests**:
  ```bash
  pytest tests/integration/
  ```
  
- **Performance Tests**:
  ```bash
  pytest tests/performance/ --run-performance
  ```

- **Security Tests**:
  ```bash
  # Install safety for dependency scanning
  pip install safety
  pytest tests/security/ --run-security
  ```

- **Documentation Tests**:
  ```bash
  pytest tests/documentation/ --run-docs
  ```

### Advanced Test Options

- Run tests in parallel (requires `pytest-xdist`):
  ```bash
  pytest -n auto
  ```

- Run tests with detailed output:
  ```bash
  pytest -v
  ```

- Run only failed tests from the last run:
  ```bash
  pytest --last-failed
  ```

- Generate JUnit XML reports (for CI):
  ```bash
  pytest --junitxml=test-results.xml
  ```

### Test Markers

Use these markers to run specific test categories:

```bash
# Run only fast tests
pytest -m "not slow"

# Run only browser tests
pytest -m "browser"

# Run only performance tests
pytest -m "performance"
# Run only security tests
pytest -m "security"
# Run only documentation tests
pytest -m "documentation"
```

## CI/CD Integration

The test suite is integrated with GitHub Actions for continuous integration. The workflow includes:

- Running tests on Python 3.9, 3.10, and 3.11
- Executing unit, integration, security, and documentation tests
- Generating code coverage reports
- Uploading coverage to Codecov

### Viewing CI Results

1. Go to the **Actions** tab in the GitHub repository
2. Select the workflow run to view test results
3. Check the **Codecov** report for coverage details

## Performance Testing

Performance benchmarks are included to ensure the visualization toolkit remains efficient:

```bash
# Run all performance tests
pytest tests/performance/ --run-performance

# Generate performance baseline
pytest tests/performance/ --benchmark-save=baseline

# Compare against baseline
pytest tests/performance/ --benchmark-compare=baseline
```

## Security Scanning

Security tests help identify potential vulnerabilities:

```bash
# Install security tools
pip install safety bandit

# Run security tests
pytest tests/security/ --run-security

# Manual security scan
bandit -r scripts/
```

## Documentation Testing

Documentation tests ensure code is properly documented:

```bash
# Check docstring coverage
pytest tests/documentation/ --run-docs

# Generate documentation coverage report
pytest --doctest-modules --cov=scripts --cov-report=term-missing
```

## Test Data

The `tests/data` directory contains sample analysis files:

- `sample_analysis_small.json`: Small dataset for quick tests (~100 scenarios)
- `sample_analysis_large.json`: Large dataset for performance testing (~10,000 scenarios)
- `sample_analysis_edge_cases.json`: Edge cases and error conditions
- `sample_analysis_minimal.json`: Minimal valid dataset for validation

## Writing New Tests

### Test Organization

1. **Unit Tests**: Test individual functions and classes in isolation
   - Place in `tests/unit/`
   - Focus on a single component
   - Mock external dependencies

2. **Integration Tests**: Test interactions between components
   - Place in `tests/integration/`
   - Test complete workflows
   - Use real dependencies when possible

3. **Performance Tests**: Test speed and resource usage
   - Place in `tests/performance/`
   - Use `pytest-benchmark` for timing
   - Include memory usage checks

4. **Security Tests**: Test for vulnerabilities
   - Place in `tests/security/`
   - Check for common security issues
   - Test input validation

5. **Documentation Tests**: Test code documentation
   - Place in `tests/documentation/`
   - Ensure all public APIs are documented
   - Check for broken examples

### Test Guidelines

1. **Naming Conventions**:
   - Test files: `test_*.py`
   - Test functions: `test_*`
   - Test classes: `Test*`

2. **Test Structure**:
   - Use the Arrange-Act-Assert pattern
   - Keep tests focused and independent
   - Use descriptive test names

3. **Fixtures**:
   - Define common test data in `conftest.py`
   - Use fixtures for setup/teardown
   - Share fixtures across tests when appropriate

4. **Assertions**:
   - Use specific assertions (`assert x == y` not `assert x`)
   - Include descriptive failure messages
   - Test both happy paths and error conditions

5. **Performance**:
   - Mark slow tests with `@pytest.mark.slow`
   - Use `pytest-benchmark` for performance testing
   - Set realistic performance thresholds

## Test Coverage

Code coverage is tracked using `pytest-cov`. To generate coverage reports:

```bash
# Basic coverage report
pytest --cov=scripts

# HTML report (opens in browser)
pytest --cov=scripts --cov-report=html

# XML report (for CI)
pytest --cov=scripts --cov-report=xml

# Fail if coverage is below threshold
pytest --cov=scripts --cov-fail-under=80
```

## Troubleshooting

### Common Issues

1. **Tests failing with Chrome errors**
   - Ensure Chrome is installed
   - Check ChromeDriver version matches Chrome version
   - Set `HEADLESS=true` for environments without display

2. **Performance test failures**
   - Run tests multiple times to account for system load
   - Adjust performance thresholds in `pytest.ini`
   - Mark flaky tests with `@pytest.mark.flaky`

3. **Security test failures**
   - Update dependencies with `pip install --upgrade -r requirements.txt`
   - Check for false positives in security scans
   - Document any intentional security exceptions

4. **Documentation test failures**
   - Add missing docstrings
   - Update outdated documentation
   - Use `# noqa: DARxxx` to disable specific docstring checks

## Contributing

1. Write tests for new features
2. Ensure all tests pass before submitting a PR
3. Update documentation when adding new features
4. Follow the existing code style
5. Keep test data up to date

## License

This test suite is part of the Willow Dataset Toolkit and is licensed under the same terms.
pytest --cov=scripts --cov-report=html
open htmlcov/index.html  # View the report in a browser
```

## Continuous Integration

The test suite is configured to run automatically on pull requests and merges to the main branch. The CI pipeline includes:

- Unit tests
- Integration tests
- Code coverage reporting
- Code style checks
- Type checking

## Troubleshooting

- **Tests are slow**: Use `pytest -n auto` to run tests in parallel.
- **Browser tests fail**: Ensure Chrome is installed and the ChromeDriver version matches your Chrome version.
- **Missing dependencies**: Run `pip install -r requirements-test.txt`.
- **Test failures**: Check the test output for detailed error messages and stack traces.

## License

This test suite is part of the Willow Dataset project and is licensed under the same terms.
