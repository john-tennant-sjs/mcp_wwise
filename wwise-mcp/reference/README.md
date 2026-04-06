# WAAPI name snapshot (offline fallback)

## Available snapshots

| File | Wwise SDK Version | Build | Notes |
|---|---|---|---|
| `wobject_waapi_names_2023_1_17.json` | 2023.1.17 | 8789 | Baseline |
| `wobject_waapi_names_2025_1_3.json` | 2025.1.3 | 9039 | See diff notes below |

Use the file that matches the version of Wwise Authoring you are connected to.

---

Each file's Wwise **type** key (for example the `type` field from `wwise_get_object`) lists:

- `property_names` — scalar/list fields (typically `setProperty` / `get` with `@Property`).
- `reference_names` — fields wired through `setReference`.
- `reference_target_types` (optional) — maps a **reference slot** name to the list of Wwise **object types** allowed as the `setReference` value (e.g. `Effect0` → `["Effect"]` on **Sound**, **Bus**, **AuxBus**, **ActorMixer**, **RandomSequenceContainer** in these snapshots). Use when the WObjects tables omit slot-level detail; see [Audiokinetic Q&A on effects and WAAPI](https://www.audiokinetic.com/qa/6315/how-to-get-and-add-effects-with-waapi). Other Wwise types with an **Effects** chain (e.g. Switch Container, Blend Container) are not in the seed JSON yet—use **`wwise_get_property_names`** live for those.
- `display_aliases` (optional) — maps **normalized** UI/SDK display labels to `{ "waapi_name", "kind" }` for `wwise_resolve_waapi_field`.
- `notes` — high-friction cases and links to the matching `wwiseobject_*.html` page.

The `_meta.changes_from_2023_1_17` array in the 2025 file documents the diff in machine-readable form.

---

## Changes: 2023.1.17 → 2025.1.3

### New properties (all voice and bus objects)

| WAAPI name | Description |
|---|---|
| `AttenuationDistanceScaling` | Per-object attenuation distance scaling |
| `GameAuxSendDSF` | Dual-shelf filter for game-defined auxiliary sends |
| `OutputBusDualshelf` | Dual-shelf filter on the output bus route |

### Renames

| Object | Old name (2023.1.x) | New name (2025.1.x) |
|---|---|---|
| `RandomSequenceContainer` | `GlobalOrPerObject` | `GlobalOrPerObjectScope` |

### Removed object types

| Type | Status |
|---|---|
| `ActorMixer` | Removed from official 2025.1.x WAAPI object reference docs (page returns 404). Omitted from the 2025 snapshot. |

---

## `display_aliases` rules (maintainers)

- Keys are **lowercased, trimmed**, with internal whitespace collapsed to a single space. Run the same normalization in code so arbitrary user casing still matches.
- `kind` must be `reference` or `property` and must match whether `waapi_name` appears in `reference_names` or `property_names` for that type.
- Prefer the **SDK display-name column** (WObjects tables for the target version) as the source of truth; do not add synonyms without a doc citation.

---

Prefer **`wwise_get_property_names`** against a running Wwise when enumerating every valid name; use **`wwise_resolve_waapi_field`** to map UI labels to WAAPI identifiers. This JSON is for offline agents or when WAAPI is unreachable. Expand the snapshot over time from the same doc family for new types.
