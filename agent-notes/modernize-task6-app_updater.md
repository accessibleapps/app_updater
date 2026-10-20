# Streamed update response cleanup

## Goal

Keep the existing updater API and behavior while releasing a streamed download response when an HTTP error interrupts download preparation. Scope is accessibleapps/app_updater only; no product pins, live updates, bootstrap execution, or publication.

## State

- Worker thread: 01a15b4c-c035-7355-a97b-abcada04c033.
- Exact origin: git@github.com:accessibleapps/app_updater.git; authenticated GitHub account ctoth has push permission.
- Fresh default master fetched 2026-10-20 at 646aac1c5e582afe98ac9a64a49eade2606e5d1b.
- Canonical checkout C:/Users/Q/code/app_updater was clean, including untracked paths; master tracked origin/master at +0/-0. Its existing ignored artifacts are untouched.
- Isolated worktree created directly at C:/Users/Q/Documents/Codex/2026-10-20/task-6/worktrees/app_updater after verifying absence; branch modernize/task6-app_updater. Only canonical worktree existed before creation. No repository-targeting Codex/Claude process command line was found; other user sessions exist and remain untouched.
- Existing PRs #2 (97efc43c19ab8aa01a7361eaa0afaa51e891debb) and #5 (30cd49b6b3e847c7384b27192dc3f018ad26ea97) are unrelated and preserved. No applicable repository AGENTS.md, CLAUDE.md, agent-notes, .agents/skills or active Git hooks were found.

## Decisions and why

- Smallest justified change: wrap the existing streamed response in contextlib.closing, already imported. Estimate: 4 added/2 removed production lines and 2 regression assertion/capture lines in the existing HTTP-error test, plus this note. No new abstraction or dependency.
- Evidence: autoupdate/autoupdate.py download_update obtains stream=True, then raise_for_status can exit without consuming/closing the response. perform_update calls it directly. The installed Requests models.py close method closes unconsumed raw and releases the connection.
- Existing tests/test_download.py::TestDownloadUpdate::test_download_http_error exercises a real Requests Response through responses and a temporary output file. Strengthen it to assert the response raw stream closes while preserving HTTPError and the existing created-file assertion. Run that file before and after the minimal fix.
- Topology node app-updater owns autoupdate and pyproject.toml. app_framework/pyproject.toml declares this owner and app_framework/updates.py imports/delegates to perform_update. No consumer source/ref or authoritative lock changes are part of this slice.
- pyproject.toml and uv.lock are tracked/clean; both retain Python >=3.8.6. README test authority is uv run pytest; focused invocation adds this actively edited file only and --locked --group test to provision its declared tests without lock changes.

## Surprises

- Sandboxed Git reads hit dubious-ownership protection. Normal approved execution as the owner succeeded; no safe.directory or security settings changed.
- No tracked .github workflow exists. GitHub actions/workflows lists only dynamic/dependabot/update-graph. Full README checks (pytest, ruff check, pyright, uv build) therefore lack an existing hosted authority; parent notified to settle an alternative under the global local-CI restriction. Do not invent CI.

## Verification

- Before fix: `uv run --locked --group test pytest tests/test_download.py` on Windows / CPython 3.13.15 / pytest 8.4.2: **1 failed, 7 passed**. The existing HTTP-error test fails at `assert error.value.response.raw.closed` with False on a real `<Response [404]>`. Existing content, progress, custom chunk size, absent Content-Length, empty and binary download cases pass. Seven pre-existing responses stream-argument deprecation warnings.
- The first sandbox invocation could not access the existing uv cache and ran no tests. Normal approved execution succeeded; no cache/security configuration changed.
- Manifest/lock diff remained empty after focused test provisioning.
- Parent approved the concrete cleanup and, because no hosted CI exists here, one execution of each README full check in this isolated worktree. No ruff format or new workflow.
- After fix: identical focused command: **8 passed**, 7 existing deprecation warnings in 3.19s.
- Full `uv run pytest`: **69 passed, 1 skipped**, 10 responses deprecation warnings in 8.57s. Windows skips the existing executable-bit test. Existing bootstrap launch tests use mocks; no live replacement was performed.
- Full `uv run ruff check`: **exit 1**, 10 pre-existing findings: tests/conftest.py:3 unused io; tests/test_bootstrap.py:6 unused MagicMock and Mock and :110 unused initial_mode; tests/test_callbacks.py:5 unused pytest; tests/test_download.py:3 unused io; tests/test_extract.py:119 unused zf; tests/test_perform_update.py:3 unused os and :4 unused platform; tests/test_session.py:3 unused pytest. Each reported source line was read from the exact base with git show. No fix or formatting run.
- Full `uv run pyright`: **exit 0**, 0 errors, 0 warnings, 0 informations. Tool printed an advisory that a newer Pyright exists; no dependency change.
- Full `uv build`: **exit 0**, built dist/autoupdate-0.24.tar.gz and dist/autoupdate-0.24-py3-none-any.whl. Build success proves packaging only, not installed behavior.
- `git diff -- pyproject.toml uv.lock` remained empty after all uv commands. Product dependency pins and Python/platform support unchanged. No active pre-commit hook is configured or installed.
- Plain `git diff --check` calls the three added CRLF source lines trailing whitespace; the source already uses CRLF. Preserve its established line endings and verify with the command-scoped cr-at-eol whitespace interpretation; no Git configuration changes.

## Next step

Local implementation is complete: production diff is 3 added/2 removed lines and regression diff is 3 added/1 removed lines, plus this living note. Final tracked diff is limited to those files; no secrets, signing keys, private data or unrelated samples are present. Canonical checkout remains clean at the captured base. Commit the named files with subject `Close streamed update responses after download`, then report exact commit to the coordinator for required publication review. No push or PR until authorized. No release, deployment, merge, ready transition, external comment or existing PR edit occurred.
