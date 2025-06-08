# Cut-It 🔪

A semantic text chunking tool that converts documents into organized task lists using AI-powered text splitting.

[![PyPI version](https://badge.fury.io/py/cut-it.svg)](https://badge.fury.io/py/cut-it)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🤖 **Semantic Text Splitting**: Uses `semantic-text-splitter` with tiktoken for intelligent chunking
- 📝 **Multiple File Types**: Supports `.txt`, `.md`, and code files with appropriate splitting strategies  
- 🌍 **Portuguese Support**: Built-in pt-BR localization
- ⚙️ **Configurable**: Customizable chunk sizes, models, and settings
- 📋 **Task Format**: Converts chunks into organized markdown task lists with progress tracking
- 🚀 **CLI Interface**: Beautiful command-line interface with rich output

## Installation

```bash
pip install cut-it
```

## Quick Start

```bash
# Process a text file
cut-it document.txt

# Process a markdown file with custom output
cut-it README.md --output tasks.md

# Use custom chunk size range
cut-it large-document.txt --size 200,800

# Force file type
cut-it code.py --type code
```

## Output Format

Cut-It converts your text into organized task chunks:

```markdown
# document.txt

---

## TASK 1
**Progress:** Pending

- ☐ Pending
- ☐ Started  
- ☐ Completed

[First chunk of your document here...]

---

## TASK 2
**Progress:** Pending

- ☐ Pending
- ☐ Started  
- ☐ Completed

[Second chunk of your document here...]

---
```

## Configuration

```bash
# Show current configuration
cut-it config --show

# Enable Portuguese (Brazil) localization
cut-it config --pt-br true

# Set default model and chunk size
cut-it config --model gpt-4 --size 300,500

# Update configuration
cut-it update
```

## Supported File Types

- **Text Files** (`.txt`): Uses semantic text splitting
- **Markdown Files** (`.md`, `.markdown`): Uses markdown-aware splitting  
- **Code Files**: Python, JavaScript, TypeScript, Java, C++, and more
- **Auto-detection**: Automatically chooses the best splitting strategy

## Advanced Usage

### Custom Chunk Sizes

```bash
# Small chunks (200-400 characters)
cut-it document.txt --size 200,400

# Large chunks (500-1000 characters) 
cut-it document.txt --size 500,1000
```

### Different Models

```bash
# Use GPT-4 tokenizer (default)
cut-it document.txt --model gpt-4

# Use GPT-3.5 tokenizer
cut-it document.txt --model gpt-3.5-turbo
```

### Configuration Management

The tool stores configuration in `~/.cut-it/config.json`:

```json
{
  "chunk_size_min": 300,
  "chunk_size_max": 500,
  "model": "gpt-4",
  "pt_br": false,
  "cli_mode": true
}
```

## Portuguese (Brazil) Support

```bash
# Ativar português brasileiro
cut-it config --pt-br true

# Processar arquivo
cut-it documento.txt
```

Output em português:

```markdown
# documento.txt

---

## TAREFA 1
**Progresso:** Pendente

- ☐ Pendente
- ☐ Iniciado  
- ☐ Concluído

[Conteúdo do primeiro bloco aqui...]
```

## Development

```bash
# Clone the repository
git clone https://github.com/arthrod/cut-it.git
cd cut-it

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black .
isort .
flake8 .
mypy src/cut_it
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [semantic-text-splitter](https://github.com/benbrandt/text-splitter) for intelligent text chunking
- Uses [Typer](https://typer.tiangolo.com/) for the beautiful CLI interface
- Powered by [Rich](https://rich.readthedocs.io/) for gorgeous terminal output

---

Made with ❤️ by [Arthur Souza Rodrigues](mailto:arthrod@umich.edu)