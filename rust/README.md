# forge — Rust SDK

Rust SDK for [corebrain](https://mcp.sbknext.com) MCP server.

## Install

```toml
[dependencies]
forge = "0.1"
```

## Quickstart (15 LOC)

```rust
use forge::Forge;

fn main() -> forge::Result<()> {
    let f = Forge::builder()
        .api_key(std::env::var("FORGE_API_KEY").unwrap())
        .build()?;

    f.memory().save("Solo devs ship like teams", Some(&["thesis"]))?;
    let hits = f.memory().search("solo dev", 5)?;
    println!("{:#}", hits);

    let tools = f.tools_list()?;
    println!("{} tools", tools.len());
    Ok(())
}
```

## License

MIT
