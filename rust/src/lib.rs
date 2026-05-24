//! # forge
//!
//! Rust SDK for the [corebrain](https://mcp.sbknext.com) MCP server.
//!
//! ```no_run
//! use sbknext_forge::Forge;
//!
//! # fn main() -> sbknext_forge::Result<()> {
//! let f = Forge::new("sk-...")?;
//! f.memory().save("solo devs ship like teams", Some(&["thesis"]))?;
//! let hits = f.memory().search("solo dev thesis", 5)?;
//! println!("{:?}", hits);
//! # Ok(())
//! # }
//! ```

pub mod client;
pub mod error;
pub mod memory;

pub use client::{Forge, ForgeBuilder};
pub use error::{ForgeError, Result};
pub use memory::Memory;
