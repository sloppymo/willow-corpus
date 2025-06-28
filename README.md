# Willow Corpus

A comprehensive, trauma-informed dataset and scenario generator for housing compliance and tenant management AI.

## 📋 Overview

Willow Corpus provides a structured dataset of housing scenarios, tenant interactions, and compliance guidelines for training AI models in fair housing and accessibility compliance. The corpus includes:

- **Scenario Blueprints**: Detailed ADA/FHA complaint-resolution flows
- **Tenant Interactions**: Realistic dialogues with trauma-informed responses
- **Staff Guidance**: Internal policies and procedures for housing staff
- **Validation Tools**: Automated validation of compliance and consistency

## 🚀 Features

- **Trauma-Informed**: Designed with psychological safety and empathy
- **Legally Compliant**: Built on ADA, FHA, and fair housing regulations
- **Structured Data**: Consistent JSON schema for all scenarios
- **Automated Validation**: Built-in validation of legal and ethical guidelines
- **Extensible**: Easy to add new scenarios and response patterns
- **Administrative Entries**: Comprehensive support for case management, reporting, communication, and training scenarios
- **CI/CD Ready**: GitHub Actions workflows for automated testing and validation

## 🛠 Installation

### Development Setup

```bash
# Clone the repository
git clone https://github.com/sloppymo/willow-corpus.git
cd willow-corpus

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e '.[dev,docs]'

# Set up pre-commit hooks
pre-commit install
```

### Quick Start

1. **Install the package** (from the project root):
   ```bash
   python scripts/install_dev.py
   ```

## 📊 Administrative Entries

The Willow Corpus includes comprehensive support for administrative scenarios, which are essential for training AI models to handle various housing management tasks. These entries cover four main categories:

1. **Case Management**
   - Track and manage tenant cases
   - Handle maintenance requests, lease violations, and other housing-related issues
   - Includes priority levels, status tracking, and assignment features

2. **Reporting**
   - Generate various types of reports (maintenance, compliance, financial, etc.)
   - Track key metrics and KPIs
   - Support for different reporting periods and formats

3. **Communication**
   - Internal and external communications
   - Memos, emails, and meeting notes
   - Document important conversations and decisions

4. **Training**
   - Staff training records and materials
   - Track training completion and certifications
   - Document training sessions and participant feedback

### Working with Administrative Entries

#### Generating New Entries

To generate new administrative entries, use the following command:

```bash
python -m scripts.generate_underrepresented_entries
```

This will create a new JSON file in `data/processed/admin_entries/` with a timestamp in the filename.

#### Merging with Main Dataset

To merge administrative entries with the main scenarios file:

```bash
python scripts/merge_admin_entries.py data/merged_scenarios.json data/processed/admin_entries/your_admin_entries.json -o data/merged_scenarios_with_admin.json
```

#### Validation

All administrative entries are automatically validated against the schema before being included in the merged dataset.

---

2. **Generate test scenarios**:
   ```bash
   # Generate a single test scenario
   willow-generate --output-dir data/scenarios
   
   # Generate 5 housing scenarios
   willow-generate --type housing --count 5 --output-dir data/scenarios
   ```

3. **Validate scenarios**:
   ```bash
   # Validate a single file
   willow-validate path/to/scenario.json
   
   # Validate all scenarios in a directory
   willow-validate data/scenarios
   ```

4. **Run tests**:
   ```bash
   pytest scripts/test_generator_integration.py -v
   ```

## 📊 Project Structure

```
willow/
├── corpus/                 # Core dataset files
│   ├── scenarios/         # Scenario definitions
│   ├── microresponses/    # Building blocks for responses
│   └── qa_pairs/          # Common Q&A pairs
├── models/                # Data models and schemas
├── validators/            # Validation logic
├── generators/            # Scenario generation tools
└── cli.py                 # Command-line interface

tests/                    # Test suite
docs/                     # Documentation
```

## 🛠️ Using the CLI

The Willow Corpus includes a command-line interface for common tasks:

```bash
# Validate scenarios
willow validate path/to/scenarios/*.json

# Format a scenario file
willow format path/to/scenario.json -o formatted_scenario.json

# Generate a new scenario from a template
willow generate --template=accessibility -o new_scenario.json
```

## 🧪 Testing & Validation

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=willow tests/

# Run a specific test file
pytest tests/test_validators.py -v
```

### Validating Scenarios

```bash
# Validate a single scenario file
python -m willow validate data/scenarios/example.json

# Validate a directory of scenarios
python -m willow validate data/scenarios/ --output validation-results.json

# Validate with verbose output
python -m willow validate data/scenarios/ -v
```

### Pre-commit Hooks

Pre-commit hooks are configured to ensure code quality. They run automatically on each commit:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Static type checking
- **pytest**: Run tests

## 🔄 CI/CD Pipeline

The GitHub Actions workflow includes:

1. **Testing**: Runs tests across Python 3.9-3.11
2. **Linting**: Checks code style and type hints
3. **Scenario Validation**: Validates all scenario files
4. **Coverage**: Reports test coverage

## 📝 Adding New Scenarios

1. Create a new JSON file in `data/scenarios/`
2. Follow the schema defined in `willow/models/scenario.py`
3. Validate your scenario:
   ```bash
   python -m willow validate path/to/your_scenario.json
   ```
4. Add tests for any new functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-scenario-type`
3. Commit your changes: `git commit -am 'Add new scenario type'`
4. Push to the branch: `git push origin feature/new-scenario-type`
5. Submit a pull request

Please ensure all tests pass and new code includes appropriate test coverage.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Support

For questions or support, please [open an issue](https://github.com/sloppymo/willow-corpus/issues).
