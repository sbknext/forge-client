use sbknext_forge::{Forge, ForgeError};
use mockito::Server;
use serde_json::json;

fn ok_body(result: serde_json::Value) -> String {
    json!({ "jsonrpc": "2.0", "id": 1, "result": result }).to_string()
}

fn err_body(code: i64, message: &str) -> String {
    json!({ "jsonrpc": "2.0", "id": 1, "error": { "code": code, "message": message } }).to_string()
}

fn make_client(server: &Server) -> Forge {
    Forge::builder()
        .base_url(server.url())
        .api_key("test")
        .build()
        .expect("build")
}

#[test]
fn tools_list_ok() {
    let mut server = Server::new();
    let body = ok_body(json!({ "tools": [{ "name": "memory_save", "description": "save" }] }));
    let _m = server.mock("POST", "/mcp").with_status(200).with_body(body).create();

    let f = make_client(&server);
    let tools = f.tools_list().expect("ok");
    assert_eq!(tools.len(), 1);
    assert_eq!(tools[0]["name"], "memory_save");
}

#[test]
fn memory_save_decodes_envelope() {
    let mut server = Server::new();
    let payload = json!({
        "content": [{ "type": "text", "text": serde_json::to_string(&json!({"id":"abc"})).unwrap() }]
    });
    let _m = server.mock("POST", "/mcp").with_status(200).with_body(ok_body(payload)).create();

    let f = make_client(&server);
    let r = f.memory().save("hi", Some(&["t"])).expect("ok");
    assert_eq!(r["id"], "abc");
}

#[test]
fn http_401_is_auth_error() {
    let mut server = Server::new();
    let _m = server.mock("POST", "/mcp").with_status(401).with_body("").create();

    let f = make_client(&server);
    match f.tools_list() {
        Err(ForgeError::Auth(_)) => {}
        other => panic!("expected Auth, got {:?}", other),
    }
}

#[test]
fn http_429_is_rate_limit() {
    let mut server = Server::new();
    let _m = server.mock("POST", "/mcp").with_status(429).with_body("").create();

    let f = make_client(&server);
    match f.tools_list() {
        Err(ForgeError::RateLimit(_)) => {}
        other => panic!("expected RateLimit, got {:?}", other),
    }
}

#[test]
fn rpc_error_minus_32600_is_tool_error() {
    let mut server = Server::new();
    let _m = server
        .mock("POST", "/mcp")
        .with_status(200)
        .with_body(err_body(-32600, "invalid request"))
        .create();

    let f = make_client(&server);
    match f.tools_list() {
        Err(ForgeError::Tool { code, .. }) => assert_eq!(code, -32600),
        other => panic!("expected Tool error, got {:?}", other),
    }
}
