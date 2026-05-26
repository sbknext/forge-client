# forge-client

> SDK wrappers for the Forge MCP ecosystem — Python, Node, Rust.
> Talks to self-hosted `forge-mcp` or hosted **Forge Cloud**.

---

## Get started in 30 seconds

**1. Get a free preview token**

→ **[mcp.sbknext.com](https://mcp.sbknext.com)** — signup, free preview token.

**2. Install the SDK**

```bash
pip install sbknext-forge                      # Python
npm install @sbkolate/forge                    # Node
# Rust — crates.io coming soon; use git for now:
# cargo add --git https://github.com/sbknext/forge-client forge
```

**3. Use it**

```python
# Python
from forge import Forge
forge = Forge(token="your-preview-token")
forge.memory.save("Sprint 23 retro: ship docs first.")
hits = forge.memory.search("docs first")
```

```ts
// Node
import { Forge } from "@sbkolate/forge";
const forge = new Forge({ token: process.env.FORGE_TOKEN });
await forge.memory.save("Sprint 23 retro: ship docs first.");
const hits = await forge.memory.search("docs first", 5);
```

```rust
// Rust (via git dependency)
use forge::Forge;
let forge = Forge::builder().token(std::env::var("FORGE_TOKEN").unwrap()).build()?;
forge.memory().save("Sprint 23 retro: ship docs first.", None)?;
let hits = forge.memory().search("docs first", 5)?;
```

---

## What is Forge MCP?

Forge MCP is the **brain your AI agents share** — memory, communities, context, skills — exposed over the Model Context Protocol.

- **Use from Claude Desktop, Cursor, VS Code** → see [mcp.sbknext.com](https://mcp.sbknext.com)
- **Use from your own code** → this repo (forge-client SDK)

---

## Two ways to run

|  | Self-host (`forge-mcp`) | Forge Cloud |
|---|---|---|
| License | MIT | Hosted by sbknext |
| Auth | Local | Token (OAuth soon) |
| Cost | Free forever | Free preview — [join waitlist](https://mcp.sbknext.com) |
| Setup | Clone + build (private alpha) | Free preview token |

Both speak the same MCP protocol. Same SDK, same code — just swap the endpoint.

---

## Minimal usage

### Python

```python
from forge import Forge

forge = Forge(token="...")            # or os.getenv("FORGE_TOKEN")
forge.memory.save("Sprint 23 retro: ship docs first.")
hits = forge.memory.search("docs first")
```

### Node / TypeScript

```ts
import { Forge } from "@sbkolate/forge";

const forge = new Forge({ token: process.env.FORGE_TOKEN });
await forge.memory.save("Sprint 23 retro: ship docs first.");
const hits = await forge.memory.search("docs first", 5);
```

### Rust

Crates.io publish coming soon. Use via git in the meantime:

```toml
[dependencies]
forge = { git = "https://github.com/sbknext/forge-client", package = "forge" }
```

```rust
use forge::Forge;

let forge = Forge::builder()
    .token(std::env::var("FORGE_TOKEN").unwrap())
    .build()?;
forge.memory().save("Sprint 23 retro: ship docs first.", None)?;
let hits = forge.memory().search("docs first", 5)?;
```

---

## Roadmap

- [shipped] PyPI + npm, token auth, memory + community tools
- [next] crates.io publish
- [next] OAuth 2.1 + PKCE per MCP spec
- [next] `forge login` CLI for browser-based auth
- [later] `forge-mcp` self-host server — public, Apache-2.0

---

## Resources

- **[mcp.sbknext.com](https://mcp.sbknext.com)** — main entry, signup, docs
- [Forge Runtime](https://forge.sbknext.com) — 4-agent SDLC orchestrator showcase
- Per-language READMEs: [python/](./python) · [node/](./node) · [rust/](./rust)
- [INSTALL.md](./INSTALL.md) — detailed install + troubleshooting
- Issues + discussions: this repo

---

## License

MIT © 2026 sbknext
