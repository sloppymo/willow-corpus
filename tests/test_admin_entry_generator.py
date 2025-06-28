"""Tests for the administrative entry generator."""
import json
import os
import pytest
import tempfile
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from scripts.generate_admin_entries import (
    EntryType,
    BaseEntry,
    CaseManagementEntry,
    ReportingEntry,
    CommunicationEntry,
    TrainingEntry,
    generate_entries,
    save_entries,
    main as generator_main
)


class TestBaseEntry:
    """Test cases for the BaseEntry class."""
    
    def test_base_entry_initialization(self):
        """Test that BaseEntry initializes with correct defaults."""
        entry = BaseEntry(EntryType.CASE_MANAGEMENT)
        assert entry.entry_type == EntryType.CASE_MANAGEMENT
        assert "scenario_id" in entry.template
        assert entry.template["entry_type"] == "case_management"
        assert "created_at" in entry.template
        assert "version_control" in entry.template
        assert entry.template["version_control"]["version"] == "2.1.0"
    
    def test_add_vulnerability_context(self):
        """Test adding vulnerability context to an entry."""
        entry = BaseEntry(EntryType.CASE_MANAGEMENT)
        test_entry = {"key": "value"}
        result = entry._add_vulnerability_context(test_entry)
        
        assert "vulnerability_context" in result
        assert "primary" in result["vulnerability_context"]
        assert "secondary" in result["vulnerability_context"]
        assert "mitigation_strategies" in result["vulnerability_context"]


class TestCaseManagementEntry:
    """Test cases for the CaseManagementEntry class."""
    
    def test_case_management_entry_initialization(self):
        """Test that CaseManagementEntry initializes correctly."""
        entry = CaseManagementEntry()
        assert entry.entry_type == EntryType.CASE_MANAGEMENT
        assert entry.status in ["open", "in_progress", "on_hold", "resolved", "closed"]
        assert "case_id" in entry.template
        
    def test_generate_case_management_entry(self):
        """Test generating a complete case management entry."""
        entry = CaseManagementEntry()
        result = entry.generate()
        
        assert "case_details" in result
        assert "title" in result
        assert "description" in result
        assert "assigned_to" in result
        assert "priority" in result
        assert "due_date" in result
        assert "related_entities" in result
        assert "notes" in result
        assert "attachments" in result


class TestReportingEntry:
    """Test cases for the ReportingEntry class."""
    
    def test_reporting_entry_initialization(self):
        """Test that ReportingEntry initializes correctly."""
        entry = ReportingEntry()
        assert entry.entry_type == EntryType.REPORTING
        assert entry.report_type in ["incident", "maintenance", "compliance", "financial"]
        
    def test_generate_reporting_entry(self):
        """Test generating a complete reporting entry."""
        entry = ReportingEntry()
        result = entry.generate()
        
        assert "report_details" in result
        assert "title" in result
        assert "description" in result
        assert "reporting_period" in result
        assert "metrics" in result
        assert "findings" in result
        assert "recommendations" in result
        assert "approvals" in result


class TestCommunicationEntry:
    """Test cases for the CommunicationEntry class."""
    
    def test_communication_entry_initialization(self):
        """Test that CommunicationEntry initializes correctly."""
        entry = CommunicationEntry()
        assert entry.entry_type == EntryType.COMMUNICATION
        assert entry.communication_type in ["email", "meeting", "phone_call", "memo"]
        
    def test_generate_communication_entry(self):
        """Test generating a complete communication entry."""
        entry = CommunicationEntry()
        result = entry.generate()
        
        assert "communication_details" in result
        assert "subject" in result
        assert "content" in result
        assert "sender" in result
        assert "recipients" in result
        assert "timestamp" in result
        assert "attachments" in result
        assert "follow_up_required" in result


class TestTrainingEntry:
    """Test cases for the TrainingEntry class."""
    
    def test_training_entry_initialization(self):
        """Test that TrainingEntry initializes correctly."""
        entry = TrainingEntry()
        assert entry.entry_type == EntryType.TRAINING
        assert entry.training_type in TrainingEntry.TrainingType
        assert entry.format in TrainingEntry.TrainingFormat
        assert entry.status in ["scheduled", "in_progress", "completed", "cancelled"]
        
    def test_generate_training_entry(self):
        """Test generating a complete training entry."""
        entry = TrainingEntry()
        result = entry.generate()
        
        assert "training_details" in result
        assert "title" in result
        assert "description" in result
        assert "participants" in result
        assert "evaluation" in result
        # Check nested fields in training_details
        assert "trainer" in result["training_details"]
        assert "location" in result["training_details"]
        assert "materials" in result["training_details"]
        assert "learning_objectives" in result["training_details"]
    
    def test_generate_dates(self):
        """Test date generation for training entries."""
        entry = TrainingEntry()
        start_date, end_date = entry._generate_dates()
        
        assert isinstance(start_date, datetime)
        assert isinstance(end_date, datetime)
        assert start_date < end_date
        assert (end_date - start_date) <= timedelta(days=3)  # Max duration is 3 days
    
    def test_generate_participants(self):
        """Test participant generation for training entries."""
        entry = TrainingEntry()
        participants = entry._generate_participants()
        
        assert 5 <= len(participants) <= 30  # Should generate between 5-30 participants
        for participant in participants:
            assert "id" in participant
            assert "name" in participant
            assert "email" in participant
            assert "department" in participant
            assert "attendance_status" in participant
            assert "completion_status" in participant
            
            if participant["completion_status"] == "completed":
                assert "score" in participant
                assert "certificate_id" in participant


class TestGeneratorFunctions:
    """Test cases for the module-level generator functions."""
    
    def test_generate_entries_single_type(self):
        """Test generating entries of a single type."""
        entries = generate_entries(3, "case_management")
        assert len(entries) == 3
        for entry in entries:
            assert entry["entry_type"] == "case_management"
    
    def test_generate_entries_all_types(self):
        """Test generating entries of all types."""
        entries = generate_entries(10)  # Should distribute across all types
        entry_types = set(entry["entry_type"] for entry in entries)
        assert len(entry_types) >= 2  # At least two different types should be present
    
    def test_save_entries_json(self):
        """Test saving entries to a JSON file."""
        test_entries = [{"test": "data"}]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_path = temp_file.name
        
        try:
            # Test with overwrite=False (should raise FileExistsError)
            with pytest.raises(FileExistsError):
                save_entries(test_entries, temp_path, "json")
            
            # Test with overwrite=True
            save_entries(test_entries, temp_path, "json", overwrite=True)
            with open(temp_path, 'r') as f:
                loaded = json.load(f)
            assert loaded == test_entries
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_save_entries_jsonl(self):
        """Test saving entries to a JSONL file."""
        test_entries = [{"test": "data1"}, {"test": "data2"}]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl") as temp_file:
            temp_path = temp_file.name
        
        try:
            # Test with overwrite=False (should raise FileExistsError)
            with pytest.raises(FileExistsError):
                save_entries(test_entries, temp_path, "jsonl")
            
            # Test with overwrite=True
            save_entries(test_entries, temp_path, "jsonl", overwrite=True)
            with open(temp_path, 'r') as f:
                lines = f.readlines()
            assert len(lines) == 2
            assert json.loads(lines[0]) == test_entries[0]
            assert json.loads(lines[1]) == test_entries[1]
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @patch('argparse.ArgumentParser.parse_args')
    @patch('scripts.generate_admin_entries.random.seed')
    @patch('scripts.generate_admin_entries.save_entries')
    @patch('scripts.generate_admin_entries.generate_entries')
    def test_main_function(self, mock_generate, mock_save, mock_seed, mock_parse_args):
        """Test the main function with mocked arguments and functions."""
        # Setup mocks
        mock_seed.return_value = None
        mock_generate.return_value = [{"id": "test1"}, {"id": "test2"}]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "test_output.json")
            
            # Test normal execution
            mock_args = MagicMock()
            mock_args.count = 2
            mock_args.type = None
            mock_args.output = output_file
            mock_args.format = "json"
            mock_args.overwrite = False
            mock_args.verbose = False
            mock_args.seed = None
            mock_parse_args.return_value = mock_args
            
            # First run - should work fine
            result = generator_main()
            assert result == 0
            mock_save.assert_called_once()
            
            # Reset mocks for next test
            mock_save.reset_mock()
            mock_generate.reset_mock()
            
            # Test FileExistsError case
            mock_save.side_effect = FileExistsError("File exists")
            result = generator_main()
            assert result == 1  # Should return 1 on FileExistsError
            
            # Test with overwrite=True
            mock_save.reset_mock(side_effect=True)
            mock_args.overwrite = True
            result = generator_main()
            assert result == 0
            mock_save.assert_called_once()
            
            # Test ValueError case
            mock_save.side_effect = ValueError("Invalid format")
            result = generator_main()
            assert result == 1
            
            # Test other exceptions
            mock_save.side_effect = Exception("Unexpected error")
            result = generator_main()
            assert result == 1


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_generate_zero_entries(self):
        """Test generating zero entries."""
        with pytest.raises(ValueError, match="Count must be a positive integer"):
            generate_entries(0)
    
    def test_invalid_entry_type(self):
        """Test generating entries with an invalid type."""
        with pytest.raises(ValueError):
            generate_entries(1, "invalid_type")
    
    def test_save_entries_invalid_format(self):
        """Test saving entries with an invalid format."""
        with pytest.raises(ValueError):
            save_entries([], "test.txt", "txt")
    
    def test_save_entries_nonexistent_directory(self, tmp_path):
        """Test saving to a non-existent directory."""
        output_path = os.path.join(tmp_path, "nonexistent", "output.json")
        # The save_entries function should create the directory if it doesn't exist
        save_entries([{"test": "data"}], output_path, "json")
        assert os.path.exists(output_path)
