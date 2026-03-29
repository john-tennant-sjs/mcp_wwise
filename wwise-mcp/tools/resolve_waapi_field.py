"""
wwise_resolve_waapi_field — map UI / display labels to canonical WAAPI names
(bundle display_aliases + exact match; optional live getPropertyNames validation).
"""

from __future__ import annotations

import json
import re
from difflib import get_close_matches
from pathlib import Path

from waapi import CannotConnectToWaapiException

from .client import (
    connect,
    load_contract,
    resolve_class_id_for_type,
    validate_response,
    write_phase2_log,
)

WAAPI_URI = "ak.wwise.core.object.getPropertyNames"
TOOL_NAME = "wwise_resolve_waapi_field"
ROOT_DIR = Path(__file__).parent.parent
BUNDLE_PATH = ROOT_DIR / "reference" / "wobject_waapi_names_2023_1_17.json"

_bundle_cache: dict | None = None


def _load_bundle() -> dict:
    global _bundle_cache
    if _bundle_cache is None:
        _bundle_cache = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
    return _bundle_cache


def _normalize_label(text: str) -> str:
    s = (text or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def _type_entry(bundle: dict, object_type: str) -> dict | None:
    key = object_type.strip()
    entry = bundle.get(key)
    if isinstance(entry, dict) and ("property_names" in entry or "reference_names" in entry):
        return entry
    return None


def _resolve_type_name_for_class_id(client, class_id: int) -> str | None:
    result = client.call("ak.wwise.core.object.getTypes", {})
    if not result or "return" not in result:
        return None
    for entry in result["return"]:
        cid = entry.get("classId")
        if cid is not None and int(cid) == int(class_id):
            return entry.get("name")
    return None


def _suggest_names(live: list[str], waapi_name: str, normalized_user: str, limit: int = 12) -> list[str]:
    compact_user = normalized_user.replace(" ", "")
    hinted = [
        n
        for n in live
        if (compact_user and compact_user in n.lower())
        or (_normalize_label(n).replace(" ", "") == compact_user)
    ]
    if len(hinted) >= limit:
        return sorted(hinted)[:limit]
    close = get_close_matches(waapi_name, live, n=limit, cutoff=0.45)
    merged: list[str] = []
    seen: set[str] = set()
    for n in hinted + close:
        if n not in seen:
            seen.add(n)
            merged.append(n)
        if len(merged) >= limit:
            break
    return merged


def normalize_label(text: str) -> str:
    """Normalize user input; same rules as reference/README (tests import this)."""
    return _normalize_label(text)


def _match_in_entry(entry: dict, user_label: str) -> tuple[dict | None, str | None]:
    """Return ({waapi_name, kind, source}, None) or (None, error_message)."""
    norm = _normalize_label(user_label)
    props = {p: "property" for p in entry.get("property_names") or []}
    refs = {r: "reference" for r in entry.get("reference_names") or []}
    aliases = entry.get("display_aliases") or {}

    if norm in aliases:
        row = aliases[norm]
        if not isinstance(row, dict):
            return None, "Invalid display_aliases row in bundle."
        candidate_name = row.get("waapi_name")
        kind = row.get("kind")
        if candidate_name not in props and candidate_name not in refs:
            return None, f"Bundle alias for {norm!r} points to missing name {candidate_name!r}."
        expected = "property" if candidate_name in props else "reference"
        if kind not in ("property", "reference"):
            return None, f"Invalid kind in display_aliases for {norm!r}."
        if kind != expected:
            return (
                None,
                f"display_aliases kind {kind!r} does not match bundle lists "
                f"for {candidate_name!r} (expected {expected!r}).",
            )
        return {"waapi_name": candidate_name, "kind": kind, "source": "alias"}, None

    prop_match = [p for p in props if _normalize_label(p) == norm]
    ref_match = [r for r in refs if _normalize_label(r) == norm]
    if len(prop_match) > 1 or len(ref_match) > 1:
        return None, "Ambiguous canonical match (duplicate normalized names)."
    if prop_match and ref_match and prop_match[0] != ref_match[0]:
        return None, "Ambiguous: label matches both a property and a reference."
    if prop_match:
        return {"waapi_name": prop_match[0], "kind": "property", "source": "exact_match"}, None
    if ref_match:
        return {"waapi_name": ref_match[0], "kind": "reference", "source": "exact_match"}, None
    return (
        None,
        f"No alias or exact match for label {user_label!r}. Use wwise_get_property_names for the full list.",
    )


def wwise_resolve_waapi_field(
    object_type: str | None = None,
    user_label: str | None = None,
    class_id: int | None = None,
    use_live_validation: bool | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Resolve a user-facing field label to a WAAPI property or reference name.

    Args:
        object_type: Wwise type from wwise_get_object (e.g. \"Sound\").
        user_label: Display label (e.g. \"Output Bus\").
        class_id: Optional; if object_type is omitted, type name is resolved via getTypes (requires WAAPI).
        use_live_validation: When True, require the name in live getPropertyNames. When None,
            defaults to (not dry_run).
        dry_run: If True, return the contract mock without WAAPI.
    """
    checks = {"pre_check": False, "execute": False, "post_check": False, "schema_match": False}

    if use_live_validation is None:
        use_live_validation = not dry_run

    if not user_label or not str(user_label).strip():
        err = "user_label is required."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}

    if dry_run and (not object_type or not object_type.strip()) and class_id is None:
        err = "object_type is required when dry_run is True."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}

    if not dry_run and (not object_type or not object_type.strip()) and class_id is None:
        err = "Provide object_type and/or class_id."
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}

    checks["pre_check"] = True

    if dry_run:
        contract = load_contract(TOOL_NAME)
        mock = dict(contract["mock_response"])
        ok, verr = validate_response(TOOL_NAME, mock)
        checks.update({"execute": True, "post_check": True, "schema_match": ok})
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, ok, verr)
        return mock

    bundle = _load_bundle()
    otype = (object_type or "").strip()
    resolved_type = otype
    data: dict | None = None

    try:
        if resolved_type and not use_live_validation:
            entry = _type_entry(bundle, resolved_type)
            if entry is None:
                err = f"No bundle entry for type {resolved_type!r} (offline reference incomplete)."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            matched, merr = _match_in_entry(entry, user_label)
            if merr or not matched:
                err = f"{merr} (type {resolved_type!r})" if merr else "Match failed."
                write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                return {"success": False, "data": None, "error": err}
            kind = matched["kind"]
            data = {
                "waapi_name": matched["waapi_name"],
                "kind": kind,
                "suggested_tool": "wwise_set_reference" if kind == "reference" else "wwise_set_property",
                "source": matched["source"],
                "object_type": resolved_type,
                "class_id": None,
            }
            checks["execute"] = True
            checks["post_check"] = True
        else:
            with connect() as client:
                cid = class_id
                if cid is not None and not resolved_type:
                    resolved_type = _resolve_type_name_for_class_id(client, cid) or ""
                    if not resolved_type:
                        err = f"Unknown class_id {cid!r} (no matching type from getTypes)."
                        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                        return {"success": False, "data": None, "error": err}

                if cid is None and resolved_type:
                    cid = resolve_class_id_for_type(client, resolved_type)
                    if cid is None:
                        err = f"Unknown Wwise type {resolved_type!r} (no matching classId from getTypes)."
                        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                        return {"success": False, "data": None, "error": err}

                if cid is None:
                    err = "Could not resolve class_id (provide object_type or class_id)."
                    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                    return {"success": False, "data": None, "error": err}

                entry = _type_entry(bundle, resolved_type)
                if entry is None:
                    err = f"No bundle entry for type {resolved_type!r} (offline reference incomplete)."
                    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                    return {"success": False, "data": None, "error": err}

                matched, merr = _match_in_entry(entry, user_label)
                if merr or not matched:
                    err = f"{merr} (type {resolved_type!r})" if merr else "Match failed."
                    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                    return {"success": False, "data": None, "error": err}

                kind = matched["kind"]
                candidate_name = matched["waapi_name"]
                norm = _normalize_label(user_label)
                data = {
                    "waapi_name": candidate_name,
                    "kind": kind,
                    "suggested_tool": "wwise_set_reference" if kind == "reference" else "wwise_set_property",
                    "source": matched["source"],
                    "object_type": resolved_type,
                    "class_id": cid,
                }

                if use_live_validation:
                    result = client.call(WAAPI_URI, {"classId": cid})
                    if result is None:
                        err = "getPropertyNames returned None."
                        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                        return {"success": False, "data": None, "error": err}
                    live = result.get("return")
                    if not isinstance(live, list):
                        err = "getPropertyNames response missing return list."
                        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                        return {"success": False, "data": None, "error": err}
                    live_set = set(live)
                    if candidate_name not in live_set:
                        alts = _suggest_names(live, candidate_name, norm)
                        err = (
                            f"Live Wwise getPropertyNames does not include {candidate_name!r} for type "
                            f"{resolved_type!r} (bundle or version mismatch). "
                            f"Try: {alts[:8]!r}"
                        )
                        data["alternatives"] = alts
                        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
                        return {"success": False, "data": data, "error": err}

                checks["execute"] = True
                checks["post_check"] = True

    except CannotConnectToWaapiException:
        err = (
            "Cannot connect to Wwise for live validation. "
            "Set use_live_validation=false to resolve from the offline bundle only, or start Wwise with WAAPI."
            if use_live_validation
            else (
                "Cannot connect to Wwise. Provide object_type and set use_live_validation=false for offline "
                "bundle-only resolution, or start Wwise with WAAPI."
            )
        )
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, err)
        return {"success": False, "data": None, "error": err}
    except Exception as e:
        write_phase2_log(TOOL_NAME, WAAPI_URI, checks, False, str(e))
        return {"success": False, "data": None, "error": str(e)}

    assert data is not None
    response = {"success": True, "data": data, "error": None}
    ok, verr = validate_response(TOOL_NAME, response)
    checks["schema_match"] = ok
    passed = all(checks.values())
    write_phase2_log(TOOL_NAME, WAAPI_URI, checks, passed, verr if not ok else None)
    if not ok:
        return {**response, "success": False, "error": verr or "schema_match failed"}
    return response


def register(mcp) -> None:
    mcp.tool()(wwise_resolve_waapi_field)
