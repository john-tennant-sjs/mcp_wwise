# mcp-wwise

An MCP server for **Audiokinetic Wwise**, providing schema-validated, safety-first WAAPI automation for AI agents and programmatic workflows.

Wwise is the dominant middleware for interactive audio in games and media. Its scripting interface (WAAPI) is powerful but unforgiving: small payload mistakes — wrong key casing, missing prefixes, choosing the wrong API for a given field type — produce opaque failures. This server wraps WAAPI in 46 validated tools so that AI assistants and automation scripts can create, inspect, and modify Wwise project content reliably without hand-authoring raw JSON payloads.

[MCP](https://modelcontextprotocol.io/) (Model Context Protocol) is an open standard that lets AI assistants call external tools over a structured interface. Any MCP-compatible host — Claude Desktop, Cursor, VS Code, or others — can connect to this server and operate a running Wwise instance through it.

## Design philosophy

**Schema validation over guesswork.** Every tool has a JSON contract defining its input schema, output schema, and a mock response for dry-run testing. Malformed requests fail fast with actionable error messages before they reach Wwise.

**Semantic preflight checks.** High-risk operations like `object.set` are inspected before execution. The server catches common mistakes — missing `@` prefixes on settable fields, incorrect key casing, ambiguous payload shapes — and returns specific guidance rather than forwarding a payload that will silently fail.

**Display-name resolution.** Users and AI agents think in Wwise UI labels ("Output Bus", "Pitch"). The server resolves these to canonical WAAPI identifiers before making calls, using a combination of live introspection (`getPropertyNames`) and a bundled offline reference snapshot. This eliminates the retry loops that occur when an agent guesses at field name spellings.

**Safety by default.** Strict mode rejects suspicious payloads. An optional autofix mode normalizes safe, obvious mistakes and reports what was changed. Every mutation is verified by reading back the affected object.

## Capabilities

The server exposes 46 tools organized around the core WAAPI surface:

| Area | Tools |
|------|-------|
| Object authoring | Create, delete, copy, move, rename, set notes, declarative batch set |
| Properties and references | Set/get scalar properties, set references, paste properties between objects |
| Field resolution | Resolve display names to WAAPI identifiers, list valid property names, enumerate allowed values |
| Events and actions | Create events, inspect action targets, retarget after duplication |
| Containers | Switch Container assignment add/get/remove |
| Audio | Import audio files, manage attenuation curves |
| SoundBanks | Get/set bank inclusions, generate banks |
| Transport and profiler | Create/destroy transports, play/stop, capture profiler data, voice contributions |
| Project | Save, undo groups (begin/end/cancel), schema introspection, log retrieval |
| UI automation | Bring Wwise to foreground, execute UI commands, read selection state |

Each tool follows the same pattern: input validation against its contract, pre-check for object existence, WAAPI call, post-check read-back, and response validation against its output contract.

## Setup

### Prerequisites

- Python 3.10+
- Wwise Authoring with WAAPI enabled (Project Settings > Allow communication via WAAPI)
- Tested with Wwise 2023.1.17 and 2025.1.3

### Install

```bash
cd wwise-mcp
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Run

```bash
python server.py
```

The server uses **stdio transport** (local process, no network exposure).

### Connect from an MCP client

Configure your MCP host to launch `python server.py` from the `wwise-mcp/` directory. For example, in Claude Desktop's `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "wwise": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/wwise-mcp"
    }
  }
}
```

Cursor, VS Code, and other MCP hosts use similar configuration. Adjust `cwd` (or `command`) to match your local checkout.

### Run tests

```bash
cd wwise-mcp
pytest tests
```

Tests that only exercise validation, dry-run paths, or offline helpers are marked `@pytest.mark.no_waapi` and run on CI. When WAAPI is not reachable (for example on GitHub Actions), all other tests are skipped automatically so the job stays green. Full integration coverage still requires Wwise Authoring open with a project loaded locally.

## Repository structure

```
wwise-mcp/
  server.py              MCP entry point
  tools/                 One module per tool (46 tools)
  tools/client.py        Shared WAAPI connection, validation, logging
  contracts/             JSON input/output contracts and mock responses
  reference/             Offline WAAPI name snapshots (versioned by SDK)
  scripts/               Contract generation, catalog build, validation
  tests/                 Pytest suite (37 test modules)
  requirements.txt       Python dependencies
```

## How safety is layered

1. **Input contract validation** — requests are checked against JSON schemas before any WAAPI call is made.
2. **Semantic preflight** — for complex payloads (`object.set`, RTPC bindings, effect assignments), the server inspects key names, detects missing `@` prefixes, and flags suspicious structures.
3. **Optional autofix** — when enabled, normalizes safe mistakes (key casing, missing prefixes) and reports every change applied.
4. **Live property validation** — before setting a field, the server can query `getPropertyNames` for the object type and reject unknown field names with close-match suggestions.
5. **Post-mutation verification** — after a successful WAAPI call, the server reads back the affected object to confirm the change took effect.
6. **Structured error guidance** — when WAAPI rejects a call, responses include a `suggestion` field with likely causes and next steps.

## Contributing

1. Implement or update a tool in `wwise-mcp/tools/`.
2. Add or update the corresponding contract in `wwise-mcp/contracts/`.
3. Add tests in `wwise-mcp/tests/`.
4. Run `pytest tests` to verify.

## Author

**John Tennant** — technical audio specialist and tools developer.
AAA credits include Returnal, Gears of War 4 and 5, and The Ascent.

[johntennant.com](https://johntennant.com) | [LinkedIn](https://linkedin.com/in/johntechsoundenthusiast)

## License

MIT. See [LICENSE](LICENSE).
