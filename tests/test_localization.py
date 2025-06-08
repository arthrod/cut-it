"""Tests for the localization module."""

import pytest
from cut_it.localization import get_messages


class TestLocalization:
    """Test cases for localization functionality."""

    def test_get_messages_english_default(self):
        """Test getting English messages (default)."""
        messages = get_messages()
        
        # Test file operations
        assert messages["file_not_found"] == "File not found"
        assert messages["reading_file"] == "Reading file..."
        assert messages["saving_file"] == "Saving file..."
        
        # Test processing
        assert messages["splitting_text"] == "Splitting text into semantic chunks..."
        assert messages["formatting_tasks"] == "Formatting as task list..."
        
        # Test results
        assert "successfully" in messages["success"]
        assert messages["chunks_created"] == "Task chunks created"
        
        # Test status
        assert messages["pending"] == "Pending"
        assert messages["started"] == "Started"
        assert messages["completed"] == "Completed"
        
        # Test tasks
        assert messages["task"] == "TASK"
        assert messages["progress"] == "Progress"

    def test_get_messages_english_explicit(self):
        """Test getting English messages explicitly."""
        messages = get_messages(pt_br=False)
        
        assert messages["file_not_found"] == "File not found"
        assert messages["task"] == "TASK"
        assert messages["progress"] == "Progress"
        assert messages["pending"] == "Pending"

    def test_get_messages_portuguese(self):
        """Test getting Portuguese (Brazil) messages."""
        messages = get_messages(pt_br=True)
        
        # Test file operations
        assert messages["file_not_found"] == "Arquivo não encontrado"
        assert messages["reading_file"] == "Lendo arquivo..."
        assert messages["saving_file"] == "Salvando arquivo..."
        
        # Test processing
        assert messages["splitting_text"] == "Dividindo texto em blocos semânticos..."
        assert messages["formatting_tasks"] == "Formatando como lista de tarefas..."
        
        # Test results
        assert "sucesso" in messages["success"]
        assert messages["chunks_created"] == "Blocos de tarefa criados"
        
        # Test status
        assert messages["pending"] == "Pendente"
        assert messages["started"] == "Iniciado"
        assert messages["completed"] == "Concluído"
        
        # Test tasks
        assert messages["task"] == "TAREFA"
        assert messages["progress"] == "Progresso"

    def test_all_keys_present_english(self):
        """Test that all required keys are present in English messages."""
        messages = get_messages(pt_br=False)
        
        required_keys = [
            "file_not_found", "encoding_error", "reading_file", "saving_file",
            "splitting_text", "formatting_tasks", "success", "chunks_created",
            "config_updated", "checking_updates", "up_to_date",
            "error", "warning", "info",
            "pending", "started", "completed",
            "task", "progress",
            "help_description", "help_file", "help_output", "help_size",
            "help_model", "help_type", "help_config_show", "help_config_ptbr",
            "help_config_cli", "help_config_model", "help_config_size"
        ]
        
        for key in required_keys:
            assert key in messages, f"Missing key: {key}"
            assert isinstance(messages[key], str), f"Key {key} is not a string"
            assert len(messages[key]) > 0, f"Key {key} is empty"

    def test_all_keys_present_portuguese(self):
        """Test that all required keys are present in Portuguese messages."""
        messages = get_messages(pt_br=True)
        
        required_keys = [
            "file_not_found", "encoding_error", "reading_file", "saving_file",
            "splitting_text", "formatting_tasks", "success", "chunks_created",
            "config_updated", "checking_updates", "up_to_date",
            "error", "warning", "info",
            "pending", "started", "completed",
            "task", "progress",
            "help_description", "help_file", "help_output", "help_size",
            "help_model", "help_type", "help_config_show", "help_config_ptbr",
            "help_config_cli", "help_config_model", "help_config_size"
        ]
        
        for key in required_keys:
            assert key in messages, f"Missing key: {key}"
            assert isinstance(messages[key], str), f"Key {key} is not a string"
            assert len(messages[key]) > 0, f"Key {key} is empty"

    def test_message_consistency(self):
        """Test that English and Portuguese have same keys."""
        english_messages = get_messages(pt_br=False)
        portuguese_messages = get_messages(pt_br=True)
        
        english_keys = set(english_messages.keys())
        portuguese_keys = set(portuguese_messages.keys())
        
        assert english_keys == portuguese_keys, "Key mismatch between languages"

    def test_no_empty_messages_english(self):
        """Test that no English messages are empty."""
        messages = get_messages(pt_br=False)
        
        for key, value in messages.items():
            assert len(value.strip()) > 0, f"Empty message for key: {key}"

    def test_no_empty_messages_portuguese(self):
        """Test that no Portuguese messages are empty."""
        messages = get_messages(pt_br=True)
        
        for key, value in messages.items():
            assert len(value.strip()) > 0, f"Empty message for key: {key}"

    def test_specific_translations(self):
        """Test specific key translations between languages."""
        english = get_messages(pt_br=False)
        portuguese = get_messages(pt_br=True)
        
        # Test that translations are actually different
        assert english["task"] != portuguese["task"]
        assert english["progress"] != portuguese["progress"]
        assert english["pending"] != portuguese["pending"]
        assert english["started"] != portuguese["started"]
        assert english["completed"] != portuguese["completed"]
        
        # Test that Portuguese actually contains Portuguese words
        assert "TAREFA" in portuguese["task"]
        assert "Progresso" in portuguese["progress"]
        assert "Pendente" in portuguese["pending"]

    def test_help_messages_exist(self):
        """Test that help messages exist for CLI documentation."""
        english = get_messages(pt_br=False)
        portuguese = get_messages(pt_br=True)
        
        help_keys = [key for key in english.keys() if key.startswith("help_")]
        
        assert len(help_keys) > 0, "No help messages found"
        
        # Test that help messages exist in both languages
        for key in help_keys:
            assert key in english
            assert key in portuguese
            assert len(english[key]) > 10  # Help messages should be descriptive
            assert len(portuguese[key]) > 10

    def test_error_messages_exist(self):
        """Test that error messages exist."""
        english = get_messages(pt_br=False)
        portuguese = get_messages(pt_br=True)
        
        error_keys = ["error", "warning", "info", "file_not_found", "encoding_error"]
        
        for key in error_keys:
            assert key in english
            assert key in portuguese
            assert len(english[key]) > 0
            assert len(portuguese[key]) > 0