/**
 * Forge — Node SDK for corebrain MCP server.
 */

import {
  ForgeAuthError,
  ForgeRateLimitError,
  ForgeRoleDeniedError,
  ForgeToolError,
} from "./errors.js";
import { MemoryNamespace } from "./memory.js";

const MCP_PATH = "/mcp";
const JSONRPC = "2.0";
const CLIENT_INFO = { name: "forge-node", version: "0.1.0" };
const DEFAULT_BASE_URL = "https://mcp.sbknext.com";

export interface ForgeOptions {
  baseUrl?: string;
  apiKey?: string;
  token?: string;
  timeoutMs?: number;
  fetch?: typeof fetch;
}

interface RpcError {
  code: number;
  message: string;
  data?: unknown;
}

interface RpcResponse {
  jsonrpc: string;
  id: number;
  result?: unknown;
  error?: RpcError;
}

function raiseForRpcError(err: RpcError): never {
  const code = err.code ?? 0;
  const message = err.message ?? "unknown error";
  const lower = message.toLowerCase();
  if (code === -32001 || lower.includes("unauthorized") || (lower.includes("auth") && !lower.includes("author"))) {
    throw new ForgeAuthError(message);
  }
  if (
    code === -32003 ||
    lower.includes("role") ||
    lower.includes("forbidden") ||
    lower.includes("permission")
  ) {
    throw new ForgeRoleDeniedError(message);
  }
  if (code === -32029 || lower.includes("rate")) {
    throw new ForgeRateLimitError(message);
  }
  throw new ForgeToolError(code, message, err.data);
}

function decodeResult(raw: unknown): unknown {
  if (raw && typeof raw === "object" && !Array.isArray(raw)) {
    const obj = raw as Record<string, unknown>;
    const content = obj.content;
    if (Array.isArray(content) && content.length > 0) {
      const first = content[0] as Record<string, unknown>;
      if (first && first.type === "text" && typeof first.text === "string") {
        try {
          return JSON.parse(first.text);
        } catch {
          return first.text;
        }
      }
    }
  }
  return raw;
}

export class Forge {
  private base: string;
  private token?: string;
  private apiKey?: string;
  private timeoutMs: number;
  private fetchImpl: typeof fetch;
  private id = 0;

  public memory: MemoryNamespace;

  constructor(opts: ForgeOptions = {}) {
    this.base = (opts.baseUrl ?? DEFAULT_BASE_URL).replace(/\/+$/, "");
    this.token = opts.token;
    this.apiKey = opts.apiKey;
    this.timeoutMs = opts.timeoutMs ?? 30_000;
    this.fetchImpl = opts.fetch ?? globalThis.fetch;
    if (!this.fetchImpl) {
      throw new Error("No fetch implementation. Pass `fetch` in options or use Node 18+.");
    }
    this.memory = new MemoryNamespace(this);
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };
    if (this.token) h["X-Brain-Token"] = this.token;
    else if (this.apiKey) h["X-Cb-Key"] = this.apiKey;
    return h;
  }

  private nextId(): number {
    this.id += 1;
    return this.id;
  }

  private async post(payload: unknown): Promise<unknown> {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), this.timeoutMs);
    let resp: Response;
    try {
      resp = await this.fetchImpl(this.base + MCP_PATH, {
        method: "POST",
        headers: this.headers(),
        body: JSON.stringify(payload),
        signal: ctrl.signal,
      });
    } finally {
      clearTimeout(timer);
    }

    if (resp.status === 401) throw new ForgeAuthError("HTTP 401 Unauthorized");
    if (resp.status === 403) throw new ForgeRoleDeniedError("HTTP 403 Forbidden");
    if (resp.status === 429) throw new ForgeRateLimitError("HTTP 429 Too Many Requests");
    if (!resp.ok) {
      const text = await resp.text().catch(() => "");
      throw new ForgeToolError(resp.status, `HTTP ${resp.status}: ${text}`);
    }
    const body = (await resp.json()) as RpcResponse;
    if (body.error) raiseForRpcError(body.error);
    return body.result;
  }

  async rpc(method: string, params?: Record<string, unknown>): Promise<unknown> {
    const payload: Record<string, unknown> = {
      jsonrpc: JSONRPC,
      id: this.nextId(),
      method,
    };
    if (params !== undefined) payload.params = params;
    return this.post(payload);
  }

  async initialize(clientInfo?: { name: string; version: string }): Promise<unknown> {
    return this.rpc("initialize", {
      protocolVersion: "2024-11-05",
      clientInfo: clientInfo ?? CLIENT_INFO,
      capabilities: {},
    });
  }

  async toolsList(): Promise<Array<Record<string, unknown>>> {
    const r = (await this.rpc("tools/list")) as { tools?: Array<Record<string, unknown>> } | null;
    if (r && Array.isArray(r.tools)) return r.tools;
    return [];
  }

  async toolsCall(name: string, args: Record<string, unknown> = {}): Promise<unknown> {
    const raw = await this.rpc("tools/call", { name, arguments: args });
    return decodeResult(raw);
  }
}
