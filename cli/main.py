"""KnowledgeVault CLI - Command-line interface for repository management."""

import typer
from rich.console import Console
from rich.table import Table

from .commands import server, import_cmd, repo, classify

app = typer.Typer(
    name="kvault",
    help="KnowledgeVault - A local knowledge repository system",
    add_completion=False,
)
console = Console()

# Add sub-commands
app.add_typer(server.app, name="serve", help="Server management")
app.command(name="import")(import_cmd.import_content)
app.add_typer(repo.app, name="repo", help="Repository management")
app.add_typer(classify.app, name="classify", help="Classification commands")


@app.command()
def version():
    """Show version information."""
    console.print("[bold blue]KnowledgeVault[/bold blue] v0.1.0")


@app.command()
def status():
    """Show vault status and statistics."""
    import httpx

    try:
        response = httpx.get("http://127.0.0.1:8000/api/stats", timeout=5.0)
        if response.status_code == 200:
            stats = response.json()

            table = Table(title="Vault Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Total Items", str(stats["total_items"]))
            table.add_row("Categories", str(stats["total_categories"]))
            table.add_row("Tags", str(stats["total_tags"]))
            table.add_row("Files", str(stats["items_by_type"]["file"]))
            table.add_row("URLs", str(stats["items_by_type"]["url"]))
            table.add_row("Notes", str(stats["items_by_type"]["note"]))

            # Format storage size
            size_bytes = stats["total_storage_bytes"]
            if size_bytes > 1024 * 1024 * 1024:
                size_str = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
            elif size_bytes > 1024 * 1024:
                size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
            elif size_bytes > 1024:
                size_str = f"{size_bytes / 1024:.2f} KB"
            else:
                size_str = f"{size_bytes} bytes"

            table.add_row("Storage Used", size_str)

            console.print(table)
        else:
            console.print("[red]Failed to get vault status[/red]")
    except httpx.ConnectError:
        console.print("[yellow]Vault server is not running.[/yellow]")
        console.print("Start the server with: [bold]kvault serve[/bold]")


@app.command()
def list_items(
    category: str = typer.Option(None, "--category", "-c", help="Filter by category"),
    content_type: str = typer.Option(None, "--type", "-t", help="Filter by content type"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of items to show"),
):
    """List items in the vault."""
    import httpx

    params = {"page_size": limit}
    if content_type:
        params["content_type"] = content_type

    try:
        # If category name provided, need to resolve to ID
        if category:
            cat_response = httpx.get("http://127.0.0.1:8000/api/categories", timeout=5.0)
            if cat_response.status_code == 200:
                categories = cat_response.json()
                for cat in categories:
                    if cat["name"].lower() == category.lower():
                        params["category_id"] = cat["id"]
                        break

        response = httpx.get(
            "http://127.0.0.1:8000/api/items/",
            params=params,
            timeout=5.0,
        )

        if response.status_code == 200:
            data = response.json()
            items = data["items"]

            if not items:
                console.print("[yellow]No items found[/yellow]")
                return

            table = Table(title=f"Items ({data['total']} total)")
            table.add_column("ID", style="dim")
            table.add_column("Title", style="cyan", max_width=50)
            table.add_column("Type", style="green")
            table.add_column("Category", style="blue")
            table.add_column("Created", style="dim")

            for item in items:
                table.add_row(
                    str(item["id"]),
                    item["title"][:50],
                    item["content_type"],
                    item.get("category_name") or "-",
                    item["created_at"][:10],
                )

            console.print(table)
        else:
            console.print(f"[red]Error: {response.status_code}[/red]")
    except httpx.ConnectError:
        console.print("[yellow]Vault server is not running.[/yellow]")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of results"),
):
    """Search items in the vault."""
    import httpx

    try:
        response = httpx.get(
            "http://127.0.0.1:8000/api/search/",
            params={"q": query, "page_size": limit},
            timeout=5.0,
        )

        if response.status_code == 200:
            data = response.json()
            items = data["items"]

            if not items:
                console.print(f"[yellow]No results for '{query}'[/yellow]")
                return

            table = Table(title=f"Search Results for '{query}' ({data['total']} found)")
            table.add_column("ID", style="dim")
            table.add_column("Title", style="cyan", max_width=50)
            table.add_column("Type", style="green")
            table.add_column("Category", style="blue")

            for item in items:
                table.add_row(
                    str(item["id"]),
                    item["title"][:50],
                    item["content_type"],
                    item.get("category_name") or "-",
                )

            console.print(table)
        else:
            console.print(f"[red]Error: {response.status_code}[/red]")
    except httpx.ConnectError:
        console.print("[yellow]Vault server is not running.[/yellow]")


@app.command()
def categories():
    """List all categories."""
    import httpx

    try:
        response = httpx.get("http://127.0.0.1:8000/api/categories/", timeout=5.0)

        if response.status_code == 200:
            cats = response.json()

            table = Table(title="Categories")
            table.add_column("ID", style="dim")
            table.add_column("Name", style="cyan")
            table.add_column("Items", style="green")
            table.add_column("Description", style="dim", max_width=40)

            for cat in cats:
                table.add_row(
                    str(cat["id"]),
                    cat["name"],
                    str(cat["item_count"]),
                    (cat.get("description") or "")[:40],
                )

            console.print(table)
        else:
            console.print(f"[red]Error: {response.status_code}[/red]")
    except httpx.ConnectError:
        console.print("[yellow]Vault server is not running.[/yellow]")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
