---
name: note-review
description: Check a single note against the vault's standard template, or be consulted for the template's required format before drafting a brand-new note — e.g. right after/before filing a note captured under dictation. On-demand, single-note counterpart to knowledge-base-review (which does the same conformance check periodically across the whole vault). Proposes changes as a diff and applies them only after the user approves — never autonomously.
---

# note-review

Checks one note against the vault's standard template. This is the single-note, on-demand counterpart to the `knowledge-base-review` skill's template-conformance question — use this one right after a note is created or edited (e.g. filed from dictation) rather than waiting for the next periodic review.

## When to use

Two modes, both single-note and on-demand — not on a schedule, and not across the whole vault:
1. **Checking an existing note** — most commonly right after Librarian-agent files or updates it.
2. **Format guidance before drafting** — Librarian-agent (or any agent about to write a brand-new note) consults this skill first to learn the template's required structure, instead of guessing or inventing a format.

For the periodic, vault-wide version of the conformance check (plus consistency, readability, and unused-note review), use `knowledge-base-review` instead.

## Pre-flight — load the standard template

Resolve and read the standard note template: its path is configured in `~/.claude/local-settings.json` under `knowledgeBaseNoteTemplate`.

**If the setting is missing, or the file it points to doesn't exist: cancel the check, not just skip it.** Notify the user of exactly what's missing (the setting key, or the resolved path that couldn't be found) and stop — don't fall back to guessing at a template. This applies equally to the format-guidance mode below: if the template can't be loaded, don't hand back a guessed format — stop and notify instead.

## Format guidance for a new note

When consulted before a note exists yet, stop after Pre-flight: hand back the template's required sections, the `References:` line placement, and heading order as the format to draft against. This is guidance only — there's no existing note to diff, so nothing is proposed or applied here; drafting the note itself stays the calling agent's job.

## Checking conformance (existing note)

Compare the note's structure against the template — required sections, the `References:` line, heading order, etc. — not its content. A structural mismatch is a candidate diff; don't rewrite the note's substance just to fit the template's shape. If the note already conforms, report that and stop — there's nothing to propose.

## Proposing and applying changes — never autonomous

Present any mismatch as an explicit diff (before/after content), not a description of what would change, carrying a reasoning comment.

No change is ever applied without the user having seen the diff and given explicit approval for it. Approving is per diff — if the note needs more than one fix, don't treat approval of one as approval for the rest.

- Approved diff: apply it exactly as shown.
- Declined diff: leave the note untouched.
- This still runs under the hard constraint of no tags (`agents/librarian-agent.md`) and the vault's established formatting/template conventions.
- Never introduce trailing spaces as part of a diff — this applies to every line the check touches, not just lines being otherwise changed.

## Scope

This check is structural only and touches one note. It doesn't update the vault index or any `last_review` / cadence metadata — that bookkeeping belongs to `knowledge-base-review`.
