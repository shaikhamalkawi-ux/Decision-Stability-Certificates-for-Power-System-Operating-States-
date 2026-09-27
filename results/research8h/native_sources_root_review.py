"""Read-only verification of the exact, licensed offline native addendum."""
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "reproducibility/native_sources"
ZIP = ROOT / ".work/research8h_delivery/DSC_Temporal_Research_2026-09-27_Checkpoint03.zip"


def sha(value):
    return hashlib.sha256(value).hexdigest()


def records(value):
    if isinstance(value, dict):
        if "path" in value and "sha256" in value:
            yield value
        for item in value.values():
            yield from records(item)
    elif isinstance(value, list):
        for item in value:
            yield from records(item)


inventory = list(csv.DictReader((BASE / "FILE_MANIFEST.csv").open(encoding="utf-8", newline="")))
assert sha((BASE / "FILE_MANIFEST.csv").read_bytes()) == "8b18311c646c0ae68d85765c57b690e2db5b5ffc071d1ab1b734b2db88d866b8"
assert len(inventory) == 24
for item in inventory:
    path = (BASE / item["path"]).resolve()
    assert path.is_relative_to(BASE.resolve()) and path.is_file()
    data = path.read_bytes()
    assert len(data) == int(item["bytes"]) and sha(data) == item["sha256"]
binding = json.loads((BASE / "source_bindings.json").read_text(encoding="utf-8"))
assert len(binding["files"]) == 17 and sum(x["bytes"] for x in binding["files"]) == 3734672
manifest_checks = set()
file_checks = []
upstream_url_checks = 0
with zipfile.ZipFile(ZIP) as archive:
    assert sha(ZIP.read_bytes()) == "4e1315dffaa6d02e55db5af225b4b0e9d3a8106ee6ba070c43d0fbad000868c6"
    for item in binding["files"]:
        original, portable = Path(item["original_path"]), BASE / item["portable_path"]
        data = portable.read_bytes()
        assert data == original.read_bytes()
        assert len(data) == item["bytes"] and sha(data) == item["sha256"]
        for ref in item["referencing_manifests"]:
            path = ROOT / ref["path"]
            raw = path.read_bytes() if path.is_file() else archive.read(ref["path"])
            assert sha(raw) == ref["sha256"]
            entries = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))) if ref["path"].endswith(".csv") else list(records(json.loads(raw)))
            selected = [entry for entry in entries if str(entry["path"]).replace("\\", "/") == item["original_path"]]
            assert selected
            assert all(entry["sha256"] == item["sha256"] and int(entry["bytes"]) == item["bytes"] for entry in selected)
            manifest_checks.add(ref["path"])
        if item["category"] == "upstream_RTS_data":
            assert "/GridMod/RTS-GMLC/3ece0d3725c844056132393ee252b3083dd4eab4/" in item["upstream_url"]
            upstream_url_checks += 1
        file_checks.append({"path": item["portable_path"], "sha256": item["sha256"], "referring_manifest_count": len(item["referencing_manifests"])})
notice = BASE / "rts_inputs/raw/RTS-GMLC_v0.2.3/UPSTREAM_README.md"
assert upstream_url_checks == 8
assert sha(notice.read_bytes()) == "9643002ac6b0d0eb85351c8477a3155ec082fd0583a17fb20b9756bc17ecba63"
assert b"DATA USE DISCLAIMER AGREEMENT" in notice.read_bytes()
maps = json.loads((BASE / "path_map.json").read_text(encoding="utf-8"))["maps"]
assert len(maps) == 2 and maps[1]["portable_relative_root"] == "reproducibility/native_sources/rts_inputs"
output = {"status": "PASS_COMPLETE", "native_files": 17, "native_bytes": 3734672, "addendum_payload_files": len(inventory), "referring_manifests_rechecked": len(manifest_checks), "files": file_checks, "upstream_url_checks": upstream_url_checks, "reviewer_correction": "The first review checked bytes and notice but used a mismatching category label, so its upstream URL branch did not execute. This revision requires exactly eight pinned URL checks. Native payloads are unchanged.", "upstream_notice_exact": True, "scope": "Byte provenance and explicit remapping only; no native reconstruction, optimizer, remote checksum or second-machine claim."}
destination = ROOT / "results/research8h/native_sources_root_review_v2.json"
with destination.open("x", encoding="utf-8") as stream:
    json.dump(output, stream, indent=2)
print(json.dumps({key: value for key, value in output.items() if key != "files"}))
