"""Tests for the Willow validators."""
import json
import pytest
from pathlib import Path
from typing import Dict, Any

from willow.validators import SchemaValidator, ScenarioValidator, validate_scenario_file
from willow.models.scenario import Scenario, UrgencyLevel

# Sample valid scenario data
VALID_SCENARIO = {
    "scenario_id": "TEST_001",
    "title": "Test Scenario",
    "description": "A test scenario for validation",
    "vulnerability_context": {
        "primary": "mobility_impairment",
        "intersectional": ["elderly"],
        "trauma_history": "None reported"
    },
    "urgency_level": "Medium",
    "legal_basis": {
        "federal": ["ADA Title II", "Fair Housing Act"],
        "state": [],
        "local": []
    },
    "golden_ratio_structure": {
        "emotional_validation": "We understand this is important for your mobility and independence.",
        "concrete_action": "We'll install a ramp at the main entrance within 7 business days.",
        "accountability_mechanism": "Maintenance supervisor will confirm completion.",
        "proof_statement": "ADA Standard 405 requires accessible routes with proper slope and handrails.",
        "realistic_boundary": "If structural limitations prevent a permanent ramp, we'll provide a temporary solution within 48 hours.",
        "closing_statement": "Your comfort and safety are our priority.",
        "closure_variants": [
            "Thank you for bringing this to our attention.",
            "We're here to help with any other needs."
        ]
    },
    "implementation_requirements": {
        "timeline": {
            "immediate": "Initial response within 1 business day",
            "short_term": "Accessibility review within 2 business days",
            "long_term": "Installation within 7 days of approval"
        },
        "cost_parameters": {
            "estimated_cost": "$1,200 - $2,500",
            "funding_sources": ["Operating Budget"],
            "cost_mitigation_strategies": ["Phased installation"]
        },
        "documentation_needed": ["Accessibility Assessment Form"],
        "staff_training": {
            "required_topics": ["ADA Compliance"],
            "training_format": ["Online Module"],
            "certification_required": True
        }
    },
    "conflict_resolution": {
        "common_objections": ["Cost is prohibitive"],
        "response_scripts": {
            "professional": "The Fair Housing Act requires reasonable accommodations.",
            "empathetic": "I understand your concern. Let's find a solution together.",
            "legal": "FHA requirements for reasonable accommodations apply."
        },
        "escalation_path": ["Property Manager"],
        "denial_grounds": ["Undue financial burden"],
        "appeal_process": "Request review in writing within 10 business days"
    },
    "compliance_metrics": {
        "implementation_timeline": "7 business days",
        "inspection_requirements": "Pre- and post-installation",
        "follow_up_schedule": "30-day check-in",
        "success_metrics": {
            "tenant_satisfaction": "95%",
            "compliance_audit_score": "100%",
            "timely_completion": "100%"
        }
    },
    "trauma_informed_care": {
        "triggers_to_avoid": ["Delaying response"],
        "communication_style": ["Written", "Verbal"],
        "safety_considerations": ["Private meeting space"]
    },
    "accessibility_features": {
        "communication": ["Email", "Phone"],
        "physical": ["Ramp", "Handrails"],
        "technological": ["Online request portal"]
    },
    "tenant_rights": {
        "right_to_modify": True,
        "right_to_accommodation": True,
        "right_to_privacy": True,
        "right_to_nondiscrimination": True
    },
    "tags": ["mobility", "accessibility"],
    "version": "1.0.0"
}

# Sample invalid scenario (missing required fields)
INVALID_SCENARIO = {
    "scenario_id": "TEST_002",
    "title": "Invalid Test Scenario",
    # Missing required fields
}

@pytest.fixture
def temp_scenario_file(tmp_path):
    """Create a temporary scenario file for testing."""
    def _create_file(content: Dict[str, Any], filename: str = "test_scenario.json") -> Path:
        file_path = tmp_path / filename
        with open(file_path, 'w') as f:
            json.dump(content, f)
        return file_path
    return _create_file

def test_schema_validator_valid():
    """Test that a valid scenario passes schema validation."""
    validator = SchemaValidator()
    is_valid, errors = validator.validate_dict(VALID_SCENARIO)
    assert is_valid
    assert not errors

def test_schema_validator_invalid():
    """Test that an invalid scenario fails schema validation."""
    validator = SchemaValidator()
    is_valid, errors = validator.validate_dict(INVALID_SCENARIO)
    assert not is_valid
    assert errors
    assert any("field='description'" in str(e) for e in errors)

def test_scenario_validator_legal_content():
    """Test legal content validation."""
    validator = ScenarioValidator()
    
    # Test missing federal law
    scenario = VALID_SCENARIO.copy()
    scenario["legal_basis"]["federal"] = []
    
    results = validator.validate(scenario)
    assert not results["legal_validation"]["is_valid"]
    assert "federal" in str(results["legal_validation"]["errors"])

def test_scenario_validator_trauma_informed():
    """Test trauma-informed language validation."""
    validator = ScenarioValidator()
    
    # Test with potentially invalidating language
    scenario = VALID_SCENARIO.copy()
    scenario["golden_ratio_structure"]["emotional_validation"] = "You must understand that..."
    
    results = validator.validate(scenario)
    assert not results["trauma_validation"]["is_valid"]
    assert "avoid using potentially invalidating language" in str(results["trauma_validation"]["errors"]).lower()

def test_validate_scenario_file(temp_scenario_file):
    """Test the file validation function."""
    # Test valid file
    valid_file = temp_scenario_file(VALID_SCENARIO, "valid_scenario.json")
    result = validate_scenario_file(valid_file)
    assert result["valid"]
    
    # Test invalid file
    invalid_file = temp_scenario_file(INVALID_SCENARIO, "invalid_scenario.json")
    result = validate_scenario_file(invalid_file)
    assert not result["valid"]

def test_scenario_model_validation():
    """Test that the Pydantic model validates correctly."""
    # This should not raise an exception
    scenario = Scenario(**VALID_SCENARIO)
    assert scenario.scenario_id == "TEST_001"
    assert scenario.urgency_level == UrgencyLevel.MEDIUM
    
    # Test with invalid data
    invalid_data = VALID_SCENARIO.copy()
    invalid_data["urgency_level"] = "InvalidLevel"
    
    with pytest.raises(ValueError):
        Scenario(**invalid_data)

def test_urgency_level_enum():
    """Test the UrgencyLevel enum."""
    assert UrgencyLevel("Low") == UrgencyLevel.LOW
    assert UrgencyLevel("High").value == "High"
    
    with pytest.raises(ValueError):
        UrgencyLevel("Invalid")
