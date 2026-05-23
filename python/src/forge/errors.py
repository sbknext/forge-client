"""forge error types."""

from __future__ import annotations


class ForgeError(Exception):
    """Base error for all forge errors."""


class ForgeAuthError(ForgeError):
    """Authentication failed — bad or missing token/key."""


class ForgeRoleDeniedError(ForgeError):
    """Caller lacks the required role for this tool."""


class ForgeRateLimitError(ForgeError):
    """Rate limit exceeded."""


class ForgeToolError(ForgeError):
    """JSON-RPC tool call error with code and message."""

    def __init__(self, code: int, message: str, data: object = None) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.data = data

    def __repr__(self) -> str:
        return f"ForgeToolError(code={self.code!r}, message={self.message!r})"
