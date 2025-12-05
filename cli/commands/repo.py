"""Repository management commands."""

import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


@app.command()
def init(
    path: str = typer.Argument(".", help="Path for the vault"),
):
    """Initialize a new vault at the specified path."""
    vault_path = Path(path).expanduser().resolve()

    # Create directory structure
    data_dir = vault_path / "data"
    files_dir = data_dir / "files"
    thumbnails_dir = data_dir / "thumbnails"

    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        files_dir.mkdir(exist_ok=True)
        thumbnails_dir.mkdir(exist_ok=True)

        # Create default config
        config_path = vault_path / "config.yaml"
        if not config_path.exists():
            config_content = '''# KnowledgeVault Configuration

server:
  host: "127.0.0.1"
  port: 8000

storage:
  data_dir: "./data"
  max_file_size: 104857600  # 100MB

classification:
  auto_classify: true
  use_ai: false
  ollama_model: "llama3.2"
  ollama_url: "http://localhost:11434"

  rules:
    - category: "Mathematical Principles"
      keywords: ["theorem", "proof", "equation", "formula", "calculus", "algebra"]
      file_types: [".tex", ".nb"]

    - category: "Program Implementation"
      keywords: ["code", "function", "algorithm", "implementation", "api"]
      file_types: [".py", ".js", ".ts", ".java", ".go", ".rs"]

    - category: "Ideas & Concepts"
      keywords: ["idea", "concept", "theory", "hypothesis", "brainstorm"]

    - category: "Affairs & Tasks"
      keywords: ["todo", "task", "meeting", "schedule", "deadline"]

import:
  extract_text: true
  generate_thumbnails: true
  deduplicate: true
'''
            with open(config_path, 'w') as f:
                f.write(config_content)

        console.print(f"[green]Vault initialized at: {vault_path}[/green]")
        console.print(f"  Config: {config_path}")
        console.print(f"  Data: {data_dir}")
        console.print()
        console.print("To start the server, run:")
        console.print(f"  cd {vault_path}")
        console.print("  kvault serve")

    except Exception as e:
        console.print(f"[red]Failed to initialize vault: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def info():
    """Show vault information."""
    import httpx

    # Find config
    config_path = Path("config.yaml")
    if config_path.exists():
        console.print(f"[cyan]Config file:[/cyan] {config_path.resolve()}")
    else:
        console.print("[yellow]No config.yaml found in current directory[/yellow]")

    # Check data directory
    data_path = Path("data")
    if data_path.exists():
        console.print(f"[cyan]Data directory:[/cyan] {data_path.resolve()}")

        # Count files
        files_path = data_path / "files"
        if files_path.exists():
            file_count = sum(1 for _ in files_path.rglob("*") if _.is_file())
            console.print(f"  Files stored: {file_count}")
    else:
        console.print("[yellow]No data directory found[/yellow]")

    # Check server
    try:
        response = httpx.get("http://127.0.0.1:8000/api/health", timeout=2.0)
        if response.status_code == 200:
            console.print("[green]Server: Running[/green]")
        else:
            console.print("[yellow]Server: Responding but unhealthy[/yellow]")
    except:
        console.print("[dim]Server: Not running[/dim]")


@app.command()
def backup(
    output: str = typer.Argument("backup.tar.gz", help="Output backup file path"),
):
    """Create a backup of the vault."""
    import tarfile
    from datetime import datetime

    data_path = Path("data")
    config_path = Path("config.yaml")

    if not data_path.exists():
        console.print("[red]No data directory found[/red]")
        raise typer.Exit(1)

    output_path = Path(output)

    # Add timestamp if no extension
    if not output_path.suffix:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"{output}_{timestamp}.tar.gz")

    try:
        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(data_path, arcname="data")
            if config_path.exists():
                tar.add(config_path, arcname="config.yaml")

        size = output_path.stat().st_size
        size_str = f"{size / (1024 * 1024):.2f} MB"

        console.print(f"[green]Backup created: {output_path}[/green]")
        console.print(f"  Size: {size_str}")

    except Exception as e:
        console.print(f"[red]Backup failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def restore(
    backup_file: str = typer.Argument(..., help="Backup file to restore"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing data"),
):
    """Restore vault from a backup."""
    import tarfile

    backup_path = Path(backup_file)

    if not backup_path.exists():
        console.print(f"[red]Backup file not found: {backup_path}[/red]")
        raise typer.Exit(1)

    data_path = Path("data")

    if data_path.exists() and not force:
        console.print("[yellow]Data directory already exists.[/yellow]")
        console.print("Use --force to overwrite, or backup existing data first.")
        raise typer.Exit(1)

    try:
        with tarfile.open(backup_path, "r:gz") as tar:
            tar.extractall(".")

        console.print(f"[green]Restored from: {backup_path}[/green]")

    except Exception as e:
        console.print(f"[red]Restore failed: {e}[/red]")
        raise typer.Exit(1)
