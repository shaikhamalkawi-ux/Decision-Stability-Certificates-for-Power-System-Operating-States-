#!/usr/bin/env python3
"""Verify a DSC-Grid package against its internal SHA-256 manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    package = args.package.resolve()
    manifest = package / "manifests" / "PACKAGE_SHA256_MANIFEST.csv"
    failures = []
    checked = 0
    with manifest.open(newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            checked += 1
            path = package / Path(row["path"])
            if not path.is_file():
                failures.append({"path": row["path"], "error": "missing"})
                continue
            actual = sha256(path)
            if actual.lower() != row["sha256"].lower():
                failures.append({"path": row["path"], "error": "hash mismatch",
                                 "expected": row["sha256"], "actual": actual})
    result = {
        "package": str(package),
        "manifest_records_checked": checked,
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
    }
    text = json.dumps(result, indent=2)
    print(text)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
