"""Async Forge client — wraps the corebrain MCP HTTP endpoint."""

from __future__ import annotations

import json
from typing import Any

import httpx

from .errors import ForgeAuthError, ForgeRateLimitError, ForgeRoleDeniedError, ForgeToolError

_MCP_PATH = "/mcp"
_JSONRPC = "2.0"
_CLIENT_INFO = {"name": "forge-python", "version": "0.1.0"}
_DEFAULT_BASE_URL = "https://mcp.sbknext.com"


def _raise_for_rpc_error(err: dict[str, Any]) -> None:
    code: int = err.get("code", 0)
    message: str = err.get("message", "unknown error")
    data = err.get("data")

    if code == -32001 or "unauthorized" in message.lower() or ("auth" in message.lower() and "author" not in message.lower()):
        raise ForgeAuthError(message)
    if code == -32003 or "role" in message.lower() or "forbidden" in message.lower() or "permission" in message.lower():
        raise ForgeRoleDeniedError(message)
    if code == -32029 or "rate" in message.lower():
        raise ForgeRateLimitError(message)
    raise ForgeToolError(code, message, data)


def _decode_result(raw: Any) -> Any:
    if isinstance(raw, dict):
        content = raw.get("content")
        if isinstance(content, list) and content:
            first = content[0]
            if isinstance(first, dict) and first.get("type") == "text":
                text = first.get("text", "")
                try:
                    return json.loads(text)
                except (json.JSONDecodeError, TypeError):
                    return text
    return raw


class AsyncForge:
    """Async client for corebrain MCP server."""

    def __init__(
        self,
        base_url: str = _DEFAULT_BASE_URL,
        token: str | None = None,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._base = base_url.rstrip("/")
        self._token = token
        self._api_key = api_key
        self._timeout = timeout
        self._id = 0
        self._http: httpx.AsyncClient | None = None

    def _get_http(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=self._timeout)
        return self._http

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json", "Accept": "application/json"}
        if self._token:
            h["X-Brain-Token"] = self._token
        elif self._api_key:
            h["X-Cb-Key"] = self._api_key
        return h

    def _next_id(self) -> int:
        self._id += 1
        return self._id

    async def _post(self, payload: dict[str, Any]) -> Any:
        http = self._get_http()
        resp = await http.post(
            self._base + _MCP_PATH,
            json=payload,
            headers=self._headers(),
        )
        if resp.status_code == 401:
            raise ForgeAuthError("HTTP 401 Unauthorized")
        if resp.status_code == 403:
            raise ForgeRoleDeniedError("HTTP 403 Forbidden")
        if resp.status_code == 429:
            raise ForgeRateLimitError("HTTP 429 Too Many Requests")
        resp.raise_for_status()
        body = resp.json()
        if "error" in body:
            _raise_for_rpc_error(body["error"])
        return body.get("result")

    async def _rpc(self, method: str, params: dict[str, Any] | None = None) -> Any:
        payload: dict[str, Any] = {
            "jsonrpc": _JSONRPC,
            "id": self._next_id(),
            "method": method,
        }
        if params is not None:
            payload["params"] = params
        return await self._post(payload)

    async def initialize(self, client_info: dict[str, str] | None = None) -> dict[str, Any]:
        return await self._rpc(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "clientInfo": client_info or _CLIENT_INFO,
                "capabilities": {},
            },
        )

    async def tools_list(self) -> list[dict[str, Any]]:
        result = await self._rpc("tools/list")
        return result.get("tools", []) if isinstance(result, dict) else result or []

    async def tools_call(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        raw = await self._rpc("tools/call", {"name": name, "arguments": arguments or {}})
        return _decode_result(raw)

    async def memory_save(
        self,
        text: str,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        args: dict[str, Any] = {"text": text}
        if tags is not None:
            args["tags"] = tags
        if metadata is not None:
            args["metadata"] = metadata
        return await self.tools_call("memory_save", args)

    async def memory_search(self, query: str, limit: int = 10) -> Any:
        return await self.tools_call("memory_search", {"query": query, "limit": limit})

    async def memory_list(self, limit: int = 50, offset: int = 0) -> Any:
        return await self.tools_call("memory_list", {"limit": limit, "offset": offset})

    async def memory_delete(self, memory_id: str) -> Any:
        return await self.tools_call("memory_delete", {"id": memory_id})

    async def community_list(self) -> Any:
        return await self.tools_call("community_list", {})

    async def community_search(
        self,
        query: str,
        community_slug: str | None = None,
        limit: int = 10,
    ) -> Any:
        args: dict[str, Any] = {"query": query, "limit": limit}
        if community_slug is not None:
            args["community_slug"] = community_slug
        return await self.tools_call("community_search", args)

    async def close(self) -> None:
        if self._http is not None:
            await self._http.aclose()
            self._http = None

    async def __aenter__(self) -> "AsyncForge":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()
