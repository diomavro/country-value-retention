"""Markdown edition of the paper, generated from paper/main.tex (the LaTeX is the source)."""

from __future__ import annotations

import os
import re
from pathlib import Path

import pypandoc

PAPER = Path("paper")


def _title_block(abstract: str) -> str:
    return (
        "# Who Captures the Value Generated in Cyprus?\n\n"
        "## A Recipient-Country Accounting of Domestic Value Retention and Foreign Leakage\n\n"
        "Diomides Mavroyiannis (Milestone Institute, Budapest) — data release v0.1, September 2026\n\n"
        "**Abstract.** " + abstract.strip() + "\n\n"
    )


def main() -> None:
    cwd = os.getcwd()
    os.chdir(PAPER)
    try:
        md = pypandoc.convert_file(
            "main.tex",
            "gfm",
            format="latex",
            extra_args=["--citeproc", "--bibliography=references.bib", "--wrap=none", "--resource-path=.:figures"],
        )
    finally:
        os.chdir(cwd)
    md = re.sub(r"\]\(figures/([\w-]+)\.pdf\)", r"](figures/\1.png)", md)  # PNGs render on GitHub
    # cleveref references arrive as bare numbers; restore the noun from the label prefix
    kinds = {"sec": "Section", "app": "Appendix", "fig": "Figure", "tab": "Table", "eq": "Equation"}
    md = re.sub(
        r'<a href="#(sec|app|fig|tab|eq):[^"]*"[^>]*>([^<]*)</a>',
        lambda m: f"{kinds[m.group(1)]} {m.group(2)}",
        md,
    )
    # title and abstract (dropped by pandoc's gfm writer), taken from the compiled PDF's source
    tex = (PAPER / "main.tex").read_text()
    # macros are defined in numbers.tex, so prepend it for the stand-alone conversion
    abstract = pypandoc.convert_text(
        "\\newcommand{\\EUR}{EUR~}\n"  # defined in the main.tex preamble, which is not converted here
        + (PAPER / "numbers.tex").read_text() + re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S).group(1),
        "gfm",
        format="latex",
        extra_args=["--wrap=none"],
    )
    md = _title_block(abstract) + md
    header = "<!-- Generated from paper/main.tex by src/cvr/paper_markdown.py; edit the LaTeX, not this file. -->\n\n"
    (PAPER / "main.md").write_text(header + md)
    print(f"paper/main.md: {len(md.split())} words")


if __name__ == "__main__":
    main()
