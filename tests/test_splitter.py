"""Tests for the text splitter module."""

import pytest
from unittest.mock import Mock, patch
from cut_it.splitter import TextProcessor


class TestTextProcessor:
    """Test cases for TextProcessor class."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        processor = TextProcessor()
        assert processor.chunk_size == (300, 500)
        assert processor.model == "gpt-4"
        assert processor.file_type == "text"

    def test_init_custom(self):
        """Test initialization with custom parameters."""
        processor = TextProcessor(
            chunk_size=(200, 400),
            model="gpt-3.5-turbo",
            file_type="markdown"
        )
        assert processor.chunk_size == (200, 400)
        assert processor.model == "gpt-3.5-turbo"
        assert processor.file_type == "markdown"

    def test_init_single_chunk_size(self):
        """Test initialization with single chunk size."""
        processor = TextProcessor(chunk_size=1000)
        assert processor.chunk_size == 1000

    @patch('cut_it.splitter.MarkdownSplitter')
    def test_create_splitter_markdown(self, mock_markdown_splitter):
        """Test splitter creation for markdown files."""
        mock_splitter = Mock()
        mock_markdown_splitter.from_tiktoken_model.return_value = mock_splitter
        
        processor = TextProcessor(file_type="markdown")
        assert processor.splitter == mock_splitter
        mock_markdown_splitter.from_tiktoken_model.assert_called_once()

    @patch('cut_it.splitter.TextSplitter')
    def test_create_splitter_text(self, mock_text_splitter):
        """Test splitter creation for text files."""
        mock_splitter = Mock()
        mock_text_splitter.from_tiktoken_model.return_value = mock_splitter
        
        processor = TextProcessor(file_type="text")
        assert processor.splitter == mock_splitter
        mock_text_splitter.from_tiktoken_model.assert_called_once()

    @patch('cut_it.splitter.TextSplitter')
    def test_create_splitter_code(self, mock_text_splitter):
        """Test splitter creation for code files."""
        mock_splitter = Mock()
        mock_text_splitter.from_tiktoken_model.return_value = mock_splitter
        
        processor = TextProcessor(file_type="code")
        assert processor.splitter == mock_splitter
        mock_text_splitter.from_tiktoken_model.assert_called_once()

    def test_split_text_empty(self):
        """Test splitting empty text."""
        processor = TextProcessor()
        result = processor.split_text("")
        assert result == []

    def test_split_text_whitespace_only(self):
        """Test splitting whitespace-only text."""
        processor = TextProcessor()
        result = processor.split_text("   \n\n   ")
        assert result == []

    @patch('cut_it.splitter.TextSplitter')
    def test_split_text_success(self, mock_text_splitter):
        """Test successful text splitting."""
        mock_splitter = Mock()
        mock_splitter.chunks.return_value = ["chunk1", "chunk2", " chunk3 "]
        mock_text_splitter.from_tiktoken_model.return_value = mock_splitter
        
        processor = TextProcessor()
        result = processor.split_text("Some test text")
        
        assert result == ["chunk1", "chunk2", "chunk3"]
        mock_splitter.chunks.assert_called_once_with("Some test text")

    @patch('cut_it.splitter.TextSplitter')
    def test_split_text_exception_fallback(self, mock_text_splitter):
        """Test fallback when splitter raises exception."""
        mock_splitter = Mock()
        mock_splitter.chunks.side_effect = Exception("Splitter error")
        mock_text_splitter.from_tiktoken_model.return_value = mock_splitter
        
        processor = TextProcessor(chunk_size=(50, 100))
        text = "This is a test paragraph.\n\nThis is another paragraph."
        result = processor.split_text(text)
        
        # Should use fallback splitting
        assert len(result) > 0
        assert isinstance(result, list)

    def test_fallback_split_simple(self):
        """Test fallback splitting method."""
        processor = TextProcessor(chunk_size=(20, 50))
        text = "Short para.\n\nAnother short para."
        
        result = processor._fallback_split(text)
        
        assert len(result) >= 1
        assert all(isinstance(chunk, str) for chunk in result)

    def test_fallback_split_long_paragraphs(self):
        """Test fallback splitting with long paragraphs."""
        processor = TextProcessor(chunk_size=(10, 30))
        text = "This is a very long paragraph that should be split." + "\n\n" + \
               "Another very long paragraph that should also be split."
        
        result = processor._fallback_split(text)
        
        assert len(result) >= 1
        # Each chunk should be roughly within size limits or be a single paragraph
        for chunk in result:
            assert len(chunk) <= 100  # Reasonable upper bound

    def test_fallback_split_empty_paragraphs(self):
        """Test fallback splitting with empty paragraphs."""
        processor = TextProcessor()
        text = "Para 1\n\n\n\nPara 2\n\n\n\nPara 3"
        
        result = processor._fallback_split(text)
        
        # Should filter out empty paragraphs
        assert all(chunk.strip() for chunk in result)

    def test_get_chunk_info_empty(self):
        """Test chunk info for empty chunks."""
        processor = TextProcessor()
        info = processor.get_chunk_info([])
        
        expected = {
            "total_chunks": 0,
            "total_characters": 0,
            "average_chunk_size": 0,
            "min_chunk_size": 0,
            "max_chunk_size": 0
        }
        assert info == expected

    def test_get_chunk_info_with_chunks(self):
        """Test chunk info with actual chunks."""
        processor = TextProcessor()
        chunks = ["short", "medium length", "this is a longer chunk"]
        info = processor.get_chunk_info(chunks)
        
        assert info["total_chunks"] == 3
        assert info["total_characters"] == sum(len(chunk) for chunk in chunks)
        assert info["min_chunk_size"] == 5  # "short"
        assert info["max_chunk_size"] == 23  # "this is a longer chunk"
        assert info["average_chunk_size"] == info["total_characters"] // 3

    def test_get_chunk_info_single_chunk(self):
        """Test chunk info with single chunk."""
        processor = TextProcessor()
        chunks = ["single chunk"]
        info = processor.get_chunk_info(chunks)
        
        assert info["total_chunks"] == 1
        assert info["total_characters"] == 12
        assert info["min_chunk_size"] == 12
        assert info["max_chunk_size"] == 12
        assert info["average_chunk_size"] == 12