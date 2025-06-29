"""
Enhanced Dataset Validator

Validates the enhanced dataset containing roommate conflict scenarios and other scenarios.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import jsonschema
from jsonschema import validate

def load_json_file(file_path: Path) -> Any:
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def validate_scenario(scenario: Dict) -> List[str]:
    """Validate a single scenario against the schema."""
    errors = []
    
    # Required fields
    required_fields = [
        'scenario_id', 'title', 'description', 'vulnerabilities', 'metadata'
    ]
    
    for field in required_fields:
        if field not in scenario:
            errors.append(f"Missing required field: {field}")
    
    # Validate metadata structure
    if 'metadata' in scenario:
        metadata = scenario['metadata']
        metadata_fields = ['created_at', 'last_updated', 'validation_status']
        
        for field in metadata_fields:
            if field not in metadata:
                errors.append(f"Missing required metadata field: {field}")
        
        # Validate timestamp format
        for ts_field in ['created_at', 'last_updated']:
            if ts_field in metadata:
                try:
                    datetime.fromisoformat(metadata[ts_field].replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    errors.append(f"Invalid timestamp format in {ts_field}: {metadata[ts_field]}")
    
    # Validate vulnerabilities
    if 'vulnerabilities' in scenario and not isinstance(scenario['vulnerabilities'], list):
        errors.append("vulnerabilities must be a list")
    
    # Validate messages if present
    if 'messages' in scenario:
        if not isinstance(scenario['messages'], list):
            errors.append("messages must be a list")
        else:
            for i, msg in enumerate(scenario['messages']):
                if not isinstance(msg, dict):
                    errors.append(f"Message {i} is not an object")
                    continue
                
                if 'role' not in msg:
                    errors.append(f"Message {i} missing required field: role")
                if 'content' not in msg:
                    errors.append(f"Message {i} missing required field: content")
    
    return errors

def validate_dataset(dataset: List[Dict]) -> Dict[str, Any]:
    """Validate the entire dataset."""
    if not isinstance(dataset, list):
        return {"valid": False, "errors": ["Dataset must be a list of scenarios"]}
    
    validation_results = {
        "valid": True,
        "scenarios_processed": 0,
        "scenarios_with_errors": 0,
        "total_errors": 0,
        "scenario_errors": {}
    }
    
    for i, scenario in enumerate(dataset):
        if not isinstance(scenario, dict):
            validation_results["scenario_errors"][f"scenario_{i}"] = ["Scenario is not an object"]
            validation_results["total_errors"] += 1
            continue
            
        scenario_id = scenario.get('scenario_id', f'scenario_{i}')
        errors = validate_scenario(scenario)
        
        if errors:
            validation_results["valid"] = False
            validation_results["scenarios_with_errors"] += 1
            validation_results["total_errors"] += len(errors)
            validation_results["scenario_errors"][scenario_id] = errors
            
        validation_results["scenarios_processed"] += 1
    
    return validation_results

def save_validation_report(validation_results: Dict, output_path: Path) -> bool:
    """Save validation results to a JSON file."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(validation_results, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving validation report: {e}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate enhanced dataset')
    parser.add_argument('-i', '--input', required=True, help='Input JSON file')
    parser.add_argument('-o', '--output', required=True, help='Output JSON report file')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    print(f"Loading dataset from {input_path}...")
    dataset = load_json_file(input_path)
    
    if dataset is None:
        print("Failed to load dataset")
        sys.exit(1)
    
    print("Validating dataset...")
    validation_results = validate_dataset(dataset)
    
    print(f"\nValidation complete. Processed {validation_results['scenarios_processed']} scenarios.")
    print(f"Scenarios with errors: {validation_results['scenarios_with_errors']}")
    print(f"Total errors found: {validation_results['total_errors']}")
    
    if save_validation_report(validation_results, output_path):
        print(f"\nValidation report saved to: {output_path}")
    
    sys.exit(0 if validation_results['valid'] else 1)

if __name__ == "__main__":
    main()
