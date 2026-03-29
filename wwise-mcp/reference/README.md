# WAAPI name snapshot (offline fallback)

The file `wobject_waapi_names_2023_1_17.json` is aligned with the **Wwise SDK 2023.1.17** public-library documentation:

- Index: https://www.audiokinetic.com/en/public-library/2023.1.17_8789/?source=SDK&id=wobjects_index.html

Each Wwise **type** key (for example the `type` field from `wwise_get_object`) lists:

- `property_names` — scalar/list fields (typically `setProperty` / `get` with `@Property`).
- `reference_names` — fields wired through `setReference`.
- `notes` — high-friction cases and links to the matching `wwiseobject_*.html` page.

Prefer **`wwise_get_property_names`** against a running Wwise when available; this JSON is for offline agents or when WAAPI is unreachable. Expand the snapshot over time from the same doc family for new types.
