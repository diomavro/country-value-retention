"""Reproducible Eurostat downloader (SDMX 2.1 REST, SDMX-CSV) -> Parquet + MANIFEST.

Usage
-----
    python -m cvr.ingest.eurostat                     # all jobs, geo=CY
    python -m cvr.ingest.eurostat --geo CY,MT,IE      # several reporters
    python -m cvr.ingest.eurostat --only bop_c6_a     # subset of jobs (by code or job name)
    python -m cvr.ingest.eurostat --list              # show the job list

Every observation keeps Eurostat's OBS_FLAG (p, e, b, d, u, ...) and CONF_STATUS
(C = confidential, suppressed) columns. Confidential cells come back with
OBS_VALUE = NaN and CONF_STATUS = 'C'; do not treat them as zero.

The SDMX 2.1 endpoint ignores query-string dimension filters; filtering is done
through the positional series key, built here from the dataset's DSD so callers
pass filters by dimension name.  Eurostat refuses extractions whose *estimated*
cube size exceeds 5M cells (HTTP 413); `fetch` then splits the period range in
halves recursively and concatenates the pieces.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import functools
import hashlib
import io
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "eurostat"
MANIFEST = RAW_DIR / "MANIFEST.csv"
MANIFEST_COLUMNS = [
    "file",
    "dataset_code",
    "dataset_title",
    "provider",
    "url",
    "filters",
    "download_date",
    "sha256",
    "rows",
    "last_update",
]
SDMX = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1"
MAX_RAW_BYTES = 300 * 1024**2  # project disk rule: never keep a raw file > 300 MB
TIMEOUT = 600

EU27 = (
    "AT BE BG CY CZ DE DK EE EL ES FI FR HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK"
).split()


class EurostatError(RuntimeError):
    pass


class NoData(EurostatError):
    pass


class TooBig(EurostatError):
    pass


# ---------------------------------------------------------------- metadata
@functools.lru_cache(maxsize=None)
def dimensions(code: str) -> tuple[str, ...]:
    """Dimension ids of `code` in DSD key order (TIME_PERIOD excluded)."""
    r = requests.get(f"{SDMX}/datastructure/ESTAT/{code}", timeout=TIMEOUT)
    r.raise_for_status()
    dims = re.findall(r'<s:Dimension id="(\w+)"[^>]*position="(\d+)"', r.text)
    if not dims:
        raise EurostatError(f"no dimensions parsed for {code}")
    return tuple(d for d, _ in sorted(dims, key=lambda x: int(x[1])))


@functools.lru_cache(maxsize=None)
def title(code: str) -> str:
    r = requests.get(f"{SDMX}/dataflow/ESTAT/{code}", timeout=TIMEOUT)
    r.raise_for_status()
    m = re.search(r'<c:Name xml:lang="en">([^<]*)</c:Name>', r.text)
    return m.group(1) if m else ""


# ---------------------------------------------------------------- helpers
def _as_list(v) -> list[str]:
    return [v] if isinstance(v, str) else list(v)


@functools.lru_cache(maxsize=None)
def available(code: str) -> dict[str, frozenset[str]]:
    """Codes actually present per dimension (Eurostat 'Actual' content constraint)."""
    r = requests.get(f"{SDMX}/contentconstraint/ESTAT/{code}", timeout=TIMEOUT)
    r.raise_for_status()
    out = {}
    for dim, body in re.findall(
        r'<c:KeyValue id="(\w+)">(.*?)</c:KeyValue>', r.text, re.S
    ):
        out[dim] = frozenset(re.findall(r"<c:Value>([^<]*)</c:Value>", body))
    return out


def constrain(code: str, filters: dict) -> tuple[dict, dict]:
    """Drop filter values absent from the dataset (Eurostat rejects the whole query
    otherwise, e.g. geo=CY in naio_10_cp1750). Returns (kept, dropped)."""
    dims = dimensions(code)
    unknown = set(filters) - set(dims)
    if unknown:
        raise ValueError(
            f"{code}: unknown dimension(s) {sorted(unknown)}; DSD has {dims}"
        )
    avail = available(code)
    kept, dropped = {}, {}
    for d, v in filters.items():
        vals = _as_list(v)
        ok = [x for x in vals if d not in avail or x in avail[d]]
        if len(ok) < len(vals):
            dropped[d] = [x for x in vals if x not in ok]
        if not ok:
            raise NoData(f"{code}: none of {d}={vals} exist in this dataset")
        kept[d] = ok
    return kept, dropped


def build_url(code: str, filters: dict, start=None, end=None) -> str:
    dims = dimensions(code)
    unknown = set(filters) - set(dims)
    if unknown:
        raise ValueError(
            f"{code}: unknown dimension(s) {sorted(unknown)}; DSD has {dims}"
        )
    key = ".".join("+".join(_as_list(filters[d])) if d in filters else "" for d in dims)
    url = f"{SDMX}/data/{code}/{key}/?format=SDMX-CSV&compressed=false"
    if start is not None:
        url += f"&startPeriod={start}"
    if end is not None:
        url += f"&endPeriod={end}"
    return url


def slugify(filters: dict, start=None, end=None) -> str:
    parts = [f"{k}-{'+'.join(sorted(_as_list(v)))}" for k, v in sorted(filters.items())]
    if start or end:
        parts.append(f"t-{start or ''}-{end or ''}")
    slug = re.sub(r"[^A-Za-z0-9+._-]", "", "_".join(parts)) or "all"
    if len(slug) > 80:  # long item lists: keep the readable head, disambiguate by hash
        slug = slug[:60] + "_" + hashlib.sha1(slug.encode()).hexdigest()[:10]
    return slug


ASYNC = "https://ec.europa.eu/eurostat/api/dissemination/1.0/async"
ASYNC_POLL_S = 10
ASYNC_MAX_WAIT_S = 3600


def _get_capped(url: str) -> tuple[int, bytes]:
    """GET `url`, refusing bodies larger than MAX_RAW_BYTES."""
    with requests.get(url, timeout=TIMEOUT, stream=True) as r:
        buf = io.BytesIO()
        for chunk in r.iter_content(1 << 20):
            buf.write(chunk)
            if buf.tell() > MAX_RAW_BYTES:
                raise TooBig(
                    f"response exceeds {MAX_RAW_BYTES >> 20} MB cap; filter further"
                )
        return r.status_code, buf.getvalue()


def _download(url: str) -> bytes:
    """SDMX-CSV bytes for `url`, following Eurostat's asynchronous-extraction protocol.

    Large extractions are answered with a SOAP envelope holding a queue id; the
    file is then polled at {ASYNC}/status/<id> and fetched from {ASYNC}/data/<id>.
    """
    status, data = _get_capped(url)
    if status != 200:
        body = data[:2000].decode(errors="replace")
        m = re.search(r"<faultstring>(.*?)</faultstring>", body, re.S)
        msg = m.group(1) if m else body[:300]
        if status == 413 or "EXTRACTION_TOO_BIG" in msg:
            raise TooBig(msg)
        if status == 404 or "NO_RECORDS_FOUND" in msg or "No results" in msg:
            raise NoData(msg)
        raise EurostatError(f"HTTP {status}: {msg}")
    if data.lstrip().startswith(b"<"):
        m = re.search(rb"<queued>\s*<id>([^<]+)</id>", data)
        if not m:
            raise EurostatError(f"expected CSV, got XML: {data[:300]!r}")
        job = m.group(1).decode()
        waited = 0
        while True:
            st = requests.get(f"{ASYNC}/status/{job}", timeout=TIMEOUT).text
            state = re.search(r"<ns1:status>([A-Z_]+)</ns1:status>", st)
            state = state.group(1) if state else "UNKNOWN"
            if state == "AVAILABLE":
                break
            if state not in ("SUBMITTED", "PROCESSING", "QUEUED", "UNKNOWN"):
                raise EurostatError(f"async job {job} ended in state {state}")
            if waited >= ASYNC_MAX_WAIT_S:
                raise EurostatError(f"async job {job} not ready after {waited}s")
            time.sleep(ASYNC_POLL_S)
            waited += ASYNC_POLL_S
        status, data = _get_capped(f"{ASYNC}/data/{job}")
        if status != 200 or data.lstrip().startswith(b"<"):
            raise EurostatError(f"async job {job}: HTTP {status}: {data[:300]!r}")
    return data


def _read_csv(data: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(data), dtype=str, keep_default_na=False, na_values=[""])
    if df.empty:
        return df
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    return df.rename(columns={"LAST UPDATE": "LAST_UPDATE"})


def _period_bounds(code: str, start, end) -> tuple[int, int]:
    """Integer year bounds for splitting; defaults from the catalogue if absent."""
    if start is None or end is None:
        lo, hi = _catalogue_years(code)
        start = start if start is not None else lo
        end = end if end is not None else hi
    return int(str(start)[:4]), int(str(end)[:4])


@functools.lru_cache(maxsize=None)
def _catalogue_years(code: str) -> tuple[int, int]:
    r = requests.get(
        "https://ec.europa.eu/eurostat/api/dissemination/catalogue/toc/txt?lang=en",
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    for row in csv.reader(io.StringIO(r.text), delimiter="\t"):
        if len(row) > 6 and row[1] == code:
            return int(row[5][:4]), int(row[6][:4])
    raise EurostatError(f"{code} not in Eurostat catalogue")


def _fetch_frame(
    code: str, filters: dict, start, end
) -> tuple[pd.DataFrame, list[str]]:
    """Download, splitting the period range on 413. Returns (frame, urls)."""
    url = build_url(code, filters, start, end)
    try:
        return _read_csv(_download(url)), [url]
    except NoData:
        return pd.DataFrame(), [url]
    except TooBig:
        lo, hi = _period_bounds(code, start, end)
        if lo >= hi:
            raise
        mid = (lo + hi) // 2
        a, ua = _fetch_frame(code, filters, lo, mid)
        b, ub = _fetch_frame(code, filters, mid + 1, hi)
        return pd.concat([a, b], ignore_index=True), ua + ub


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _append_manifest(row: dict) -> None:
    """Append `row`; an earlier row for the same file is replaced (re-runs stay 1 row/file)."""
    rows = []
    if MANIFEST.exists():
        with open(MANIFEST, newline="") as f:
            rows = [r for r in csv.DictReader(f) if r["file"] != row["file"]]
    rows.append(row)
    with open(MANIFEST, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS)
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------- public API
def fetch(
    code: str,
    filters: dict,
    out_path: str | Path | None = None,
    *,
    start=None,
    end=None,
) -> Path:
    """Download `code` filtered by `filters` ({dim: code or [codes]}) as Parquet.

    `start`/`end` are SDMX startPeriod/endPeriod (e.g. 2010, "2010-Q1").
    Writes data/raw/eurostat/<code>__<slug>.parquet unless `out_path` is given,
    and records the file in MANIFEST.csv. Raises NoData if nothing matches.
    """
    requested = filters
    filters, dropped = constrain(code, filters)
    if dropped:
        print(f"WARN {code}: not in dataset, dropped {dropped}", file=sys.stderr)
    df, urls = _fetch_frame(code, filters, start, end)
    if df.empty:
        raise NoData(f"{code}: no observations for {filters} [{start}-{end}]")
    out = (
        Path(out_path)
        if out_path
        else RAW_DIR / f"{code}__{slugify(requested, start, end)}.parquet"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    last = ""
    if "LAST_UPDATE" in df:  # 'dd/mm/yy HH:MM:SS' -> ISO date
        stamps = pd.to_datetime(
            df["LAST_UPDATE"], format="%d/%m/%y %H:%M:%S", errors="coerce"
        )
        last = stamps.max().date().isoformat() if stamps.notna().any() else ""
    try:
        rel = out.resolve().relative_to(PROJECT_ROOT)
    except ValueError:
        rel = out.resolve()
    _append_manifest(
        {
            "file": str(rel),
            "dataset_code": code,
            "dataset_title": title(code),
            "provider": "Eurostat",
            "url": " | ".join(urls),
            "filters": repr(
                {k: _as_list(v) for k, v in sorted(filters.items())}
                | {"startPeriod": start, "endPeriod": end}
                | ({"dropped_absent": dropped} if dropped else {})
            ),
            "download_date": dt.date.today().isoformat(),
            "sha256": _sha256(out),
            "rows": len(df),
            "last_update": last,
        }
    )
    return out


# ---------------------------------------------------------------- job list
BOP_PRIMARY = [
    "CA",
    "IN1",
    "IN2",
    "D1",
    "D4P__F",
    "D4P__D__F",
    "D4S__D__F5",
    "D42S__D__F5",
    "D43S__D__F5",
    "D4Q__D__FL",
    "D41__D__FLA",
    "D4P__P__F",
    "D4S__P__F5",
    "D42__P__F51",
    "D443__P__F52",
    "D41__P__F3",
    "D4P__O__F",
    "D41__O__FLA",
    "D44P__O__F6",
    "D4P__R__F",
    "D4O",
    "D2",
    "D3",
    "D45",
]

# (job name, dataset code, filters, start, end, eu)
# A filter value of "{geo}" is replaced by the reporter list at run time.
# eu=True: also pull the EU27_2020 aggregate; eu="EU": the job *is* an EU-aggregate
# pull (fixed geo). Both are skipped with --no-eu-aggregate.
JOBS: list[tuple] = [
    # 1. National accounts ----------------------------------------------------
    (
        "gdp_income",
        "nama_10_gdp",
        {"geo": "{geo}", "unit": ["CP_MEUR", "CLV20_MEUR"]},
        2010,
        None,
        True,
    ),
    ("gni_pc", "nama_10_pp", {"geo": "{geo}"}, None, None, False),
    (
        "sector_nf",
        "nasa_10_nf_tr",
        {
            "geo": "{geo}",
            "unit": "CP_MEUR",
            "sector": ["S1", "S11", "S12", "S13", "S14_S15", "S2"],
        },
        2010,
        None,
        True,
    ),
    (
        "gva_a64",
        "nama_10_a64",
        {"geo": "{geo}", "unit": ["CP_MEUR", "CLV20_MEUR"]},
        2010,
        None,
        False,
    ),
    (
        "emp_a64",
        "nama_10_a64_e",
        {
            "geo": "{geo}",
            "unit": ["THS_PER", "THS_HW"],
            "na_item": ["EMP_DC", "SAL_DC", "SELF_DC"],
        },
        2010,
        None,
        False,
    ),
    # 2. National SUT / SIOT (all years) --------------------------------------
    ("sup", "naio_10_cp15", {"geo": "{geo}", "unit": "MIO_EUR"}, None, None, False),
    ("use_pp", "naio_10_cp16", {"geo": "{geo}", "unit": "MIO_EUR"}, None, None, False),
    (
        "use_bp",
        "naio_10_cp1610",
        {"geo": "{geo}", "unit": "MIO_EUR"},
        None,
        None,
        False,
    ),
    (
        "margins",
        "naio_10_cp1620",
        {"geo": "{geo}", "unit": "MIO_EUR"},
        None,
        None,
        False,
    ),
    ("taxes", "naio_10_cp1630", {"geo": "{geo}", "unit": "MIO_EUR"}, None, None, False),
    (
        "siot_pxp",
        "naio_10_cp1700",
        {"geo": "{geo}", "unit": "MIO_EUR"},
        None,
        None,
        False,
    ),
    (
        "siot_ixi",
        "naio_10_cp1750",
        {"geo": "{geo}", "unit": "MIO_EUR"},
        None,
        None,
        False,
    ),
    # 3. FIGARO: reporter's slices of the inter-country IxI table + TiVA indicators
    ("figaro_ii_in", "naio_10_fcp_ii4", {"c_dest": "{geo}"}, None, None, False),
    ("figaro_ii_out", "naio_10_fcp_ii4", {"c_orig": "{geo}"}, None, None, False),
    ("figaro_ii3_in", "naio_10_fcp_ii3", {"c_dest": "{geo}"}, None, None, False),
    ("figaro_ii3_out", "naio_10_fcp_ii3", {"c_orig": "{geo}"}, None, None, False),
    ("figaro_ii2_in", "naio_10_fcp_ii2", {"c_dest": "{geo}"}, None, None, False),
    ("figaro_ii2_out", "naio_10_fcp_ii2", {"c_orig": "{geo}"}, None, None, False),
    ("figaro_ii1_in", "naio_10_fcp_ii1", {"c_dest": "{geo}"}, None, None, False),
    ("figaro_ii1_out", "naio_10_fcp_ii1", {"c_orig": "{geo}"}, None, None, False),
    ("fva_fd", "naio_10_fgfd", {"geo": "{geo}"}, None, None, False),
    ("dva_ffd", "naio_10_fgdf", {"geo": "{geo}"}, None, None, False),
    ("dva_exp", "naio_10_fgdm", {"geo": "{geo}"}, None, None, False),
    ("fva_exp_orig", "naio_10_fgfoem", {"geo": "{geo}"}, None, None, False),
    ("imp_ind", "naio_10_fgti", {"geo": "{geo}"}, None, None, False),
    ("exp_ind", "naio_10_fgte", {"geo": "{geo}"}, None, None, False),
    ("gvc_part", "naio_10_fggvcm", {"geo": "{geo}"}, None, None, False),
    # 4. BoP primary income by partner -----------------------------------------
    (
        "bop_pi",
        "bop_c6_a",
        {
            "geo": "{geo}",
            "currency": "MIO_EUR",
            "bop_item": BOP_PRIMARY,
            "sector10": "S1",
            "sectpart": "S1",
            "stk_flow": ["CRE", "DEB", "BAL"],
        },
        2010,
        None,
        False,
    ),
    # bop_c6_a has no EU aggregate; the EU27 extra-EU BoP lives in bop_eu6_q.
    (
        "bop_pi_eu",
        "bop_eu6_q",
        {
            "geo": "EU27_2020",
            "freq": "A",
            "currency": "MIO_EUR",
            "bop_item": BOP_PRIMARY,
            "sector10": "S1",
            "sectpart": "S1",
            "s_adj": "NSA",
            "stk_flow": ["CRE", "DEB", "BAL"],
        },
        2010,
        None,
        "EU",
    ),
    (
        "bop_pi_sector",
        "bop_c6_a",
        {
            "geo": "{geo}",
            "currency": "MIO_EUR",
            "bop_item": BOP_PRIMARY,
            "partner": ["WRL_REST", "EU27_2020", "EXT_EU27_2020"],
            "stk_flow": ["CRE", "DEB", "BAL"],
        },
        2010,
        None,
        False,
    ),
    ("bop_rem", "bop_rem6", {"geo": "{geo}", "currency": "MIO_EUR"}, 2010, None, False),
    (
        "fdi_inc",
        "bop_fdi6_inc",
        {"geo": "{geo}", "currency": "MIO_EUR", "nace_r2": "FDI"},
        None,
        None,
        False,
    ),
    (
        "fdi_inc_nace",
        "bop_fdi6_inc",
        {
            "geo": "{geo}",
            "currency": "MIO_EUR",
            "partner": ["WRL_REST", "EU27_2020", "EXT_EU27_2020"],
        },
        None,
        None,
        False,
    ),
    ("fdi_geo", "bop_fdi6_geo", {"geo": "{geo}"}, None, None, False),
    # 5. FDI positions: immediate vs ultimate counterpart, SPE split -----------
    (
        "fdi_pos",
        "bop_fdi6_pos",
        {"geo": "{geo}", "currency": "MIO_EUR", "nace_r2": "FDI"},
        None,
        None,
        False,
    ),
    (
        "fdi_pos_nace",
        "bop_fdi6_pos",
        {
            "geo": "{geo}",
            "currency": "MIO_EUR",
            "partner": ["WRL_REST", "EU27_2020", "EXT_EU27_2020"],
        },
        None,
        None,
        False,
    ),
    # 6. Inward FATS -------------------------------------------------------------
    ("fats_activ", "fats_activ", {"geo": "{geo}"}, None, None, False),
    ("fats_ctrl", "fats_ctrl", {"geo": "{geo}"}, None, None, False),
    ("fats_g1a_08", "fats_g1a_08", {"geo": "{geo}"}, None, None, False),
    ("fats_g1b_08", "fats_g1b_08", {"geo": "{geo}"}, None, None, False),
    # 7. Commuting / cross-border work -------------------------------------------
    ("commute", "lfst_r_lfe2ecomm", {"geo": "{geo}"}, None, None, False),
    # Citizenship is NOT residence: LFS covers residents only, so cross-border
    # in-commuters are absent; this splits resident employment by nationality.
    (
        "emp_citizen",
        "lfsa_egan",
        {"geo": "{geo}", "sex": "T", "age": ["Y15-64", "Y20-64", "Y_GE15"]},
        2010,
        None,
        False,
    ),
]


# ---------------------------------------------------------------- FIGARO bulk
# The full inter-country tables are not practical through the dissemination API
# (naio_10_fcp_ii* hold ~44M cells per 4-year block; the API caps at 5M), but
# Eurostat publishes them as files in the public CIRCABC group "Integrated Global
# Accounts Expert Group" > Library > FIGARO database > <edition>. The guest REST
# API lists folders; files download from /rest/download/<node id>.
CIRCABC = "https://circabc.europa.eu"
FIGARO_FOLDERS = {  # 2026 edition (26ed, years 2010-2024)
    "ind-by-ind": "e6896a70-5dbf-479c-8852-94b5dd1e3952",  # CSV matrix, 64 industries
}


def circabc_list(folder_id: str) -> list[dict]:
    r = requests.get(
        f"{CIRCABC}/service/circabc/spaces/{folder_id}/children",
        params=dict(
            language="en",
            guest="true",
            limit=500,
            page=1,
            order="name_ASC",
            folderOnly="false",
            fileOnly="false",
            skipExpiredItems="true",
        ),
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    js = r.json()
    return js.get("data", js)


def fetch_figaro_matrix(year: int, table: str = "ind-by-ind") -> Path:
    """Download one year of the FIGARO inter-country IO table (CSV matrix layout,
    ~50 MB) and store it as Parquet (rows = rowLabels, columns = country_industry)."""
    files = [
        f
        for f in circabc_list(FIGARO_FOLDERS[table])
        if f["name"].endswith(f"_{year}.csv")
    ]
    if len(files) != 1:
        raise NoData(f"FIGARO {table} {year}: found {[f['name'] for f in files]}")
    node = files[0]
    url = f"{CIRCABC}/rest/download/{node['id']}"
    status, data = _get_capped(url)
    if status != 200:
        raise EurostatError(f"HTTP {status} for {url}")
    src_sha = hashlib.sha256(data).hexdigest()
    df = pd.read_csv(io.BytesIO(data), index_col=0)
    df.index.name = "rowLabels"
    out = RAW_DIR / "figaro" / node["name"].replace(".csv", ".parquet")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out)
    _append_manifest(
        {
            "file": str(out.relative_to(PROJECT_ROOT)),
            "dataset_code": f"FIGARO_{table}_matrix",
            "dataset_title": f"FIGARO EU inter-country IO table, {table}, {year} (CIRCABC file {node['name']})",
            "provider": "Eurostat",
            "url": url,
            "filters": repr(
                {"year": year, "source_csv_sha256": src_sha, "source_bytes": len(data)}
            ),
            "download_date": dt.date.today().isoformat(),
            "sha256": _sha256(out),
            "rows": len(df),
            "last_update": str((node.get("properties") or {}).get("modified", ""))[:10],
        }
    )
    return out


def _resolve(filters: dict, geos: list[str]) -> dict:
    return {k: (geos if v == "{geo}" else v) for k, v in filters.items()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--geo", default="CY", help="comma-separated reporters, or EU27")
    ap.add_argument(
        "--only", default="", help="comma-separated job names or dataset codes"
    )
    ap.add_argument(
        "--no-eu-aggregate",
        action="store_true",
        help="skip the EU27_2020 aggregate pull for primary-income jobs",
    )
    ap.add_argument("--list", action="store_true")
    ap.add_argument(
        "--raw-dir",
        default=None,
        help="write files and MANIFEST.csv here instead of data/raw/eurostat "
        "(comparison countries go to data/raw/eurostat_eu so they never mix with the Cyprus inputs)",
    )
    ap.add_argument(
        "--figaro-year",
        type=int,
        default=None,
        help="also download the full FIGARO industry-by-industry matrix for this year",
    )
    a = ap.parse_args(argv)
    if a.raw_dir:
        global RAW_DIR, MANIFEST
        RAW_DIR = Path(a.raw_dir).resolve()
        MANIFEST = RAW_DIR / "MANIFEST.csv"
    geos = (
        EU27
        if a.geo.upper() == "EU27"
        else [g.strip() for g in a.geo.split(",") if g.strip()]
    )
    only = {s.strip() for s in a.only.split(",") if s.strip()}
    failures = 0
    for name, code, filters, start, end, eu_agg in JOBS:
        if only and name not in only and code not in only:
            continue
        if eu_agg == "EU":
            runs = [] if a.no_eu_aggregate else [["EU27_2020"]]
        else:
            runs = [geos] + (
                [["EU27_2020"]] if eu_agg and not a.no_eu_aggregate else []
            )
        for g in runs:
            f = _resolve(filters, g)
            if a.list:
                print(f"{name:16s} {code:18s} {f} {start}-{end}")
                continue
            try:
                p = fetch(code, f, start=start, end=end)
                print(
                    f"OK   {name:16s} {code:18s} {g} -> {p.name} ({p.stat().st_size / 1e6:.1f} MB)"
                )
            except NoData as e:
                print(f"NONE {name:16s} {code:18s} {g}: {e}")
            except EurostatError as e:
                failures += 1
                print(f"FAIL {name:16s} {code:18s} {g}: {e}", file=sys.stderr)
    if a.figaro_year and not a.list:
        try:
            p = fetch_figaro_matrix(a.figaro_year)
            print(
                f"OK   figaro_matrix {a.figaro_year} -> {p.name} ({p.stat().st_size / 1e6:.1f} MB)"
            )
        except EurostatError as e:
            failures += 1
            print(f"FAIL figaro_matrix {a.figaro_year}: {e}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
