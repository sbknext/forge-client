# forge — Python SDK

Python SDK + CLI for [corebrain](https://mcp.sbknext.com) MCP server.

## Install

```bash
pip install forge-client
```

## Quickstart

```python
from forge import Forge

with Forge(api_key="sk-...") as f:
    f.memory.save("Sambhaji ships solo via Sonnet sub-agents", tags=["thesis"])
    hits = f.memory.search("solo dev thesis", limit=5)
    print(hits)
```

Async:

```python
from forge import AsyncForge

async with AsyncForge(api_key="sk-...") as f:
    await f.memory.save("async note")
    print(await f.memory.list(limit=10))
```

## CLI

```bash
forge init                       # writes ~/.forge/config.toml
forge memory save "hello" -t demo
forge memory search "hello"
forge memory list
forge tools-list
```

## License

MIT
