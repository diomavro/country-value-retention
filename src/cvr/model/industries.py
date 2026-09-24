"""Canonical 64-industry classification (CYSTAT SIOT product codes without the CPA_ prefix)."""

from __future__ import annotations

import re

from .suiot import products

# nama_10_a64 / FATS spell ranges differently from the SIOT; map to SIOT spelling.
_NAMA_TO_CANON = {
    "C10-C12": "C10-12",
    "C13-C15": "C13-15",
    "C31_C32": "C31-32",
    "E37-E39": "E37-39",
    "J59_J60": "J59-60",
    "J62_J63": "J62-63",
    "M69_M70": "M69-70",
    "M74_M75": "M74-75",
    "N80-N82": "N80-82",
    "Q87_Q88": "Q87-88",
    "R90-R92": "R90-92",
}


def canon(year: int = 2022) -> list[str]:
    return [p.removeprefix("CPA_") for p in products(year)]


def from_nama(code: str) -> str:
    """nama_10_a64 ('C31_C32'), FIGARO ('C31_32') and FATS spellings -> SIOT spelling ('C31-32')."""
    if code in _NAMA_TO_CANON:
        return _NAMA_TO_CANON[code]
    return re.sub(r"^([A-U]\d\d)_(\d\d)$", r"\1-\2", code)


def section(code: str) -> str:
    return re.match(r"[A-U]", code).group(0)


SECTION_DIVISIONS = {
    "A": range(1, 4), "B": range(5, 10), "C": range(10, 34), "D": range(35, 36), "E": range(36, 40),
    "F": range(41, 44), "G": range(45, 48), "H": range(49, 54), "I": range(55, 57), "J": range(58, 64),
    "K": range(64, 67), "L": range(68, 69), "M": range(69, 76), "N": range(77, 83), "O": range(84, 85),
    "P": range(85, 86), "Q": range(86, 89), "R": range(90, 94), "S": range(94, 97), "T": range(97, 99),
    "U": range(99, 100),
}


def divisions(code: str) -> frozenset[int] | None:
    """NACE 2-digit divisions covered by a code in any of the spellings used here.

    'C10-C12', 'C10-12', 'C31_C32', 'C31_32', 'H52_H53', 'M69-M71', 'K', 'L68A' ...
    Returns None for codes finer than a division (e.g. 'F411') or aggregates spanning
    sections (e.g. 'B-S_X_O_S94'), which the allocation must not use.
    """
    if code in SECTION_DIVISIONS:
        return frozenset(SECTION_DIVISIONS[code])
    m = re.fullmatch(r"([A-U])(\d\d)(?:[A-Z])?(?:[-_]([A-U])?(\d\d))?", code)
    if not m:
        return None
    lo = int(m.group(2))
    hi = int(m.group(4)) if m.group(4) else lo
    if m.group(3) and m.group(3) != m.group(1):
        return None
    return frozenset(range(lo, hi + 1))


def cover(code: str, industries: list[str]) -> list[str] | None:
    """Canonical industries exactly covered by `code`; None if the code cuts across one."""
    d = divisions(code)
    if d is None:
        return None
    members = [k for k in industries if (dk := divisions(k)) is not None and dk <= d]
    union = frozenset().union(*(divisions(k) for k in members)) if members else frozenset()
    return members if members and union == d else None
