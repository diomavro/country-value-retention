"""Numbers written by hand in README and docs must match the generated paper macros.

Why: the paper and dashboard are generated, but prose in README.md and docs/ is typed. When the
data or method changes, these tests name every sentence that has gone stale.
"""

import re
from pathlib import Path

import pytest

NUMBERS = Path("paper/numbers.tex")
pytestmark = pytest.mark.skipif(
    not NUMBERS.exists(), reason="paper numbers not generated"
)


def macro(name: str) -> str:
    m = re.search(r"\\newcommand\{\\" + name + r"\}\{(.*?)\}\n", NUMBERS.read_text())
    assert m, name
    return m.group(1).replace("\\%", "%").replace("{,}", ",")


def text(path: str) -> str:
    return Path(path).read_text()


@pytest.mark.parametrize(
    "path, template",
    [
        ("README.md", "**{OfficialOutLast} of GDP**"),
        ("README.md", "is about **{FVLLast} of GDP**"),
        ("docs/concepts.md", "| Cyprus | 10.5 | {OfficialOutLast_} | {FVLLast_} |"),
        ("docs/concepts.md", "about {RecUnknownShare} of the"),
        (
            "docs/limitations.md",
            "Retention moves by about {SensThetaSpreadPP} pp of GDP",
        ),
        ("docs/limitations.md", "understated by about {InsAuxShareFirstFats} of GDP"),
        ("docs/limitations.md", "€{IrishFinBoundFirst}–{IrishFinBoundLast}m a year"),
        ("docs/methodology.md", "€{IrishFinBoundFirst}–{IrishFinBoundLast}m a year"),
        ("docs/limitations.md", "{ConfFatsLow_}–{ConfFatsHigh} of FATS cells"),
        ("docs/limitations.md", "and {ConfFdi} of FDI-income cells"),
        (
            "README.md",
            "{ConfFatsLow_}–{ConfFatsHigh} of FATS cells (and {ConfFdi} of FDI-income cells",
        ),
        (
            "docs/limitations.md",
            "split 2023 bank profit after tax (€{ECBBankAllLast}m) into €{ECBBankDomLast}m for domestic banking groups and €{ECBBankForLast}m for foreign-controlled banks; the BoP figure (€{BankBopLast}m)",
        ),
        ("docs/limitations.md", "is about €{RealEstateFdiAbsMax}m a year or less in absolute value"),
    ],
)
def test_hand_written_number_matches_the_data(path, template):
    def sub(m):
        name = m.group(1)
        v = macro(name.rstrip("_"))
        return v.rstrip("%") if name.endswith("_") else v

    expected = re.sub(r"\{(\w+)\}", sub, template)
    assert expected in text(path), f"{path}: expected '{expected}'"


def test_readme_rounded_retention_matches():
    # "~93%": the headline rounded to a whole percent
    dvr = float(macro("DVRLast").rstrip("%"))
    assert f"**~{round(dvr)}%**" in text("README.md")
