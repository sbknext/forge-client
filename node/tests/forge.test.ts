import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { Forge, ForgeAuthError, ForgeRateLimitError, ForgeRoleDeniedError, ForgeToolError } from "../src/index.js";

const BASE = "https://mcp.sbknext.com";

function okResponse(result: unknown): Response {
  return new Response(JSON.stringify({ jsonrpc: "2.0", id: 1, result }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

function rpcErr(code: number, message: string): Response {
  return new Response(
    JSON.stringify({ jsonrpc: "2.0", id: 1, error: { code, message } }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
}

function statusResp(status: number): Response {
  return new Response("", { status });
}

function mockFetch(impl: (url: string, init: RequestInit) => Promise<Response>) {
  return vi.fn(impl) as unknown as typeof fetch;
}

describe("Forge", () => {
  it("tools list happy path", async () => {
    const fetchMock = mockFetch(async () =>
      okResponse({ tools: [{ name: "memory_save", description: "save" }] })
    );
    const f = new Forge({ baseUrl: BASE, token: "tok", fetch: fetchMock });
    const tools = await f.toolsList();
    expect(tools.length).toBe(1);
    expect(tools[0]!.name).toBe("memory_save");
  });

  it("decodes MCP content text envelope as JSON", async () => {
    const payload = { content: [{ type: "text", text: JSON.stringify({ id: "abc" }) }] };
    const fetchMock = mockFetch(async () => okResponse(payload));
    const f = new Forge({ baseUrl: BASE, apiKey: "k", fetch: fetchMock });
    const r = (await f.memory.save("hello", { tags: ["t"] })) as { id: string };
    expect(r.id).toBe("abc");
  });

  it("memory.search returns parsed list", async () => {
    const payload = { content: [{ type: "text", text: JSON.stringify([{ text: "x" }]) }] };
    const fetchMock = mockFetch(async () => okResponse(payload));
    const f = new Forge({ baseUrl: BASE, token: "tok", fetch: fetchMock });
    const r = (await f.memory.search("x")) as unknown[];
    expect(Array.isArray(r)).toBe(true);
  });

  it("plain text content stays a string", async () => {
    const payload = { content: [{ type: "text", text: "not-json" }] };
    const fetchMock = mockFetch(async () => okResponse(payload));
    const f = new Forge({ baseUrl: BASE, token: "tok", fetch: fetchMock });
    const r = await f.toolsCall("some_tool", {});
    expect(r).toBe("not-json");
  });

  it("HTTP 401 → ForgeAuthError", async () => {
    const fetchMock = mockFetch(async () => statusResp(401));
    const f = new Forge({ baseUrl: BASE, token: "bad", fetch: fetchMock });
    await expect(f.toolsList()).rejects.toBeInstanceOf(ForgeAuthError);
  });

  it("HTTP 403 → ForgeRoleDeniedError", async () => {
    const fetchMock = mockFetch(async () => statusResp(403));
    const f = new Forge({ baseUrl: BASE, token: "tok", fetch: fetchMock });
    await expect(f.toolsCall("admin", {})).rejects.toBeInstanceOf(ForgeRoleDeniedError);
  });

  it("HTTP 429 → ForgeRateLimitError", async () => {
    const fetchMock = mockFetch(async () => statusResp(429));
    const f = new Forge({ baseUrl: BASE, token: "tok", fetch: fetchMock });
    await expect(f.toolsCall("memory_save", {})).rejects.toBeInstanceOf(ForgeRateLimitError);
  });

  it("RPC error -32001 → ForgeAuthError", async () => {
    const fetchMock = mockFetch(async () => rpcErr(-32001, "unauthorized"));
    const f = new Forge({ baseUrl: BASE, token: "tok", fetch: fetchMock });
    await expect(f.toolsList()).rejects.toBeInstanceOf(ForgeAuthError);
  });

  it("RPC error -32600 → ForgeToolError with code", async () => {
    const fetchMock = mockFetch(async () => rpcErr(-32600, "invalid request"));
    const f = new Forge({ baseUrl: BASE, token: "tok", fetch: fetchMock });
    await expect(f.toolsList()).rejects.toMatchObject({ code: -32600 });
  });

  it("sends X-Cb-Key header when api_key is provided", async () => {
    let captured: Record<string, string> = {};
    const fetchMock = mockFetch(async (_url, init) => {
      captured = init.headers as Record<string, string>;
      return okResponse({ tools: [] });
    });
    const f = new Forge({ baseUrl: BASE, apiKey: "secret", fetch: fetchMock });
    await f.toolsList();
    expect(captured["X-Cb-Key"]).toBe("secret");
  });

  it("sends X-Brain-Token header when token is provided", async () => {
    let captured: Record<string, string> = {};
    const fetchMock = mockFetch(async (_url, init) => {
      captured = init.headers as Record<string, string>;
      return okResponse({ tools: [] });
    });
    const f = new Forge({ baseUrl: BASE, token: "jwt", fetch: fetchMock });
    await f.toolsList();
    expect(captured["X-Brain-Token"]).toBe("jwt");
  });
});
