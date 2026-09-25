---
name: blog-format
description: The blog's technical format and editorial rules, plus the workflow for starting, proofreading, format-checking and preparing a blog article for publishing. Use this skill any time work touches a blog article or post, including drafting, editing, reviewing, proofreading, setting up a new post file, filling in post header attributes (title, link, published_date, meta_description, tags), or getting a post ready to publish (e.g. on Bear blog). Use it even if the user only says "look at my post", "is this ready?", or "start the article about X". Librarian-agent consults it before checking or creating any article content. Not for vault/knowledge-base notes (use note-review for those).
---

# blog-format

This skill defines how a blog article is laid out and checked. It has two layers:

1. **Generic mechanics** (this skill): the workflow, the platform reference in `references/`, and a mechanical checker in `scripts/check_post.py`.
2. **The author's own rules** (a style guide kept outside this skill): the platform, file naming, required header attributes, markdown rules, language, voice, confidentiality, and the per-article questions. They live outside the skill because this skill is shared publicly and they are personal.

If the two layers disagree, the style guide wins. It reflects decisions the author actually made.

## Pre-flight: load the style guide

1. Read `~/.claude/local-settings.json` and resolve the `blogStyleGuide` key. It holds the path to the author's style guide.
2. Read that file in full.
3. Read the platform reference that the style guide names, from `references/` (e.g. `references/bear-blog.md`).

**If the setting is missing, the file doesn't exist, or there is no reference file for the named platform, stop.** Tell the user exactly what is missing (the key, the resolved path, or the platform) and don't guess a format. A guessed format is worse than none: every later check would enforce rules nobody agreed to.

## The author writes, you assist

The article belongs to the author. Your job is structure, checking and quality, not prose. Don't write body content unless the author explicitly asks, and then write only the part they asked for. When you fix something, keep their voice and meaning: a proofreading fix that "improves" the text into someone else's style is a regression.

## Per-article questions

Some decisions change from article to article (the style guide lists them, typically **target audience** and **length**). They are recorded in the article's local brief block, as the style guide describes.

When an article is being **created or reviewed** and a brief value is missing:
- Ask the author, and show the example options listed in the style guide, highlighted, so they can pick one quickly or write their own.
- Explain in one line why it matters: audience decides what "clear" and "makes sense in context" mean, and length decides whether the piece needs cutting or expanding.
- Record the answer in the brief (as a proposed diff, like any other change).

Don't silently assume a default. The author chose per-article answers on purpose, because articles have different goals.

## Mode 1: starting a new article

1. Run Pre-flight.
2. Ask the per-article questions (see above) and agree on a slug with the author.
3. Create the file with the draft name the style guide specifies, containing:
   - the brief block with the answers;
   - the platform header, with every required attribute present. Where a value isn't known yet, use the explicit placeholder format the style guide gives (e.g. a date placeholder with a worked example), so the expected format is visible in the file;
   - the separator line, and an empty body, or the author's own outline/skeleton if they supplied one.
4. Offer a **skeleton of guiding topics**: suggested `##` sections, each with the questions it should answer, written as prompts and not as prose. Many authors find it easier to write from a skeleton than from a blank page. Add it only if the author accepts, and keep it free of draft content, since the prose is theirs to write. Two gates apply:
   - **Goal and thesis first.** Don't propose a skeleton until the author has agreed what the post is for (e.g. an opinion, a story, a how-to) and has stated its point in one sentence. Record both in the brief. A skeleton without a thesis invites the author to answer every prompt, and the post then drifts between several ideas.
   - **Size it to the length.** Derive the number of sections from the brief's length target (roughly one `##` per 150–200 words), and give each section a word budget, so the budgets add up to the target. Every section must serve the thesis. Park any extra ideas as future posts.
5. Run the checker (see "Running the checker") and report what is still to be filled in. Placeholders are expected at this stage, so present them as a to-do list, not as failures.

## Mode 2: reviewing or proofreading an article

Do the checks in this order, because the mechanical pass is cheap and removes noise before the editorial read.

1. **Pre-flight**, then check the brief. Ask the per-article questions if values are missing.
2. **Mechanical format check**: run the checker and collect its findings.
3. **Editorial proofreading**: read the whole article against the style guide and the brief:
   - Spelling and grammar, in the language and spelling variant the guide specifies. The checker's spelling hints are heuristics: confirm each one in context before you report it.
   - Meaning in context: does each section make sense for *this* article's audience? Is anything unclear, contradictory, repeated, or unsupported? Does the argument flow?
   - Voice: does it match the voice rules in the guide? Flag drift (e.g. passive constructions, filler, hype words, vague claims) and suggest a fix that stays in the author's register.
   - Length against the brief's target.
   - Confidentiality: apply the guide's confidentiality rules. Flag anything that might be non-public (employer-internal system names, customer names, unpublished figures) for the author to confirm. Don't delete it yourself, because the author may have clearance.
   - Unsupported factual claims: flag them. Never "fix" a claim by inventing a detail or a source.
4. **Report**, grouped as Format / Proofreading / Confidentiality. Every proposed change is shown as a before → after diff with a short reason. Apply a change only after explicit approval of that change. Approving one diff doesn't approve the others.
5. **Verdict**: end with a one-line status. Either **Ready** (no errors, all brief values set, all diffs resolved) or **Not ready**, followed by the blocking items. You're accountable for this verdict, so don't soften it.

## Mode 3: preparing to publish

1. Run a full Mode 2 review first. Publishing an article that hasn't been reviewed defeats the purpose of the gate.
2. Agree on the publish date and time with the author. Set the date attribute in the exact format the guide requires.
3. Propose the rename from the draft name to the published name (per the guide) and do it only after approval.
4. Run the checker in publish mode (it switches automatically on the published file name). Every placeholder must be gone at this point.
5. Remind the author of the publishing mechanics from the platform reference and the guide (e.g. which part of the file to paste into the editor, and that images must already be hosted).

## Running the checker

```bash
python3 ~/.claude/skills/blog-format/scripts/check_post.py <article.md> --style <style-guide.md>
```

- The checker reads its configuration from the JSON block in the style guide that is marked `blog-format:config`.
- The mode is detected from the file name: draft files are checked leniently (placeholders become `TODO`s), published files strictly. Force a mode with `--mode draft|publish`.
- Output lines are `ERROR` (must fix), `WARN` (check and decide) and `INFO` (e.g. word count, and brief values the checker couldn't find). The exit code is 1 when there are errors.
- The checker only verifies mechanics. A clean run doesn't mean the article is good. The editorial pass is still yours.

## Scope

This skill covers blog articles only. It doesn't apply to knowledge-base notes, and the vault's rules (no tags, vault index updates) don't apply here; whether an article has tags is up to the style guide.
