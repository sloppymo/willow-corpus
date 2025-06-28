#!/usr/bin/env python3
"""
Tests for the legal citation validator.
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Any

# Add the scripts directory to the path
import sys
sys.path.append(str(Path(__file__).parent.parent / 'scripts'))

from validate_legal_citations import LegalCitationValidator, ValidationResult, Severity

class TestLegalCitationValidator(unittest.TestCase):    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = LegalCitationValidator()
    
    def test_validate_fair_housing_act(self):
        """Test validation of Fair Housing Act citations."""
        # Valid citation
        results = self.validator.validate_text("42 U.S.C. § 3601 et seq. (Fair Housing Act)")
        self.assertTrue(any(r.is_valid for r in results))
        
        # Different formatting
        results = self.validator.validate_text("42 USC 3601 (Fair Housing Act)")
        self.assertTrue(any(r.is_valid for r in results))
        
        # Vague reference
        results = self.validator.validate_text("under fair housing laws")
        self.assertFalse(all(r.is_valid for r in results))
        self.assertTrue(any(i.severity == Severity.CRITICAL for r in results for i in r.issues))
    
    def test_validate_ada(self):
        """Test validation of Americans with Disabilities Act citations."""
        # Valid citation
        results = self.validator.validate_text("42 U.S.C. § 12101 et seq. (Americans with Disabilities Act)")
        self.assertTrue(any(r.is_valid for r in results))
        
        # Different formatting
        results = self.validator.validate_text("42 USC 12101 (ADA)")
        self.assertTrue(any(r.is_valid for r in results))
    
    def test_validate_state_laws(self):
        """Test validation of state law citations."""
        # California FEHA
        results = self.validator.validate_text("Cal. Gov. Code § 12900 et seq. (FEHA)")
        self.assertTrue(any(r.is_valid for r in results))
        
        # Different formatting
        results = self.validator.validate_text("California Government Code 12900")
        self.assertTrue(any(r.is_valid for r in results))
        
        # Vague state law reference
        results = self.validator.validate_text("under state housing laws")
        self.assertFalse(all(r.is_valid for r in results))
    
    def test_validate_section_504(self):
        """Test validation of Section 504 citations."""
        # Valid citation
        results = self.validator.validate_text("29 U.S.C. § 794 (Section 504)")
        self.assertTrue(any(r.is_valid for r in results))
        
        # Different formatting
        results = self.validator.validate_text("29 USC 794 (Rehabilitation Act Section 504)")
        self.assertTrue(any(r.is_valid for r in results))
    
    def test_validate_vawa(self):
        """Test validation of VAWA citations."""
        # Valid citation
        results = self.validator.validate_text("34 U.S.C. § 12491 (VAWA)")
        self.assertTrue(any(r.is_valid for r in results))
        
        # Vague reference
        results = self.validator.validate_text("under VAWA protections")
        self.assertFalse(all(r.is_valid for r in results))
    
    def test_validate_code_of_federal_regulations(self):
        """Test validation of CFR citations."""
        # Valid citation
        results = self.validator.validate_text("24 C.F.R. § 100.1")
        self.assertTrue(any(r.is_valid for r in results))
    
        # Different formatting
        results = self.validator.validate_text("24 CFR 100.1")
        self.assertTrue(any(r.is_valid for r in results))
    
    def test_validate_public_law(self):
        """Test validation of public law citations."""
        # Valid citation
        results = self.validator.validate_text("Pub. L. No. 90-284 (Civil Rights Act of 1968)")
        self.assertTrue(any(r.is_valid for r in results))
        
        # Different formatting
        results = self.validator.validate_text("Public Law 90-284")
        self.assertTrue(any(r.is_valid for r in results))
    
    def test_validate_vague_references(self):
        """Test detection of vague legal references."""
        vague_phrases = [
            "fair housing laws",
            "ADA requirements",
            "Section 504",
            "state housing laws",
            "disability accommodations",
            "housing discrimination laws",
            "tenant rights",
            "VAWA protections"
        ]
        
        for phrase in vague_phrases:
            with self.subTest(phrase=phrase):
                results = self.validator.validate_text(phrase)
                self.assertGreater(len(results), 0, f"No issues found for: {phrase}")
                self.assertFalse(all(r.is_valid for r in results), f"Vague reference not flagged: {phrase}")
                self.assertTrue(any(i.severity in [Severity.CRITICAL, Severity.MAJOR] 
                                 for r in results for i in r.issues),
                               f"Vague reference not properly flagged: {phrase}")

class TestLegalCitationIntegration(unittest.TestCase):
    """Integration tests for the legal citation validator."""
    
    def test_full_document_validation(self):
        """Test validation of a full document with multiple citations."""
        # Create a test document with various citations
        test_doc = """
        This is a test document with various legal citations:
    
        1. Fair Housing Act: 42 U.S.C. § 3601 et seq.
        2. ADA: 42 U.S.C. § 12101 et seq.
        3. Section 504: 29 U.S.C. § 794
        4. California FEHA: Cal. Gov. Code § 12900 et seq.
        5. Vague reference: under fair housing laws
        6. Another vague reference: as required by ADA
        7. 24 C.F.R. § 100.1 (HUD regulations)
        8. Pub. L. No. 90-284 (Civil Rights Act of 1968)
        """
    
        validator = LegalCitationValidator()
        results = validator.validate_text(test_doc)
    
        # Should find all citations
        self.assertGreaterEqual(len(results), 8)
    
        # Should flag vague references
        self.assertTrue(any(any(i.severity in [Severity.CRITICAL, Severity.MAJOR]
                             for i in r.issues)
                         for r in results))
    
        # Should find valid citations
        self.assertTrue(any(r.is_valid for r in results if "42 U.S.C." in r.original_text))
        self.assertTrue(any(r.is_valid for r in results if "29 U.S.C." in r.original_text))
        self.assertTrue(any(r.is_valid for r in results if "Cal. Gov. Code" in r.original_text))
        self.assertTrue(any(r.is_valid for r in results if "24 C.F.R." in r.original_text))
        self.assertTrue(any(r.is_valid for r in results if "Pub. L." in r.original_text))

def create_test_file():
    """Create a test file with sample legal citations for manual testing."""
    test_file = """# Legal Citations Test Document

## Federal Laws
- Fair Housing Act: 42 U.S.C. § 3601 et seq.
- Americans with Disabilities Act: 42 U.S.C. § 12101 et seq.
- Section 504: 29 U.S.C. § 794
- VAWA: 34 U.S.C. § 12491
- Title VI: 42 U.S.C. § 2000d et seq.

## State Laws
- California FEHA: Cal. Gov. Code § 12900 et seq.
- California Unruh Act: Cal. Civ. Code § 51
- New York SHRL: N.Y. Exec. Law § 290 et seq.
- Illinois HRA: 775 ILCS 5/1-101 et seq.
- Texas FHA: Tex. Prop. Code § 301.001 et seq.

## Regulations
- HUD FHA Regulations: 24 C.F.R. Part 100
- Section 504 Regulations: 24 C.F.R. Part 8
- VAWA Regulations: 24 C.F.R. Part 5, Subpart L

## Public Laws
- Civil Rights Act of 1968: Pub. L. No. 90-284
- Fair Housing Amendments Act: Pub. L. No. 100-430

## Vague References (Should Be Flagged)
- fair housing laws
- ADA requirements
- Section 504
- state housing laws
- disability accommodations
- housing discrimination laws
- tenant rights
- VAWA protections
"""
    with open("test_legal_citations.md", "w") as f:
        f.write(test_file)
    print("Created test_legal_citations.md with sample legal citations.")

if __name__ == "__main__":
    # Create a test file for manual testing
    create_test_file()
    
    # Run the tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    
    # Example of how to use the validator programmatically
    print("\nExample usage:")
    validator = LegalCitationValidator()
    results = validator.validate_text("""
    The Fair Housing Act (42 U.S.C. § 3601) prohibits discrimination in housing.
    State housing laws also provide additional protections.
    """)
    
    from validate_legal_citations import LegalCitationReporter
    print("\nValidation Report:")
    print(LegalCitationReporter.generate_report(results))
