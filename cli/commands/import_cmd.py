"""Import commands."""

import os
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def import_content(
    path: str = typer.Argument(..., help="File, directory, or URL to import"),
    category: str = typer.Option(None, "--category", "-c", help="Category name"),
    no_classify: bool = typer.Option(False, "--no-classify", help="Disable auto-classification"),
):
    """Import files, directories, or URLs into the vault."""
    import httpx

    # Check if it's a URL
    if path.startswith(("http://", "https://")):
        _import_url(path, category, not no_classify)
    else:
        # It's a local path
        local_path = Path(path).expanduser().resolve()

        if not local_path.exists():
            console.print(f"[red]Path not found: {local_path}[/red]")
            raise typer.Exit(1)

        _import_path(local_path, category, not no_classify)


def _import_url(url: str, category: str = None, auto_classify: bool = True):
    """Import a URL."""
    import httpx

    console.print(f"[cyan]Importing URL: {url}[/cyan]")

    try:
        # Get category ID if name provided
        category_id = None
        if category:
            category_id = _get_category_id(category)
            if not category_id:
                console.print(f"[yellow]Category '{category}' not found, skipping category assignment[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching and processing...", total=None)

            response = httpx.post(
                "http://127.0.0.1:8000/api/import/url",
                params={
                    "url": url,
                    "category_id": category_id,
                    "auto_classify": auto_classify,
                },
                timeout=60.0,
            )

            progress.update(task, completed=True)

        if response.status_code == 200:
            item = response.json()
            console.print(f"[green]Successfully imported: {item['title']}[/green]")
            console.print(f"  ID: {item['id']}")
            console.print(f"  Category: {item.get('category_name') or 'Uncategorized'}")
        else:
            error = response.json().get("detail", "Unknown error")
            console.print(f"[red]Failed to import: {error}[/red]")

    except httpx.ConnectError:
        console.print("[yellow]Vault server is not running.[/yellow]")
        console.print("Start the server with: [bold]kvault serve[/bold]")


def _import_path(path: Path, category: str = None, auto_classify: bool = True):
    """Import a file or directory."""
    import httpx

    if path.is_file():
        console.print(f"[cyan]Importing file: {path}[/cyan]")
    else:
        console.print(f"[cyan]Importing directory: {path}[/cyan]")

    try:
        # Get category ID if name provided
        category_id = None
        if category:
            category_id = _get_category_id(category)
            if not category_id:
                console.print(f"[yellow]Category '{category}' not found, skipping category assignment[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing files...", total=None)

            response = httpx.post(
                "http://127.0.0.1:8000/api/import/path",
                json={
                    "path": str(path),
                    "category_id": category_id,
                    "auto_classify": auto_classify,
                },
                timeout=300.0,  # 5 minutes for large imports
            )

            progress.update(task, completed=True)

        if response.status_code == 200:
            result = response.json()
            console.print(f"[green]Import completed![/green]")
            console.print(f"  Imported: {result['items_imported']} items")
            console.print(f"  Skipped: {result['items_skipped']} items")

            if result['errors']:
                console.print(f"[yellow]Errors:[/yellow]")
                for error in result['errors'][:5]:  # Show first 5 errors
                    console.print(f"  - {error}")
                if len(result['errors']) > 5:
                    console.print(f"  ... and {len(result['errors']) - 5} more")
        else:
            error = response.json().get("detail", "Unknown error")
            console.print(f"[red]Failed to import: {error}[/red]")

    except httpx.ConnectError:
        console.print("[yellow]Vault server is not running.[/yellow]")
        console.print("Start the server with: [bold]kvault serve[/bold]")


def _get_category_id(category_name: str) -> int | None:
    """Get category ID by name."""
    import httpx

    try:
        response = httpx.get("http://127.0.0.1:8000/api/categories/", timeout=5.0)
        if response.status_code == 200:
            categories = response.json()
            for cat in categories:
                if cat["name"].lower() == category_name.lower():
                    return cat["id"]
    except:
        pass

    return None
