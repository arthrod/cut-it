"""Tests for the CLI module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typer.testing import CliRunner
from cut_it.cli import app, get_file_type


class TestFileTypeDetection:
    """Test cases for file type detection."""

    def test_get_file_type_markdown(self):
        """Test file type detection for markdown files."""
        assert get_file_type(Path("test.md")) == "markdown"
        assert get_file_type(Path("README.markdown")) == "markdown"
        assert get_file_type(Path("docs.MD")) == "markdown"

    def test_get_file_type_code(self):
        """Test file type detection for code files."""
        code_files = [
            "script.py", "app.js", "component.tsx", "Main.java",
            "program.cpp", "header.h", "App.cs", "script.php",
            "app.rb", "main.go", "lib.rs", "App.swift"
        ]
        
        for filename in code_files:
            assert get_file_type(Path(filename)) == "code"

    def test_get_file_type_text_default(self):
        """Test file type detection defaults to text."""
        assert get_file_type(Path("document.txt")) == "text"
        assert get_file_type(Path("data.csv")) == "text"
        assert get_file_type(Path("config.conf")) == "text"
        assert get_file_type(Path("readme")) == "text"  # No extension


class TestCLICommands:
    """Test cases for CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch('cut_it.cli.ConfigManager')
    @patch('cut_it.cli.TextProcessor')
    @patch('cut_it.cli.TaskFormatter')
    @patch('cut_it.cli.Path')
    def test_process_command_basic(self, mock_path, mock_formatter, mock_processor, mock_config_manager):
        """Test basic process command."""
        # Setup mocks
        mock_config = Mock()
        mock_config.chunk_size_min = 300
        mock_config.chunk_size_max = 500
        mock_config.model = "gpt-4"
        mock_config.pt_br = False
        
        mock_config_manager_instance = Mock()
        mock_config_manager_instance.load.return_value = mock_config
        mock_config_manager.return_value = mock_config_manager_instance
        
        mock_input_path = Mock()
        mock_input_path.exists.return_value = True
        mock_input_path.read_text.return_value = "Test content"
        mock_input_path.name = "test.txt"
        mock_input_path.with_suffix.return_value = Path("test.tasks.md")
        
        mock_output_path = Mock()
        
        mock_path.side_effect = lambda x: mock_input_path if "test.txt" in str(x) else mock_output_path
        
        mock_processor_instance = Mock()
        mock_processor_instance.split_text.return_value = ["chunk1", "chunk2"]
        mock_processor.return_value = mock_processor_instance
        
        mock_formatter_instance = Mock()
        mock_formatter_instance.format_as_tasks.return_value = "formatted output"
        mock_formatter.return_value = mock_formatter_instance
        
        # Run command
        result = self.runner.invoke(app, ["process", "test.txt"])
        
        # Assertions
        assert result.exit_code == 0
        mock_processor_instance.split_text.assert_called_once_with("Test content")
        mock_formatter_instance.format_as_tasks.assert_called_once()
        mock_output_path.write_text.assert_called_once_with("formatted output", encoding='utf-8')

    def test_process_command_file_not_found(self):
        """Test process command with non-existent file."""
        result = self.runner.invoke(app, ["process", "nonexistent.txt"])
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower() or "not found" in str(result.exception).lower()

    @patch('cut_it.cli.ConfigManager')
    @patch('cut_it.cli.Path')
    def test_process_command_encoding_error(self, mock_path, mock_config_manager):
        """Test process command with encoding error."""
        # Setup mocks
        mock_config = Mock()
        mock_config.pt_br = False
        mock_config_manager_instance = Mock()
        mock_config_manager_instance.load.return_value = mock_config
        mock_config_manager.return_value = mock_config_manager_instance
        
        mock_input_path = Mock()
        mock_input_path.exists.return_value = True
        mock_input_path.read_text.side_effect = UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')
        
        mock_path.return_value = mock_input_path
        
        result = self.runner.invoke(app, ["process", "test.txt"])
        assert result.exit_code == 1

    @patch('cut_it.cli.ConfigManager')
    def test_config_show(self, mock_config_manager):
        """Test config show command."""
        mock_config = Mock()
        mock_config.chunk_size_min = 300
        mock_config.chunk_size_max = 500
        mock_config.model = "gpt-4"
        mock_config.pt_br = False
        mock_config.cli_mode = True
        
        mock_config_manager_instance = Mock()
        mock_config_manager_instance.load.return_value = mock_config
        mock_config_manager.return_value = mock_config_manager_instance
        
        result = self.runner.invoke(app, ["config", "--show"])
        
        assert result.exit_code == 0
        assert "Current Configuration" in result.stdout
        assert "300-500" in result.stdout
        assert "gpt-4" in result.stdout

    @patch('cut_it.cli.ConfigManager')
    def test_config_update_pt_br(self, mock_config_manager):
        """Test config update for pt-br setting."""
        mock_config = Mock()
        mock_config.pt_br = True
        
        mock_config_manager_instance = Mock()
        mock_config_manager_instance.update.return_value = mock_config
        mock_config_manager.return_value = mock_config_manager_instance
        
        result = self.runner.invoke(app, ["config", "--pt-br", "true"])
        
        assert result.exit_code == 0
        mock_config_manager_instance.update.assert_called_once_with(pt_br=True)

    @patch('cut_it.cli.ConfigManager')
    def test_config_update_model(self, mock_config_manager):
        """Test config update for model setting."""
        mock_config = Mock()
        mock_config.pt_br = False
        
        mock_config_manager_instance = Mock()
        mock_config_manager_instance.update.return_value = mock_config
        mock_config_manager.return_value = mock_config_manager_instance
        
        result = self.runner.invoke(app, ["config", "--model", "gpt-3.5-turbo"])
        
        assert result.exit_code == 0
        mock_config_manager_instance.update.assert_called_once_with(model="gpt-3.5-turbo")

    @patch('cut_it.cli.ConfigManager')
    def test_config_update_size(self, mock_config_manager):
        """Test config update for size setting."""
        mock_config = Mock()
        mock_config.pt_br = False
        
        mock_config_manager_instance = Mock()
        mock_config_manager_instance.update.return_value = mock_config
        mock_config_manager.return_value = mock_config_manager_instance
        
        result = self.runner.invoke(app, ["config", "--size", "200", "400"])
        
        assert result.exit_code == 0
        mock_config_manager_instance.update.assert_called_once_with(
            chunk_size_min=200, 
            chunk_size_max=400
        )

    @patch('cut_it.cli.ConfigManager')
    def test_config_no_changes(self, mock_config_manager):
        """Test config command with no changes."""
        mock_config_manager_instance = Mock()
        mock_config_manager.return_value = mock_config_manager_instance
        
        result = self.runner.invoke(app, ["config"])
        
        assert result.exit_code == 0
        assert "No configuration changes" in result.stdout

    @patch('cut_it.cli.ConfigManager')
    def test_update_command(self, mock_config_manager):
        """Test update command."""
        mock_config = Mock()
        mock_config.pt_br = False
        
        mock_config_manager_instance = Mock()
        mock_config_manager_instance.load.return_value = mock_config
        mock_config_manager.return_value = mock_config_manager_instance
        
        result = self.runner.invoke(app, ["update"])
        
        assert result.exit_code == 0
        # Should check for updates (mocked to show up to date)
        assert "up to date" in result.stdout.lower() or "atualizado" in result.stdout.lower()

    @patch('cut_it.cli.ConfigManager')
    @patch('cut_it.cli.TextProcessor')
    @patch('cut_it.cli.TaskFormatter')
    @patch('cut_it.cli.Path')
    def test_process_with_custom_options(self, mock_path, mock_formatter, mock_processor, mock_config_manager):
        """Test process command with custom options."""
        # Setup mocks similar to basic test but with custom parameters
        mock_config = Mock()
        mock_config.pt_br = False
        
        mock_config_manager_instance = Mock()
        mock_config_manager_instance.load.return_value = mock_config
        mock_config_manager.return_value = mock_config_manager_instance
        
        mock_input_path = Mock()
        mock_input_path.exists.return_value = True
        mock_input_path.read_text.return_value = "Test content"
        mock_input_path.name = "test.md"
        
        mock_output_path = Mock()
        
        def path_side_effect(x):
            if "test.md" in str(x):
                return mock_input_path
            elif "custom.md" in str(x):
                return mock_output_path
            return Mock()
        
        mock_path.side_effect = path_side_effect
        
        mock_processor_instance = Mock()
        mock_processor_instance.split_text.return_value = ["chunk1"]
        mock_processor.return_value = mock_processor_instance
        
        mock_formatter_instance = Mock()
        mock_formatter_instance.format_as_tasks.return_value = "formatted output"
        mock_formatter.return_value = mock_formatter_instance
        
        # Run command with custom options
        result = self.runner.invoke(app, [
            "process", "test.md",
            "--output", "custom.md",
            "--size", "200", "400",
            "--model", "gpt-3.5-turbo",
            "--type", "markdown"
        ])
        
        assert result.exit_code == 0
        
        # Verify processor was called with custom settings
        mock_processor.assert_called_once()
        call_args = mock_processor.call_args
        assert call_args[1]['chunk_size'] == (200, 400)
        assert call_args[1]['model'] == "gpt-3.5-turbo"
        assert call_args[1]['file_type'] == "markdown"