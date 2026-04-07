---
name: Harden Wwise Guardrails
overview: Implement layered guardrails for wwise_set_object and related tools so agents can’t submit malformed WAAPI payloads, while improving diagnostics and providing safer high-level APIs for complex operations like RTPC creation.
todos:
  - id: add-input-validation
    content: Implement reusable validate_input in client utilities and integrate into setter tools first.
    status: completed
  - id: tighten-set-object-contract
    content: Harden wwise_set_object input schema and regenerate/sync contract definitions.
    status: completed
  - id: set-object-preflight
    content: Add semantic preflight checks for @-prefixed WAAPI fields and curve-key validation.
    status: completed
  - id: strict-autofix-mode
    content: Implement strict/autofix options with normalization trace metadata.
    status: completed
  - id: add-rtpc-helper-tool
    content: Create and register wwise_add_rtpc_binding tool + contract + tests.
    status: completed
  - id: improve-error-diagnostics
    content: Enhance set_object error responses with likely-cause and suggestion payloads.
    status: completed
  - id: expand-tests
    content: Add/adjust tests for schema rejection, autofix behavior, diagnostics, and regressions.
    status: completed
isProject: false
---

# Harden MCP-Wwise Payload Guardrails

## Scope
Implement items 1, 2, 3, 4, 5, and 7 from the proposed guardrail list, explicitly excluding XML->WAAPI translation helpers.

## Implementation Plan

- Add reusable **input-schema enforcement** in [T:/MCP_Wwise_Project/wwise-mcp/tools/client.py](T:/MCP_Wwise_Project/wwise-mcp/tools/client.py):
  - Introduce `validate_input(tool_name, args) -> (ok, err)` using each contract’s `input_schema`.
  - Keep existing `validate_response` behavior unchanged.
  - Standardize error text so tools return clear, actionable failures before WAAPI calls.

- Wire input validation into tool entry points (start with high-risk setters, then all tools):
  - First pass: [T:/MCP_Wwise_Project/wwise-mcp/tools/set_object.py](T:/MCP_Wwise_Project/wwise-mcp/tools/set_object.py), [T:/MCP_Wwise_Project/wwise-mcp/tools/set_reference.py](T:/MCP_Wwise_Project/wwise-mcp/tools/set_reference.py), [T:/MCP_Wwise_Project/wwise-mcp/tools/set_property.py](T:/MCP_Wwise_Project/wwise-mcp/tools/set_property.py).
  - Second pass: all remaining tool modules under [T:/MCP_Wwise_Project/wwise-mcp/tools](T:/MCP_Wwise_Project/wwise-mcp/tools).

- Tighten `wwise_set_object` contract schema in [T:/MCP_Wwise_Project/wwise-mcp/contracts/wwise_set_object.json](T:/MCP_Wwise_Project/wwise-mcp/contracts/wwise_set_object.json) (and source generator [T:/MCP_Wwise_Project/wwise-mcp/scripts/write_contracts.py](T:/MCP_Wwise_Project/wwise-mcp/scripts/write_contracts.py)):
  - Enforce `additionalProperties: false` where appropriate.
  - Explicitly allow valid non-`@` structural keys (`object`, `name`, `type`, `notes`, `children`, `listMode`, etc.).
  - Use `patternProperties` for dynamic WAAPI fields `^@[:_a-zA-Z0-9]+$`.
  - Ensure malformed keys (e.g., `PropertyName`, `Curve` when `@...` expected) fail early.

- Add `set_object` semantic preflight in [T:/MCP_Wwise_Project/wwise-mcp/tools/set_object.py](T:/MCP_Wwise_Project/wwise-mcp/tools/set_object.py):
  - Validate each item’s target object exists and type can be resolved.
  - Validate payload keys against WAAPI rules and live metadata where feasible (`getPropertyNames`, `getSchema` fallback/bundle fallback).
  - Add targeted checks for common mistakes: missing `@` on settable fields, wrong curve key casing (`points`), and suspicious unknown keys.
  - Return structured diagnostics including probable fix + nearest valid alternatives.

- Add optional normalization/autofix behavior for obvious mistakes in [T:/MCP_Wwise_Project/wwise-mcp/tools/set_object.py](T:/MCP_Wwise_Project/wwise-mcp/tools/set_object.py):
  - Add `strict` (default `true`) and `autofix` (default `false`) arguments.
  - If `autofix=true`, apply safe rewrites only (e.g., `PropertyName -> @PropertyName`, `ControlInput -> @ControlInput`, `Curve -> @Curve`, `Points -> points`).
  - Include `normalizations_applied` in response metadata for traceability.

- Add high-level typed tool for RTPC list operations:
  - New tool module [T:/MCP_Wwise_Project/wwise-mcp/tools/add_rtpc_binding.py](T:/MCP_Wwise_Project/wwise-mcp/tools/add_rtpc_binding.py) that composes a correct `object.set` payload internally.
  - Register in [T:/MCP_Wwise_Project/wwise-mcp/tools/__init__.py](T:/MCP_Wwise_Project/wwise-mcp/tools/__init__.py).
  - Add contract [T:/MCP_Wwise_Project/wwise-mcp/contracts/wwise_add_rtpc_binding.json](T:/MCP_Wwise_Project/wwise-mcp/contracts/wwise_add_rtpc_binding.json) and generation support in [T:/MCP_Wwise_Project/wwise-mcp/scripts/write_contracts.py](T:/MCP_Wwise_Project/wwise-mcp/scripts/write_contracts.py).
  - Document usage and when to prefer it over raw `wwise_set_object` in [T:/MCP_Wwise_Project/wwise-mcp/server.py](T:/MCP_Wwise_Project/wwise-mcp/server.py) instructions text.

- Improve runtime error guidance in `wwise_set_object`:
  - On WAAPI `None` or schema mismatch, attach likely causes and “try this exact shape” suggestions.
  - Mirror the quality of diagnostics already present in `wwise_set_reference`.

## Testing Plan

- Extend and update tests:
  - [T:/MCP_Wwise_Project/wwise-mcp/tests/test_set_object.py](T:/MCP_Wwise_Project/wwise-mcp/tests/test_set_object.py):
    - Reject missing `objects` wrapper / missing `object`.
    - Reject malformed non-`@` keys where `@` is required.
    - Validate curve key casing behavior and autofix behavior.
    - Validate diagnostic contents (suggested key names).
  - Add tests for input schema validator (new or existing shared test file).
  - Add tests for new RTPC helper tool (new `test_add_rtpc_binding.py`).

- Regression checks:
  - Confirm existing tests for `set_reference` and `set_property` still pass.
  - Run full test suite under [T:/MCP_Wwise_Project/wwise-mcp/tests](T:/MCP_Wwise_Project/wwise-mcp/tests).

## Acceptance Criteria

- Invalid payloads that previously reached WAAPI now fail fast with actionable errors.
- Common RTPC payload mistakes are either auto-corrected (`autofix=true`) or clearly diagnosed (`autofix=false`).
- New high-level RTPC tool can create a valid RTPC with curve on an EffectSlot in one call.
- Existing tool behavior remains backward-compatible unless `strict/autofix` flags are explicitly used.
