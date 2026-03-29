---
name: Wwise WAAPI reference hardening
overview: Reduce blind retries on `wwise_set_reference` / `wwise_set_property` by combining runtime WAAPI discovery (`getPropertyNames`) with a version-pinned, bundled snapshot of Wwise object property/reference names derived from the official WObjects docs—plus clearer MCP guidance and failure hints.
todos:
  - id: implement-get-property-names
    content: Add wwise_get_property_names tool + contract + tests; set waapi-catalog implemented/verified flags
    status: completed
  - id: implement-get-property-lists
    content: Add wwise_get_property_and_object_lists tool + contract + tests
    status: completed
  - id: add-reference-json
    content: Create wwise-mcp/reference/wobject_waapi_names_2023_1_17.json (seed types) from SDK child pages; document source URL/version (2023.1.17)
    status: completed
  - id: instructions-and-errors
    content: Update server.py MCP instructions; enrich set_reference failures with suggestion (+ optional set_property later)
    status: completed
  - id: verify-output-bus
    content: Confirm OutputBus vs OutputBus* send props from 2023.1.17 WObjects + bundle notes (live Wwise E2E optional)
    status: completed
isProject: false
---

# Harden WAAPI property/reference names in mcp-wwise

## Status (implemented 2026-03-29)

Phases A–D are **done** in the repo. Still open as follow-ups: **strict-mode pre-validation** (was explicitly “later” in the plan), `**set_property.py` richer errors** (only `set_reference` gained an optional `suggestion` field), and a **manual live** output-bus `setReference` check in your own project (bundle + WObjects tables are aligned; not run as an automated CI step).

### What shipped


| Area                  | Details                                                                                                                                                                                                                                                                                                                                                  |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A**                 | `[wwise-mcp/tools/get_property_names.py](wwise-mcp/tools/get_property_names.py)`, `[wwise-mcp/contracts/wwise_get_property_names.json](wwise-mcp/contracts/wwise_get_property_names.json)`, `[wwise-mcp/tests/test_get_property_names.py](wwise-mcp/tests/test_get_property_names.py)`                                                                   |
| **B**                 | `[wwise-mcp/tools/get_property_and_object_lists.py](wwise-mcp/tools/get_property_and_object_lists.py)`, `[wwise-mcp/contracts/wwise_get_property_and_object_lists.json](wwise-mcp/contracts/wwise_get_property_and_object_lists.json)`, `[wwise-mcp/tests/test_get_property_and_object_lists.py](wwise-mcp/tests/test_get_property_and_object_lists.py)` |
| **Shared**            | `resolve_class_id_for_type` in `[wwise-mcp/tools/client.py](wwise-mcp/tools/client.py)`; registration in `[wwise-mcp/tools/__init__.py](wwise-mcp/tools/__init__.py)`; `[wwise-mcp/scripts/validate_contracts.py](wwise-mcp/scripts/validate_contracts.py)` dry-run coverage (**42** tools with contracts)                                               |
| **C**                 | `[wwise-mcp/reference/wobject_waapi_names_2023_1_17.json](wwise-mcp/reference/wobject_waapi_names_2023_1_17.json)`, `[wwise-mcp/reference/README.md](wwise-mcp/reference/README.md)` — seed types: `Sound`, `Bus`, `AuxBus`, `ActorMixer`, `RandomSequenceContainer`                                                                                     |
| **D**                 | `[wwise-mcp/server.py](wwise-mcp/server.py)` FastMCP instructions; `[wwise-mcp/tools/set_reference.py](wwise-mcp/tools/set_reference.py)` clearer errors + optional `suggestion`; `[wwise-mcp/contracts/wwise_set_reference.json](wwise-mcp/contracts/wwise_set_reference.json)` updated                                                                 |
| **Catalog**           | `[wwise-mcp/waapi-catalog.json](wwise-mcp/waapi-catalog.json)`: `getPropertyNames` + `getPropertyAndObjectLists` → `implemented: true`, `requires_object_path: false`, `verified_at: 2026-03-29`                                                                                                                                                         |
| **Cursor MCP mirror** | Descriptor JSON for the two tools under the Cursor project’s `mcps/user-wwise-mcp/tools/` (project-relative for this workspace); `INSTRUCTIONS.md` there matches server guidance                                                                                                                                                                         |


### Plan changes during implementation

1. `**getPropertyNames` args** — WAAPI expects `**classId`**, not the type string. The MCP tool accepts `**object_type**` (from `wwise_get_object`) and resolves `**classId**` via `**ak.wwise.core.object.getTypes**`, or callers pass `**class_id**` directly.
2. `**getPropertyAndObjectLists` args** — Two call shapes: `**{"object", "property"}`** when `**object_ref**` is set; else `**{"classId", "property"}**` after resolving the type.
3. **Contracts** — New tools use hand-maintained files under `[wwise-mcp/contracts/](wwise-mcp/contracts/)`. `[wwise-mcp/scripts/write_contracts.py](wwise-mcp/scripts/write_contracts.py)` was **not** extended (it still reflects the older Phase-2 generator subset only).
4. `**suggestion` on failures** — `wwise_set_reference` can return a top-level `**suggestion`** string in addition to `**error**` for invalid / failed reference operations.
5. **Output bus** — `**OutputBus`** is a **reference** on `**Sound`** (and listed containers); `**OutputBusVolume**`, `**OutputBusHighpass**`, `**OutputBusLowpass**` are **properties**. Recorded in the JSON `**notes`** from **2023.1.17** WObjects pages.
6. **Strict mode** (`validate_reference_against`) — **Not** implemented; remains a future enhancement.

## Context

- `[wwise-mcp/tools/set_reference.py](wwise-mcp/tools/set_reference.py)` historically accepted any `reference` string; vague failures encouraged guessing casing such as `OutputBus` vs `outputBus`.
- The [WObjects index (SDK 2023.1.17)](https://www.audiokinetic.com/en/public-library/2023.1.17_8789/?source=SDK&id=wobjects_index.html) lists **object types**; child pages (e.g. `wwiseobject_sound.html`) document **exact WAAPI names** and **reference vs property**.
- `[wwise-mcp/waapi-catalog.json](wwise-mcp/waapi-catalog.json)` tracks `**getPropertyNames`** and `**getPropertyAndObjectLists**` — authoritative for the **connected** Wwise version; both are **implemented in MCP** now.

## Recommended approach: two layers

```mermaid
flowchart TD
  intent[Agent intent: set output bus etc]
  getObj[wwise_get_object: type + path]
  live[wwise_get_property_names: type from Wwise]
  static[bundled JSON snapshot 2023.1.17]
  choose[Pick API: setReference vs setProperty]
  call[Single call with canonical name]
  intent --> getObj
  getObj --> live
  live -->|Wwise running| choose
  getObj -->|offline or error| static
  static --> choose
  choose --> call
```



1. **Runtime layer** — MCP tools wrapping WAAPI:
  - `**wwise_get_property_names`** → `ak.wwise.core.object.getPropertyNames` (via `**classId**`, resolved from `**object_type**` or supplied as `**class_id**`).
  - `**wwise_get_property_and_object_lists**` → `ak.wwise.core.object.getPropertyAndObjectLists` (`**property_name**` + `**object_ref**` *or* `**object_type` / `class_id*`*).
   Wired through `[wwise-mcp/tools/client.py](wwise-mcp/tools/client.py)`, `[wwise-mcp/contracts/](wwise-mcp/contracts/)`, `[wwise-mcp/scripts/validate_contracts.py](wwise-mcp/scripts/validate_contracts.py)`, `[wwise-mcp/tools/__init__.py](wwise-mcp/tools/__init__.py)`, tests similar to `[wwise-mcp/tests/test_get_schema.py](wwise-mcp/tests/test_get_schema.py)`.
2. **Bundled snapshot** — `[wwise-mcp/reference/wobject_waapi_names_2023_1_17.json](wwise-mcp/reference/wobject_waapi_names_2023_1_17.json)` (**SDK 2023.1.17**, public-library `**2023.1.17_8789`** in `_meta`) keyed by Wwise `**type**` with:
  - `**property_names**` — `setProperty` / `get` `@Property`
  - `**reference_names**` — `setReference` `**reference**` argument
  - optional `**notes**` — e.g. output bus reference vs send-level properties
   Traceability: `[wwise-mcp/reference/README.md](wwise-mcp/reference/README.md)` + `_meta` in the JSON.

## Behavior changes to stop “try every spelling”

- `**server.py**` — Instructions require reading `**type**`, then `**wwise_get_property_names**` (or the bundle offline), before `**wwise_set_property` / `wwise_set_reference**`; forbid guessing labels or alternate casings.
- `**set_reference.py**` — Clearer `**error**` text and optional `**suggestion**` pointing at `**wwise_get_property_names**` and the reference bundle.

Optional **strict mode** (later): `validate_reference_against: "live" | "bundle" | "off"` with default `**off`**.

## Phased delivery


| Phase | Deliverable                                                                                                              | Status                                           |
| ----- | ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------ |
| A     | `wwise_get_property_names` + contract + tests; catalog `implemented: true`                                               | **Done**                                         |
| B     | `wwise_get_property_and_object_lists` + contract + tests                                                                 | **Done**                                         |
| C     | Initial `reference/wobject_waapi_names_2023_1_17.json` for high-traffic types from **2023.1.17** pages; expand over time | **Done** (seed set); expansion ongoing as needed |
| D     | Server instructions + improved errors; output-bus naming verified in docs + bundle                                       | **Done** (live project E2E optional)             |


## Out of scope for this plan

- Automatically scraping all WObjects HTML pages in CI (follow-up script possible).
- Changing WAAPI behavior inside Wwise; if `**setReference`** cannot set a field, document the `**setProperty**` path in bundle `**notes**` once verified.

