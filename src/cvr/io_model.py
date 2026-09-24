"""Single-country input-output engine with separate domestic and imported input blocks.

Notation (all flows in the same currency unit, n products or industries):

    Zd  n x n   domestic intermediate use (row = supplying product, col = using industry)
    Zm  n x n   imported intermediate use
    t   n       net taxes on products paid on intermediate inputs, by using column
    v   n       gross value added by column
    x   n       output by column  (x = 1'Zd + 1'Zm + t + v)

    Ad = Zd diag(x)^-1,  Am = Zm diag(x)^-1,  L = (I - Ad)^-1

Column identity: 1'Ad + 1'Am + t/x + v/x = 1', so for final demand of
domestic output the propagated shares satisfy  vL + mL + tL = 1'  (value added,
imported inputs and product taxes exhaust each euro).  Imported inputs are
counted once, as imports; foreign value added *embodied* in those imports is a
decomposition of the same euros, never an addition to them.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

TOL = 1e-6


class AccountingIdentityError(AssertionError):
    """Raised when an input-output accounting identity is violated."""


@dataclass(frozen=True)
class IOTable:
    labels: list[str]
    Zd: np.ndarray
    Zm: np.ndarray
    t: np.ndarray
    v: np.ndarray
    x: np.ndarray

    def __post_init__(self) -> None:
        n = len(self.labels)
        for name in ("Zd", "Zm"):
            if getattr(self, name).shape != (n, n):
                raise ValueError(f"{name} must be {n}x{n}")
        for name in ("t", "v", "x"):
            if getattr(self, name).shape != (n,):
                raise ValueError(f"{name} must have length {n}")

    @property
    def n(self) -> int:
        return len(self.labels)

    def check_column_identity(self, rel_tol: float = 1e-4) -> np.ndarray:
        """Output = domestic inputs + imported inputs + product taxes + value added."""
        gap = self.x - (self.Zd.sum(0) + self.Zm.sum(0) + self.t + self.v)
        scale = np.maximum(np.abs(self.x), 1.0)
        bad = np.abs(gap) > rel_tol * scale
        if bad.any():
            worst = [(self.labels[i], float(gap[i])) for i in np.flatnonzero(bad)[:5]]
            raise AccountingIdentityError(
                f"column identity fails for {bad.sum()} columns: {worst}"
            )
        return gap


@dataclass(frozen=True)
class IOResult:
    labels: list[str]
    Ad: np.ndarray
    Am: np.ndarray
    L: np.ndarray
    va_coef: np.ndarray  # v/x
    tax_coef: np.ndarray  # t/x
    direct_import_share: np.ndarray  # imported / total intermediate inputs, by column
    direct_import_intensity: np.ndarray  # imported inputs per unit output
    total_import_content: np.ndarray  # 1'Am L : imports embodied per unit final demand
    total_va_content: np.ndarray  # (v/x) L
    total_tax_content: np.ndarray  # (t/x) L


def _safe_div(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    out = np.zeros_like(a, dtype=float)
    np.divide(a, b, out=out, where=b != 0)
    return out


def solve(table: IOTable, check: bool = True) -> IOResult:
    if check:
        table.check_column_identity()
    x = table.x.astype(float)
    Ad = _safe_div(table.Zd, x[None, :])
    Am = _safe_div(table.Zm, x[None, :])
    va = _safe_div(table.v, x)
    tx = _safe_div(table.t, x)
    if np.any(Ad.sum(0) >= 1 - 1e-9):
        raise AccountingIdentityError(
            "domestic coefficient column sum >= 1: Leontief inverse not productive"
        )
    L = np.linalg.inv(np.eye(table.n) - Ad)
    if check and (L < -TOL).any():
        raise AccountingIdentityError("Leontief inverse has negative entries")
    inter = table.Zd.sum(0) + table.Zm.sum(0)
    res = IOResult(
        labels=list(table.labels),
        Ad=Ad,
        Am=Am,
        L=L,
        va_coef=va,
        tax_coef=tx,
        direct_import_share=_safe_div(table.Zm.sum(0), inter),
        direct_import_intensity=Am.sum(0),
        total_import_content=Am.sum(0) @ L,
        total_va_content=va @ L,
        total_tax_content=tx @ L,
    )
    if check:
        check_exhaustion(res, active=x > 0)
    return res


def check_exhaustion(res: IOResult, active: np.ndarray | None = None) -> np.ndarray:
    """Each euro of final demand is exhausted by domestic VA + imports + product taxes."""
    total = res.total_va_content + res.total_import_content + res.total_tax_content
    gap = total - 1.0
    mask = np.ones_like(gap, dtype=bool) if active is None else active
    if np.any(np.abs(gap[mask]) > 1e-6):
        i = int(np.argmax(np.abs(np.where(mask, gap, 0))))
        raise AccountingIdentityError(
            f"VA+import+tax content != 1 for {res.labels[i]}: {total[i]:.8f}"
        )
    return gap


def decompose_final_demand(res: IOResult, f: np.ndarray) -> dict[str, float]:
    """Split a final-demand vector for domestic output into VA, imported inputs, product taxes."""
    f = np.asarray(f, dtype=float)
    out = {
        "final_demand": float(f.sum()),
        "domestic_value_added": float(res.total_va_content @ f),
        "imported_inputs": float(res.total_import_content @ f),
        "product_taxes_on_inputs": float(res.total_tax_content @ f),
    }
    parts = (
        out["domestic_value_added"]
        + out["imported_inputs"]
        + out["product_taxes_on_inputs"]
    )
    if abs(parts - out["final_demand"]) > 1e-6 * max(1.0, abs(out["final_demand"])):
        raise AccountingIdentityError(
            "final-demand decomposition does not exhaust final demand"
        )
    return out
