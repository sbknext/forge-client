# @sbknext/forge — Node SDK

Node.js / TypeScript SDK for [corebrain](https://mcp.sbknext.com) MCP server.

## Install

```bash
npm install @sbknext/forge
```

## Quickstart (15 LOC)

```ts
import { Forge } from "@sbknext/forge";

const f = new Forge({ apiKey: process.env.FORGE_API_KEY });

await f.memory.save("Solo devs ship like teams with Sonnet sub-agents", {
  tags: ["thesis"],
});

const hits = await f.memory.search("solo dev thesis", 5);
console.log(hits);

const tools = await f.toolsList();
console.log(`Server exposes ${tools.length} tools.`);
```

ESM and CJS dual-built. Node 18+ (native `fetch`).

## License

MIT
