//! Synchronous Forge client.

use std::sync::atomic::{AtomicI64, Ordering};
use std::time::Duration;

use serde::Serialize;
use serde_json::{json, Value};

use crate::error::{ForgeError, Result};

const MCP_PATH: &str = "/mcp";
const JSONRPC: &str = "2.0";
const DEFAULT_BASE_URL: &str = "https://mcp.sbknext.com";

#[derive(Debug, Clone)]
pub struct ForgeBuilder {
    base_url: String,
    token: Option<String>,
    api_key: Option<String>,
    timeout: Duration,
}

impl Default for ForgeBuilder {
    fn default() -> Self {
        Self {
            base_url: DEFAULT_BASE_URL.into(),
            token: None,
            api_key: None,
            timeout: Duration::from_secs(30),
        }
    }
}

impl ForgeBuilder {
    pub fn base_url(mut self, url: impl Into<String>) -> Self {
        self.base_url = url.into();
        self
    }
    pub fn token(mut self, token: impl Into<String>) -> Self {
        self.token = Some(token.into());
        self
    }
    pub fn api_key(mut self, key: impl Into<String>) -> Self {
        self.api_key = Some(key.into());
        self
    }
    pub fn timeout(mut self, t: Duration) -> Self {
        self.timeout = t;
        self
    }
    pub fn build(self) -> Result<Forge> {
        let http = reqwest::blocking::Client::builder()
            .timeout(self.timeout)
            .build()?;
        Ok(Forge {
            base: self.base_url.trim_end_matches('/').to_string(),
            token: self.token,
            api_key: self.api_key,
            http,
            id: AtomicI64::new(0),
        })
    }
}

pub struct Forge {
    base: String,
    token: Option<String>,
    api_key: Option<String>,
    http: reqwest::blocking::Client,
    id: AtomicI64,
}

#[derive(Serialize)]
struct RpcPayload<'a, P: Serialize> {
    jsonrpc: &'static str,
    id: i64,
    method: &'a str,
    #[serde(skip_serializing_if = "Option::is_none")]
    params: Option<P>,
}

impl Forge {
    pub fn builder() -> ForgeBuilder {
        ForgeBuilder::default()
    }

    pub fn new(api_key: impl Into<String>) -> Result<Self> {
        Self::builder().api_key(api_key).build()
    }

    fn next_id(&self) -> i64 {
        self.id.fetch_add(1, Ordering::SeqCst) + 1
    }

    fn post(&self, payload: &Value) -> Result<Value> {
        let mut req = self
            .http
            .post(format!("{}{}", self.base, MCP_PATH))
            .header("Content-Type", "application/json")
            .header("Accept", "application/json");

        if let Some(t) = &self.token {
            req = req.header("X-Brain-Token", t);
        } else if let Some(k) = &self.api_key {
            req = req.header("X-Cb-Key", k);
        }

        let resp = req.json(payload).send()?;
        let status = resp.status();
        if status.as_u16() == 401 {
            return Err(ForgeError::Auth("HTTP 401 Unauthorized".into()));
        }
        if status.as_u16() == 403 {
            return Err(ForgeError::RoleDenied("HTTP 403 Forbidden".into()));
        }
        if status.as_u16() == 429 {
            return Err(ForgeError::RateLimit("HTTP 429 Too Many Requests".into()));
        }
        if !status.is_success() {
            let body = resp.text().unwrap_or_default();
            return Err(ForgeError::Tool {
                code: status.as_u16() as i64,
                message: format!("HTTP {}: {}", status.as_u16(), body),
                data: None,
            });
        }
        let body: Value = resp.json()?;
        if let Some(err) = body.get("error") {
            return Err(map_rpc_error(err));
        }
        Ok(body.get("result").cloned().unwrap_or(Value::Null))
    }

    pub fn rpc(&self, method: &str, params: Option<Value>) -> Result<Value> {
        let payload = RpcPayload {
            jsonrpc: JSONRPC,
            id: self.next_id(),
            method,
            params,
        };
        let payload = serde_json::to_value(&payload)?;
        self.post(&payload)
    }

    pub fn initialize(&self) -> Result<Value> {
        self.rpc(
            "initialize",
            Some(json!({
                "protocolVersion": "2024-11-05",
                "clientInfo": { "name": "forge-rust", "version": "0.1.0" },
                "capabilities": {}
            })),
        )
    }

    pub fn tools_list(&self) -> Result<Vec<Value>> {
        let r = self.rpc("tools/list", None)?;
        Ok(r.get("tools")
            .and_then(|t| t.as_array().cloned())
            .unwrap_or_default())
    }

    pub fn tools_call(&self, name: &str, arguments: Value) -> Result<Value> {
        let raw = self.rpc(
            "tools/call",
            Some(json!({ "name": name, "arguments": arguments })),
        )?;
        Ok(decode_result(raw))
    }
}

pub(crate) fn map_rpc_error(err: &Value) -> ForgeError {
    let code = err.get("code").and_then(|c| c.as_i64()).unwrap_or(0);
    let message = err
        .get("message")
        .and_then(|m| m.as_str())
        .unwrap_or("unknown error")
        .to_string();
    let data = err.get("data").cloned();
    let lower = message.to_lowercase();

    if code == -32001
        || lower.contains("unauthorized")
        || (lower.contains("auth") && !lower.contains("author"))
    {
        return ForgeError::Auth(message);
    }
    if code == -32003
        || lower.contains("role")
        || lower.contains("forbidden")
        || lower.contains("permission")
    {
        return ForgeError::RoleDenied(message);
    }
    if code == -32029 || lower.contains("rate") {
        return ForgeError::RateLimit(message);
    }
    ForgeError::Tool {
        code,
        message,
        data,
    }
}

pub(crate) fn decode_result(raw: Value) -> Value {
    if let Some(obj) = raw.as_object() {
        if let Some(content) = obj.get("content").and_then(|c| c.as_array()) {
            if let Some(first) = content.first() {
                if first.get("type").and_then(|t| t.as_str()) == Some("text") {
                    if let Some(text) = first.get("text").and_then(|t| t.as_str()) {
                        if let Ok(parsed) = serde_json::from_str::<Value>(text) {
                            return parsed;
                        }
                        return Value::String(text.to_string());
                    }
                }
            }
        }
    }
    raw
}
