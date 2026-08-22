---
name: claude-config-sync
description: Keep the `claude-config` repository (`~/.claude/`) in sync with its remote — pull latest changes and/or detect, scan, and commit/push local changes. Use at session start to pull, after any agent lifecycle action (onboard/retire) to commit, or whenever asked to "sync agents" or "update agents". Not tied to any single agent — invoke from HAL directly or from any agent that needs the `claude-config` repo synced. Request explicit user permission before running this skill.
---

# claude-config-sync

Keeps the `claude-config` repository (`~/.claude/`) in sync with its remote. All git operations are scoped to that repository only.

## Remote awareness
- Read `gitRemote` from `~/.claude/settings.json` to identify the canonical remote URL.
- Before any push, verify the local `origin` remote matches that URL. If it does not match, abort — do not push — and report it to the user.

## Pull / sync check
Run this at session start, or whenever asked to "sync agents" / "update agents":
1. Run `git fetch` inside `~/.claude/`.
2. Check if the local branch is behind the remote.
3. If behind, run `git pull --ff-only`.
4. If a conflict arises, report it and stop — do not attempt to auto-resolve.
5. Report the outcome (up to date / pulled N commits / conflict) back to whoever invoked the skill.

## Change detection
- Run `git status` inside `~/.claude/` to detect modified or newly tracked files.
- Perform this after any agent lifecycle action (onboard/retire), whenever a session-start sync is due, or whenever explicitly requested (e.g. "sync agents" / "update agents").

## Pre-commit safety scan
Before staging any file, scan all changed files (never `settings.json`) for:
- Absolute local paths (e.g. `/Users/`, `/home/`)
- Credential patterns: `sk-`, `Bearer `, `password`, `token`, `secret`, `key =`
- Names of people

If any match is found: block the commit, report the exact file and line number, and wait for it to be fixed before retrying. Do not proceed with a partial commit.

## Commit and push (user confirmation required)
1. Draft a descriptive commit message summarising what changed (e.g. `Add trainer-agent; update CLAUDE.md roster`).
2. Present the proposed message and a diff summary to the user.
3. Wait for explicit confirmation before running `git add` / `git commit` / `git push`.
4. Only stage files in the tracked scope: `CLAUDE.md`, `agents/**`, and `skills/**`, follow .gitignore as a source of truth. Never stage `settings.json` or any other file.

## Slash-style commands
Respond to the natural-language commands `sync agents` and `update agents` by running the pull/sync check followed by the change-detection and commit/push flow.
