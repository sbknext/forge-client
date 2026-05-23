# forge — Multi-language SDK for corebrain

> **Solo devs ship like teams.** forge is the client SDK for [corebrain](https://mcp.sbknext.com) — a hosted MCP server that gives your agents persistent memory, community context, and structured tool calls. Python, Node, and Rust, one consistent surface.

- 🧠 **Memory**: save, search, list, delete — semantic + tag-based
- 👥 **Community**: shared knowledge spaces with role-gated access
- 🔧 **Generic MCP**: any tool exposed on `mcp.sbknext.com` is one `tools_call` away
- 🛡️ **Typed errors**: `Auth / RoleDenied / RateLimit / Tool` surface in every language
- 🪶 **Light**: httpx / fetch / reqwest — no heavy SDK runtimes

→ Backend code: [`sbknext/corebrain`](https://github.com/sbknext/corebrain)
→ Hosted endpoint: <https://mcp.sbknext.com>
→ Website: <https://forge.sbknext.com>

---

## Quickstart — Python

```bash
pip install forge-client
```

```python
from forge import Forge

with Forge(api_key="sk-...") as f:
    f.memory.save("Solo devs ship like teams via Sonnet sub-agents", tags=["thesis"])
    hits = f.memory.search("solo dev thesis", limit=5)
    print(hits)

    tools = f.tools_list()
    print(f"{len(tools)} tools available")
```

## Quickstart — Node / TypeScript

```bash
npm install @sbknext/forge
```

```ts
import { Forge } from "@sbknext/forge";

const f = new Forge({ apiKey: process.env.FORGE_API_KEY });

await f.memory.save("Solo devs ship like teams", { tags: ["thesis"] });
const hits = await f.memory.search("solo dev thesis", 5);
console.log(hits);

const tools = await f.toolsList();
console.log(`${tools.length} tools available`);
```

## Quickstart — Rust

```toml
[dependencies]
forge = "0.1"
```

```rust
use forge::Forge;

fn main() -> forge::Result<()> {
    let f = Forge::builder()
        .api_key(std::env::var("FORGE_API_KEY").unwrap())
        .build()?;

    f.memory().save("Solo devs ship like teams", Some(&["thesis"]))?;
    let hits = f.memory().search("solo dev thesis", 5)?;
    println!("{:#}", hits);

    let tools = f.tools_list()?;
    println!("{} tools available", tools.len());
    Ok(())
}
```

---

## CLI

```bash
pip install forge-client

forge init                           # writes ~/.forge/config.toml
forge memory save "hello" --tag demo
forge memory search "hello"
forge memory list
forge tools-list
```

---

## Why forge?

The thesis: a single human plus Sonnet sub-agents can ship what used to take a team. forge is the persistent-memory + shared-context layer that makes those sub-agents survive across sessions. corebrain is the server; forge is how everything else talks to it.

## Layout

```
forge-client/
├── python/   # forge-client (PyPI) — Forge, AsyncForge, CLI
├── node/     # @sbknext/forge (npm) — ESM + CJS + .d.ts
├── rust/     # forge (crates.io) — sync blocking client
├── docs/
└── examples/
```

## License

MIT — see [LICENSE](./LICENSE).
