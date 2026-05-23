/**
 * forge SDK error types.
 */

export class ForgeError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ForgeError";
  }
}

export class ForgeAuthError extends ForgeError {
  constructor(message: string) {
    super(message);
    this.name = "ForgeAuthError";
  }
}

export class ForgeRoleDeniedError extends ForgeError {
  constructor(message: string) {
    super(message);
    this.name = "ForgeRoleDeniedError";
  }
}

export class ForgeRateLimitError extends ForgeError {
  constructor(message: string) {
    super(message);
    this.name = "ForgeRateLimitError";
  }
}

export class ForgeToolError extends ForgeError {
  code: number;
  data: unknown;
  constructor(code: number, message: string, data?: unknown) {
    super(`[${code}] ${message}`);
    this.name = "ForgeToolError";
    this.code = code;
    this.data = data;
  }
}
