# wwise-mcp (MCP server for Wwise/WAAPI)

MCP server tooling for controlling **Audiokinetic Wwise Authoring** through **WAAPI**, with a strong focus on **safe, schema-validated automation** for AI agents.

This repository exists because raw WAAPI payload authoring is easy to get wrong, especially for complex `ak.wwise.core.object.set` operations (RTPCs, Effects lists, nested objects). The goal is to make agent-driven changes reliable, explainable, and testable.

## Quickstart

### Prerequisites

- Wwise Authoring installed
- WAAPI enabled in Wwise (websocket)

### Install

```bash
cd wwise-mcp
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Run (stdio)

```bash
cd wwise-mcp
python server.py
```

## Using it from an MCP client

This server uses **stdio transport** (local process). Configure your MCP client to launch `python server.py` from the `wwise-mcp/` directory.

## What’s intentionally not included

- Any Wwise project content. A local playground project is expected for live testing, and should remain untracked (see `MCP_Wwise_Playground/` in `.gitignore`).

## License

MIT. See `LICENSE`.

## Why this project emphasizes schema validation

LLMs are good at patterns, but WAAPI authoring has sharp edges:

- Similar-looking structures from different layers (Wwise WWU XML vs WAAPI JSON) are not interchangeable.
- `object.set` payloads mix structural keys (`object`, `type`, `name`) with WAAPI-settable fields that require `@` prefixes (`@RTPC`, `@PropertyName`, `@ControlInput`, `@Curve`).
- Small casing differences break calls (`points` vs `Points`).
- WAAPI may return generic failures (`None`) without enough context unless the server adds diagnostics.

In practice, common failures include:

- Missing top-level `objects` wrapper for `object.set`.
- Forgetting `@` on settable fields (for example `PropertyName` instead of `@PropertyName`).
- Using values copied from docs/examples that are syntactically close but invalid for the active WAAPI schema.
- Choosing the wrong tool (`setReference` when `set` list/object composition is required).

This server adds guardrails so these errors are caught early with actionable messages.

## Repository structure

- `wwise-mcp/server.py`  
  MCP entrypoint and instruction layer for agents.

- `wwise-mcp/tools/`  
  One Python module per MCP tool (`get`, `set`, references, profiler, transport, etc).

- `wwise-mcp/contracts/`  
  JSON contracts for each tool:
  - `input_schema` (what callers may send)
  - `output_schema` (what tool returns)
  - mock responses for dry-run/testing flows

- `wwise-mcp/scripts/write_contracts.py`  
  Generates/synchronizes contract files.

- `wwise-mcp/reference/`  
  Offline WAAPI name snapshots and notes (fallback when live WAAPI lookup is unavailable).

- `wwise-mcp/tests/`  
  Pytest suite for behavior and regressions.

## Guardrail model (how safety is layered)

### 1) Input contract validation (before WAAPI call)

Tools validate input against contract schemas, so malformed requests fail fast before touching Wwise.

### 2) Semantic preflight checks

For complex operations like `wwise_set_object`, preflight checks detect likely intent errors:

- missing `@` prefixes on settable fields
- suspicious unknown keys in object payloads
- common curve-shape mistakes (`Points` -> `points`)

### 3) Optional normalization/autofix

`wwise_set_object` supports:

- `strict` (default true): reject ambiguous or suspicious payloads
- `autofix` (default false): normalize safe, obvious mistakes and report what was rewritten

### 4) Runtime diagnostics

If WAAPI still rejects a call, tool responses include likely-cause guidance and suggested fixes.

### 5) Helper tools for complex workflows

When raw payload authoring is too brittle, helper tools provide typed operations.  
Example: `wwise_add_rtpc_binding` builds a valid RTPC payload (`@RTPC`, `@PropertyName`, `@ControlInput`, `@Curve.points`) so callers do not handcraft nested `object.set` JSON.

## Key design principle: WAAPI schema is source of truth

When docs, examples, and project XML differ, use the live WAAPI schema (`ak.wwise.waapi.getSchema`) and tool contracts as canonical validation targets.

This is especially important for:

- deciding when `@` prefixes are required
- determining valid key names and nested object shapes
- avoiding layer confusion between WWU serialization and WAAPI payloads

## Typical workflow for contributors

1. Implement or update tool logic in `wwise-mcp/tools/`.
2. Update contract definitions in `wwise-mcp/contracts/` (and generator if needed).
3. Add/adjust tests in `wwise-mcp/tests/`.
4. Run test suite:

```bash
cd wwise-mcp
pytest tests
```

## Current direction

The project is intentionally evolving toward:

- stronger preflight validation for high-risk tools
- better error UX for agent users
- more high-level helper tools for recurring WAAPI tasks
- preserving low-level escape hatches while making safe paths the default

