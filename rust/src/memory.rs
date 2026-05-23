//! Memory namespace helpers.

use serde_json::{json, Value};

use crate::client::Forge;
use crate::error::Result;

pub struct Memory<'a> {
    client: &'a Forge,
}

impl<'a> Memory<'a> {
    pub(crate) fn new(client: &'a Forge) -> Self {
        Self { client }
    }

    pub fn save(&self, text: &str, tags: Option<&[&str]>) -> Result<Value> {
        let mut args = json!({ "text": text });
        if let Some(t) = tags {
            args["tags"] = json!(t);
        }
        self.client.tools_call("memory_save", args)
    }

    pub fn search(&self, query: &str, limit: u32) -> Result<Value> {
        self.client
            .tools_call("memory_search", json!({ "query": query, "limit": limit }))
    }

    pub fn list(&self, limit: u32, offset: u32) -> Result<Value> {
        self.client
            .tools_call("memory_list", json!({ "limit": limit, "offset": offset }))
    }

    pub fn delete(&self, id: &str) -> Result<Value> {
        self.client.tools_call("memory_delete", json!({ "id": id }))
    }
}

impl Forge {
    pub fn memory(&self) -> Memory<'_> {
        Memory::new(self)
    }
}
