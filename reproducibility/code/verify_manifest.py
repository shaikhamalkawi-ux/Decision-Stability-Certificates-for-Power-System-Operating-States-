#!/usr/bin/env python3
"""Verify all files recorded by the public snapshot SHA-256 manifest."""
import argparse
import csv
import hashlib
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("package", type=Path)
args = parser.parse_args()
root = args.package.resolve()
manifest = root / "provenance" / "PACKAGE_SHA256_MANIFEST.csv"
failures = []
count = 0
with manifest.open(newline="", encoding="utf-8") as stream:
    for row in csv.DictReader(stream):
        path = (root / row["path"]).resolve()
        if not path.is_relative_to(root):
            failures.append(row["path"] + ": path outside package")
            continue
        if not path.is_file():
            failures.append(row["path"] + ": missing")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != row["sha256"] or path.stat().st_size != int(row["bytes"]):
            failures.append(row["path"] + ": mismatch")
        count += 1
print(f"Checked {count} recorded files; {len(failures)} failure(s).")
for failure in failures:
    print(failure)
raise SystemExit(bool(failures))
