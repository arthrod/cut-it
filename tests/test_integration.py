"""Integration tests for the complete cut-it pipeline."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from cut_it.cli import app
from cut_it.config import ConfigManager
from cut_it.splitter import TextProcessor
from cut_it.formatter import TaskFormatter
from typer.testing import CliRunner


@pytest.mark.integration
class TestIntegration:
    """Integration tests for the complete pipeline."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_complete_pipeline_text_file(self, temp_text_file, temp_dir):
        """Test complete pipeline with a text file."""
        output_file = temp_dir / "output.md"
        
        # Mock the semantic splitter since we can't install it in tests
        with patch('cut_it.splitter.TextSplitter') as mock_splitter_class:
            mock_splitter = Mock()
            mock_splitter.chunks.return_value = [
                "First semantic chunk from the text file.",
                "Second semantic chunk with more content.",
                "Final chunk completing the processing."
            ]
            mock_splitter_class.from_tiktoken_model.return_value = mock_splitter
            
            # Create processor and test it
            processor = TextProcessor(
                chunk_size=(200, 400),
                model="gpt-4",
                file_type="text"
            )
            
            # Read the file content
            content = temp_text_file.read_text()
            chunks = processor.split_text(content)
            
            # Verify chunks were created
            assert len(chunks) == 3
            assert all(isinstance(chunk, str) for chunk in chunks)
            
            # Create formatter and format as tasks
            formatter = TaskFormatter(pt_br=False)
            formatted_output = formatter.format_as_tasks(
                chunks=chunks,
                filename=temp_text_file.name
            )
            
            # Verify formatted output
            assert temp_text_file.name in formatted_output
            assert "## TASK 1" in formatted_output
            assert "## TASK 2" in formatted_output
            assert "## TASK 3" in formatted_output
            assert "First semantic chunk" in formatted_output
            assert "Progress:** Pending" in formatted_output
            assert "☐ Pending" in formatted_output
            
            # Write output file
            output_file.write_text(formatted_output)
            assert output_file.exists()
            assert len(output_file.read_text()) > 0

    def test_complete_pipeline_markdown_file(self, temp_markdown_file, temp_dir):
        """Test complete pipeline with a markdown file."""
        output_file = temp_dir / "markdown_output.md"
        
        with patch('cut_it.splitter.MarkdownSplitter') as mock_splitter_class:
            mock_splitter = Mock()
            mock_splitter.chunks.return_value = [
                "# Main Title\n\nThis is the introduction paragraph.",
                "## Section 1\n\nThis section contains important information.",
                "## Section 2\n\nThis is the second major section."
            ]
            mock_splitter_class.from_tiktoken_model.return_value = mock_splitter
            
            processor = TextProcessor(
                chunk_size=(300, 600),
                model="gpt-4",
                file_type="markdown"
            )
            
            content = temp_markdown_file.read_text()
            chunks = processor.split_text(content)
            
            formatter = TaskFormatter(pt_br=False)
            formatted_output = formatter.format_as_tasks(
                chunks=chunks,
                filename=temp_markdown_file.name
            )
            
            # Verify markdown-specific content is preserved
            assert "# Main Title" in formatted_output
            assert "## Section 1" in formatted_output
            assert "## TASK 1" in formatted_output
            
            output_file.write_text(formatted_output)
            assert output_file.exists()

    def test_complete_pipeline_portuguese(self, temp_text_file, temp_dir):
        """Test complete pipeline with Portuguese localization."""
        with patch('cut_it.splitter.TextSplitter') as mock_splitter_class:
            mock_splitter = Mock()
            mock_splitter.chunks.return_value = [
                "Primeiro bloco de texto em português.",
                "Segundo bloco com mais conteúdo para teste."
            ]
            mock_splitter_class.from_tiktoken_model.return_value = mock_splitter
            
            processor = TextProcessor()
            content = temp_text_file.read_text()
            chunks = processor.split_text(content)
            
            formatter = TaskFormatter(pt_br=True)
            formatted_output = formatter.format_as_tasks(
                chunks=chunks,
                filename=temp_text_file.name
            )
            
            # Verify Portuguese labels
            assert "## TAREFA 1" in formatted_output
            assert "**Progresso:** Pendente" in formatted_output
            assert "☐ Pendente" in formatted_output
            assert "☐ Iniciado" in formatted_output
            assert "☐ Concluído" in formatted_output

    def test_config_persistence(self, temp_dir):
        """Test configuration persistence across operations."""
        config_path = temp_dir / "config.json"
        config_manager = ConfigManager(config_path)
        
        # Update configuration
        updated_config = config_manager.update(
            chunk_size_min=250,
            chunk_size_max=750,
            model="gpt-3.5-turbo",
            pt_br=True
        )
        
        # Verify changes were applied
        assert updated_config.chunk_size_min == 250
        assert updated_config.chunk_size_max == 750
        assert updated_config.model == "gpt-3.5-turbo"
        assert updated_config.pt_br is True
        
        # Create new manager instance and verify persistence
        new_config_manager = ConfigManager(config_path)
        loaded_config = new_config_manager.load()
        
        assert loaded_config.chunk_size_min == 250
        assert loaded_config.chunk_size_max == 750
        assert loaded_config.model == "gpt-3.5-turbo"
        assert loaded_config.pt_br is True

    def test_error_handling_file_not_found(self):
        """Test error handling for non-existent files."""
        result = self.runner.invoke(app, ["process", "nonexistent.txt"])
        assert result.exit_code == 1

    def test_error_handling_invalid_chunk_size(self, temp_text_file):
        """Test error handling for invalid chunk size."""
        # This should work as typer will handle the validation
        result = self.runner.invoke(app, [
            "process", str(temp_text_file),
            "--size", "invalid", "size"
        ])
        assert result.exit_code != 0

    @patch('cut_it.cli.ConfigManager')
    @patch('cut_it.cli.TextProcessor')
    @patch('cut_it.cli.TaskFormatter')
    @patch('cut_it.cli.Path')
    def test_cli_integration_with_mocks(self, mock_path, mock_formatter, mock_processor, mock_config_manager):
        """Test CLI integration with comprehensive mocking."""
        # Setup configuration mock
        mock_config = Mock()
        mock_config.chunk_size_min = 300
        mock_config.chunk_size_max = 500
        mock_config.model = "gpt-4"
        mock_config.pt_br = False
        
        mock_config_manager_instance = Mock()
        mock_config_manager_instance.load.return_value = mock_config
        mock_config_manager.return_value = mock_config_manager_instance
        
        # Setup file path mocks
        mock_input_path = Mock()
        mock_input_path.exists.return_value = True
        mock_input_path.read_text.return_value = "Sample text content for processing"
        mock_input_path.name = "test.txt"
        mock_input_path.with_suffix.return_value = Path("test.tasks.md")
        
        mock_output_path = Mock()
        
        def path_side_effect(x):
            if "test.txt" in str(x):
                return mock_input_path
            else:
                return mock_output_path
        
        mock_path.side_effect = path_side_effect
        
        # Setup processor mock
        mock_processor_instance = Mock()
        mock_processor_instance.split_text.return_value = [
            "First chunk of processed text",
            "Second chunk of processed text"
        ]
        mock_processor.return_value = mock_processor_instance
        
        # Setup formatter mock
        mock_formatter_instance = Mock()
        mock_formatter_instance.format_as_tasks.return_value = """# test.txt

---

## TASK 1
**Progress:** Pending

- ☐ Pending
- ☐ Started
- ☐ Completed

First chunk of processed text

---

## TASK 2
**Progress:** Pending

- ☐ Pending
- ☐ Started
- ☐ Completed

Second chunk of processed text

---"""
        mock_formatter.return_value = mock_formatter_instance
        
        # Run the CLI command
        result = self.runner.invoke(app, ["process", "test.txt"])
        
        # Verify success
        assert result.exit_code == 0
        
        # Verify all components were called correctly
        mock_config_manager_instance.load.assert_called_once()
        mock_input_path.read_text.assert_called_once_with(encoding='utf-8')
        mock_processor.assert_called_once_with(
            chunk_size=(300, 500),
            model="gpt-4",
            file_type="text"
        )
        mock_processor_instance.split_text.assert_called_once_with("Sample text content for processing")
        mock_formatter.assert_called_once_with(pt_br=False)
        mock_formatter_instance.format_as_tasks.assert_called_once()
        mock_output_path.write_text.assert_called_once()

    def test_task_status_update_integration(self, sample_chunks):
        """Test task status update functionality integration."""
        formatter = TaskFormatter(pt_br=False)
        
        # Create initial formatted tasks
        formatted_content = formatter.format_as_tasks(
            chunks=sample_chunks,
            filename="test.txt"
        )
        
        # Verify initial state
        assert "**Progress:** Pending" in formatted_content
        task_count = formatter.get_task_count(formatted_content)
        assert task_count == 3
        
        # Update task status
        updated_content = formatter.update_task_status(
            content=formatted_content,
            task_number=2,
            new_status="Started"
        )
        
        # Verify update
        lines = updated_content.split('\n')
        task_2_lines = []
        in_task_2 = False
        
        for line in lines:
            if "## TASK 2" in line:
                in_task_2 = True
            elif "## TASK 3" in line:
                in_task_2 = False
            
            if in_task_2:
                task_2_lines.append(line)
        
        task_2_content = '\n'.join(task_2_lines)
        assert "**Progress:** Started" in task_2_content
        assert "☑ Pending" in task_2_content
        assert "☑ Started" in task_2_content
        assert "☐ Completed" in task_2_content

    def test_chunk_info_integration(self, temp_text_file):
        """Test chunk information integration."""
        with patch('cut_it.splitter.TextSplitter') as mock_splitter_class:
            mock_splitter = Mock()
            test_chunks = [
                "Short chunk",
                "This is a medium length chunk for testing",
                "This is a much longer chunk that contains significantly more content for comprehensive testing"
            ]
            mock_splitter.chunks.return_value = test_chunks
            mock_splitter_class.from_tiktoken_model.return_value = mock_splitter
            
            processor = TextProcessor()
            content = temp_text_file.read_text()
            chunks = processor.split_text(content)
            
            # Get chunk information
            chunk_info = processor.get_chunk_info(chunks)
            
            # Verify chunk info
            assert chunk_info["total_chunks"] == 3
            assert chunk_info["min_chunk_size"] == len("Short chunk")
            assert chunk_info["max_chunk_size"] == len(test_chunks[2])
            assert chunk_info["total_characters"] == sum(len(chunk) for chunk in test_chunks)
            assert chunk_info["average_chunk_size"] > 0