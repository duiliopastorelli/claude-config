---
name: knowledge-base-review
description: Perform a periodic structural review of a notes/knowledge-base vault — checks consistency, readability, and usage-based cleanup candidates, then updates the vault index's review metadata. Invoke from Librarian-agent (or HAL) when a vault's index metadata shows a review is due; requires explicit user consent before any review work starts. Proposes changes as diffs and applies them only after the user approves each diff — never autonomously.
---

# knowledge-base-review

Describes how to perform a periodic structural review of a notes/knowledge-base vault (Obsidian-style or plain-markdown). This is the procedure Librarian-agent follows once a vault's review cadence is due.

## Trigger

Cadence is configurable per vault via the vault index's own metadata block: `review_interval_days` (default 7) and `review_change_threshold` (default 10). A review becomes due when at least `review_interval_days` days have passed since `last_review`, OR `notes_changed_since_last_review` >= `review_change_threshold`.

**Counting changes.** The stored counter only sees agent edits, so when checking whether a review is due, count the vault's notes (excluding templates and hidden folders such as `.obsidian/`) whose file modification time is later than `last_review`, and use the higher of that count and `notes_changed_since_last_review`. This catches edits the user made directly in their notes app. Caveats: cloud-sync clients can occasionally touch modification times without a real edit, and an agent bulk edit on review day resets the baseline for every note it touched — treat the count as a signal, not an exact figure.

Being due only means the review *may* be offered — it does not authorize starting it.

## Hard gate — explicit user consent required

Before doing any analysis, reading beyond what's needed to ask the question, or otherwise starting review work, explicitly ask the user for permission to run the periodic structural review. Do not proceed on an assumed yes, a prior general approval, or the trigger condition alone — the user must say so explicitly for this specific review.

If the user declines or doesn't respond: set `last_review_outcome: skipped` in the vault index and leave `last_review` / `notes_changed_since_last_review` untouched. Stop here.

## Pre-flight — load the standard template

Before any of the review questions run, resolve and read the standard note template: its path is configured in `~/.claude/local-settings.json` under `knowledgeBaseNoteTemplate`.

**If the setting is missing, or the file it points to doesn't exist: cancel the entire review, not just the template-conformance step.** Notify the user of exactly what's missing (the setting key, or the resolved path that couldn't be found) and stop — don't fall back to guessing at a template, and don't run the other three review questions in a degraded mode. Treat this the same as a declined consent: set `last_review_outcome: skipped`, leave `last_review` / `notes_changed_since_last_review` untouched.

## Review questions

Once consent is given and the template has loaded successfully, ask four questions to surface candidate changes — analysis only, nothing is written yet:
1. Is the vault still consistent?
2. Is the vault still human-readable?
3. Are there notes that could be deleted for lack of usage? — carve-out: a note that's unused but still linked to a topic currently in use stays; only flag notes both unused AND disconnected from any in-use topic.
4. Does each note still conform to the vault's standard template? — compare structure only (required sections, the `References:` line, heading order, etc.), not content; a structural mismatch is a candidate diff, but don't rewrite a note's substance just to fit the template's shape. A note that predates the template, or was deliberately filed differently for a documented reason, still gets flagged — conformance candidates go through the same proposal/diff/consent flow as any other change, so the user decides whether to update it.

Every proposed change must carry a reasoning comment.

## Proposing changes

Present each candidate change as an explicit diff (before/after content), not a description of what would change. Route diffs through the orchestrator (and, in workspaces that define one, a validation step) before the user sees them. Group diffs that belong to the same note together so they can be reviewed coherently, but never bundle unrelated notes into a single approval step.

## Applying changes — never autonomous

No change is ever applied without the user having seen its diff and given explicit approval for that specific change (or an explicitly-approved batch of diffs, if the user chooses to approve a group at once). Approving the review to run, or approving one diff, does not carry approval for any other diff.

- Approved diff: apply it exactly as shown, then move to the next.
- Declined diff: leave that note untouched; don't re-propose the same change later in the same review pass.
- This still runs under the hard constraint of no tags (`agents/librarian-agent.md`) and the vault's established formatting/template conventions — a diff that would violate either isn't a valid proposal to begin with.
- Never introduce trailing spaces as part of a diff — this applies to every line the review touches, not just lines being otherwise changed.

## After the review

A review pass is complete once every proposed diff has been resolved (applied or declined) — not merely generated. At that point, update the vault index: set `last_review` to today, reset `notes_changed_since_last_review` to 0, and set `last_review_outcome: ran`.
