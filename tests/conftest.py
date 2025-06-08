"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock
from cut_it.config import Config, ConfigManager
from cut_it.formatter import TaskFormatter
from cut_it.splitter import TextProcessor


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def temp_config_file(temp_dir):
    """Create a temporary config file."""
    config_path = temp_dir / "config.json"
    return config_path


@pytest.fixture
def sample_config():
    """Create a sample configuration."""
    return Config(
        chunk_size_min=250,
        chunk_size_max=750,
        model="gpt-3.5-turbo",
        pt_br=True,
        cli_mode=False
    )


@pytest.fixture
def config_manager(temp_config_file):
    """Create a ConfigManager with temporary file."""
    return ConfigManager(temp_config_file)


@pytest.fixture
def task_formatter():
    """Create a TaskFormatter instance."""
    return TaskFormatter(pt_br=False)


@pytest.fixture
def task_formatter_ptbr():
    """Create a TaskFormatter instance with Portuguese localization."""
    return TaskFormatter(pt_br=True)


@pytest.fixture
def text_processor():
    """Create a TextProcessor instance."""
    return TextProcessor(
        chunk_size=(300, 500),
        model="gpt-4",
        file_type="text"
    )


@pytest.fixture
def markdown_processor():
    """Create a TextProcessor instance for markdown."""
    return TextProcessor(
        chunk_size=(400, 600),
        model="gpt-4",
        file_type="markdown"
    )


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return """
    This is a sample text for testing the text processing functionality.
    It contains multiple paragraphs to test the chunking behavior.
    
    This is the second paragraph. It should be part of the text splitting
    process and help us verify that the semantic splitting works correctly.
    
    The third paragraph is here to provide more content for testing.
    We want to ensure that the text is split appropriately based on
    semantic boundaries rather than just character counts.
    
    Finally, this is the fourth paragraph. It concludes our sample text
    and should help us test various edge cases in the text processing
    pipeline including proper handling of whitespace and formatting.
    """.strip()


@pytest.fixture
def sample_markdown():
    """Sample markdown for testing."""
    return """
# Main Title

This is the introduction paragraph that explains what this document is about.

## Section 1

This section contains important information about the first topic.
It has multiple sentences to provide enough content for testing.

### Subsection 1.1

Here we dive deeper into the first topic with more specific details.

## Section 2

This is the second major section of the document.

- List item 1
- List item 2
- List item 3

### Subsection 2.1

More detailed information in this subsection.

```python
def example_code():
    return "This is a code block"
```

## Conclusion

This concludes our sample markdown document.
    """.strip()


@pytest.fixture
def sample_code():
    """Sample code for testing."""
    return '''
def calculate_total(items):
    """Calculate the total price of items."""
    total = 0
    for item in items:
        total += item.price
    return total

class ShoppingCart:
    """A simple shopping cart implementation."""
    
    def __init__(self):
        self.items = []
    
    def add_item(self, item):
        """Add an item to the cart."""
        self.items.append(item)
    
    def get_total(self):
        """Get the total price of all items."""
        return calculate_total(self.items)
    
    def clear(self):
        """Clear all items from the cart."""
        self.items.clear()

if __name__ == "__main__":
    cart = ShoppingCart()
    print("Shopping cart initialized")
    '''.strip()


@pytest.fixture
def mock_splitter():
    """Create a mock splitter for testing."""
    splitter = Mock()
    splitter.chunks.return_value = [
        "First chunk of text",
        "Second chunk of text", 
        "Third chunk of text"
    ]
    return splitter


@pytest.fixture
def sample_chunks():
    """Sample text chunks for testing."""
    return [
        "This is the first chunk of text that contains some content.",
        "Here is the second chunk with different content for testing.",
        "The third and final chunk completes our sample data set."
    ]


@pytest.fixture
def temp_text_file(temp_dir, sample_text):
    """Create a temporary text file with sample content."""
    file_path = temp_dir / "sample.txt"
    file_path.write_text(sample_text, encoding='utf-8')
    return file_path


@pytest.fixture
def temp_markdown_file(temp_dir, sample_markdown):
    """Create a temporary markdown file with sample content."""
    file_path = temp_dir / "sample.md"
    file_path.write_text(sample_markdown, encoding='utf-8')
    return file_path


@pytest.fixture
def temp_code_file(temp_dir, sample_code):
    """Create a temporary code file with sample content."""
    file_path = temp_dir / "sample.py"
    file_path.write_text(sample_code, encoding='utf-8')
    return file_path


@pytest.fixture
def formatted_tasks():
    """Sample formatted task output."""
    return '''# sample.txt

---

## TASK 1
**Progress:** Pending

- ☑ Pending
- ☐ Started
- ☐ Completed

This is the first chunk of text that contains some content.

---

## TASK 2
**Progress:** Pending

- ☑ Pending
- ☐ Started
- ☐ Completed

Here is the second chunk with different content for testing.

---

## TASK 3
**Progress:** Pending

- ☑ Pending
- ☐ Started
- ☐ Completed

The third and final chunk completes our sample data set.

---'''


# Configure pytest
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )