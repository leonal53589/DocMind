"""Server management commands."""

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.callback(invoke_without_command=True)
def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
):
    """Start the KnowledgeVault server."""
    import uvicorn

    console.print(f"[bold green]Starting KnowledgeVault server...[/bold green]")
    console.print(f"Server running at: [bold blue]http://{host}:{port}[/bold blue]")
    console.print(f"API docs at: [bold blue]http://{host}:{port}/docs[/bold blue]")
    console.print("Press Ctrl+C to stop")

    uvicorn.run(
        "backend.app.main:app",
        host=host,
        port=port,
        reload=reload,
    )


@app.command()
def check():
    """Check if the server is running."""
    import httpx

    try:
        response = httpx.get("http://127.0.0.1:8000/api/health", timeout=5.0)
        if response.status_code == 200:
            console.print("[green]Server is running[/green]")
        else:
            console.print(f"[yellow]Server responded with status {response.status_code}[/yellow]")
    except httpx.ConnectError:
        console.print("[red]Server is not running[/red]")
