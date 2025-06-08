"""Tests for the task formatter module."""

import pytest
from cut_it.formatter import TaskFormatter


class TestTaskFormatter:
    """Test cases for TaskFormatter class."""

    def test_init_english(self):
        """Test initialization with English language."""
        formatter = TaskFormatter(pt_br=False)
        assert formatter.pt_br is False
        assert formatter.labels["task"] == "TASK"
        assert formatter.labels["progress"] == "Progress"

    def test_init_portuguese(self):
        """Test initialization with Portuguese language."""
        formatter = TaskFormatter(pt_br=True)
        assert formatter.pt_br is True
        assert formatter.labels["task"] == "TAREFA"
        assert formatter.labels["progress"] == "Progresso"

    def test_format_as_tasks_empty(self):
        """Test formatting with empty chunks list."""
        formatter = TaskFormatter()
        result = formatter.format_as_tasks([], "test.txt")
        assert "test.txt" in result
        assert "No content to process" in result

    def test_format_as_tasks_single_chunk(self):
        """Test formatting with single chunk."""
        formatter = TaskFormatter()
        chunks = ["This is a test chunk."]
        result = formatter.format_as_tasks(chunks, "test.txt")
        
        assert "# test.txt" in result
        assert "## TASK 1" in result
        assert "**Progress:** Pending" in result
        assert "☐ Pending" in result
        assert "☐ Started" in result
        assert "☐ Completed" in result
        assert "This is a test chunk." in result

    def test_format_as_tasks_multiple_chunks(self):
        """Test formatting with multiple chunks."""
        formatter = TaskFormatter()
        chunks = ["First chunk", "Second chunk", "Third chunk"]
        result = formatter.format_as_tasks(chunks, "test.txt")
        
        assert "## TASK 1" in result
        assert "## TASK 2" in result
        assert "## TASK 3" in result
        assert "First chunk" in result
        assert "Second chunk" in result
        assert "Third chunk" in result

    def test_format_as_tasks_portuguese(self):
        """Test formatting with Portuguese localization."""
        formatter = TaskFormatter(pt_br=True)
        chunks = ["Primeiro bloco"]
        result = formatter.format_as_tasks(chunks, "teste.txt")
        
        assert "## TAREFA 1" in result
        assert "**Progresso:** Pendente" in result
        assert "☐ Pendente" in result
        assert "☐ Iniciado" in result
        assert "☐ Concluído" in result

    def test_generate_checkboxes_pending(self):
        """Test checkbox generation for pending status."""
        formatter = TaskFormatter()
        checkboxes = formatter._generate_checkboxes("Pending")
        
        assert "☑ Pending" in checkboxes
        assert "☐ Started" in checkboxes
        assert "☐ Completed" in checkboxes

    def test_generate_checkboxes_started(self):
        """Test checkbox generation for started status."""
        formatter = TaskFormatter()
        checkboxes = formatter._generate_checkboxes("Started")
        
        assert "☑ Pending" in checkboxes
        assert "☑ Started" in checkboxes
        assert "☐ Completed" in checkboxes

    def test_generate_checkboxes_completed(self):
        """Test checkbox generation for completed status."""
        formatter = TaskFormatter()
        checkboxes = formatter._generate_checkboxes("Completed")
        
        assert "☑ Pending" in checkboxes
        assert "☑ Started" in checkboxes
        assert "☑ Completed" in checkboxes

    def test_get_task_count(self):
        """Test task count extraction."""
        formatter = TaskFormatter()
        chunks = ["First", "Second", "Third"]
        content = formatter.format_as_tasks(chunks, "test.txt")
        
        count = formatter.get_task_count(content)
        assert count == 3

    def test_extract_task_content(self):
        """Test task content extraction."""
        formatter = TaskFormatter()
        chunks = ["First chunk content", "Second chunk content"]
        content = formatter.format_as_tasks(chunks, "test.txt")
        
        task1_content = formatter.extract_task_content(content, 1)
        task2_content = formatter.extract_task_content(content, 2)
        
        assert task1_content == "First chunk content"
        assert task2_content == "Second chunk content"