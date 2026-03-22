#!/usr/bin/env python3
"""Build a PDF book from the course markdown files using pandoc + tectonic."""

import subprocess
import tempfile
import re
from pathlib import Path

COURSE_DIR = Path(__file__).parent
MODULES_DIR = COURSE_DIR / "modules"

MODULE_FILES = [
    "01-tokens-and-inference.md",
    "02-context-window-size.md",
    "03-messages-array.md",
    "04-tool-calling.md",
    "05-ralph-wiggum-loop.md",
    "06-sub-agents.md",
    "07-message-passing.md",
    "08-context-management.md",
]

YAML_HEADER = """\
---
title: "Context Engineering"
subtitle: |
  Master the art of managing what goes into a language model's
  context window — from tokens and system prompts to tool calls
  and memory strategies.
author: "Based on the course outline from latentpatterns.com"
date: "2026"
documentclass: report
classoption:
  - 11pt
  - letterpaper
geometry:
  - margin=1in
fontfamily: libertinus
monofont: "Courier New"
linestretch: 1.3
toc: true
toc-depth: 2
highlight-style: kate
colorlinks: true
linkcolor: "black"
urlcolor: "blue"
header-includes:
  - |
    \\usepackage{fancyhdr}
    \\pagestyle{fancy}
    \\fancyhf{}
    \\fancyfoot[C]{\\thepage}
    \\fancyhead[L]{\\small\\textit{Context Engineering}}
    \\fancyhead[R]{\\small\\textit{\\leftmark}}
    \\renewcommand{\\headrulewidth}{0.4pt}
    \\renewcommand{\\footrulewidth}{0pt}
    \\usepackage{titling}
    \\pretitle{\\begin{center}\\vspace*{2cm}\\Huge\\bfseries}
    \\posttitle{\\end{center}\\vspace{1cm}}
    \\preauthor{\\begin{center}\\large}
    \\postauthor{\\end{center}}
    \\predate{\\begin{center}\\large}
    \\postdate{\\end{center}\\vfill}
---
"""


def strip_navigation(text: str) -> str:
    """Remove navigation links and surrounding horizontal rules."""
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        s = line.strip()
        if s.startswith("←") or s.startswith("[←"):
            continue
        if re.match(r"^\[?←.*→\]?\(", s):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def strip_duplicate_hrs(text: str) -> str:
    """Collapse multiple consecutive horizontal rules."""
    return re.sub(r"(\n---\n)+", "\n---\n", text)


def make_refs_subsection(text: str) -> str:
    """Convert ## References to a smaller heading so it doesn't clutter TOC."""
    return text.replace("## References", "#### References")


def process_module(filepath: Path) -> str:
    """Read and clean a module markdown file."""
    text = filepath.read_text()
    text = strip_navigation(text)
    text = strip_duplicate_hrs(text)
    text = make_refs_subsection(text)
    # Remove standalone --- lines (they become LaTeX \\rule which looks odd)
    text = re.sub(r"^\s*---\s*$", "", text, flags=re.MULTILINE)
    return text.strip()


def build_combined_markdown() -> str:
    """Combine YAML header + all modules into a single markdown string."""
    parts = [YAML_HEADER]

    for filename in MODULE_FILES:
        filepath = MODULES_DIR / filename
        content = process_module(filepath)
        parts.append(content)
        parts.append("")  # blank line between modules

    return "\n\n".join(parts)


def main():
    combined = build_combined_markdown()
    output = COURSE_DIR / "context-engineering-course.pdf"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, dir=COURSE_DIR
    ) as f:
        f.write(combined)
        tmp_path = f.name

    try:
        cmd = [
            "pandoc",
            tmp_path,
            "-o", str(output),
            "--pdf-engine=tectonic",
            "--standalone",
        ]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            print(f"pandoc stderr:\n{result.stderr}")
            return 1

        size_kb = output.stat().st_size / 1024
        print(f"PDF generated: {output} ({size_kb:.0f} KB)")
        return 0

    finally:
        Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    exit(main())
