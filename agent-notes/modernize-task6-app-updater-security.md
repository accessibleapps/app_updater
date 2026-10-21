# Goal

Update the locked runtime HTTP dependencies to supported security patches, preserving every Python >=3.8.6 target and existing resolution branch.

# State

- Worker identity supplied by host: /root/modernize_audio_urls.
- Exact owner accessibleapps/app_updater, origin git@github.com:accessibleapps/app_updater.git, authenticated ctoth with admin/push access, public non-fork/non-archived, default master.
- Initial base was 646aac1c5e582afe98ac9a64a49eade2606e5d1b. Current fresh master/base is a0cce9c386bbf4ae19008e55c8ffbdb8ad1c2220, which merged #6 after prerequisite #8; postmerge push CI 39519210719 passed. Canonical master remains clean at initial 646aac1 and was not moved; ignored files remain untouched.
- Published draft PR #7: https://github.com/accessibleapps/app_updater/pull/7, remote head a65b75dffae9640094e1b4d58f1b871b7df3942d. This isolated modernize/task6-app-updater-security worktree rebased locally with --no-update-refs; original local and remote tips remain in distinct archive/task6-updater-7-local-before-baseline and archive/task6-updater-7-remote-before-baseline refs. No push yet.
- #6 merged at a0cce9c after actual Claude approval and green CI, preserving its separate branch/worktree. Open PRs #2 and #5 remain untouched. This local follow-up refreshes only this existing note; the original security lock is unchanged.
- Global AGENTS.md, repository inventory, README, pyproject.toml, uv.lock, updater session/download source and tests, existing branch note and relevant ownership/shared-dependency skills were read. No repository/nested AGENTS.md, CLAUDE.md, .agents/skills or active Git hooks/core.hooksPath were found.

# Initial decisions and why (historical dependency scope retained)

- Smallest coherent slice: approximately 50-100 changed lock lines plus this required note. Final lock diff is +43/-12: idna 3.10 -> 3.15 on every target, Requests 2.32.5 -> 2.33.0 and urllib3 2.5.0 -> 2.8.0 only on Python >=3.10. Original Python 3.8 and 3.9 Requests/urllib3 versions and artifact metadata are retained. No runtime code/test/manifest/consumer edit or unrelated package upgrade. No custom vulnerability payload or new test is needed for a lock-only update; existing real Requests/session/download compatibility tests supply application verification.
- Official PyPI metadata declares Requests 2.33.0 and urllib3 2.8.0 require Python >=3.10, idna 3.15 requires >=3.8. Official changelogs were read at https://requests.readthedocs.io/en/latest/community/updates/ and https://urllib3.readthedocs.io/en/stable/changelog.html . These support limits determine the forks; the project support floor remains unchanged.
- urllib3 2.8.0 release notes and primary advisories GHSA-8988-9cw3-xx77, GHSA-vxq7-64xx-v4gw, GHSA-gh4c-6fx4-qh6g identify proxy TLS and streaming fixes. Its proxy TLS correction concerns custom proxy_ssl_context/identity overrides; inspected updater source uses an ordinary Requests Session without custom adapters, proxy TLS parameters, retries or decompressors. No relevant custom application configuration needs migration in this owner source.
- Authenticated Dependabot alert #10 names uv.lock and GHSA-65pc-fj4g-8rjx, affecting idna <3.15. Official advisory: https://github.com/kjd/idna/security/advisories/GHSA-65pc-fj4g-8rjx . Version 3.15 adds early DNS label-length validation: https://github.com/kjd/idna/blob/v3.15/HISTORY.md . Official PyPI metadata https://pypi.org/pypi/idna/3.15/json declares Requires-Python >=3.8, compatible with all project targets.
- Source path: perform_update creates a requests Session; find_update uses Session.get and download_update uses streaming Session.get. uv.lock requests 2.32.4 and 2.32.5 both depend on idna. Existing session/download/update-check tests use real Requests through responses, with update/bootstrap activity mocked.
- Topology node app-updater owns autoupdate and pyproject.toml. The existing validator passed: 6 products, 17 shared owners, 91 edges. Declared consumers include app-framework and QFeed (autoupdate manifests) and QCast (app_updater requirements). No consumer revision/pin/source changes are authorized or made; the owner's development lock is the only dependency surface updated.
- README and topology authority: uv sync --all-groups; uv run pytest; uv run ruff check; uv run pyright; uv build. uv run ruff format is a mutating formatter and is excluded from this security slice. Parent authorized those full nonpublishing checks locally once because only dynamic/dependabot/update-graph exists, no hosted test CI. Known baseline Ruff findings will be reported without changing unrelated source.
- The tracked lock has requires-python >=3.8.6 and three resolution markers (<3.9, 3.9.*, >=3.10); every unrelated package/version/artifact and these markers must remain unchanged. Only references needed to select the three HTTP dependencies may change. Command invocations must retain lock freshness and preserve the exact scoped diff.

# Historical initial implementation surprises

- Canonical checkout is currently clean despite the earlier task snapshot mentioning dirty locks; current clean state is the captured ledger and no files were discarded.

# Verification

- Current local rebase was conflict-free; range-diff reports the original security commit unchanged. Lock SHA256 remains A47E8E75246FE12BC6268092232C768CF33023391C8B6934FCEFF33C6701EB1B. Production, tests, manifest and inherited workflow match current master; baseline lint cleanup and streamed-response fix are retained.
- Current master tracks .github/workflows/ci.yml and has green full Windows Python 3.13 CI. No local full checks rerun. Proposed hosted coverage is Python 3.8, 3.9, 3.10 and 3.13 for the actual differing HTTP/test dependency branches; workflow changes await coordinator scope review before authorship/publication. This head has no new hosted result or actual Claude review yet.
- Current residual limit: Python 3.8/3.9 retain known Requests/urllib3 advisories because the selected fully patched upstream versions require >=3.10. No all-advisories-clean claim, invented backport or support-policy change. The lock governs owner development/tests; consumers do not consume it automatically.

## Historical initial implementation checks (before #8/#6 baseline merges and rebase)

- Narrow resolver operations: uv lock --upgrade-package idna==3.15; scoped Requests/urllib3 upgrades; final older-target record retention via apply_patch using original artifact metadata. Complete final diff inspected. All unrelated lock records are identical to base except autoupdate/responses references to the selected HTTP forks; their other fields are identical. Global requires-python and resolution-markers are identical.
- Final uv lock --check: exit 0, 38 resolved package records. Target-marker evaluation yields Python 3.8.6: Requests 2.32.4 / urllib3 2.2.3; 3.9.0: Requests 2.32.5 / urllib3 2.5.0; 3.10.0 and 3.13.15: Requests 2.33.0 / urllib3 2.8.0; idna 3.15 throughout. This proves graph selection, not execution on all interpreters.
- uv sync --all-groups completed in the isolated worktree. uv run pytest: 69 passed, 1 skipped, 10 existing responses deprecation warnings in 2.77s; Python 3.13.15 / pytest 8.4.2. Executed HTTP versions verified directly: Requests 2.33.0, urllib3 2.8.0, idna 3.15. The existing Windows skip is the Unix executable-bit test.
- uv run pyright: exit 0, 0 errors/0 warnings/0 informations. uv build: exit 0; dist/autoupdate-0.24.tar.gz and dist/autoupdate-0.24-py3-none-any.whl produced. No publication or bootstrap invocation.
- uv run ruff check: exit 1 with ten known findings on unchanged tests (unused imports/variables). Tracked test sources were mechanically compared to base and are identical. No lint repair or formatter run.
- Lock SHA256 during these full checks: 7352322D655AA9F8E99F5E3381B249884B8C5B9D62A130741C19B2ADAB680316, unchanged by every check. Subsequent coordinator-directed Python 3.9 record retention changes no installed Python 3.13 dependency; final lock check and target graph passed without rerunning unchanged full checks. Final lock SHA256: A47E8E75246FE12BC6268092232C768CF33023391C8B6934FCEFF33C6701EB1B.
- git diff --check passed. Only uv.lock and this note are authored/staged. Reviewed for scope, secrets and unrelated data; no credentials, private data, signing keys or samples included. Canonical base and separate draft #6 head remain unchanged.

# Next step

Return the complete rebased lock/note diff, exact local head and proposed minimal hosted Python 3.8/3.9/3.10/3.13 matrix with dependency/runtime authorities to the coordinator before any push. Matrix authoring, publication and final-head actual Claude/hosted gates remain pending coordinator action. PR #7 stays draft and unmerged; preserve all branches/worktrees and archive refs. No local full CI rerun, support-policy change, old PR-description edit, release, deployment, default push or closure.
