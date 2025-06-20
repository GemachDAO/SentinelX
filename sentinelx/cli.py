from __future__ import annotations
import typer
import asyncio
import yaml
from .core.registry import PluginRegistry
from .core.context import Context

app = typer.Typer()
PluginRegistry.discover()

@app.command()
def run(task: str, params: str = typer.Option(..., help="YAML/JSON string")):
    """Run any registered Sentinel X task."""
    p = yaml.safe_load(params)
    ctx = Context.load()
    coro = PluginRegistry.create(task, ctx=ctx, **p)
    result = asyncio.run(coro())
    typer.echo(yaml.dump(result))

if __name__ == "__main__":
    app()
