# Goal

Update the locked runtime HTTP dependencies to supported security patches, preserving every Python >=3.8.6 target and existing resolution branch.

# State

- Worker identity supplied by host: /root/modernize_audio_urls.
- Exact owner accessibleapps/app_updater, origin git@github.com:accessibleapps/app_updater.git, authenticated ctoth with admin/push access, public non-fork/non-archived, default master.
- Fresh ls-remote and fetch base: 646aac1c5e582afe98ac9a64a49eade2606e5d1b. Canonical master matches origin/master (0/0), clean including staged/unstaged/untracked files at inspection; ignored files remain untouched.
- Existing worktree worktrees/app_updater and draft PR #6/head 051d54598678d3cdc7120b6e3cc2ec85fa8b4c36 are separate and preserved. Open PRs #2 and #5 are unrelated and untouched. New branch modernize/task6-app-updater-security created directly in worktrees/app-updater-security after checking absence.
- Global AGENTS.md, repository inventory, README, pyproject.toml, uv.lock, updater session/download source and tests, existing branch note and relevant ownership/shared-dependency skills were read. No repository/nested AGENTS.md, CLAUDE.md, .agents/skills or active Git hooks/core.hooksPath were found.

# Decisions and why

- Smallest coherent slice: approximately 50-100 changed lock lines plus this required note. Final lock diff is +43/-12: idna 3.10 -> 3.15 on every target, Requests 2.32.5 -> 2.33.0 and urllib3 2.5.0 -> 2.8.0 only on Python >=3.10. Original Python 3.8 and 3.9 Requests/urllib3 versions and artifact metadata are retained. No runtime code/test/manifest/consumer edit or unrelated package upgrade. No custom vulnerability payload or new test is needed for a lock-only update; existing real Requests/session/download compatibility tests supply application verification.
- Official PyPI metadata declares Requests 2.33.0 and urllib3 2.8.0 require Python >=3.10, idna 3.15 requires >=3.8. Official changelogs were read at https://requests.readthedocs.io/en/latest/community/updates/ and https://urllib3.readthedocs.io/en/stable/changelog.html . These support limits determine the forks; the project support floor remains unchanged.
- urllib3 2.8.0 release notes and primary advisories GHSA-8988-9cw3-xx77, GHSA-vxq7-64xx-v4gw, GHSA-gh4c-6fx4-qh6g identify proxy TLS and streaming fixes. Its proxy TLS correction concerns custom proxy_ssl_context/identity overrides; inspected updater source uses an ordinary Requests Session without custom adapters, proxy TLS parameters, retries or decompressors. No relevant custom application configuration needs migration in this owner source.
- Authenticated Dependabot alert #10 names uv.lock and GHSA-65pc-fj4g-8rjx, affecting idna <3.15. Official advisory: https://github.com/kjd/idna/security/advisories/GHSA-65pc-fj4g-8rjx . Version 3.15 adds early DNS label-length validation: https://github.com/kjd/idna/blob/v3.15/HISTORY.md . Official PyPI metadata https://pypi.org/pypi/idna/3.15/json declares Requires-Python >=3.8, compatible with all project targets.
- Source path: perform_update creates a requests Session; find_update uses Session.get and download_update uses streaming Session.get. uv.lock requests 2.32.4 and 2.32.5 both depend on idna. Existing session/download/update-check tests use real Requests through responses, with update/bootstrap activity mocked.
- Topology node app-updater owns autoupdate and pyproject.toml. The existing validator passed: 6 products, 17 shared owners, 91 edges. Declared consumers include app-framework and QFeed (autoupdate manifests) and QCast (app_updater requirements). No consumer revision/pin/source changes are authorized or made; the owner's development lock is the only dependency surface updated.
- README and topology authority: uv sync --all-groups; uv run pytest; uv run ruff check; uv run pyright; uv build. uv run ruff format is a mutating formatter and is excluded from this security slice. Parent authorized those full nonpublishing checks locally once because only dynamic/dependabot/update-graph exists, no hosted test CI. Known baseline Ruff findings will be reported without changing unrelated source.
- The tracked lock has requires-python >=3.8.6 and three resolution markers (<3.9, 3.9.*, >=3.10); every unrelated package/version/artifact and these markers must remain unchanged. Only references needed to select the three HTTP dependencies may change. Command invocations must retain lock freshness and preserve the exact scoped diff.

# Surprises

- Canonical checkout is currently clean despite the earlier task snapshot mentioning dirty locks; current clean state is the captured ledger and no files were discarded.

# Verification

- Narrow resolver operations: uv lock --upgrade-package idna==3.15; scoped Requests/urllib3 upgrades; final older-target record retention via apply_patch using original artifact metadata. Complete final diff inspected. All unrelated lock records are identical to base except autoupdate/responses references to the selected HTTP forks; their other fields are identical. Global requires-python and resolution-markers are identical.
- Final uv lock --check: exit 0, 38 resolved package records. Target-marker evaluation yields Python 3.8.6: Requests 2.32.4 / urllib3 2.2.3; 3.9.0: Requests 2.32.5 / urllib3 2.5.0; 3.10.0 and 3.13.15: Requests 2.33.0 / urllib3 2.8.0; idna 3.15 throughout. This proves graph selection, not execution on all interpreters.
- uv sync --all-groups completed in the isolated worktree. uv run pytest: 69 passed, 1 skipped, 10 existing responses deprecation warnings in 2.77s; Python 3.13.15 / pytest 8.4.2. Executed HTTP versions verified directly: Requests 2.33.0, urllib3 2.8.0, idna 3.15. The existing Windows skip is the Unix executable-bit test.
- uv run pyright: exit 0, 0 errors/0 warnings/0 informations. uv build: exit 0; dist/autoupdate-0.24.tar.gz and dist/autoupdate-0.24-py3-none-any.whl produced. No publication or bootstrap invocation.
- uv run ruff check: exit 1 with ten known findings on unchanged tests (unused imports/variables). Tracked test sources were mechanically compared to base and are identical. No lint repair or formatter run.
- Lock SHA256 during these full checks: 7352322D655AA9F8E99F5E3381B249884B8C5B9D62A130741C19B2ADAB680316, unchanged by every check. Subsequent coordinator-directed Python 3.9 record retention changes no installed Python 3.13 dependency; final lock check and target graph passed without rerunning unchanged full checks. Final lock SHA256: A47E8E75246FE12BC6268092232C768CF33023391C8B6934FCEFF33C6701EB1B.
- git diff --check passed. Only uv.lock and this note are authored/staged. Reviewed for scope, secrets and unrelated data; no credentials, private data, signing keys or samples included. Canonical base and separate draft #6 head remain unchanged.

# Next step

The completed local slice consists only of uv.lock plus this note. Return concrete commit/base/head and concise PR text for required coordinator review before any push or draft PR. Preserve existing PR #6 and every branch/worktree. No merge, ready transition, release, deployment, default push, closure, external comment/review or other PR edit is authorized.
