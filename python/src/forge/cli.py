"""forge CLI — command-line interface for corebrain MCP."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .client import Forge
from .errors import ForgeAuthError, ForgeError, ForgeRateLimitError, ForgeRoleDeniedError, ForgeToolError

app = typer.Typer(help="forge — CLI for corebrain MCP server", add_completion=False)
memory_app = typer.Typer(help="Memory operations")
app.add_typer(memory_app, name="memory")

console = Console()

_DEFAULT_CONFIG_PATH = Path("~/.forge/config.toml").expanduser()
_CONFIG_PATH = Path(
    os.environ.get("FORGE_CONFIG") or os.environ.get("BRAIN_CONFIG") or _DEFAULT_CONFIG_PATH
).expanduser()


def _expand_env(value: str) -> str:
    import re
    def replacer(m):  # type: ignore[no-untyped-def]
        return os.environ.get(m.group(1), m.group(0))
    return re.sub(r"\$\{([^}]+)\}", replacer, value)


def _load_config() -> dict:
    if not _CONFIG_PATH.exists():
        return {}
    try:
        if sys.version_info >= (3, 11):
            import tomllib
            with open(_CONFIG_PATH, "rb") as f:
                return tomllib.load(f)
        else:
            import tomli  # type: ignore[import]
            with open(_CONFIG_PATH, "rb") as f:
                return tomli.load(f)
    except Exception:
        return {}


def _make_client() -> Forge:
    cfg = _load_config()
    base_url = (
        os.environ.get("FORGE_URL")
        or os.environ.get("BRAIN_URL")
        or cfg.get("server", {}).get("url", "https://mcp.sbknext.com")
    )
    token = (
        os.environ.get("FORGE_TOKEN")
        or os.environ.get("BRAIN_TOKEN")
        or _expand_env(cfg.get("auth", {}).get("token", ""))
    )
    api_key = (
        os.environ.get("FORGE_API_KEY")
        or os.environ.get("BRAIN_API_KEY")
        or _expand_env(cfg.get("auth", {}).get("api_key", ""))
    )
    return Forge(base_url=base_url, token=token or None, api_key=api_key or None)


def _handle_error(exc: ForgeError) -> None:
    if isinstance(exc, ForgeAuthError):
        console.print(f"[red]Auth error:[/red] {exc}")
    elif isinstance(exc, ForgeRoleDeniedError):
        console.print(f"[red]Role denied:[/red] {exc}")
    elif isinstance(exc, ForgeRateLimitError):
        console.print(f"[yellow]Rate limit:[/yellow] {exc}")
    elif isinstance(exc, ForgeToolError):
        console.print(f"[red]Tool error {exc.code}:[/red] {exc.message}")
    else:
        console.print(f"[red]Error:[/red] {exc}")
    raise typer.Exit(1)


@app.command()
def init(
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key (will prompt if omitted)"),
    url: str = typer.Option("https://mcp.sbknext.com", "--url", help="Server base URL"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config"),
) -> None:
    """Write ~/.forge/config.toml interactively."""
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if _CONFIG_PATH.exists() and not force:
        console.print(f"[yellow]Config already exists:[/yellow] {_CONFIG_PATH} (use --force to overwrite)")
        raise typer.Exit()
    if api_key is None:
        api_key = typer.prompt("API key", hide_input=True, default="", show_default=False)
    api_key_line = f'api_key = "{api_key}"' if api_key else 'api_key = "${FORGE_API_KEY}"'
    content = f"""\
[server]
url = "{url}"

[auth]
# Use one of: token (JWT) or api_key
{api_key_line}
# token = "${{FORGE_TOKEN}}"
"""
    _CONFIG_PATH.write_text(content)
    try:
        os.chmod(_CONFIG_PATH, 0o600)
    except OSError:
        pass
    console.print(f"[green]Created:[/green] {_CONFIG_PATH}")
    console.print("Try [bold]forge tools-list[/bold] to verify.")


@app.command("tools-list")
def tools_list() -> None:
    """List all tools available on the server."""
    try:
        with _make_client() as c:
            tools = c.tools_list()
    except ForgeError as e:
        _handle_error(e)
        return
    table = Table(title="Available Tools", show_lines=True)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description")
    for t in tools:
        table.add_row(t.get("name", ""), t.get("description", ""))
    console.print(table)
    console.print(f"\n[dim]{len(tools)} tool(s)[/dim]")


@app.command("call")
def raw_call(
    tool_name: str = typer.Argument(..., help="Tool name"),
    arguments_json: str = typer.Argument("{}", help="JSON arguments string"),
) -> None:
    """Call any tool with raw JSON arguments."""
    try:
        args = json.loads(arguments_json)
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON:[/red] {e}")
        raise typer.Exit(1)
    try:
        with _make_client() as c:
            result = c.tools_call(tool_name, args)
    except ForgeError as e:
        _handle_error(e)
        return
    rprint(result)


@memory_app.command("save")
def memory_save(
    text: str = typer.Argument(..., help="Text to save"),
    tags: Optional[list[str]] = typer.Option(None, "--tag", "-t", help="Tag (repeat for multiple)"),
) -> None:
    """Save a memory entry."""
    try:
        with _make_client() as c:
            result = c.memory_save(text, tags=tags or None)
    except ForgeError as e:
        _handle_error(e)
        return
    console.print("[green]Saved.[/green]")
    if result:
        rprint(result)


@memory_app.command("search")
def memory_search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(10, "--limit", "-n", help="Max results"),
) -> None:
    """Search memories semantically."""
    try:
        with _make_client() as c:
            result = c.memory_search(query, limit=limit)
    except ForgeError as e:
        _handle_error(e)
        return
    rprint(result)


@memory_app.command("list")
def memory_list(
    limit: int = typer.Option(20, "--limit", "-n"),
    offset: int = typer.Option(0, "--offset"),
) -> None:
    """List recent memories."""
    try:
        with _make_client() as c:
            result = c.memory_list(limit=limit, offset=offset)
    except ForgeError as e:
        _handle_error(e)
        return
    rprint(result)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
