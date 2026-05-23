"""forge — Python SDK for corebrain MCP server."""

from .async_client import AsyncForge
from .client import Forge
from .errors import (
    ForgeAuthError,
    ForgeError,
    ForgeRateLimitError,
    ForgeRoleDeniedError,
    ForgeToolError,
)

# Back-compat aliases (brain-client legacy names)
BrainClient = Forge
AsyncBrainClient = AsyncForge
BrainError = ForgeError
BrainAuthError = ForgeAuthError
BrainRoleDeniedError = ForgeRoleDeniedError
BrainRateLimitError = ForgeRateLimitError
BrainToolError = ForgeToolError

__all__ = [
    "Forge",
    "AsyncForge",
    "ForgeError",
    "ForgeAuthError",
    "ForgeRoleDeniedError",
    "ForgeRateLimitError",
    "ForgeToolError",
    # Back-compat
    "BrainClient",
    "AsyncBrainClient",
    "BrainError",
    "BrainAuthError",
    "BrainRoleDeniedError",
    "BrainRateLimitError",
    "BrainToolError",
]
__version__ = "0.1.0"
