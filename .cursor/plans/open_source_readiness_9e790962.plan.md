---
name: Open Source Readiness
overview: Prepare `MCP_Wwise_Project` to be safely published as an MIT-licensed open-source repo by cleaning private artifacts, adding baseline public docs/metadata, and doing a pre-public release pass.
todos:
  - id: shape-repo
    content: Decide the public repo layout and whether `wwise-mcp/` or the repo root is the primary package surface
    status: completed
  - id: privacy-cleanup
    content: Add to .gitignore personal workspace/editor/planning artifacts; stop tracking sensitive files (keep locally)
    status: completed
  - id: test-portability
    content: Refactor tests and setup docs so they do not depend on hardcoded playground paths
    status: completed
  - id: public-docs
    content: Add MIT `LICENSE`, root `README.md`, dependency metadata, and contributor-facing docs
    status: completed
  - id: history-audit
    content: Review git history for sensitive content before changing the GitHub repo from private to public
    status: pending
  - id: release-hygiene
    content: Add GitHub templates/CI, smoke-test the repo from a clean environment, and prepare the first public tag
    status: in_progress
isProject: false
---

# Open-Source Plan For MCP_Wwise

## Goal

Turn the current private repo into a public, MIT-licensed GitHub project that is safe to publish, understandable to new users, and clear about Wwise/WAAPI prerequisites.

## What To Keep Public

- The actual server code appears to live in [T:\MCP_Wwise_Project\wwise-mcp](T:\MCP_Wwise_Project\wwise-mcp).
- The local Wwise playground project is already excluded by [T:\MCP_Wwise_Projectgitignore](T:\MCP_Wwise_Project.gitignore) and should remain local-only.

## Step-By-Step Plan

### 1. Decide the public repo shape

- Publish the repo around [T:\MCP_Wwise_Project\wwise-mcp](T:\MCP_Wwise_Project\wwise-mcp) as the main product.
- Decide whether the repo root should stay a workspace/umbrella repo or whether `wwise-mcp` should become the visible primary package. If you keep the current layout, the root `README.md` should make that structure explicit.
- Keep `MCP_Wwise_Playground/` private/local and document it as an optional local test fixture, not part of the open-source deliverable.

### 2. Exclude private/personal artifacts

- **Done:** `MCP_Wwise_Project.code-workspace` and root `plan.md` are no longer tracked (`git rm --cached …`); both stay on disk. `plan.md` is listed in `.gitignore`; `*.code-workspace` is ignored.
- Reference (why the workspace was sensitive) — it contained personal paths:

```6:11:T:\MCP_Wwise_Project\MCP_Wwise_Project.code-workspace
		{
			"path": "C:/Users/j0hnt/.gemini"
		},
		{
			"path": "C:/Users/j0hnt/AppData/Local/Claude"
		}
```

- Rewrite [T:\MCP_Wwise_Project\plan.md](T:\MCP_Wwise_Project\plan.md) before publishing. It contains internal planning language and absolute machine-specific paths such as `T:\MCP_Wwise_Project\...`.
- Ensure internal agent/editor artifacts are not tracked going forward, especially `.cursor/` content and any machine-local AI settings.
- Reconfirm that [T:\MCP_Wwise_Projectclaude\settings.local.json](T:\MCP_Wwise_Project.claude\settings.local.json) is untracked.

### 3. Replace local path assumptions in code and tests

- Fix tests that rely on your personal drive layout before publishing. For example, [T:\MCP_Wwise_Project\wwise-mcp\tests\test_import_audio.py](T:\MCP_Wwise_Project\wwise-mcp\tests\test_import_audio.py) hardcodes a local path:

```10:12:T:\MCP_Wwise_Project\wwise-mcp\tests\test_import_audio.py
# Correct Originals path for this project
ORIGINALS_SFX = "T:\\MCP_Wwise_Project\\MCP_Wwise_Playground\\Originals\\SFX"
```

- Convert these assumptions to one of:
  - a configurable environment variable,
  - a pytest option/fixture,
  - or a documented integration-test-only setup.
- Separate tests into clear buckets such as `unit` vs `live Wwise integration`, so outside contributors can run at least part of the suite without your local playground project.

### 4. Add baseline open-source files

- Add `LICENSE` with MIT text.
- Add a root `README.md` that explains:
  - what the project does,
  - who it is for,
  - that it requires Wwise plus WAAPI access,
  - how to install and run it,
  - how to connect to it from MCP clients,
  - how local/live testing works,
  - what is intentionally not included in the repo.

- Add `CONTRIBUTING.md` with a lightweight workflow for issues, PRs, local setup, and test expectations.
- Add a short `CHANGELOG.md` or start using GitHub releases from the first public tag.

### 5. Rewrite repo messaging for public users

- Update the project’s public framing so it reads like a reusable tool, not a private build log.
- Review the server description in [T:\MCP_Wwise_Project\wwise-mcp\server.py](T:\MCP_Wwise_Project\wwise-mcp\server.py):

```1:4:T:\MCP_Wwise_Project\wwise-mcp\server.py
"""
Wwise MCP Server — entry point.
Transport: stdio (local only).
"""
```

- Keep `stdio` if that is the intended transport, but explain in the README what “local only” means operationally for users.
- Add a concise feature list and supported Wwise/WAAPI expectations.

### 6. Document legal and ecosystem constraints

- Use the MIT License as planned.
- In the README, clearly state that the server integrates with Audiokinetic Wwise via WAAPI and that users need their own valid Wwise installation/license as applicable.
- Avoid bundling proprietary Wwise assets, generated project data, or anything that should not be redistributed.

### 7. Audit commit history before going public

- Review the full git history for:
  - secrets,
  - temporary credentials,
  - internal notes,
  - private customer/company references,
  - absolute paths and usernames.
- If sensitive history exists, decide whether to clean history before publishing or create a new clean public history.
- This is the highest-risk step because files removed today may still exist in old commits.

### 8. Add basic GitHub hygiene

- Add `.github/ISSUE_TEMPLATE/` for bug reports and setup issues.
- Add a PR template if you want outside contributions.
- Add a simple CI workflow if possible for any checks that can run without a live Wwise instance, such as linting, schema validation, or dry-run/unit tests.
- Prepare a first tagged release such as `v0.1.0` once the docs and repo layout are stable.

### 9. Do a pre-public verification pass

- Clone the repo into a clean directory or test from a fresh machine/user context.
- Confirm a new user can understand setup from the README without private knowledge.
- Confirm no tracked file reveals your username, local directories, editor state, or private tooling setup.
- Confirm ignored local-only assets stay ignored. The current ignore rules in [T:\MCP_Wwise_Projectgitignore](T:\MCP_Wwise_Project.gitignore) are a good start.

### 10. Publish and announce deliberately

- Flip the GitHub repo to public only after the history and docs pass.
- Publish the MIT license and first release tag at the same time or immediately after.
- Announce it with a short positioning statement aimed at the game-audio/Wwise community and link to the README’s quickstart.

## Recommended order of execution

1. Remove private artifacts and clean tracked files.
2. Fix hardcoded local paths in tests/docs.
3. Add `LICENSE`, `README.md`, dependency metadata, and contribution docs.
4. Audit git history.
5. Add GitHub templates/CI.
6. Smoke-test from a clean environment.
7. Make the repo public and tag the first release.

## Key considerations to keep in mind

- `MIT` is the right low-friction choice for adoption.
- The main technical risk is not the license; it is publishing a repo that still assumes your exact machine layout.
- The main legal/communication risk is being unclear about the Wwise dependency and what parts of the toolchain are proprietary vs yours.
- The main reputational risk is weak first-run documentation; for a niche integration project, the README matters almost as much as the code.

## Execution notes (2026)

What was done:

- **`.gitignore`**: Expanded to ignore `*.code-workspace`, `.cursor/`, `agent-transcripts/`, local AI tool dirs, and **`plan.md`**. `MCP_Wwise_Playground/` was already ignored.
- **Stop tracking, keep local**: Ran `git rm --cached MCP_Wwise_Project.code-workspace plan.md` so they no longer ship in the repo; files remain on disk. `plan.md` is explicitly listed in `.gitignore` so it is not re-added by mistake.
- **Tests**: `wwise-mcp/tests/test_import_audio.py` uses env var `WWISE_ORIGINALS_SFX` for the Originals/SFX folder; the import-audio integration test **skips** when unset. Documented in `CONTRIBUTING.md`.
- **OSS files**: Root `LICENSE` (MIT), `CONTRIBUTING.md`, `wwise-mcp/requirements-dev.txt`; root `README.md` updated with quickstart, stdio MCP client note, prerequisites, and license pointer.
- **GitHub**: Issue template (`bug_report`), PR template, and `.github/workflows/ci.yml` (Ubuntu, Python 3.11, `pip install` + `pytest` in `wwise-mcp/`).

Still to do before going public:

- **History audit** (step 7): `plan.md` and the workspace file may still exist in **old commits**; consider `git filter-repo`/BFG or a fresh public history if that matters.
- **`release-hygiene`**: Run a clean clone smoke test; tag e.g. `v0.1.0` when ready. Optional: `CHANGELOG.md` or GitHub Releases only.
- **CI caveat**: Full pytest may need Wwise/live WAAPI for some tests; if CI fails on integration tests, split markers or skip rules may be needed next.

