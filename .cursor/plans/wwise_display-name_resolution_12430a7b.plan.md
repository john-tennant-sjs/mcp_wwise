---
name: Wwise display-name resolution
overview: Add a server-side resolution path so agents map user-facing labels (display names / natural phrasing) to canonical WAAPI property and reference strings before calling `wwise_set_property` or `wwise_set_reference`, extending the existing 2023.1.17 reference bundle and MCP guidance.
todos:
  - id: extend-bundle-aliases
    content: "Add display_aliases to wobject_waapi_names_2023_1_17.json (seed: Sound/Output Bus, etc.); document in reference/README.md"
    status: completed
  - id: implement-resolve-tool
    content: Add wwise_resolve_waapi_field (tool + client.py helpers if needed) + contract + waapi-catalog entry
    status: completed
  - id: tests-resolve
    content: Add tests/test_resolve_waapi_field.py (bundle + dry_run; optional live mock)
    status: completed
  - id: update-instructions-mcp-mirror
    content: Update server.py instructions; sync mcps/user-wwise-mcp tools + INSTRUCTIONS if present
    status: completed
isProject: false
---

# Display-name to WAAPI resolution (mcp-wwise)

## Background (already in repo)

Reference hardening is **implemented**: `[wwise_get_property_names](wwise-mcp/tools/get_property_names.py)`, `[wwise_get_property_and_object_lists](wwise-mcp/tools/get_property_and_object_lists.py)`, `[wobject_waapi_names_2023_1_17.json](wwise-mcp/reference/wobject_waapi_names_2023_1_17.json)`, and `[server.py](wwise-mcp/server.py)` instructions. Gaps for a **new** agent to close:

- Users (and models) still think in **UI / doc display labels** (“Output Bus”, “Conversion settings”); the bundle lists **canonical** names only.
- There is **no single tool** that turns a fuzzy label into `{waapi_name, kind: property|reference, suggested_tool}` in one call, so models may still burn turns guessing.

## Goals

1. **Deterministic alias resolution** from normalized user input → canonical strings, scoped by **Wwise `type`** (e.g. `Sound`).
2. **Optional live validation**: when Wwise is connected, intersect candidate names with `getPropertyNames` so stale bundle rows cannot win.
3. **Fast path**: one MCP call for resolution instead of multiple `set_`* retries.
4. Keep scope **narrow** at first: seed **aliases only where** the [2023.1.17 WObjects](https://www.audiokinetic.com/en/public-library/2023.1.17_8789/?source=SDK&id=wobjects_index.html) tables give a clear display/internal pairing (e.g. Output Bus → `OutputBus` reference). Expand incrementally.

## Data model (extend the bundle)

In `[wobject_waapi_names_2023_1_17.json](wwise-mcp/reference/wobject_waapi_names_2023_1_17.json)`, per object type (alongside existing `property_names`, `reference_names`, `notes`), add an optional object, e.g.:

```json
"display_aliases": {
  "output bus": { "waapi_name": "OutputBus", "kind": "reference" },
  "outputbus": { "waapi_name": "OutputBus", "kind": "reference" }
}
```

Rules for maintainers (document in `[reference/README.md](wwise-mcp/reference/README.md)`):

- Keys are **lowercased, trimmed**; normalization happens in code so unknown casing from the user still matches.
- `kind` is `reference` or `property` and must align with whether the name appears in `reference_names` or `property_names` for that type (assert or test).
- Prefer **SDK display-name column** as source of truth; avoid inventing synonyms without a doc citation.

## New MCP tool: `wwise_resolve_waapi_field`

Add `[wwise-mcp/tools/resolve_waapi_field.py](wwise-mcp/tools/resolve_waapi_field.py)` (name can match `TOOL_NAME` / contract):

**Inputs (suggested):**

- `object_type`: string from `wwise_get_object` (required unless you also support `class_id` like `get_property_names`).
- `user_label`: free text from the user (“output bus”, “Output Bus”).
- `use_live_validation`: boolean, default `true` when not `dry_run` — after bundle/alias match, require the name to appear in live `getPropertyNames` for that type; on mismatch, return error + list closest valid names (optional: substring filter on the live list).

**Output (`data`):**

- `waapi_name`, `kind` (`reference` | `property`), `suggested_tool` (`wwise_set_reference` | `wwise_set_property`).
- `source`: `alias` | `exact_match` | `live_only` (if you add fallback matching against live list).
- Optional `alternatives` if ambiguous.

**Behavior:**

1. Normalize `user_label` (lower, strip, collapse internal spaces).
2. If `display_aliases[normalized]` exists → candidate.
3. Else if normalized equals a canonical `property_names` or `reference_names` entry (case-insensitive) → candidate with `source: exact_match`.
4. Optional Phase 2: **fuzzy** match only against the **union** of property + reference for that type (e.g. single Levenshtein threshold or “only one substring match”) — default **off** or very strict to avoid wrong mutations.
5. If `use_live_validation` and Wwise connected: call `getPropertyNames` (reuse `[resolve_class_id_for_type](wwise-mcp/tools/client.py)`); reject if `waapi_name` not in returned set; include short `error` + `suggestion`.

**Registration:** `[tools/__init__.py](wwise-mcp/tools/__init__.py)`, new contract `[contracts/wwise_resolve_waapi_field.json](wwise-mcp/contracts/wwise_resolve_waapi_field.json)`, `[validate_contracts.py](wwise-mcp/scripts/validate_contracts.py)` dry-run entry, `[waapi-catalog.json](wwise-mcp/waapi-catalog.json)` row (`mutates: false`, `implemented: true` after verify).

**Tests:** `[tests/test_resolve_waapi_field.py](wwise-mcp/tests/test_resolve_waapi_field.py)` — load bundle in-process or fixture; assert alias → `OutputBus` / `reference`; assert exact canonical match; `dry_run` path; optionally mock client for live validation.

## Server and client packaging

- Update `[server.py](wwise-mcp/server.py)` `instructions`: assume natural-language **field** labels are **not** WAAPI strings; **call `wwise_resolve_waapi_field` first** (with `object_type` from `wwise_get_object`), then call the appropriate setter **once** with the returned `waapi_name`. Keep existing guidance about `get_property_names` as the full enum when exploring.
- If this workspace mirrors MCP tool descriptors under `[mcps/user-wwise-mcp/tools/](mcps/user-wwise-mcp/tools/)`, add JSON for the new tool and refresh any `INSTRUCTIONS.md` there to match `server.py`.

## Non-goals (for this pass)

- Scraping all WObjects pages into aliases automatically.
- Resolving **object paths** by display name (that remains WAQL / `get_object` search).
- Full i18n of display strings.

## Verification

- Unit tests green; `validate_contracts.py` passes.
- Manual smoke: resolve “output bus” for type `Sound` → `OutputBus`, `reference`, then one successful `wwise_set_reference` against a real Bus in a test project (agent or user).

---

## Implementation status (2026-03-29)

All planned deliverables are in place. Summary of **what shipped** and **differences from the original sketch** above.

### Completed tasks


| Area                                                           | Status                                                                                                                                                     |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `display_aliases` in `wobject_waapi_names_2023_1_17.json`      | Done — seeded for **Sound**, **ActorMixer**, and **RandomSequenceContainer** (same reference set as in those types’ docs).                                 |
| Maintainer rules in `reference/README.md`                      | Done — keys, `kind` alignment, SDK column as source of truth.                                                                                              |
| `wwise_resolve_waapi_field` in `tools/resolve_waapi_field.py`  | Done — bundle + exact match; optional live `getPropertyNames` validation.                                                                                  |
| Contract, `tools/__init__.py`, `validate_contracts.py` dry-run | Done — **43** tools in the validator (was 42 + new tool).                                                                                                  |
| `waapi-catalog.json`                                           | Done — entry `wwise-mcp:resolve_waapi_field` (`mutates: false`, `implemented: true`; `verified` left false until someone confirms against a live project). |
| `server.py` instructions                                       | Done — resolve first, then setter; `get_property_names` kept for full exploration.                                                                         |
| `tests/test_resolve_waapi_field.py`                            | Done — alias, exact match, dry_run, errors, plus `**test_bundle_display_aliases_align_with_lists`** (alias rows vs `property_names` / `reference_names`).  |
| `mcps/user-wwise-mcp` mirror                                   | **N/A** — that path was not present in the workspace at implementation time; no JSON mirror added.                                                         |


### Seed aliases (broader than the doc example)

In addition to **Output Bus** → `OutputBus`, the same three types include aliases for **conversion settings** / **conversion** → `Conversion`, and **attenuation** → `Attenuation`, plus compact **outputbus** (no space).

### Behavioral / API adjustments during implementation

1. **Parameter order** — Tool signature uses `**object_type`** first, then `**user_label**`, matching the plan’s emphasis on type-scoped resolution (callers typically pass both as keywords).
2. `**use_live_validation**` — Defaults to `**not dry_run**` (same intent as the plan). When `**use_live_validation=False**` and `**object_type**` is set, resolution uses **only the bundle** and **does not open a Wwise connection** (offline-friendly).
3. `**class_id` in `data`** — `**null**` on the offline-only path above; populated when WAAPI is used (live validation or `**class_id`-only** input). `**class_id`-only** still requires a running Wwise once to map `classId` → type name for bundle lookup.
4. `**source` values** — Only `**alias`** and `**exact_match**` are emitted. `**live_only**` and **Phase 2 fuzzy** matching were **not** implemented (still non-goals / future work).
5. **Live validation failure** — Returns `**success: false`** with `**data**` (including resolved fields) plus `**alternatives**`: substring-style hints on the live list plus `**difflib.get_close_matches**`, not a separate `suggestion` field name.
6. `**client.py**` — No new shared helpers were required; resolution logic lives in `resolve_waapi_field.py` and reuses existing `**connect**`, `**resolve_class_id_for_type**`, `**validate_response**`, etc.

### Verification run

- `python scripts/validate_contracts.py` — pass (all tools, including `wwise_resolve_waapi_field` dry_run).
- `pytest` — full suite green (including new resolver tests).
- Manual smoke against real Wwise remains optional for the user.

