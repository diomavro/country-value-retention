"""Download the Central Bank of Cyprus files (SPE definition, BoP/FDI cross-checks).

python -m cvr.ingest.cbc
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

from ..catalogue import CBC, CBC_FILES, cbc_manifest


def main() -> None:
    CBC.mkdir(parents=True, exist_ok=True)
    for name, (_, url) in CBC_FILES.items():
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        Path(CBC / name).write_bytes(urllib.request.urlopen(req, timeout=120).read())
        print(name)
    cbc_manifest()


if __name__ == "__main__":
    main()
