"""Text processing and splitting functionality using semantic-text-splitter."""

from typing import List, Tuple, Union
from semantic_text_splitter import TextSplitter, MarkdownSplitter


class TextProcessor:
    """Handles semantic text splitting based on file type and configuration."""
    
    def __init__(
        self,
        chunk_size: Union[int, Tuple[int, int]] = (300, 500),
        model: str = "gpt-4",
        file_type: str = "text"
    ):
        """Initialize text processor.
        
        Args:
            chunk_size: Maximum chunk size (int) or range (tuple)
            model: Tiktoken model name for tokenization
            file_type: Type of file being processed (text, markdown, code)
        """
        self.chunk_size = chunk_size
        self.model = model
        self.file_type = file_type
        self.splitter = self._create_splitter()
    
    def _create_splitter(self) -> Union[TextSplitter, MarkdownSplitter]:
        """Create appropriate splitter based on file type."""
        
        # Use tiktoken tokenizer for accurate token counting
        if self.file_type == "markdown":
            if isinstance(self.chunk_size, tuple):
                return MarkdownSplitter.from_tiktoken_model(
                    self.model, 
                    capacity=self.chunk_size
                )
            else:
                return MarkdownSplitter.from_tiktoken_model(
                    self.model, 
                    capacity=self.chunk_size
                )
        else:
            # Use TextSplitter for both text and code files
            if isinstance(self.chunk_size, tuple):
                return TextSplitter.from_tiktoken_model(
                    self.model, 
                    capacity=self.chunk_size
                )
            else:
                return TextSplitter.from_tiktoken_model(
                    self.model, 
                    capacity=self.chunk_size
                )
    
    def split_text(self, text: str) -> List[str]:
        """Split text into semantic chunks.
        
        Args:
            text: Input text to split
            
        Returns:
            List of text chunks
        """
        if not text.strip():
            return []
        
        try:
            chunks = self.splitter.chunks(text)
            # Filter out empty chunks
            return [chunk.strip() for chunk in chunks if chunk.strip()]
        except Exception as e:
            # Fallback: simple text splitting if semantic splitting fails
            return self._fallback_split(text)
    
    def _fallback_split(self, text: str) -> List[str]:
        """Fallback splitting method when semantic splitting fails."""
        # Simple paragraph-based splitting
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        max_size = self.chunk_size[1] if isinstance(self.chunk_size, tuple) else self.chunk_size
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # If adding this paragraph would exceed chunk size, save current chunk
            if current_chunk and len(current_chunk) + len(paragraph) + 2 > max_size:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk if it exists
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text.strip()]
    
    def get_chunk_info(self, chunks: List[str]) -> dict:
        """Get information about the chunks.
        
        Args:
            chunks: List of text chunks
            
        Returns:
            Dictionary with chunk statistics
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "total_characters": 0,
                "average_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0
            }
        
        chunk_sizes = [len(chunk) for chunk in chunks]
        
        return {
            "total_chunks": len(chunks),
            "total_characters": sum(chunk_sizes),
            "average_chunk_size": sum(chunk_sizes) // len(chunks),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes)
        }