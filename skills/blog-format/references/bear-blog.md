# Bear blog: platform reference

Source: https://docs.bearblog.dev/post/ (Anatomy of a post) and the Markdown cheatsheet linked from https://docs.bearblog.dev/ (checked 2026-09-24). If something here seems off, re-check the live docs. Bear changes attributes occasionally (e.g. `make_discoverable` was renamed to `discoverable`).

## Post layout

All post attributes go at the very top of the post, one per line, as `key: value`. A line with `___` (three underscores) separates them from the content:

```
title: I like Bears
link: i-like-bears
published_date: 2022-12-30 09:00
meta_description: Bears are pretty cool, according to science.
meta_image: https://i.imgur.com/3jxqrKP.jpeg
tags: bears, writing, thoughts
lang: en
___
Here is my article outlining why bears are dope.
```

Consequences:
- Nothing may come before the attributes in the text that is pasted into Bear. A local-only block kept in the file (e.g. an author's brief) must sit *above* the header and must not be pasted.
- The title is displayed from `title:`. The body shouldn't repeat it as a `#` heading.

## Attributes

| Attribute | Required | Format / default | Notes |
|---|---|---|---|
| `title` | yes | free text | Shown on the post and in the blog list |
| `link` | no | relative path, auto-generated from the title | e.g. `i-like-bears` → `/i-like-bears/`. Paths are allowed (`blog/i-like-bears`) |
| `alias` | no | old path | Redirects a legacy URL to this post |
| `canonical_url` | no | absolute URL | Only when the post is a copy of an original published elsewhere |
| `lang` | no | HTML lang code (default: blog language) | e.g. `en` |
| `published_date` | no | `YYYY-MM-DD HH:MM` (local time), or `YYYY-MM-DD`; default: now | A future date schedules the post in lists and feeds, **but the post is readable at its URL straight away**. Use a Bear draft to keep it private |
| `is_page` | no | `true` / `false` (default false) | Pages don't appear in the blog list |
| `meta_description` | no | text, default: first 160 characters of the content | Shown in search results and link previews. Keep it ≤ 160 characters |
| `meta_image` | no | absolute image URL | Preview image when shared on social media or in messaging apps |
| `tags` | no | comma-separated list | Generates tag filter links |
| `discoverable` | no | `true` / `false` (default true) | `false` keeps the post off Bear's Discover page |
| `class_name` | no | CSS class name | For per-post styling |

## Markdown

- Emphasis: `**bold**`, `*italics*`, `~~strike~~`, `==highlight==`
- Headings: `#` to `####`. Heading ids are slugified, so `[jump](#my-heading)` works as an internal link.
- Links: `[text](https://example.com)` opens in the same tab. `[text](tab:https://example.com)` opens in a **new tab**. `<https://example.com>` is an autolink and can't take the `tab:` prefix.
- Line breaks: a single newline is not rendered. End the line with `\` or two spaces. A blank line starts a new paragraph.
- Footnotes: `text[^1]`, with `[^1]: note` at the bottom. Named footnotes such as `[^named-note]` work too.
- Quotes (`>`), tables (GitHub-style pipes), fenced code blocks with a language for highlighting, and LaTeX are supported.
- Typographic replacements: `(c)` → ©, `(tm)` → ™, `+-` → ±, `H~2~O` for subscript, `6^th^` for superscript.
- Raw HTML is allowed in the content.
- Template variables: `{{ post_title }}`, `{{ post_published_date }}`, `{{ tags }}`, `{{ previous_post }} {{ next_post }}`, `{{ blog_title }}`, etc.

## Images

Bear only hosts images on paid plans. Otherwise upload elsewhere (Bear suggests ImgBB) and reference the absolute URL:

```
![Meaningful alt text](https://i.ibb.co/xxxx/image.jpg)
```

A local path (`./img/x.png`) won't work once the text is pasted into Bear.

## SEO notes

Bear generates meta, OpenGraph, robots.txt and sitemap tags automatically. The one manual lever it recommends is a well-written `meta_description`.
