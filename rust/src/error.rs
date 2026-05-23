//! Error types for the forge SDK.

use thiserror::Error;

#[derive(Debug, Error)]
pub enum ForgeError {
    #[error("authentication failed: {0}")]
    Auth(String),

    #[error("role denied: {0}")]
    RoleDenied(String),

    #[error("rate limited: {0}")]
    RateLimit(String),

    #[error("tool error [{code}]: {message}")]
    Tool {
        code: i64,
        message: String,
        data: Option<serde_json::Value>,
    },

    #[error("http error: {0}")]
    Http(#[from] reqwest::Error),

    #[error("decode error: {0}")]
    Decode(#[from] serde_json::Error),

    #[error("other: {0}")]
    Other(String),
}

pub type Result<T> = std::result::Result<T, ForgeError>;
