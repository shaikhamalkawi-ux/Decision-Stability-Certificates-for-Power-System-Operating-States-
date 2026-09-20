#!/usr/bin/env python3
"""Acquire the frozen public Elexon Insights evidence used in DSC-Grid V8.

No API key is required.  The script writes each HTTP response unchanged and
records the exact URL, acquisition timestamp, byte count, and SHA-256 digest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlencode

import requests


BASE = "https://data.elexon.co.uk/bmrs/api/v1"
DATES = ("2023-01-11", "2023-07-12")
DATASETS = ("B1610", "PN", "MELS", "MILS", "MNZT", "MZT", "RURE", "RDRE")
SNAPSHOT_UNITS = (
    "T_KEAD-2", "T_LBAR-1", "T_TORN-2", "T_DRAXX-2", "T_SPLN-1", "T_HRTL-2",
    "T_HEYM28", "T_SHBA-1", "T_PEMB-41", "T_PEMB-11", "T_STAY-1", "T_STAY-3",
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def fetch(session: requests.Session, url: str, destination: Path) -> dict:
    destination.parent.mkdir(parents=True, exist_ok=True)
    acquired = datetime.now(timezone.utc).isoformat()
    with session.get(url, stream=True, timeout=180) as response:
        response.raise_for_status()
        with destination.open("wb") as output:
            for block in response.iter_content(1024 * 1024):
                if block:
                    output.write(block)
        status = response.status_code
    return {
        "file": destination.as_posix(),
        "url": url,
        "acquired_utc": acquired,
        "http_status": status,
        "bytes": destination.stat().st_size,
        "sha256": digest(destination),
    }


def dataset_url(dataset: str, day: str) -> str:
    params = urlencode({
        "from": f"{day}T00:00Z",
        "to": f"{day}T00:00Z",
        "settlementPeriodFrom": 1,
        "settlementPeriodTo": 48,
    })
    return f"{BASE}/datasets/{dataset}/stream?{params}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root = args.output.resolve()
    records = []
    with requests.Session() as session:
        session.headers["User-Agent"] = "DSC-Grid reproducibility acquisition/8"
        records.append(fetch(
            session,
            f"{BASE}/reference/bmunits/all",
            root / f"BMU_REFERENCE_ALL_{datetime.now(timezone.utc).date().isoformat()}.json",
        ))
        for day in DATES:
            for dataset in DATASETS:
                records.append(fetch(
                    session, dataset_url(dataset, day), root / f"{dataset}_{day}.json"
                ))
            for unit in SNAPSHOT_UNITS:
                encoded = quote(unit, safe="")
                stamp = quote(f"{day}T00:00Z", safe="")
                for kind, filename in (
                    ("dynamic", f"dynamic_{unit}_{day}.json"),
                    ("dynamic/rates", f"rates_{unit}_{day}.json"),
                ):
                    url = f"{BASE}/balancing/{kind}?bmUnit={encoded}&snapshotAt={stamp}"
                    records.append(fetch(session, url, root / "snapshots" / filename))
    (root / "acquisition_register.json").write_text(
        json.dumps(records, indent=2), encoding="utf-8"
    )
    print(json.dumps({"files": len(records), "output": str(root)}, indent=2))


if __name__ == "__main__":
    main()
