# Dependabot configuration integration

## Goal

Integrate existing PR #2's GitHub-native Dependabot configuration with the repository's current uv manifest and lockfile. Smallest amendment: change one ecosystem value from pip to uv; retain the original daily schedule, root directory and ten-PR limit. No package updates, additional ecosystems or policy changes.

## State

- Repository: accessibleapps/app_updater; origin git@github.com:accessibleapps/app_updater.git.
- Reviewed original PR #2 head: 97efc43c19ab8aa01a7361eaa0afaa51e891debb, branch dependabot/add-v2-config-file. No pre-existing local branch with that name existed.
- Fresh master: a0cce9c386bbf4ae19008e55c8ffbdb8ad1c2220. Its README uses uv, its tracked uv.lock is consumed by locked CI, and it has no Dependabot configuration.
- Isolated owned candidate: repair/task6-updater-dependabot in task-6/worktrees/updater-dependabot. Rebased the original commit with --no-update-refs onto that master; range-diff reports the original configuration commit unchanged before this amendment.
- Original remote tip and initial local candidate tip are preserved separately in refs/archive/task6-updater-2-remote-original and refs/archive/task6-updater-2-local-before-rebase, both at 97efc43.
- Fork PR #5's exact original 30cd49b6b3e847c7384b27192dc3f018ad26ea97 is preserved locally in refs/archive/task6-updater-5-fork-original. Its entire force-include deletion already landed in master commit 646aac1; no fork or replacement integration edit is justified.
- Canonical checkout and existing feature/security worktrees are preserved. No original PR head, title or description changed.

## Decisions and why

- PR #2 was created for the 2021 Dependabot Preview shutdown. Its useful remaining change is repository-owned configuration; the migration announcement itself is historical.
- Current uv documentation explicitly configures package-ecosystem: uv to update uv.lock: https://docs.astral.sh/uv/guides/integration/dependabot/ . GitHub's supported-ecosystems reference separately lists uv and pip: https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories .
- Keep the PR's requested schedule and limit. No added registries, credentials, permissions, ignore rules, support-floor changes or dependency refresh.
- Existing PR/master CI already runs locked full tests, Ruff, Pyright and package build. No local full CI or new implementation-mirroring test is needed for this one-field configuration amendment. Static source/diff inspection is not a hosted Dependabot execution claim.

## Surprises

- GitHub's PR baseRefOid was historical; authenticated commits/master and fresh git fetch/ls-remote agree on a0cce9c. The candidate uses that actual current default.

## Next step

Return the complete master-to-candidate configuration/note diff and exact local head to the coordinator before publication. Hosted checks must run on the eventual published head; actual Claude review remains blocked under the separate normal-context denial and cannot be retried by this worker. Dependabot's service behavior is only observable after its configuration lands; no dispatch, settings, release or merge action is authorized here.
