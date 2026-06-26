---
name: sync-upstream-fork
description: Safely update a fork from its upstream/original repository. Use when the user asks to get upstream changes, sync a fork, catch up a repo that is commits behind upstream, merge upstream into their branch, explain merge conflicts without overwriting local changes, resolve conflicts by choosing upstream/ours/manual per user direction, validate, commit, and push.
---

# Sync Upstream Fork

Safely merge upstream changes into the current fork without silently overwriting local edits.

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

3. Fetch and summarize drift:

```bash
git fetch origin --prune
git fetch upstream --prune
git log --oneline --decorate HEAD..upstream/main
git log --oneline --decorate upstream/main..HEAD
```

Use the upstream default branch if it is not `main`:

```bash
git remote show upstream
```

4. Merge upstream into the current branch:

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

6. After conflicts are resolved:

```bash
git status --short
git diff --check
```

Run the repo's required check command from local instructions. For this repo, prefer `make check`; avoid live provider/keychain/browser-cookie probes unless the user explicitly requested them.

7. Commit and push:

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
