#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# ///
"""Build a PDF book from the course markdown files.

Usage:
    uv run build_pdf.py          # requires pandoc + tectonic installed locally
    uv run build_pdf.py --docker  # uses Docker (no local dependencies needed)
"""

import subprocess
import sys
import tempfile
import re
from pathlib import Path

COURSE_DIR = Path(__file__).parent
MODULES_DIR = COURSE_DIR / "modules"
OUTPUT = COURSE_DIR / "context-engineering-course.pdf"
HEADER_TEX = COURSE_DIR / "header.tex"
METADATA = COURSE_DIR / "metadata.yaml"
IMAGE_NAME = "context-engineering-pdf"


def discover_modules() -> list[Path]:
    """Find module files by convention: modules/NN-*.md, sorted by name."""
    return sorted(MODULES_DIR.glob("[0-9][0-9]-*.md"))


def make_refs_subsection(text: str) -> str:
    """Convert ## References to a smaller heading so it doesn't clutter TOC."""
    return text.replace("## References", "#### References")


def process_module(filepath: Path) -> str:
    """Read and clean a module markdown file for PDF output."""
    text = filepath.read_text()
    text = make_refs_subsection(text)
    text = re.sub(r"^\s*---\s*$", "", text, flags=re.MULTILINE)
    return text.strip()


def build_combined_markdown() -> str:
    """Combine metadata + all modules into a single markdown string."""
    parts = [METADATA.read_text()]
    for filepath in discover_modules():
        parts.append(process_module(filepath))
        parts.append("")
    return "\n\n".join(parts)


def run_pandoc_local(md_path: str) -> int:
    """Run pandoc locally (requires pandoc + tectonic on PATH)."""
    cmd = [
        "pandoc", md_path,
        "-o", str(OUTPUT),
        "--pdf-engine=tectonic",
        "--standalone",
        f"--include-in-header={HEADER_TEX}",
    ]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"pandoc stderr:\n{result.stderr}", file=sys.stderr)
    return result.returncode


def run_pandoc_docker(md_path: str) -> int:
    """Run pandoc via Docker (no local dependencies needed)."""
    print(f"Building Docker image '{IMAGE_NAME}'...")
    build = subprocess.run(
        ["docker", "build", "-t", IMAGE_NAME, str(COURSE_DIR)],
        capture_output=True, text=True, timeout=600,
    )
    if build.returncode != 0:
        print(f"Docker build failed:\n{build.stderr}", file=sys.stderr)
        return build.returncode

    md_name = Path(md_path).name
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{COURSE_DIR}:/course",
        IMAGE_NAME,
        f"/course/{md_name}",
        "-o", f"/course/{OUTPUT.name}",
        "--pdf-engine=xelatex",
        "--standalone",
        f"--include-in-header=/course/{HEADER_TEX.name}",
    ]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"pandoc stderr:\n{result.stderr}", file=sys.stderr)
    return result.returncode


def main():
    use_docker = "--docker" in sys.argv
    combined = build_combined_markdown()

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, dir=COURSE_DIR
    ) as f:
        f.write(combined)
        tmp_path = f.name

    try:
        rc = run_pandoc_docker(tmp_path) if use_docker else run_pandoc_local(tmp_path)
        if rc != 0:
            return rc
        size_kb = OUTPUT.stat().st_size / 1024
        print(f"PDF generated: {OUTPUT} ({size_kb:.0f} KB)")
        return 0
    finally:
        Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    exit(main())
