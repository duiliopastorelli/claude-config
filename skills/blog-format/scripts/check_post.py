#!/usr/bin/env python3
"""Mechanical format checker for a blog article (currently: Bear blog layout).

Usage:
    check_post.py <article.md> --style <style-guide.md> [--mode draft|publish]

Configuration comes from the JSON block in the style guide that follows the
marker `<!-- blog-format:config -->`. Only mechanics are checked; editorial
proofreading is left to the reviewer.

Exit code: 0 = no errors, 1 = errors found, 2 = could not run (bad input/config).
"""
import argparse
import json
import re
import sys
from pathlib import Path

BEAR_ATTRIBUTES = {
    "title", "link", "alias", "canonical_url", "lang", "published_date",
    "is_page", "meta_description", "meta_image", "tags", "discoverable",
    "class_name",
}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}( \d{2}:\d{2})?$")
PUBLISHED_NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*(/[a-z0-9]+(-[a-z0-9]+)*)*$")
PLACEHOLDER_RE = re.compile(r"<[^<>\n]+>|YYYY-MM-DD|\bTODO\b|\bTBD\b")

# American -> British hints. Heuristic only: the reviewer confirms in context.
US_SPELLINGS = {
    "color": "colour", "colors": "colours", "behavior": "behaviour",
    "behaviors": "behaviours", "favorite": "favourite", "honor": "honour",
    "labor": "labour", "center": "centre", "centers": "centres",
    "centered": "centred", "program": "programme (non-software only)",
    "catalog": "catalogue", "dialog": "dialogue", "analyze": "analyse",
    "analyzed": "analysed", "analyzing": "analysing", "license": "licence (noun)",
    "defense": "defence", "offense": "offence", "traveled": "travelled",
    "traveling": "travelling", "modeling": "modelling", "labeled": "labelled",
    "labeling": "labelling", "canceled": "cancelled", "fulfill": "fulfil",
    "enroll": "enrol", "judgment": "judgement", "aging": "ageing",
}
IZE_ALLOWLIST = {"size", "sizes", "sized", "prize", "prizes", "seize", "seized",
                 "capsize", "maize", "baize", "downsize", "downsized", "resize",
                 "resized", "oversize", "oversized", "citizen", "citizens", "wizard"}
IZE_RE = re.compile(r"\b([A-Za-z]+i)z(e|es|ed|ing|ation|ations|er|ers)\b")


class Report:
    def __init__(self):
        self.lines = []

    def add(self, level, msg, line=None):
        where = f" (line {line})" if line else ""
        self.lines.append((level, f"{level}{where}: {msg}"))

    def count(self, level):
        return sum(1 for lvl, _ in self.lines if lvl == level)


def load_config(style_path):
    text = Path(style_path).read_text(encoding="utf-8")
    m = re.search(r"<!--\s*blog-format:config\s*-->\s*```json\s*(\{.*?\})\s*```", text, re.S)
    if not m:
        raise ValueError("no `<!-- blog-format:config -->` JSON block found in the style guide")
    return json.loads(m.group(1))


def split_article(text, report):
    """Return (brief:dict|None, header:list[(lineno,key,value)], body_lines:list[(lineno,str)])."""
    lines = text.split("\n")
    i = 0
    brief = None
    # skip leading blank lines
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].lstrip().startswith("<!--"):
        start = i
        block = []
        while i < len(lines):
            block.append(lines[i])
            if "-->" in lines[i]:
                break
            i += 1
        else:
            report.add("ERROR", "brief comment block is never closed with -->", start + 1)
            return None, [], []
        i += 1
        if "brief" in block[0].lower():
            brief = {}
            for raw in block[1:]:
                raw = raw.replace("-->", "").strip()
                if ":" in raw:
                    k, v = raw.split(":", 1)
                    brief[k.strip().lower()] = v.strip()
    while i < len(lines) and not lines[i].strip():
        i += 1
    header = []
    sep_found = False
    while i < len(lines):
        raw = lines[i]
        if raw.strip() == "___":
            sep_found = True
            i += 1
            break
        if raw.strip():
            if ":" in raw:
                k, v = raw.split(":", 1)
                header.append((i + 1, k.strip(), v.strip()))
            else:
                report.add("ERROR", f"header line is not `key: value`: {raw.strip()!r}", i + 1)
        i += 1
    if not sep_found:
        report.add("ERROR", "no `___` separator line between the header and the content")
        return brief, header, []
    body = [(n + 1, lines[n]) for n in range(i, len(lines))]
    return brief, header, body


def check(article_path, cfg, mode):
    report = Report()
    path = Path(article_path)
    text = path.read_text(encoding="utf-8")
    name = path.name
    draft_prefix = cfg.get("draft_prefix", "draft-")

    # ---- mode + file name
    pub_match = PUBLISHED_NAME_RE.match(name)
    if mode is None:
        mode = "publish" if pub_match else "draft"
    strict = mode == "publish"
    if name.startswith(draft_prefix):
        file_slug = name[len(draft_prefix):-3] if name.endswith(".md") else None
        if strict:
            report.add("ERROR", f"file is still named as a draft ({name}); rename to <YYYY-MM-DD>-<slug>.md when publishing")
    elif pub_match:
        file_slug = pub_match.group(2)
    else:
        file_slug = None
        report.add("ERROR", f"file name {name!r} matches neither `{draft_prefix}<slug>.md` nor `<YYYY-MM-DD>-<slug>.md`")
    report.add("INFO", f"mode: {mode}")

    brief, header, body = split_article(text, report)

    # ---- brief
    brief_fields = cfg.get("brief_fields", [])
    if brief_fields:
        if brief is None:
            report.add("WARN", f"no brief block found; ask the author for: {', '.join(brief_fields)}")
        else:
            for f in brief_fields:
                val = brief.get(f, "")
                if not val or PLACEHOLDER_RE.search(val):
                    report.add("WARN", f"brief `{f}` is not set; ask the author (show the style guide's options)")
                else:
                    report.add("INFO", f"brief {f}: {val}")

    # ---- header
    attrs = {}
    for lineno, k, v in header:
        if k in attrs:
            report.add("ERROR", f"duplicate header attribute `{k}`", lineno)
        attrs[k] = (lineno, v)
        if k not in BEAR_ATTRIBUTES:
            hint = " (renamed to `discoverable`)" if k == "make_discoverable" else ""
            report.add("ERROR", f"unknown Bear attribute `{k}`{hint}", lineno)

    def placeholder_issue(key, lineno, v):
        if strict:
            report.add("ERROR", f"`{key}` still has a placeholder: {v!r}", lineno)
        else:
            report.add("TODO", f"fill `{key}` before publishing (currently {v!r})", lineno)

    for key in cfg.get("required_attributes", ["title"]):
        if key not in attrs:
            report.add("ERROR", f"required attribute `{key}` is missing")
            continue
        lineno, v = attrs[key]
        if not v:
            (report.add("ERROR", f"required attribute `{key}` is empty", lineno) if strict
             else report.add("TODO", f"fill `{key}` before publishing (empty)", lineno))
        elif PLACEHOLDER_RE.search(v):
            placeholder_issue(key, lineno, v)

    if "published_date" in attrs:
        lineno, v = attrs["published_date"]
        if v and not PLACEHOLDER_RE.search(v):
            if not DATE_RE.match(v):
                report.add("ERROR", f"`published_date` must be `YYYY-MM-DD HH:MM` (e.g. 2026-10-01 09:00), got {v!r}", lineno)
            elif pub_match and v[:10] != pub_match.group(1):
                report.add("ERROR", f"file-name date {pub_match.group(1)} doesn't match published_date {v[:10]}", lineno)
            elif len(v) == 10:
                report.add("WARN", "`published_date` has no time; the expected format is `YYYY-MM-DD HH:MM`", lineno)
        elif strict and not v:
            report.add("ERROR", "`published_date` is empty", lineno)

    if "link" in attrs:
        lineno, v = attrs["link"]
        if v and not PLACEHOLDER_RE.search(v):
            if not SLUG_RE.match(v):
                report.add("ERROR", f"`link` should be lowercase kebab-case, got {v!r}", lineno)
            if cfg.get("slug_equals_link") and file_slug is not None and file_slug != v:
                report.add("ERROR", f"file slug {file_slug!r} doesn't match `link: {v}`", lineno)

    if "lang" in attrs and cfg.get("lang"):
        lineno, v = attrs["lang"]
        if v and v != cfg["lang"] and not PLACEHOLDER_RE.search(v):
            report.add("ERROR", f"`lang` should be {cfg['lang']!r}, got {v!r}", lineno)

    if "meta_description" in attrs:
        lineno, v = attrs["meta_description"]
        mx = cfg.get("meta_description_max", 160)
        if v and not PLACEHOLDER_RE.search(v) and len(v) > mx:
            report.add("WARN", f"`meta_description` is {len(v)} characters (max {mx}); it will be cut off in previews", lineno)

    if "meta_image" in attrs:
        lineno, v = attrs["meta_image"]
        if v and not PLACEHOLDER_RE.search(v) and not re.match(r"^https?://", v):
            report.add("ERROR", f"`meta_image` must be an absolute http(s) URL, got {v!r}", lineno)

    if "tags" in attrs:
        lineno, v = attrs["tags"]
        if v and not PLACEHOLDER_RE.search(v):
            tags = [t.strip() for t in v.split(",")]
            if any(not t for t in tags):
                report.add("WARN", "`tags` has an empty item (stray comma?)", lineno)

    # ---- body
    in_code = False
    prose_words = 0
    footnote_refs, footnote_defs = {}, {}
    for lineno, raw in body:
        if raw.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        line = re.sub(r"`[^`]*`", "", raw)  # ignore inline code

        mdef = re.match(r"^\[\^([^\]]+)\]:\s*(.*)$", line)
        if mdef:
            footnote_defs.setdefault(mdef.group(1), lineno)
        else:
            prose_words += len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*", re.sub(r"\(([^)]*)\)", " ", line)))
        for ref in re.findall(r"\[\^([^\]]+)\](?!:)", line):
            footnote_refs.setdefault(ref, lineno)

        if re.match(r"^#\s", line):
            report.add("WARN", "`#` heading in the body; Bear already shows `title:` as the page title", lineno)

        if strict and PLACEHOLDER_RE.search(line) and not line.lstrip().startswith("<!--"):
            report.add("ERROR", f"placeholder left in the body: {PLACEHOLDER_RE.search(line).group(0)!r}", lineno)

        if cfg.get("images_require_hosted_url_and_alt", True):
            for alt, url in re.findall(r"!\[([^\]]*)\]\(([^)\s]+)[^)]*\)", line):
                if not alt.strip():
                    report.add("ERROR", f"image without alt text: {url}", lineno)
                if not re.match(r"^https?://", url):
                    report.add("ERROR", f"image is not an absolute hosted URL: {url}", lineno)
            for tag in re.findall(r"<img\b[^>]*>", line, re.I):
                if not re.search(r'alt\s*=\s*"[^"]+"', tag, re.I):
                    report.add("ERROR", "<img> without alt text", lineno)
                src = re.search(r'src\s*=\s*"([^"]+)"', tag, re.I)
                if src and not re.match(r"^https?://", src.group(1)):
                    report.add("ERROR", f"<img> src is not an absolute hosted URL: {src.group(1)}", lineno)

        if cfg.get("external_links_new_tab", False):
            for text_, url in re.findall(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)[^)]*\)", line):
                if re.match(r"^https?://", url):
                    report.add("ERROR", f"external link opens in the same tab; use `(tab:{url})`: [{text_}]", lineno)
            for url in re.findall(r"<(https?://[^>\s]+)>", line):
                report.add("WARN", f"autolink <{url}> can't open in a new tab; use `[text](tab:{url})`", lineno)

        if cfg.get("spelling") == "en-GB" and not mdef:
            for word in re.findall(r"\b[A-Za-z]+\b", line):
                lw = word.lower()
                if lw in US_SPELLINGS:
                    report.add("WARN", f"possible American spelling {word!r} → {US_SPELLINGS[lw]}? (confirm in context)", lineno)
                elif IZE_RE.fullmatch(word) and lw not in IZE_ALLOWLIST:
                    report.add("WARN", f"possible American -ize spelling {word!r} → -ise? (confirm in context)", lineno)

    if in_code:
        report.add("ERROR", "unclosed ``` code block")

    if cfg.get("sources_as_footnotes", False):
        for ref, ln in footnote_refs.items():
            if ref not in footnote_defs:
                report.add("ERROR", f"footnote [^{ref}] is referenced but never defined", ln)
        for d, ln in footnote_defs.items():
            if d not in footnote_refs:
                report.add("WARN", f"footnote [^{d}] is defined but never referenced", ln)
        for lineno, raw in body:
            if re.match(r"^#{1,6}\s*(sources|references|bibliography)\s*$", raw.strip(), re.I):
                report.add("WARN", "a Sources/References section was found; the style guide wants sources as footnotes", lineno)

    report.add("INFO", f"word count (body, excluding code and footnote definitions): {prose_words}")
    if brief and brief.get("length"):
        nums = [int(n.replace(",", "")) for n in re.findall(r"\d[\d,]*", brief["length"])]
        if len(nums) >= 2:
            lo, hi = nums[0], nums[1]
            if prose_words and not (lo <= prose_words <= hi):
                report.add("WARN" if strict else "INFO",
                           f"word count {prose_words} is outside the brief's target {lo}–{hi}")
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("article")
    ap.add_argument("--style", required=True, help="path to the style guide with the blog-format:config block")
    ap.add_argument("--mode", choices=["draft", "publish"], help="override the mode detected from the file name")
    args = ap.parse_args()
    try:
        cfg = load_config(args.style)
    except (OSError, ValueError) as e:
        print(f"CANNOT RUN: {e}", file=sys.stderr)
        return 2
    if cfg.get("platform", "bear") != "bear":
        print(f"CANNOT RUN: platform {cfg.get('platform')!r} is not supported by this checker", file=sys.stderr)
        return 2
    try:
        report = check(args.article, cfg, args.mode)
    except OSError as e:
        print(f"CANNOT RUN: {e}", file=sys.stderr)
        return 2
    order = {"ERROR": 0, "TODO": 1, "WARN": 2, "INFO": 3}
    for _, msg in sorted(report.lines, key=lambda x: order.get(x[0], 9)):
        print(msg)
    e, t, w = report.count("ERROR"), report.count("TODO"), report.count("WARN")
    print(f"\nSummary: {e} error(s), {t} to-do(s), {w} warning(s)")
    return 1 if e else 0


if __name__ == "__main__":
    sys.exit(main())
