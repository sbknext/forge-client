"""Tests for AsyncForge using respx."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from forge import AsyncForge
from forge.errors import ForgeAuthError, ForgeToolError

BASE = "https://mcp.sbknext.com"
MCP = f"{BASE}/mcp"


def _ok(result: object, req_id: int = 1) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _err(code: int, message: str, req_id: int = 1) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


@pytest.mark.asyncio
@respx.mock
async def test_async_tools_list():
    tools = [{"name": "memory_save", "description": "Save memory"}]
    respx.post(MCP).mock(return_value=httpx.Response(200, json=_ok({"tools": tools})))
    async with AsyncForge(base_url=BASE, token="tok") as c:
        result = await c.tools_list()
    assert result[0]["name"] == "memory_save"


@pytest.mark.asyncio
@respx.mock
async def test_async_memory_save():
    payload = {"content": [{"type": "text", "text": json.dumps({"id": "xyz"})}]}
    respx.post(MCP).mock(return_value=httpx.Response(200, json=_ok(payload)))
    async with AsyncForge(base_url=BASE, token="tok") as c:
        result = await c.memory_save("async hello", tags=["async"])
    assert result["id"] == "xyz"


@pytest.mark.asyncio
@respx.mock
async def test_async_auth_error():
    respx.post(MCP).mock(return_value=httpx.Response(401))
    async with AsyncForge(base_url=BASE, token="bad") as c:
        with pytest.raises(ForgeAuthError):
            await c.tools_list()


@pytest.mark.asyncio
@respx.mock
async def test_async_rpc_error():
    respx.post(MCP).mock(return_value=httpx.Response(200, json=_err(-32700, "parse error")))
    async with AsyncForge(base_url=BASE, token="tok") as c:
        with pytest.raises(ForgeToolError) as exc_info:
            await c.tools_call("any_tool", {})
    assert exc_info.value.code == -32700
