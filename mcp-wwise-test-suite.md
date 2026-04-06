# MCP-Wwise Autonomous Test Suite

This document is a progressive overnight test runbook for a **Wwise MCP server** (any implementation that exposes WAAPI to an MCP host) in an empty Wwise project.

It is designed for an AI agent connected through an MCP client (for example Claude Desktop, Cursor, or another host) to execute with minimal user intervention. The prompts begin with simple connectivity and object-authoring tasks, then build toward more complex hierarchy duplication and event retargeting workflows.

## Portability

- **No machine-specific filesystem paths** appear in this document. Paths that look like `\Actor-Mixer Hierarchy\...` or `\Events\...` are **Wwise Project Explorer paths** (Wwise’s own hierarchy notation), not Windows or Unix paths.
- **Tool names** such as `wwise_get_object` or `wwise_set_property` match the reference **mcp-wwise** server in this repository. If your server uses different tool identifiers, map each prompt to the equivalent tool that performs the same WAAPI operation.
- **`self-report.md`**: write it to the **workspace or repository root** your MCP host allows the agent to edit, or to any path the user specifies at the start of the run. Do not assume a particular drive letter or OS.
- **Wwise version**: behavior may vary slightly by authoring version; discovery tools (`get_property_names`, `get_schema`, etc., or your server’s equivalents) should be used when defaults differ.

## Mission For The AI Agent

Work through this suite in order and complete as many prompts as possible without human intervention.

For every prompt:

- Execute the authoring task.
- Perform at least one self-validation step after the authoring step.
- Record what you attempted, what succeeded, what failed, and what you validated.
- If a prompt fails, do not stop the entire run unless the project state is too broken to continue safely.
- If possible, continue to later prompts using the surviving project state.

At the end of the full run, create a file named `self-report.md` (see **Portability** above for where to place it) and summarize the entire session.

## Required Deliverable

The agent must create:

- `self-report.md` in a writable project or workspace root (or a path given by the user when starting the run). 

The report should contain:

- Run date and approximate start/end time
- Which prompts were attempted
- Which prompts passed, partially passed, or failed
- For each prompt:
  - The exact prompt used
  - The main MCP tools used
  - The main objects created or modified
  - The self-validation step performed
  - The outcome of that self-validation
  - Any errors, ambiguity, retries, or suspicious behavior
- A short section on repeated failure patterns
- A final section titled `Suggestions For Improving MCP-Wwise` with concrete suggestions for improving the tooling, agent ergonomics, and the interaction model between the **Wwise MCP server you used** and AI assistants

## Assumptions

- You are starting from an empty or nearly empty Wwise project.
- Wwise Authoring is running and reachable over WAAPI.
- The prompts are intended to build on each other in sequence.
- The agent should prefer canonical WAAPI names internally, even when the prompt uses display labels like `Output Bus`.
- The agent should avoid guessing field names if a discovery or resolution tool is available.

## Execution Rules For The Agent

- Run the prompts in order unless a failed state makes that impossible.
- After each prompt, immediately run at least one self-check using read-only inspection tools.
- Prefer validating by reading back the exact object, property, reference, child structure, or event target that should have changed.
- When changing a field, report the canonical WAAPI name used.
- When self-validation fails, note whether the failure appears to be:
  - authoring failure
  - verification failure
  - ambiguity in the MCP tool surface
  - ambiguity in the Wwise data model
- If a prompt partially succeeds, document the exact partial state in `self-report.md` and continue if safe.
- Do not silently skip prompts. If you skip one, explain why in `self-report.md`.

## Suggested Self-Validation Patterns

These are preferred validation patterns for the run:

- Re-query created objects by path and confirm `type`, `name`, and `path`
- Read back changed properties or references after mutation
- Re-query container children to confirm hierarchy changes
- Re-query Event children and Action targets after event authoring or retargeting
- Compare original and duplicate object paths during copy workflows
- Validate that a Bus assignment points to a `Bus` object, not an `AuxBus`

## Prompt 1: Connectivity Smoke Test

```text
Connect to Wwise and tell me the currently selected objects, if any. Then show me the top-level objects under the Actor-Mixer Hierarchy and Events tab so I know the project is reachable and empty enough for testing.
```

### Goal

Verify that the MCP server can talk to Wwise and perform basic read operations.

### Expected coverage

- Connection to WAAPI
- Project browsing
- Basic object queries

### Minimum self-validation

After the initial query, perform one additional read to confirm that the Actor-Mixer Hierarchy and Events tab can both be queried successfully and that the results are internally consistent.

## Prompt 2: Create Basic Test Structure

```text
In the Actor-Mixer Hierarchy, create a Work Unit named "MCP_Test". Inside it create folders named "Source", "Variants", "Templates", and "Copies". In the Events tab, create a Work Unit named "MCP_Test_Events". Then report the full paths of everything you created.
```

### Goal

Establish a clean, reusable structure for all subsequent prompts.

### Expected coverage

- Object creation
- Work Unit creation
- Folder creation
- Clear path reporting

### Minimum self-validation

Re-query each created Work Unit and folder by path and confirm that:

- each object exists
- each object has the expected type
- each object is under the expected parent

## Prompt 3: Create Simple Sound Objects

```text
Under \Actor-Mixer Hierarchy\MCP_Test\Source, create three Sound objects named "Play_Footstep_01", "Play_Footstep_02", and "Play_Footstep_03". Do not import audio. Just create the Wwise objects and show me their types, names, and paths.
```

### Goal

Verify simple object creation for common authoring objects.

### Expected coverage

- Creating `Sound` objects
- Type-aware object placement
- Result summarization

### Minimum self-validation

Re-query all three Sound objects and confirm:

- they exist at the expected paths
- their type is `Sound`
- their parent is `\Actor-Mixer Hierarchy\MCP_Test\Source`

## Prompt 4: Change A Simple Property

```text
For all three Footstep Sound objects under \Actor-Mixer Hierarchy\MCP_Test\Source, set Pitch to slightly different values so they are easy to distinguish: -50, 0, and 50. Use proper WAAPI property resolution rather than guessing field names, and tell me which canonical WAAPI property name you used.
```

### Goal

Test scalar property changes and confirm canonical property resolution.

### Expected coverage

- Display label to WAAPI property resolution
- `setProperty`
- Reporting canonical WAAPI field names

### Minimum self-validation

Read the property values back from all three Sound objects and confirm that:

- the canonical WAAPI property name used was consistent
- the three values are distinct and match `-50`, `0`, and `50`

## Prompt 5: Change A Reference Using A Display Label

```text
Create a Bus named "MCP_Test_Bus" under the Master-Mixer Hierarchy in a suitable test location, then assign the Output Bus of all three Footstep Sound objects to that bus. Treat "Output Bus" as a display label and resolve it to the proper WAAPI reference name before changing anything. Report the canonical reference name you used and the target bus path.
```

### Goal

Exercise reference resolution and one of the historically tricky cases in Wwise.

### Expected coverage

- Bus creation
- Display label to WAAPI reference resolution
- `setReference`
- Bus-vs-AuxBus correctness

### Minimum self-validation

Re-query the created bus and all three Sound objects and confirm:

- the target object is of type `Bus`
- the resolved field name was the expected canonical WAAPI reference name
- each Sound object now points to the created bus through that reference

## Prompt 6: Create A First Event

```text
Create an Event named "Play_Footstep_01" under \Events\MCP_Test_Events that targets the Sound \Actor-Mixer Hierarchy\MCP_Test\Source\Play_Footstep_01. After creation, show me the event, its Action children, and the Action target.
```

### Goal

Verify event creation and target wiring.

### Expected coverage

- Event creation
- Action inspection
- Event target validation

### Minimum self-validation

Re-query the Event and its children and confirm:

- the Event exists under `\Events\MCP_Test_Events`
- it has at least one `Action` child
- the Action target resolves to `Play_Footstep_01`

## Prompt 7: Create Matching Events For A Set

```text
Create matching Play Events for the other two Sounds under \Actor-Mixer Hierarchy\MCP_Test\Source. The Events should be named "Play_Footstep_02" and "Play_Footstep_03" under \Events\MCP_Test_Events. Then summarize each Event and what object it targets.
```

### Goal

Test repeated event authoring with consistent naming and targeting.

### Expected coverage

- Batch authoring
- Event naming consistency
- Multi-object targeting summaries

### Minimum self-validation

Re-query all three Footstep Events and confirm that each Event name maps to the correspondingly named Footstep Sound.

## Prompt 8: Group Sounds Into A Random Container

```text
Under \Actor-Mixer Hierarchy\MCP_Test\Variants, create a Random Container named "Footstep". Move or organize the three Footstep Sound objects from the Source folder so they become children of that Random Container, while keeping the structure clean and easy to inspect. Then show me the resulting hierarchy.
```

### Goal

Test container creation and child reorganization.

### Expected coverage

- Random Container creation
- Moving or regrouping existing objects
- Hierarchy reporting

### Minimum self-validation

Re-query the `Footstep` Random Container and confirm:

- it exists under `\Actor-Mixer Hierarchy\MCP_Test\Variants`
- it has exactly the expected Footstep child Sounds
- the child paths reflect the new hierarchy

### Inspiration

This mirrors the grouping workflow used in `create_random_containers_from_selection.py`.

## Prompt 9: Template-Based Container Settings

```text
In \Actor-Mixer Hierarchy\MCP_Test\Templates, create a Random Container named "_template". Give it a few clearly visible settings that make sense for a test template. Then create another Random Container named "Footstep_TemplateBased" under \Actor-Mixer Hierarchy\MCP_Test\Variants and copy the relevant settings from _template onto it. Tell me exactly which properties and references were copied.
```

### Goal

Test template-driven authoring and copying settings from one object to another.

### Expected coverage

- Template object creation
- Property and reference inspection
- Property copying or paste behavior

### Minimum self-validation

Read back at least one copied property or reference from both `_template` and `Footstep_TemplateBased` and confirm that the values match after the copy operation.

### Inspiration

This mirrors the template-oriented approach used in `create_random_containers_from_selection_template.py`.

## Prompt 10: Create Multiple Variation Families

```text
Under \Actor-Mixer Hierarchy\MCP_Test\Source, create six new Sound objects named:
Stone_01
Stone_02
Stone_03
Wood_01
Wood_02
Wood_03

Then under \Actor-Mixer Hierarchy\MCP_Test\Variants, create one Random Container for Stone and one for Wood, and place the corresponding Sounds under each container. Finally summarize the grouping logic you used.
```

### Goal

Test naming-based grouping and multi-container authoring.

### Expected coverage

- Creating multiple related objects
- Group-by-name logic
- Organizing siblings into container families

### Minimum self-validation

Re-query the `Stone` and `Wood` Random Containers and confirm that each one has exactly the three expected child Sounds and no cross-contamination between groups.

## Prompt 11: One Work Unit Per Object Group

```text
Take the two Random Containers named "Stone" and "Wood" under \Actor-Mixer Hierarchy\MCP_Test\Variants and reorganize them so each one lives in its own Work Unit under \Actor-Mixer Hierarchy\MCP_Test. Preserve the objects and their children. Then report the before-and-after paths.
```

### Goal

Test structural reorganization into separate Work Units.

### Expected coverage

- Work Unit creation
- Moving existing objects
- Preserving child hierarchies during moves

### Minimum self-validation

Re-query both moved containers and confirm:

- the old paths no longer represent the live location
- the new Work Unit paths exist
- the moved containers still retain their original children

### Inspiration

This is conceptually similar to `create_wwu_per_selected_object.py`.

## Prompt 12: Duplicate A Hierarchy

```text
Duplicate the Random Container \Actor-Mixer Hierarchy\MCP_Test\Stone and place the copy alongside it with a sensible unique name ending in "_Copy". Preserve its internal child structure. Then show me the original path, new path, and all child names under the copy.
```

### Goal

Test object duplication and naming conflict handling.

### Expected coverage

- `copy`
- `setName`
- Preserving internal hierarchy

### Minimum self-validation

Re-query both the original and copied `Stone` hierarchies and confirm:

- both exist simultaneously
- the copy has a unique name ending in `_Copy`
- the copy contains the expected child count and child naming pattern

## Prompt 13: Duplicate Referencing Events And Retarget Them

```text
Find any Events that reference the original Stone hierarchy. Duplicate those Events with names ending in "_Copy", then retarget the duplicated Event Actions so they point to the duplicated Stone hierarchy instead of the original. Afterward, list each original Event, its duplicate, the duplicated Action objects, and the new Action targets.
```

### Goal

Test graph-aware duplication where copied events must be rewired to copied content.

### Expected coverage

- Finding references to a hierarchy
- Duplicating Events
- Inspecting Action children
- Setting the `Target` reference correctly

### Minimum self-validation

For at least one duplicated Event, re-query its Action children and confirm that:

- the duplicated Event exists
- the Action target points to the copied `Stone` hierarchy or one of its descendants
- the target is no longer the original object path

### Inspiration

This follows the same overall shape as `duplicate_structure_and_events.py`.

## Prompt 14: Mix Reference And Property Changes On The Copy

```text
For the duplicated Stone hierarchy, assign it to the same test bus as before, then also change a few ordinary properties on the copied children so I can confirm both references and scalar properties were handled correctly. Report which fields were treated as references and which were treated as properties.
```

### Goal

Confirm that the agent distinguishes between properties and references after the project becomes more complex.

### Expected coverage

- Mixed `setReference` and `setProperty`
- Canonical field resolution
- Reporting of mutation categories

### Minimum self-validation

Read back one changed reference and at least one changed scalar property from the duplicated hierarchy and explicitly note in `self-report.md` which verification corresponded to a reference and which corresponded to a property.

## Prompt 15: End-To-End Content Authoring Test

```text
Starting from the existing MCP_Test structure, create a new variation family called "Metal". Make three Sound children, group them into a Random Container, create a matching Play Event, duplicate that hierarchy and its Event, retarget the duplicated Event to the duplicated hierarchy, and route both original and copied versions to the MCP_Test_Bus. At the end, give me a concise audit of every object created or modified, grouped by hierarchy section.
```

### Goal

Run a dense end-to-end workflow that combines authoring, grouping, events, duplication, retargeting, and routing.

### Expected coverage

- Multi-step planning
- Hierarchy creation
- Event creation
- Duplication
- Reference retargeting
- Property/reference correctness
- Final audit summary

### Minimum self-validation

Perform an end-to-end audit by re-querying the new `Metal` family and confirming at least:

- original and copied hierarchies both exist
- original and copied Events both exist
- copied Event Actions target copied content
- both original and copied content are routed to `MCP_Test_Bus`

## Suggested Evaluation Criteria

When reviewing each run, pay attention to:

- Did the agent use the correct object type and parent path?
- Did it resolve display labels into canonical WAAPI names without guessing?
- Did it choose `setProperty` vs `setReference` correctly?
- Did it report the canonical names it used when asked?
- Did copied Events target copied content rather than the original hierarchy?
- Did the final hierarchy remain clean and inspectable?
- Did the agent successfully validate its own work rather than only claiming success?

## Required Final Section In `self-report.md`

The report must end with a section titled:

## Suggestions For Improving MCP-Wwise

That section should include thoughtful recommendations about how to improve:

- the MCP tool surface
- field and object-name resolution
- error messages and retry behavior
- validation tooling
- discoverability for AI agents
- the overall working relationship between the Wwise MCP server and AI assistants (whatever MCP host was used)

The suggestions should be based on what happened during the overnight run, not just generic ideas.

## Notes For Future Expansion

- Add a parallel suite for imported audio and source assignment once `import_audio` workflows are stable.
- Add a suite for Switch Containers, States, and assignment workflows.
- Add a suite for SoundBank inclusion authoring.
- Add a suite specifically for negative tests, such as invalid display labels or ambiguous target names.
