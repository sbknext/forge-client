# forge — Python SDK

Part of [forge-client](../README.md). Start at **[mcp.sbknext.com](https://mcp.sbknext.com)** for a token.

---

## Install

```bash
pip install sbknext-forge
```

## Quickstart

```python
from forge import Forge

forge = Forge(token="...")            # or os.getenv("FORGE_TOKEN")
forge.memory.save("Sprint 23 retro: ship docs first.", tags=["retro"])
hits = forge.memory.search("docs first", limit=5)
print(hits)
```

Async:

```python
from forge import AsyncForge

async with AsyncForge(token="...") as forge:
    await forge.memory.save("async note")
    print(await forge.memory.list(limit=10))
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
