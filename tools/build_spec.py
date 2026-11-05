#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import markdown


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO_ROOT / "specification/ai-catalog.md"
DEFAULT_OUTPUT = REPO_ROOT / "dist/index.html"
DEFAULT_CONFIG = REPO_ROOT / "specification/respec-config.json"


DEFAULT_RESPEC_CONFIG = {
    "specStatus": "Official",
    "editors": [],
    "latestVersion": None,
    "noRecTrack": True,
}

HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*$")
FENCE_RE = re.compile(r"^(`{3,}|~{3,})")
MERMAID_BLOCK_RE = re.compile(
    r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.DOTALL
)
SLUG_INVALID_RE = re.compile(r"[^a-z0-9]+")


@dataclass
class Section:
    level: int
    title: str
    section_id: str
    body_lines: list[str] = field(default_factory=list)
    children: list["Section"] = field(default_factory=list)
    appendix: bool = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the AI Catalog specification into a ReSpec HTML page."
    )
    parser.add_argument(
        "source",
        type=Path,
        nargs="?",
        default=DEFAULT_SOURCE,
        help="Markdown source file",
    )
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        default=DEFAULT_OUTPUT,
        help="HTML output path",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="ReSpec configuration JSON file",
    )
    return parser.parse_args()


def slugify(text: str, counts: dict[str, int]) -> str:
    slug = SLUG_INVALID_RE.sub("-", text.casefold()).strip("-") or "section"
    count = counts.get(slug, 0)
    counts[slug] = count + 1
    if count:
        return f"{slug}-{count + 1}"
    return slug


def is_appendix(title: str, appendix_headers: list[str]) -> bool:
    lowered_title = title.casefold()
    return any(lowered_title.startswith(prefix.casefold()) for prefix in appendix_headers)


def build_section_tree(source_text: str, appendix_headers: list[str]) -> list[Section]:
    root = Section(level=0, title="", section_id="root")
    stack: list[Section] = [root]
    slug_counts: dict[str, int] = {}
    in_fence = False
    active_fence = ""

    for line in source_text.splitlines():
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if not in_fence:
                in_fence = True
                active_fence = marker[0]
            elif marker[0] == active_fence:
                in_fence = False
                active_fence = ""

        if not in_fence:
            heading_match = HEADING_RE.match(line)
            if heading_match:
                level = len(heading_match.group(1))
                title = re.sub(r"\s+#+\s*$", "", heading_match.group(2)).strip()
                section = Section(
                    level=level,
                    title=title,
                    section_id=slugify(title, slug_counts),
                    appendix=level == 1 and is_appendix(title, appendix_headers),
                )
                while stack and stack[-1].level >= level:
                    stack.pop()
                stack[-1].children.append(section)
                stack.append(section)
                continue

        stack[-1].body_lines.append(line)

    return root.children


def render_markdown(converter: markdown.Markdown, text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""

    rendered = converter.reset().convert(stripped)

    def replace_mermaid(match: re.Match[str]) -> str:
        diagram = html.unescape(match.group(1)).strip("\n")
        return f'<pre class="mermaid nohighlight">\n{diagram}\n</pre>'

    return MERMAID_BLOCK_RE.sub(replace_mermaid, rendered)


def render_sections(converter: markdown.Markdown, sections: list[Section]) -> str:
    rendered_sections: list[str] = []

    for section in sections:
        heading_tag = f"h{section.level}"
        class_attr = ' class="appendix"' if section.appendix else ""

        parts = [
            f'<section{class_attr} id="{section.section_id}">',
            f"<{heading_tag}>{html.escape(section.title)}</{heading_tag}>",
        ]

        body_html = render_markdown(converter, "\n".join(section.body_lines))
        if body_html:
            parts.append(body_html)

        if section.children:
            parts.append(render_sections(converter, section.children))

        parts.append("</section>")
        rendered_sections.append("\n".join(parts))

    return "\n".join(rendered_sections)


def load_config(path: Path) -> tuple[dict[str, object], str, str, list[str]]:
    config = json.loads(path.read_text(encoding="utf-8"))
    title = str(config.pop("title"))
    abstract = str(config.pop("abstract"))
    appendix_headers = list(config.pop("appendixHeaders", []))
    final_config = {**DEFAULT_RESPEC_CONFIG, **config}
    return final_config, title, abstract, appendix_headers


def build_document(source: Path, output: Path, config_path: Path) -> None:
    respec_config, title, abstract, appendix_headers = load_config(config_path)
    sections = build_section_tree(source.read_text(encoding="utf-8"), appendix_headers)

    converter = markdown.Markdown(
        extensions=["extra", "sane_lists"],
        output_format="html",
    )

    abstract_html = render_markdown(converter, abstract)
    body_html = render_sections(converter, sections)
    config_json = json.dumps(respec_config, indent=6, ensure_ascii=False)

    # The empty .copyright element is deliberate: ReSpec uses an author-supplied
    # .copyright in place of its default W3C copyright notice.
    document = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>{html.escape(title)}</title>
  <script src=\"https://www.w3.org/Tools/respec/respec-w3c\" class=\"remove\" defer></script>
  <script class=\"remove\">
    var respecConfig = {config_json};
  </script>
  <style>
    pre {{ background: #f8f8f8; padding: 1em; overflow-x: auto; }}
    pre.mermaid {{ background: white; border: 1px solid #e0e0e0; text-align: center; }}
  </style>
  <script type=\"module\">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    mermaid.initialize({{ startOnLoad: false, theme: 'default' }});
    if (document.respec) {{
      await document.respec.ready;
    }}
    await mermaid.run({{ querySelector: 'pre.mermaid' }});
  </script>
</head>
<body>

<p class=\"copyright\"></p>

<section id=\"abstract\">
  <h2>Abstract</h2>
  {abstract_html}
</section>

<section id=\"sotd\">
  <h2>Status of This Document</h2>
  <p>This is a draft document and may be updated at any time.</p>
</section>

<section id=\"conformance\">
  <p>
    The key words \"MUST\", \"MUST NOT\", \"REQUIRED\", \"SHALL\", \"SHALL NOT\",
    \"SHOULD\", \"SHOULD NOT\", \"RECOMMENDED\", \"NOT RECOMMENDED\", \"MAY\", and
    \"OPTIONAL\" in this document are to be interpreted as described in BCP 14
    [[RFC2119]] [[RFC8174]] when, and only when, they appear in all capitals,
    as shown here.
  </p>
</section>

{body_html}
</body>
</html>
"""

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    print(output)


def main() -> None:
    args = parse_args()
    build_document(args.source, args.output, args.config)


if __name__ == "__main__":
    main()