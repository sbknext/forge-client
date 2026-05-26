# forge — Rust SDK

Part of [forge-client](../README.md). Start at **[mcp.sbknext.com](https://mcp.sbknext.com)** for a token.

---

## Install

Crates.io publish coming soon. Use via git today:

```toml
[dependencies]
forge = { git = "https://github.com/sbknext/forge-client", package = "forge" }
```

## Quickstart

```rust
use forge::Forge;

fn main() -> forge::Result<()> {
    let forge = Forge::builder()
        .token(std::env::var("FORGE_TOKEN").unwrap())
        .build()?;

    forge.memory().save("Sprint 23 retro: ship docs first.", None)?;
    let hits = forge.memory().search("docs first", 5)?;
    println!("{:#}", hits);

    let tools = forge.tools_list()?;
    println!("{} tools available", tools.len());
    Ok(())
}
```

## License

MIT
