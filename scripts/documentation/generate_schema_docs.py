"""
Schema Documentation Generator for Enhanced Dataset

Generates Markdown documentation for the enhanced dataset schema.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime

def load_json_file(file_path: Path) -> Any:
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None

def analyze_schema(dataset: List[Dict]) -> Dict[str, Any]:
    """Analyze the dataset to extract schema information."""
    schema_info = {
        "scenarios_count": len(dataset),
        "fields": {},
        "vulnerabilities": set(),
        "message_roles": set(),
        "emotional_states": set(),
        "validation_statuses": set()
    }
    
    for scenario in dataset:
        # Track top-level fields
        for field, value in scenario.items():
            if field not in schema_info["fields"]:
                schema_info["fields"][field] = {
                    "type": type(value).__name__,
                    "required": True,
                    "description": ""
                }
            
            # Special handling for specific fields
            if field == "vulnerabilities" and isinstance(value, list):
                schema_info["vulnerabilities"].update(value)
            
            # Analyze messages
            if field == "messages" and isinstance(value, list):
                for msg in value:
                    if isinstance(msg, dict):
                        if "role" in msg:
                            schema_info["message_roles"].add(msg["role"])
                        if "emotional_state" in msg:
                            schema_info["emotional_states"].add(msg["emotional_state"])
            
            # Track validation statuses
            if field == "metadata" and isinstance(value, dict) and "validation_status" in value:
                schema_info["validation_statuses"].add(value["validation_status"])
    
    # Convert sets to sorted lists
    for key in ["vulnerabilities", "message_roles", "emotional_states", "validation_statuses"]:
        schema_info[key] = sorted(list(schema_info[key]))
    
    return schema_info

def generate_markdown_docs(schema_info: Dict[str, Any], output_path: Path) -> bool:
    """Generate Markdown documentation from schema information."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("# Enhanced Dataset Schema Documentation\n\n")
            f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            # Overview
            f.write("## Overview\n\n")
            f.write(f"This document describes the schema for the enhanced dataset containing "
                   f"{schema_info['scenarios_count']} scenarios.\n\n")
            
            # Fields Section
            f.write("## Fields\n\n")
            f.write("| Field | Type | Required | Description |\n")
            f.write("|-------|------|----------|-------------|\n")
            
            for field, info in schema_info["fields"].items():
                f.write(f"| `{field}` | `{info['type']}` | {'Yes' if info['required'] else 'No'} | {info['description'] or 'No description available'} |\n")
            
            # Vulnerabilities Section
            if schema_info["vulnerabilities"]:
                f.write("\n## Vulnerabilities\n\n")
                f.write("The following vulnerability types are used in the dataset:\n\n")
                for vuln in schema_info["vulnerabilities"]:
                    f.write(f"- `{vuln}`\n")
            
            # Message Roles Section
            if schema_info["message_roles"]:
                f.write("\n## Message Roles\n\n")
                f.write("The following message roles are used in the dataset:\n\n")
                for role in schema_info["message_roles"]:
                    f.write(f"- `{role}`\n")
            
            # Emotional States Section
            if schema_info["emotional_states"]:
                f.write("\n## Emotional States\n\n")
                f.write("The following emotional states are used in the dataset:\n\n")
                for state in schema_info["emotional_states"]:
                    f.write(f"- `{state}`\n")
            
            # Validation Statuses Section
            if schema_info["validation_statuses"]:
                f.write("\n## Validation Statuses\n\n")
                f.write("The following validation statuses are used in the dataset:\n\n")
                for status in schema_info["validation_statuses"]:
                    f.write(f"- `{status}`\n")
            
            # Example Section
            f.write("\n## Example Scenario\n\n")
            f.write("```json\n{\n  \"scenario_id\": \"example_id\",\n")
            f.write("  \"title\": \"Example Scenario\",\n")
            f.write("  \"description\": \"Example scenario description\",\n")
            f.write("  \"vulnerabilities\": [\n    \"example_vulnerability\"\n  ],\n")
            f.write("  \"messages\": [\n    {\n      \"role\": \"tenant\",\n      \"content\": \"Example message\",\n      \"emotional_state\": \"neutral\"\n    }\n  ],\n")
            f.write("  \"metadata\": {\n    \"created_at\": \"2025-01-01T00:00:00Z\",\n    \"last_updated\": \"2025-01-01T00:00:00Z\",\n    \"validation_status\": \"validated\"\n  }\n}\n```")
            
        return True
    except Exception as e:
        print(f"Error generating documentation: {e}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate schema documentation for enhanced dataset')
    parser.add_argument('-i', '--input', required=True, help='Input JSON file')
    parser.add_argument('-o', '--output', required=True, help='Output Markdown file')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    print(f"Loading dataset from {input_path}...")
    dataset = load_json_file(input_path)
    
    if not dataset:
        print("Failed to load dataset")
        sys.exit(1)
    
    print("Analyzing schema...")
    schema_info = analyze_schema(dataset)
    
    print(f"Generating documentation to {output_path}...")
    if generate_markdown_docs(schema_info, output_path):
        print(f"Documentation generated successfully at {output_path}")
        sys.exit(0)
    else:
        print("Failed to generate documentation")
        sys.exit(1)

if __name__ == "__main__":
    main()
