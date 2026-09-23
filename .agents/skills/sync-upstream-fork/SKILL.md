---
name: sync-upstream-fork
description: Safely update a fork from its upstream/original repository while enforcing its fork contract. Use when the user asks to get upstream changes, sync a fork, catch up a repo that is commits behind upstream, merge upstream into their branch, explain merge conflicts without overwriting local changes, resolve conflicts by choosing upstream/ours/manual per user direction, validate, commit, and push.
---

# Sync Upstream Fork

Safely merge upstream changes into the current fork without silently overwriting local edits or
intentional fork behavior.

## Workflow

1. Inspect the repo before changing anything:

```bash
git status --short --branch
git remote -v
git branch --show-current
```

If tracked files are modified, stop and ask whether to commit, stash, or leave them alone. Do not run merge/rebase with a dirty worktree unless the user explicitly says to.

2. Find upstream:

- Use `upstream` if it already exists.
- If missing, infer the GitHub parent with `gh repo view --json parent,url` when `gh` is authenticated.
- If still unclear, ask for the upstream URL.
- After adding a remote, use the name `upstream`.

3. Fetch and inspect the fork contract before any merge:

```bash
git fetch origin --prune
git fetch upstream --prune
git log --oneline --decorate HEAD..upstream/main
git log --oneline --decorate upstream/main..HEAD
python3 .agents/skills/sync-upstream-fork/scripts/fork_contract_report.py --upstream upstream/main --check
```

The fork contract at `.agents/fork-contract.md` is mandatory. Do not create, edit, or weaken it
during a sync to make the report pass. It is maintained alongside normal fork-specific changes.

Exit status `2` from the report is an intentional stop, not a failure. Before merging, show the
user every protected item touched by upstream and every fork-only path missing from the contract.
Ask whether each protected item should be preserved manually, replaced by upstream, or changed in
a specified way. For unlisted fork-only paths, ask whether to add a contract item or explicitly
allow upstream to replace them. Do not merge, commit, or push until the user decides.

The report matches paths conservatively. A match requires a decision even if Git would merge the
file cleanly and even if the upstream hunk appears unrelated.

Use the upstream default branch if it is not `main`:

```bash
git remote show upstream
```

4. Merge upstream into the current branch only after the contract report requires no decision or
the user has made every required decision:

```bash
git merge --no-ff upstream/main
```

Do not use `-X ours`, `-X theirs`, `git checkout --ours`, or `git checkout --theirs` globally before showing the user the conflicts.

5. If conflicts happen, report them before editing:

```bash
python3 .agents/skills/sync-upstream-fork/scripts/conflict_report.py
git diff --name-only --diff-filter=U
git diff --cc -- <path>
```

For each conflicted file, explain:

- what the local side changed
- what upstream changed
- why Git could not combine them automatically
- the smallest safe choices: `ours`, `upstream`, or `manual`

Pause for user direction. If the user chooses per file or hunk, apply only that choice. Preserve intentional fork changes unless the user explicitly chooses upstream.

For this repo, use `.agents/fork-contract.md` as the complete source of preservation rules. Do not
take upstream wholesale for a protected file. Apply the user's per-item decision manually and keep
all unrelated protected behavior intact.

6. After conflicts are resolved, verify every preserved contract item still has its stated behavior
and run its focused test when one is named. Then run:

```bash
git status --short
git diff --check
```

Run the repo's required check command from local instructions. For this repo, prefer `make check`; avoid live provider/keychain/browser-cookie probes unless the user explicitly requested them.

If package, signing, or bundle metadata changed, verify that the packaged app matches the current
fork contract. When the contract does not protect product identity, use upstream's product name,
bundle ID, and signing identifiers.

For packaging validation, prefer `./Scripts/package_app.sh debug` for a non-launching check. Run the user's exact `./Scripts/compile_and_run.sh` command when they are explicitly validating the app bundle.

7. Before committing, show the user the final contract summary: preserved items, items intentionally
replaced by upstream, and any contract additions requested by the user. Do not add a contract item
merely because a file is fork-only; its behavior must be intentional and user-approved.

8. Commit and push:

```bash
git add <resolved-files>
git commit -m "Merge upstream changes"
git push origin HEAD
```

If checks fail, fix the failure before pushing. If conflicts were resolved manually, show the final changed files and ask for confirmation before pushing.

## Conflict Rules

- Treat generated artifacts as low-value unless repo instructions say otherwise.
- Prefer deleting fork-only code only when upstream made the same behavior obsolete.
- Prefer manual edits over whole-file `ours`/`theirs` when both sides changed adjacent logic.
- Never abort a merge unless the user asks or the worktree cannot be made safe.
- Never force-push as part of this skill.
