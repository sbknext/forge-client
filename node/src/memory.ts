/**
 * Memory namespace for the Forge client.
 */

import type { Forge } from "./client.js";

export interface MemorySaveOptions {
  tags?: string[];
  metadata?: Record<string, unknown>;
}

export class MemoryNamespace {
  constructor(private client: Forge) {}

  async save(text: string, opts: MemorySaveOptions = {}): Promise<unknown> {
    const args: Record<string, unknown> = { text };
    if (opts.tags) args.tags = opts.tags;
    if (opts.metadata) args.metadata = opts.metadata;
    return this.client.toolsCall("memory_save", args);
  }

  async search(query: string, limit = 10): Promise<unknown> {
    return this.client.toolsCall("memory_search", { query, limit });
  }

  async list(limit = 50, offset = 0): Promise<unknown> {
    return this.client.toolsCall("memory_list", { limit, offset });
  }

  async delete(id: string): Promise<unknown> {
    return this.client.toolsCall("memory_delete", { id });
  }
}
