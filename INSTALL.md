# Install forge-client

## Step 1: Get a token

→ **[mcp.sbknext.com](https://mcp.sbknext.com)** — free preview token via signup.

Or self-host: [`forge-mcp` (private alpha)](https://github.com/sbknext/corebrain) — request access via erp@sbknext.com.

---

## Step 2: Pick your language

### Python (PyPI)

```bash
pip install sbknext-forge
```

Import as:

```python
from forge import Forge
```

### Node (npm)

```bash
npm install @sbkolate/forge
```

Note: npm scope is `sbkolate` (no npm org yet). Import as `@sbkolate/forge`.

### Rust (crates.io — coming soon)

Crates.io publish is pending. Use via git today:

```toml
[dependencies]
forge = { git = "https://github.com/sbknext/forge-client", package = "forge" }
```

---

## Step 3: Configure

Set the `FORGE_TOKEN` environment variable:

```bash
export FORGE_TOKEN=your-preview-token
```

Or pass it directly:

```python
forge = Forge(token="your-preview-token")
```

Auth header used: `X-Brain-Token` (OAuth 2.1 + PKCE coming soon per MCP spec).

---

## Step 4: Use in Claude Desktop / Cursor too

→ [mcp.sbknext.com](https://mcp.sbknext.com) shows the exact MCP client config for each editor.

MCP endpoint: `cb.sbknext.com/mcp` (Streamable HTTP).

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'forge'`**
Check you installed `sbknext-forge` (not `forge-client` — that's the old package name):
```bash
pip install sbknext-forge
```

**`401 Unauthorized`**
Token missing or invalid. Set `FORGE_TOKEN` or pass `token=` to `Forge()`. Get a token at [mcp.sbknext.com](https://mcp.sbknext.com).

**`npm ERR! 404 @sbknext/forge`**
Package scope is `sbkolate`, not `sbknext`:
```bash
npm install @sbkolate/forge
```

**Rust: `error[E0433]: failed to resolve`**
Crates.io not yet published. Use the git dependency form shown in Step 2.
