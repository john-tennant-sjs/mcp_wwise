# WAAPI name snapshot (offline fallback)

The file `wobject_waapi_names_2023_1_17.json` is aligned with the **Wwise SDK 2023.1.17** public-library documentation:

- Index: https://www.audiokinetic.com/en/public-library/2023.1.17_8789/?source=SDK&id=wobjects_index.html

Each Wwise **type** key (for example the `type` field from `wwise_get_object`) lists:

- `property_names` — scalar/list fields (typically `setProperty` / `get` with `@Property`).
- `reference_names` — fields wired through `setReference`.
- `display_aliases` (optional) — maps **normalized** UI/SDK display labels to `{ "waapi_name", "kind" }` for `wwise_resolve_waapi_field`.
- `notes` — high-friction cases and links to the matching `wwiseobject_*.html` page.

### `display_aliases` rules (maintainers)

- Keys are **lowercased, trimmed**, with internal whitespace collapsed to a single space. Run the same normalization in code so arbitrary user casing still matches.
- `kind` must be `reference` or `property` and must match whether `waapi_name` appears in `reference_names` or `property_names` for that type.
- Prefer the **SDK display-name column** (2023.1.17 WObjects tables) as the source of truth; do not add synonyms without a doc citation.

Prefer **`wwise_get_property_names`** against a running Wwise when enumerating every valid name; use **`wwise_resolve_waapi_field`** to map UI labels to WAAPI identifiers. This JSON is for offline agents or when WAAPI is unreachable. Expand the snapshot over time from the same doc family for new types.
