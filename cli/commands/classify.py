"""Classification commands."""

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


@app.command()
def item(
    item_id: int = typer.Argument(..., help="Item ID to reclassify"),
):
    """Reclassify a specific item."""
    import httpx

    try:
        response = httpx.post(
            f"http://127.0.0.1:8000/api/import/{item_id}/reclassify",
            timeout=30.0,
        )

        if response.status_code == 200:
            item = response.json()
            console.print(f"[green]Item reclassified![/green]")
            console.print(f"  Title: {item['title']}")
            console.print(f"  Category: {item.get('category_name') or 'Uncategorized'}")
            console.print(f"  Confidence: {item.get('confidence', 0):.2%}")
        elif response.status_code == 404:
            console.print(f"[red]Item not found: {item_id}[/red]")
        else:
            error = response.json().get("detail", "Unknown error")
            console.print(f"[red]Failed: {error}[/red]")

    except httpx.ConnectError:
        console.print("[yellow]Vault server is not running.[/yellow]")


@app.command()
def all_items(
    force: bool = typer.Option(False, "--force", "-f", help="Reclassify all items, not just uncategorized"),
):
    """Reclassify all items (or just uncategorized ones)."""
    import httpx

    try:
        # Get all items
        params = {"page_size": 1000}
        if not force:
            # Only uncategorized - we'll filter client-side
            pass

        response = httpx.get(
            "http://127.0.0.1:8000/api/items/",
            params=params,
            timeout=30.0,
        )

        if response.status_code != 200:
            console.print("[red]Failed to get items[/red]")
            return

        items = response.json()["items"]

        if not force:
            items = [i for i in items if i.get("category_id") is None]

        if not items:
            console.print("[green]No items to reclassify[/green]")
            return

        console.print(f"Reclassifying {len(items)} items...")

        success_count = 0
        for item in items:
            try:
                resp = httpx.post(
                    f"http://127.0.0.1:8000/api/import/{item['id']}/reclassify",
                    timeout=30.0,
                )
                if resp.status_code == 200:
                    success_count += 1
                    result = resp.json()
                    console.print(f"  [dim]{item['title'][:40]}[/dim] -> {result.get('category_name') or 'Uncategorized'}")
            except Exception as e:
                console.print(f"  [red]Error: {item['title'][:40]}: {e}[/red]")

        console.print(f"[green]Reclassified {success_count}/{len(items)} items[/green]")

    except httpx.ConnectError:
        console.print("[yellow]Vault server is not running.[/yellow]")


@app.command()
def rules():
    """Show current classification rules."""
    console.print("[cyan]Default Classification Rules:[/cyan]")
    console.print()

    rules_data = {
        "Mathematical Principles": {
            "keywords": ["theorem", "proof", "equation", "formula", "calculus", "algebra"],
            "file_types": [".tex", ".nb", ".m"],
        },
        "Ideas & Concepts": {
            "keywords": ["idea", "concept", "theory", "hypothesis", "brainstorm"],
            "file_types": [],
        },
        "Program Implementation": {
            "keywords": ["code", "function", "algorithm", "implementation", "api"],
            "file_types": [".py", ".js", ".ts", ".java", ".go", ".rs"],
        },
        "Affairs & Tasks": {
            "keywords": ["todo", "task", "meeting", "schedule", "deadline"],
            "file_types": [],
        },
    }

    for category, rules in rules_data.items():
        console.print(f"[bold]{category}[/bold]")
        console.print(f"  Keywords: {', '.join(rules['keywords'][:5])}...")
        if rules['file_types']:
            console.print(f"  File types: {', '.join(rules['file_types'])}")
        console.print()

    console.print("[dim]Edit config.yaml to customize classification rules.[/dim]")
