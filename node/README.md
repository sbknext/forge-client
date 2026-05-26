# @sbkolate/forge — Node SDK

Part of [forge-client](../README.md). Start at **[mcp.sbknext.com](https://mcp.sbknext.com)** for a token.

---

## Install

```bash
npm install @sbkolate/forge
```

Note: npm scope is `sbkolate` (no npm org yet).

## Quickstart

```ts
import { Forge } from "@sbkolate/forge";

const forge = new Forge({ token: process.env.FORGE_TOKEN });

await forge.memory.save("Sprint 23 retro: ship docs first.", { tags: ["retro"] });
const hits = await forge.memory.search("docs first", 5);
console.log(hits);

const tools = await forge.toolsList();
console.log(`${tools.length} tools available`);
```

ESM and CJS dual-built. Node 18+ (native `fetch`).

## License

MIT
