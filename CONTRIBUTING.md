# Contributing

Thanks for considering a contribution.

## What this project is (and isn’t)

- This repo is an MCP server that controls **Audiokinetic Wwise Authoring** via **WAAPI**.
- Most meaningful tests require a local Wwise Authoring installation with WAAPI enabled.
- The repo intentionally does **not** include any Wwise project content (see `MCP_Wwise_Playground/` in `.gitignore`).

## Getting started

### Prerequisites

- Python 3.10+ (recommended: 3.11+)
- Wwise Authoring installed (for integration tests)
- WAAPI enabled in Wwise (default websocket URL used by tests: `ws://127.0.0.1:9000/waapi`)

### Install

From the repo root:

```bash
cd wwise-mcp
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Running

Run the MCP server via stdio:

```bash
cd wwise-mcp
python server.py
```

## Tests

### Test types

- **Unit / offline**: should run without Wwise (where available).
- **Integration (live Wwise)**: require Wwise running with WAAPI enabled and a suitable test project.

### Running tests

```bash
cd wwise-mcp
pytest
```

Some tests need additional local configuration:

- Import-audio tests require an **Originals/SFX** folder to write a temporary WAV into.
  Set `WWISE_ORIGINALS_SFX` to your project’s `Originals/SFX` folder. If unset, those tests skip.

## Style & quality

- Keep tool inputs/outputs validated against the project’s JSON contracts.
- Prefer small, well-scoped PRs.
- Avoid adding machine-specific paths to committed files.

## Submitting a PR

- Describe what changed and why.
- Include a test plan (what you ran, and what environment you ran it in).
- If your change requires Wwise to validate, say which Wwise version you used.

