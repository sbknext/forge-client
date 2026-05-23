"""Tests for Forge (sync) using respx to mock HTTP."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from forge import Forge
from forge.errors import ForgeAuthError, ForgeRateLimitError, ForgeRoleDeniedError, ForgeToolError

BASE = "https://mcp.sbknext.com"
MCP = f"{BASE}/mcp"


def _ok(result: object, req_id: int = 1) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _err(code: int, message: str, req_id: int = 1) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


@respx.mock
def test_initialize():
    respx.post(MCP).mock(return_value=httpx.Response(200, json=_ok({"protocolVersion": "2024-11-05", "capabilities": {}})))
    c = Forge(base_url=BASE, token="tok")
    result = c.initialize()
    assert result["protocolVersion"] == "2024-11-05"


@respx.mock
def test_tools_list():
    tools = [{"name": "memory_save", "description": "Save memory"}, {"name": "memory_search", "description": "Search"}]
    respx.post(MCP).mock(return_value=httpx.Response(200, json=_ok({"tools": tools})))
    c = Forge(base_url=BASE, token="tok")
    result = c.tools_list()
    assert len(result) == 2
    assert result[0]["name"] == "memory_save"


@respx.mock
def test_tools_call_raw_dict():
    payload = {"content": [{"type": "text", "text": json.dumps({"id": "abc123"})}]}
    respx.post(MCP).mock(return_value=httpx.Response(200, json=_ok(payload, req_id=1)))
    c = Forge(base_url=BASE, token="tok")
    result = c.tools_call("memory_save", {"text": "hello"})
    assert result == {"id": "abc123"}


@respx.mock
def test_tools_call_plain_text():
    payload = {"content": [{"type": "text", "text": "not-json"}]}
    respx.post(MCP).mock(return_value=httpx.Response(200, json=_ok(payload)))
    c = Forge(base_url=BASE, token="tok")
    result = c.tools_call("some_tool", {})
    assert result == "not-json"


@respx.mock
def test_memory_save_convenience():
    payload = {"content": [{"type": "text", "text": json.dumps({"saved": True})}]}
    respx.post(MCP).mock(return_value=httpx.Response(200, json=_ok(payload)))
    c = Forge(base_url=BASE, api_key="key123")
    result = c.memory_save("hello world", tags=["test"])
    assert result["saved"] is True


@respx.mock
def test_memory_search_convenience():
    payload = {"content": [{"type": "text", "text": json.dumps([{"text": "hello"}])}]}
    respx.post(MCP).mock(return_value=httpx.Response(200, json=_ok(payload)))
    c = Forge(base_url=BASE, token="tok")
    result = c.memory_search("hello")
    assert isinstance(result, list)


@respx.mock
def test_memory_namespace_api():
    payload = {"content": [{"type": "text", "text": json.dumps({"id": "n1"})}]}
    respx.post(MCP).mock(return_value=httpx.Response(200, json=_ok(payload)))
    c = Forge(base_url=BASE, api_key="k")
    result = c.memory.save("note", tags=["x"])
    assert result["id"] == "n1"


@respx.mock
def test_auth_error_http_401():
    respx.post(MCP).mock(return_value=httpx.Response(401))
    c = Forge(base_url=BASE, token="bad")
    with pytest.raises(ForgeAuthError):
        c.tools_list()


@respx.mock
def test_role_denied_http_403():
    respx.post(MCP).mock(return_value=httpx.Response(403))
    c = Forge(base_url=BASE, token="tok")
    with pytest.raises(ForgeRoleDeniedError):
        c.tools_call("admin_tool", {})


@respx.mock
def test_rate_limit_http_429():
    respx.post(MCP).mock(return_value=httpx.Response(429))
    c = Forge(base_url=BASE, token="tok")
    with pytest.raises(ForgeRateLimitError):
        c.tools_call("memory_save", {"text": "x"})


@respx.mock
def test_rpc_auth_error():
    respx.post(MCP).mock(return_value=httpx.Response(200, json=_err(-32001, "unauthorized")))
    c = Forge(base_url=BASE, token="tok")
    with pytest.raises(ForgeAuthError):
        c.tools_list()


@respx.mock
def test_rpc_tool_error():
    respx.post(MCP).mock(return_value=httpx.Response(200, json=_err(-32600, "invalid request")))
    c = Forge(base_url=BASE, token="tok")
    with pytest.raises(ForgeToolError) as exc_info:
        c.tools_list()
    assert exc_info.value.code == -32600


@respx.mock
def test_rpc_role_denied_message():
    respx.post(MCP).mock(return_value=httpx.Response(200, json=_err(-32003, "forbidden: admin role required")))
    c = Forge(base_url=BASE, token="tok")
    with pytest.raises(ForgeRoleDeniedError):
        c.tools_call("admin_only", {})


@respx.mock
def test_context_manager():
    tools = [{"name": "memory_save", "description": "Save"}]
    respx.post(MCP).mock(return_value=httpx.Response(200, json=_ok({"tools": tools})))
    with Forge(base_url=BASE, token="tok") as c:
        result = c.tools_list()
    assert result[0]["name"] == "memory_save"
