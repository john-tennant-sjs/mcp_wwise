# MCP-Wwise Autonomous Test Suite — Part 2

This document is the continuation of `mcp-wwise-test-suite.md` (Part 1).

It targets WAAPI-related capabilities that Part 1 did not exercise: schema inspection, notes, undo groups, paste-properties, declarative object authoring, attenuation curves, Switch Container assignments, UI commands, log inspection, audio import, and object deletion.

**Tool names** in this file (for example `wwise_get_schema`, `wwise_paste_properties`) follow the reference **mcp-wwise** server naming. Other Wwise MCP implementations should map each mention to the equivalent tool on that server.

**Excluded from this suite (reserved for dedicated suites):**
- Profiler tools (e.g. `wwise_profiler_*` or equivalents)
- SoundBank tools (generate bank, bank inclusions, etc.)
- Transport tools (create transport, play/stop, etc.)

## Portability

- **Wwise paths** such as `\Actor-Mixer Hierarchy\...` are **Project Explorer paths inside Wwise**, not filesystem paths. They are the same on any OS.
- **No drive letters or OS-specific filesystem paths** are required by this suite. If a prompt needs a `.wav` file, discovery is described in generic terms (project folder, environment, user-supplied path).
- **Default Work Unit** names and parent folders (`Default Work Unit`, `Attenuations`, `Switch Groups`, etc.) can differ between projects and Wwise versions. The agent should **discover** the correct parent path by querying the hierarchy before creating objects.
- **`self-report.md`**: append the Part 2 section to the same report file Part 1 used, in whatever location the MCP host allows (workspace root, user-specified path, etc.).

## Prerequisites

Complete **Part 1** (`mcp-wwise-test-suite.md`) first so the test hierarchy exists. Part 2 assumes at least the following **Wwise** state (names follow Part 1 conventions; if your Part 1 run used different work-unit layout, adapt paths consistently):

- `\Actor-Mixer Hierarchy\MCP_Test` (Work Unit) with folders `Source`, `Variants`, `Templates`, `Copies`
- Three footstep Sounds under `\Actor-Mixer Hierarchy\MCP_Test\Source` with distinct Pitch values from Part 1 prompt 4
- Stone and Wood **Random** (or Random Sequence) container families and a Metal family as created in Part 1 prompts 10–15, including duplicated Stone and retargeted events where applicable
- A test bus named `MCP_Test_Bus` reachable from the Master-Mixer Hierarchy (exact parent path may vary; discover by query)
- `\Events\MCP_Test_Events` with Events that reference the footstep Sounds and, if Part 1 was completed fully, Stone / Metal–related Events as created there

**Paste source for Prompt 4:** Part 1 does not require a dedicated template **Sound** by name. Before Prompt 4, if no suitable template Sound exists under `\Actor-Mixer Hierarchy\MCP_Test\Templates`, create a Sound there (for example `MCP_PasteTemplate`) with **Volume = -6** and **Pitch = 25** and use it as the paste source. Do not rely on a fixed machine path for media.

**Optional objects** used only by specific prompts: a copy of `Play_Footstep_01` under `Copies`, `Stone_Copy`, and Events such as `Play_Stone_Copy` / `Play_Metal_Copy` — if missing, either skip the prompts that require them or create minimal stand-ins and document that in `self-report.md`.

## Mission For The AI Agent

Work through all 11 prompts in order. For every prompt:

- Execute the authoring or inspection task.
- Perform at least one self-validation step using read-only inspection tools after every mutation.
- Record what you attempted, what succeeded, what failed, and what you validated.
- If a prompt fails, do not stop unless the project state is too broken to continue safely.
- If a prompt partially succeeds, document the exact partial state and continue.

At the end of the full run, append a `## Part 2 Run` section to the existing `self-report.md` (same file and location as Part 1), following the same format as the Part 1 report.

## Rules Of Engagement

- Never guess WAAPI field names. Use your server’s property/schema resolution tools (for example `wwise_get_property_names`, `wwise_get_schema`, `wwise_resolve_waapi_field`, or equivalents) before mutating anything unfamiliar.
- Wrap multi-step destructive operations in undo groups where instructed.
- Validate every mutation by re-querying the affected object.
- Log every tool call outcome — success, failure, partial — as you go.

---

## Prompt 1: Schema And Property List Inspection

```text
Using wwise_get_schema, retrieve the type definition for RandomSequenceContainer and report its class ID. Then pick the "Mode" property on the Stone Random Container and use wwise_get_property_and_object_lists to retrieve its valid enumerated values. Report the class ID, the canonical property name you used, and the full list of valid Mode values you got back.
```

### Goal

Verify that schema introspection and property-list enumeration tools work, and that the agent can use them to understand valid property values before authoring.

### Target tools (reference names)

- Schema: `wwise_get_schema` or equivalent
- Property lists: `wwise_get_property_and_object_lists` or equivalent

### Expected Coverage

- Schema type lookup by object type string
- Enumeration of valid values for a property on a live object
- Reporting canonical type metadata

### Minimum Self-Validation

After retrieving the schema, confirm that:
- the returned `class_id` is a non-zero integer
- the Mode property value list contains at least two entries (e.g. Random, Sequence)
- the values match what the Wwise UI would show for a Random/Sequence Container's mode selector

---

## Prompt 2: Annotate The Test Hierarchy With Notes

```text
Add a short descriptive note to each of the following objects so future editors know what they are for:
- \Actor-Mixer Hierarchy\MCP_Test (the top-level test work unit)
- \Actor-Mixer Hierarchy\MCP_Test_Stone\Stone (the original Stone container)
- \Actor-Mixer Hierarchy\MCP_Test_Wood\Wood (the original Wood container)
- \Actor-Mixer Hierarchy\MCP_Test_Metal\Metal (the original Metal container)
- One object under \Actor-Mixer Hierarchy\MCP_Test\Templates that is clearly part of the test data (for example the `_template` Random Container from Part 1, or a template Sound you created for paste tests)

Use notes that clearly identify the object as part of the MCP automated test suite. Then read the notes back from at least two of those objects to confirm they were saved.
```

### Goal

Verify that `wwise_set_notes` writes metadata correctly and that the notes are readable back via `wwise_get_object`.

### Target tools (reference names)

- `wwise_set_notes`, `wwise_get_object` (validation; request `notes` in return properties)

### Expected Coverage

- Writing notes to multiple object types (WorkUnit, RandomSequenceContainer, Sound)
- Confirming notes survive a read-back query

### Minimum Self-Validation

Re-query at least two of the annotated objects requesting the notes field in the object query (for example `notes` in `return_props` or your tool’s equivalent) and confirm:
- the notes field is non-empty
- the content matches what was written

---

## Prompt 3: Undo Group Workflow

```text
Perform the following sequence to test undo group behavior:

Step A — Begin an undo group labeled "TestUndo_Cancel". Inside it, set the Pitch on Play_Footstep_01 to 999 cents (a deliberately wrong value). Then cancel the undo group without committing it. Read back the Pitch on Play_Footstep_01 to confirm the change was rolled back.

Step B — Begin a second undo group labeled "TestUndo_Commit". Inside it, set the Volume on Play_Footstep_02 to -12 dB. End the group normally. Read back the Volume on Play_Footstep_02 to confirm the change persisted.

Report the Pitch value after Step A and the Volume value after Step B.
```

### Goal

Verify that undo groups work as a transactional wrapper — cancelled groups roll back, ended groups commit.

### Target tools (reference names)

- Undo: `wwise_undo_begin_group`, `wwise_undo_cancel_group`, `wwise_undo_end_group` (or equivalents)
- Mutation / validation: `wwise_set_property`, `wwise_get_object` (or equivalents)

### Expected Coverage

- Undo group begin, cancel, and end lifecycle
- Confirming rollback on cancel
- Confirming commit on end

### Minimum Self-Validation

After Step A: confirm Pitch on Play_Footstep_01 is **not** 999 (should have reverted to -50).
After Step B: confirm Volume on Play_Footstep_02 is **-12**.

### Note For The Agent

If undo cancel does not roll back the change automatically (Wwise may require an explicit undo after cancel), document the exact observed behavior and what actually happened to the property value — do not assume the rollback occurred without reading it back.

---

## Prompt 4: Paste Properties From A Template

```text
Ensure a template Sound exists under \Actor-Mixer Hierarchy\MCP_Test\Templates with Volume=-6 and Pitch=25 (create one named MCP_PasteTemplate if needed). Use the paste-properties tool (wwise_paste_properties or your server’s equivalent) to paste from that template onto all three Stone child Sounds (Stone_01, Stone_02, Stone_03 under the Stone Random / Random Sequence container created in Part 1 — typically under \Actor-Mixer Hierarchy\MCP_Test_Stone\Stone or under Variants before Part 1’s work-unit move; resolve the live path by query). After pasting, read back Volume and Pitch on each Stone Sound and confirm they match the template. Report exactly which properties were included in the paste operation.
```

### Goal

Test the paste-properties tool as a bulk template application mechanism, which is the core of the `create_random_containers_from_selection_template.py` workflow.

### Target tools (reference names)

- `wwise_paste_properties`, `wwise_get_object` (request Volume and Pitch in returned properties)

### Expected Coverage

- Applying a source object's properties to multiple targets
- Confirming property values match the source after paste
- Understanding which properties the tool includes or excludes

### Minimum Self-Validation

After pasting, re-query all three Stone Sounds for Volume and Pitch. Confirm:
- Volume matches the template Sound’s value (-6)
- Pitch matches the template Sound’s value (25)
- All three Sounds show the same values

If paste_properties requires specifying an explicit property list, use `wwise_get_property_names` to enumerate the Sound type properties first and pick Volume and Pitch.

---

## Prompt 5: Declarative Object Authoring With set_object

```text
Use wwise_set_object to create a new Sound named "Metal_Template" under \Actor-Mixer Hierarchy\MCP_Test\Templates in a single call that specifies Volume=-6, Pitch=0 inline in the object definition. Do not use wwise_create_object followed by wwise_set_property — the goal is to author the object declaratively in one call.

After creation, read back the new Sound and confirm its Volume and Pitch values match what was specified.
```

### Goal

Verify that the declarative `wwise_set_object` pathway works and produces the correct result, offering an alternative to the create-then-set pattern used throughout Part 1.

### Target tools (reference names)

- `wwise_set_object`, optional `wwise_get_schema`, `wwise_get_object` for validation

### Expected Coverage

- Declarative object authoring in a single call
- Inline property specification
- Confirming the resulting object matches the definition

### Minimum Self-Validation

Re-query `\Actor-Mixer Hierarchy\MCP_Test\Templates\Metal_Template` and confirm:
- type is Sound
- Volume = -6
- Pitch = 0

---

## Prompt 6: Attenuation Curve Read And Write

```text
Do the following attenuation curve workflow:

1. Create an Attenuation ShareSet named "MCP_Test_Attenuation" under \Attenuations\Default Work Unit.
2. Use wwise_get_attenuation_curve to read the default Volume attenuation curve from the new ShareSet. Report the curve type used and the default control points.
3. Use wwise_set_attenuation_curve to replace the Volume curve with a simple two-point linear falloff: full volume (0 dB) at distance 0 and silence (-96 dB) at distance 100.
4. Read the curve back again and confirm the new control points are in place.
```

### Goal

Test the full attenuation curve read/write cycle, which is one of the more structurally distinct parts of the WAAPI surface.

### Target tools (reference names)

- `wwise_create_object`, `wwise_get_attenuation_curve`, `wwise_set_attenuation_curve` (re-read curve after write)

### Expected Coverage

- Attenuation ShareSet creation
- Reading curve control points
- Writing a custom curve shape
- Validating the written curve

### Minimum Self-Validation

After writing the new curve, re-read it and confirm:
- there are exactly 2 control points (or the minimum required by Wwise)
- the first point is at x=0, y=0 (or the equivalent full-volume representation)
- the second point is at x=100, y=-96 (or the nearest valid representation)

### Note For The Agent

If the Attenuations hierarchy path is different in this project, discover the correct path by querying `\Attenuations` or `\Attenuations\Default Work Unit` before attempting creation. Report the actual path used.

---

## Prompt 7: Switch Container Assignments

```text
Do the following Switch Container workflow:

1. Create a Switch Group named "MCP_SurfaceType" under \Game Parameters\Default Work Unit (or the correct Switch Groups path). Add two Switch States to it: "Stone" and "Wood".
2. Create a Switch Container named "Surface_Footstep" under \Actor-Mixer Hierarchy\MCP_Test\Variants. Set it to use the MCP_SurfaceType Switch Group.
3. Add the Stone Random Container and Wood Random Container as children of Surface_Footstep by moving them under it.
4. Use wwise_switch_container_add_assignment to assign the Stone Random Container child to the "Stone" state and the Wood Random Container child to the "Wood" state.
5. Use wwise_switch_container_get_assignments to read back all assignments and confirm each child is mapped to the correct state.
6. Remove the Wood assignment using wwise_switch_container_remove_assignment, then re-read assignments to confirm it is gone.

Report all assignment states at steps 5 and 6.
```

### Goal

Test the full Switch Container assignment lifecycle: add, read, and remove. This mirrors the kind of surface-type routing used in game audio projects.

### Target tools (reference names)

- `wwise_create_object`, `wwise_move_object`, `wwise_set_reference`, `wwise_switch_container_add_assignment`, `wwise_switch_container_get_assignments`, `wwise_switch_container_remove_assignment`, `wwise_get_object`

### Expected Coverage

- Switch Group and State creation
- Switch Container creation and Switch Group wiring
- Adding child-to-state assignments
- Reading and validating assignments
- Removing an assignment and confirming removal

### Minimum Self-Validation

After step 5: confirm assignments list contains both Stone→Stone and Wood→Wood.
After step 6: confirm the Wood assignment no longer appears in the assignments list.

### Note For The Agent

Switch Group paths vary by project. Query `\Switch Groups` or `\Switch Groups\Default Work Unit` first to confirm the correct parent path. If the move in step 3 disrupts the Stone/Wood containers' existing routing to MCP_Test_Bus, restore that routing afterward.

---

## Prompt 8: UI Commands And Foreground

```text
Do the following UI operations:

1. Use wwise_ui_bring_to_foreground to bring the Wwise Authoring window to the foreground.
2. Use wwise_ui_commands_execute to execute the "FindInProjectExplorerSyncGroup1" command (or an equivalent navigation command) to select and reveal \Actor-Mixer Hierarchy\MCP_Test in the Project Explorer.
3. After the UI command, use wwise_ui_get_selected_objects to read back the currently selected objects and confirm that MCP_Test (or a descendant) is selected.

Report the command ID you used, whether bring-to-foreground succeeded, and what was selected after the command.
```

### Goal

Verify that the UI automation tools work for basic window management and Project Explorer navigation.

### Target tools (reference names)

- `wwise_ui_bring_to_foreground`, `wwise_ui_commands_execute`, `wwise_ui_get_selected_objects`

### Expected Coverage

- Window focus control
- Executing a named UI command with an object argument
- Reading back selection state as a post-command validation

### Minimum Self-Validation

After the UI command, re-query selected objects. Confirm:
- at least one object is selected
- the selected object is within the MCP_Test hierarchy

### Note For The Agent

Use `wwise_get_schema` or check the WAAPI documentation reference to discover valid command IDs if `FindInProjectExplorerSyncGroup1` is not found. Alternative candidates include `FindInProjectExplorer` or similar. Report whatever command ID was actually used and whether it accepted an object argument.

---

## Prompt 9: Log Inspection

```text
Retrieve the Wwise WAAPI log using wwise_log_get. Report:
- The total number of log entries returned
- How many entries are at each severity level (Info, Warning, Error)
- Any entries that mention objects from the MCP_Test hierarchy by name or path
- Any entries that look like failures, WAAPI errors, or unexpected behavior

If the log is large, focus on the most recent entries and any non-Info level entries.
```

### Goal

Verify that the log retrieval tool works and can surface errors or warnings that silent tool-call success statuses might have missed.

### Target tools (reference names)

- `wwise_log_get` or equivalent

### Expected Coverage

- Log retrieval
- Severity-level enumeration
- Surfacing project-relevant entries
- Using the log as a passive validation mechanism

### Minimum Self-Validation

Confirm that:
- the tool returns a response (even if the log is empty)
- the structure of the log entries is reported (fields present per entry)
- any Error or Warning entries are explicitly called out, not silently ignored

---

## Prompt 10: Import Audio

```text
Locate an available .wav file for import using only portable discovery — in this order:
1. Any .wav file already under the current Wwise project’s Originals (or Media) folder on disk, if your MCP host can read the project directory
2. A path supplied by the user or by an environment variable (for example WWISE_TEST_WAV) if the user configured one for automated runs
3. Sample or demo content shipped with the Wwise installation (search under the Wwise install root only — do not assume a specific drive letter or folder name; common layouts vary by version and platform)

If a .wav file is found, use the import-audio tool (wwise_import_audio or equivalent) to import it as a new Sound under \Actor-Mixer Hierarchy\MCP_Test\Source named "Imported_Test_Sound". After import, read back the Sound and report its Wwise path, type, and whether an audio source is attached.

If no suitable file can be found, document every search attempt (locations checked) and skip to the next prompt. Do not invent a filesystem path.
```

### Goal

Verify that the audio import pathway works end-to-end: file discovery, WAAPI import call, and confirmation that a Sound object with an audio source was created.

### Target tools (reference names)

- `wwise_import_audio`, `wwise_get_object`

### Expected Coverage

- Audio file discovery (filesystem search)
- Import call with target parent and object name
- Confirming resulting Sound object has an attached source

### Minimum Self-Validation

If import succeeded: re-query `\Actor-Mixer Hierarchy\MCP_Test\Source\Imported_Test_Sound` and confirm:
- type is Sound
- an audio source reference is present (query with `audioSource` or equivalent in return_props if supported)

If import failed: report the exact error message returned and whether it was a file-not-found, permission, or WAAPI-level error.

### Note For The Agent

This prompt is explicitly contingent on a suitable file being present. Do not fabricate a path. If no file is found after reasonable, portable discovery, skip and document.

---

## Prompt 11: Selective Cleanup With Delete

```text
Clean up temporary objects that are no longer needed after Part 2 testing, but only if they exist (resolve paths by query first):

1. \Actor-Mixer Hierarchy\MCP_Test\Copies\Play_Footstep_01_Copy (or equivalent copy Sound under Copies, if present)
2. The duplicated Stone hierarchy from Part 1 (often named Stone_Copy under the Stone work unit — delete the container and its children if present)
3. Any duplicated Stone-related Event such as \Events\MCP_Test_Events\Play_Stone_Copy (if present)

For each deletion:
- Call the delete-object tool (wwise_delete_object or equivalent)
- Immediately re-query the deleted Wwise path
- Confirm the re-query returns empty or error (not a valid object)

After deletions, re-query \Actor-Mixer Hierarchy\MCP_Test\Copies and the parent of the original Stone container to confirm only expected survivors remain.

Do not delete anything not listed above. If an object is missing, note it in the report and continue.
```

### Goal

Verify that `wwise_delete_object` removes objects and that the deletions are confirmed by failed re-queries rather than assumed.

### Target tools (reference names)

- `wwise_delete_object`, `wwise_get_object` (post-deletion validation — expect empty or error)

### Expected Coverage

- Deleting individual objects and entire subtrees
- Confirming deletion via a negative query result
- Scope control (delete only what was asked, nothing else)

### Minimum Self-Validation

For each deleted path:
- Confirm the re-query returns an error or empty data (not a valid object)

For the surviving parents:
- Confirm `\Actor-Mixer Hierarchy\MCP_Test\Copies` is empty or contains only expected objects
- Confirm `\Actor-Mixer Hierarchy\MCP_Test_Stone` still contains the original `Stone` container with its children intact

---

## Suggested Evaluation Criteria

When reviewing a Part 2 run, pay attention to (using your server’s equivalent tool names where applicable):

- Did the agent use schema and property-list tools to discover structure before authoring, or did it guess?
- Did undo group cancel actually roll back the change, and did the agent verify rather than assume?
- Did `wwise_paste_properties` copy the expected fields, and did the agent report which fields were included?
- Did `wwise_set_object` produce the correct property values in a single call?
- Were attenuation curve control points read and written in the correct format?
- Did Switch Container assignments survive a get-assignments read-back?
- Did the agent surface any log warnings that might indicate silent failures in Part 1?
- Did the agent confirm deletions via negative queries rather than trusting the delete response alone?
- Did the agent respect the "do not delete anything not listed" constraint?

## Notes For Future Expansion

- Add a dedicated profiler suite once real game content (looping events, voices) is available to capture.
- Add a transport suite: create a transport, play an event, poll state, destroy transport.
- Add a SoundBank suite: add MCP_Test content to a bank, set inclusions, generate, verify.
- Add a negative-test suite: invalid property names, missing Wwise object paths, type mismatches, AuxBus-as-OutputBus.
- Add a suite for States and Game Parameters: create a State Group, add States, assign RTPC curves, verify.
- Add a suite for RTPC: create a Game Parameter, attach it to a property via set_object or set_reference, verify curve data.
