# Contributing to forge

Thanks for your interest. forge is intentionally small — three language SDKs that wrap one HTTP API. The bar for new code is "does it keep all three SDKs consistent and tested."

## Issues

Open an issue if you find a bug, want to propose a new helper, or notice the SDKs drift across languages. Include the language, version, and a minimal repro.

## Pull requests

- Keep changes scoped to one concern.
- Update **all three SDKs** when changing the public surface (Python, Node, Rust). Out-of-sync SDKs will not merge.
- Add or update tests in the affected language(s).
- Run the test suite for any SDK you touched.

## Dev setup

### Python

```bash
cd python
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

### Node

```bash
cd node
npm install
npm test
npm run build
```

### Rust

```bash
cd rust
cargo test
cargo clippy --all-targets -- -D warnings
```

## Style

- Python: PEP 8, type hints, `httpx` only.
- Node: TypeScript strict, ESM-first, native `fetch`.
- Rust: 2021 edition, `reqwest` + `serde` + `thiserror`.
- Error mapping must stay symmetric across languages — see `_raise_for_rpc_error` / `raiseForRpcError` / `map_rpc_error`.

## License

By contributing, you agree your contribution is licensed under the MIT License.
