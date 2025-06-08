"""Command-line interface for cut-it."""

from pathlib import Path
from typing import Optional, Tuple
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import ConfigManager, Config
from .splitter import TextProcessor
from .formatter import TaskFormatter
from .localization import get_messages

app = typer.Typer(
    name="cut-it",
    help="Semantic text chunking tool that converts documents into organized task lists",
    rich_markup_mode="rich"
)
console = Console()


def get_file_type(file_path: Path) -> str:
    """Determine file type based on extension."""
    suffix = file_path.suffix.lower()
    
    # Markdown files
    if suffix in ['.md', '.markdown']:
        return 'markdown'
    
    # Code files
    code_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
        '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
        '.clj', '.hs', '.ml', '.fs', '.elm', '.dart', '.lua', '.r',
        '.sql', '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd'
    }
    if suffix in code_extensions:
        return 'code'
    
    # Default to text
    return 'text'


@app.command()
def process(
    file_path: str = typer.Argument(..., help="Path to the text file to process"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path (optional)"),
    chunk_size: Optional[Tuple[int, int]] = typer.Option(None, "--size", "-s", help="Chunk size range (min,max)"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Tiktoken model to use"),
    force_type: Optional[str] = typer.Option(None, "--type", "-t", help="Force file type (text, markdown, code)"),
) -> None:
    """Process a text file and convert it into organized task chunks."""
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load()
    
    # Override config with command line arguments
    if chunk_size:
        config.chunk_size_min, config.chunk_size_max = chunk_size
    if model:
        config.model = model
    
    # Get localized messages
    messages = get_messages(config.pt_br)
    
    # Validate input file
    input_path = Path(file_path)
    if not input_path.exists():
        console.print(f"[red]{messages['file_not_found']}: {file_path}[/red]")
        raise typer.Exit(1)
    
    # Determine file type
    file_type = force_type or get_file_type(input_path)
    
    # Setup output path
    if output:
        output_path = Path(output)
    else:
        output_path = input_path.with_suffix('.tasks.md')
    
    # Process file
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        
        # Read file
        task = progress.add_task(messages['reading_file'], total=None)
        try:
            text_content = input_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            console.print(f"[red]{messages['encoding_error']}[/red]")
            raise typer.Exit(1)
        progress.remove_task(task)
        
        # Split text
        task = progress.add_task(messages['splitting_text'], total=None)
        processor = TextProcessor(
            chunk_size=(config.chunk_size_min, config.chunk_size_max),
            model=config.model,
            file_type=file_type
        )
        chunks = processor.split_text(text_content)
        progress.remove_task(task)
        
        # Format as tasks
        task = progress.add_task(messages['formatting_tasks'], total=None)
        formatter = TaskFormatter(pt_br=config.pt_br)
        formatted_output = formatter.format_as_tasks(
            chunks=chunks,
            filename=input_path.name
        )
        progress.remove_task(task)
        
        # Save output
        task = progress.add_task(messages['saving_file'], total=None)
        output_path.write_text(formatted_output, encoding='utf-8')
        progress.remove_task(task)
    
    console.print(f"[green]{messages['success']}[/green] {output_path}")
    console.print(f"{messages['chunks_created']}: {len(chunks)}")


@app.command()
def config_cmd(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    pt_br: Optional[bool] = typer.Option(None, "--pt-br", help="Enable/disable Portuguese (Brazil) localization"),
    cli: Optional[bool] = typer.Option(None, "--cli", help="Enable/disable CLI mode"),
    model: Optional[str] = typer.Option(None, "--model", help="Set default tiktoken model"),
    size: Optional[Tuple[int, int]] = typer.Option(None, "--size", help="Set default chunk size range"),
) -> None:
    """Manage cut-it configuration settings."""
    
    config_manager = ConfigManager()
    
    if show:
        config = config_manager.load()
        console.print("\n[bold]Current Configuration:[/bold]")
        console.print(f"Chunk size: {config.chunk_size_min}-{config.chunk_size_max}")
        console.print(f"Model: {config.model}")
        console.print(f"Portuguese (BR): {'enabled' if config.pt_br else 'disabled'}")
        console.print(f"CLI mode: {'enabled' if config.cli_mode else 'disabled'}")
        return
    
    # Update configuration
    updates = {}
    if pt_br is not None:
        updates['pt_br'] = pt_br
    if cli is not None:
        updates['cli_mode'] = cli
    if model is not None:
        updates['model'] = model
    if size is not None:
        updates['chunk_size_min'], updates['chunk_size_max'] = size
    
    if updates:
        config = config_manager.update(**updates)
        messages = get_messages(config.pt_br)
        console.print(f"[green]{messages['config_updated']}[/green]")
    else:
        console.print("[yellow]No configuration changes specified. Use --show to view current settings.[/yellow]")


@app.command()
def update() -> None:
    """Update cut-it configuration or check for updates."""
    config_manager = ConfigManager()
    config = config_manager.load()
    messages = get_messages(config.pt_br)
    
    console.print(f"[blue]{messages['checking_updates']}[/blue]")
    # In a real implementation, this would check for package updates
    console.print(f"[green]{messages['up_to_date']}[/green]")


if __name__ == "__main__":
    app()