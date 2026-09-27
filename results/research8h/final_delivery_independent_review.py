"""Prospective independent final-ZIP integrity audit; no model arithmetic or replay.

Run only after separate execution approval, using externally trusted digest arguments.
All output is written to a fresh private directory beneath .work/research8h_delivery.
This source does not assert that any final package or candidate replay has passed.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import time
import zipfile

BASE_SHA = "495dcd6831ddbcd1c8263b32a536d5d9ff7ef2943fe54250c1c5532359e366d7"
BASE_BYTES = 88756097
BASE_PAYLOADS = 3501
STRICT_COMMIT = "579ecf20452b7838fdc5802744b24f597af5e1c7"
SCOPE = "strict-flow-capped-and-uncapped-v1"
PAYLOAD_EXCEPTIONS = frozenset({"FILE_ALLOWLIST.txt", "PACKAGE_PROVENANCE.json"})
OUTER = "FILE_MANIFEST.csv"
SELF = "results/research8h/final_delivery_independent_review.py"
GENERATED = frozenset({"README_FINAL_AR.md", "STRICT_FLOW_CANDIDATE.json", *PAYLOAD_EXCEPTIONS})
OLD_ROOT = "C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3"
NATIVE = "reproducibility/native_sources/"
CHECKPOINT_ROOT = "results/research8h/"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            value.update(block)
    return value.hexdigest()


def no_links(path):
    path = Path(path).absolute()
    for part in reversed((path, *path.parents)):
        if part.exists() or part.is_symlink():
            info = os.lstat(part)
            need(not stat.S_ISLNK(info.st_mode) and not (getattr(info, "st_file_attributes", 0) & 0x400),
                 "Link/reparse component: " + str(part))


def relative(value):
    need(type(value) is str and value and "\\" not in value and ":" not in value and "\x00" not in value,
         "Invalid relative path")
    path = PurePosixPath(value)
    need(not path.is_absolute() and ".." not in path.parts and str(path) == value and value != ".",
         "Noncanonical/escaping path: " + value)
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                *(f"LPT{i}" for i in range(1, 10))}
    for component in path.parts:
        need(component.rstrip(" .") == component and component.split(".")[0].upper() not in reserved,
             "Windows-ambiguous component: " + value)
        need(not any(ord(character) < 32 or character in '<>"|?*' for character in component),
             "Windows-invalid component: " + value)
    return value


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "Duplicate JSON key: " + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError("Nonfinite JSON value: " + value)

    return json.loads(data.decode("utf-8-sig"), object_pairs_hook=pairs, parse_constant=invalid)


def manifest(data, historical=False):
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
    need(len(reader.fieldnames or []) == 3 and set(reader.fieldnames) == {"path", "sha256", "bytes"},
         "Manifest fields differ")
    result, folded = {}, set()
    for row in reader:
        need(set(row) == {"path", "sha256", "bytes"}, "Malformed manifest row")
        name = row["path"]
        if historical:
            name = name.replace("\\", "/")
            if name.startswith(OLD_ROOT + "/"):
                name = name[len(OLD_ROOT) + 1:]
        name = relative(name)
        need(name.casefold() not in folded and name != OUTER, "Duplicate/self-binding manifest path")
        folded.add(name.casefold())
        need(re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is not None and
             re.fullmatch(r"[0-9]+", row["bytes"]) is not None, "Invalid hash/size")
        result[name] = {"bytes": int(row["bytes"]), "sha256": row["sha256"]}
    need(result, "Empty manifest")
    return result


def inspect_zip(path, expected_sha, expected_manifest=None, expected_count=None):
    no_links(path)
    need(Path(path).is_file() and sha(path) == expected_sha, "Wrong ZIP SHA256: " + str(path))
    records, folded = {}, set()
    with zipfile.ZipFile(path) as archive:
        for entry in archive.infolist():
            name = relative(entry.filename)
            need(not entry.is_dir() and name.casefold() not in folded, "Directory/duplicate/case-colliding member")
            folded.add(name.casefold())
            need(stat.S_IFMT(entry.external_attr >> 16) in (0, stat.S_IFREG) and not (entry.external_attr & 0x400),
                 "Special/link ZIP member: " + name)
            need(not (entry.flag_bits & 1) and entry.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED),
                 "Encrypted/unsupported ZIP member")
            digest, blob = hashlib.sha256(), hashlib.sha1()
            blob.update(b"blob " + str(entry.file_size).encode("ascii") + b"\0")
            size = 0
            with archive.open(entry) as stream:
                for block in iter(lambda: stream.read(1048576), b""):
                    size += len(block)
                    digest.update(block)
                    blob.update(block)
            need(size == entry.file_size, "Member size mismatch: " + name)
            records[name] = {"bytes": size, "sha256": digest.hexdigest(), "git_blob": blob.hexdigest()}
        for name in records:
            need(not any(str(parent) in records for parent in PurePosixPath(name).parents if str(parent) != "."),
                 "File/ancestor collision: " + name)
        need(OUTER in records and archive.testzip() is None, "Missing outer manifest/CRC failure")
        if expected_manifest is not None:
            need(records[OUTER]["sha256"] == expected_manifest, "Trusted outer-manifest SHA mismatch")
        declared = manifest(archive.read(OUTER))
        need(set(records) == set(declared) | {OUTER}, "Unmanifested/missing ZIP member")
        if expected_count is not None:
            need(len(declared) == expected_count, "Payload count differs")
        for name, item in declared.items():
            need(all(records[name][key] == value for key, value in item.items()), "Payload manifest mismatch: " + name)
    return {"zip_sha256": expected_sha, "zip_bytes": Path(path).stat().st_size,
            "outer_manifest_sha256": records[OUTER]["sha256"], "records": records,
            "payloads": declared, "crc_verified": True}


def member_json(path, name):
    with zipfile.ZipFile(path) as archive:
        return strict_json(archive.read(relative(name)))


def equal_payloads(left_path, right_path, names):
    with zipfile.ZipFile(left_path) as left, zipfile.ZipFile(right_path) as right:
        for name in sorted(names):
            with left.open(name) as first, right.open(name) as second:
                while True:
                    a, b = first.read(1048576), second.read(1048576)
                    need(a == b, "Actual member bytes differ: " + name)
                    if not a:
                        break


def git_overlay(repository, commit):
    resolved = subprocess.check_output(["git", "rev-parse", "--verify", commit + "^{commit}"], cwd=repository).decode().strip()
    need(resolved == commit, "Expected local Git commit unavailable")
    listing = subprocess.check_output(["git", "ls-tree", "-r", "-z", commit,
                                      "docs/research8h", "results/research8h", "results/seasonal_uncapped",
                                      "src", "reproducibility"], cwd=repository)
    result = {}
    for entry in listing.split(b"\0"):
        if not entry:
            continue
        meta, raw_name = entry.split(b"\t", 1)
        mode, kind, oid = meta.decode("ascii").split()
        name = relative(raw_name.decode("utf-8"))
        if name.startswith("src/") and not PurePosixPath(name).name.startswith("research8h_"):
            continue
        need(kind == "blob" and mode == "100644" and name not in result, "Unexpected Git mode/type/path")
        result[name] = oid
    need(result and SELF in result, "Empty overlay or audit source not committed")
    return result


def audit(args):
    inputs = {
        "audit_source": Path(__file__).resolve(), "baseline_zip": args.baseline_zip,
        "candidate_zip": args.candidate_zip, "candidate_summary": args.candidate_replay_summary,
        "final_zip": args.final_zip, "final_receipt": args.final_receipt,
    }
    for path in inputs.values():
        no_links(path)
        need(path.is_file(), "Missing regular audit input: " + str(path))
    before = {name: sha(path) for name, path in inputs.items()}
    need(before["audit_source"] == args.expected_self_sha256, "Unreviewed audit source")
    need(before["final_receipt"] == args.expected_receipt_sha256, "Untrusted final receipt")
    need(before["candidate_summary"] == args.expected_candidate_summary_sha256, "Untrusted candidate summary")
    receipt = strict_json(args.final_receipt.read_bytes())
    need(receipt["status"] == "VERIFIED_LOCAL" and receipt["git_commit"] == args.expected_commit and
         receipt["strict_replay_evidence_commit"] == STRICT_COMMIT, "Final receipt status/commit mismatch")
    need(receipt["crc_verified"] is True and receipt["every_member_matches_manifest"] is True,
         "Final receipt lacks complete integrity assertion")
    need(Path(receipt["zip_path"]).name == args.final_zip.name, "Final receipt archive filename differs")

    base = inspect_zip(args.baseline_zip, BASE_SHA, expected_count=BASE_PAYLOADS)
    need(base["zip_bytes"] == BASE_BYTES, "Immutable baseline size differs")
    candidate = inspect_zip(args.candidate_zip, args.expected_candidate_sha256,
                            args.expected_candidate_manifest_sha256, args.expected_candidate_payloads)
    final = inspect_zip(args.final_zip, receipt["sha256"], receipt["outer_manifest_sha256"], receipt["payload_files"])
    need(final["zip_bytes"] == receipt["bytes"] and len(final["records"]) == receipt["zip_members"],
         "Final receipt size/member count mismatch")
    digest = hashlib.md5()
    with args.final_zip.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            digest.update(block)
    need(digest.hexdigest() == receipt["md5"], "Final receipt auxiliary MD5 differs")

    summary = strict_json(args.candidate_replay_summary.read_bytes())
    expected_summary = {"status": "PORTABLE_STRICT_FLOW_REPLAY_PASS", "scope": SCOPE,
                        "strict_points": 5, "selected_negative_certificates": 2, "ray_candidates": 8,
                        "selected_lower_bounds": 3, "lower_candidates": 15, "penalty_intervals": 2,
                        "optimizer_calls": 0, "network_calls": 0, "native_reconstruction": False,
                        "package_files_unchanged": True, "package_evidence_commit": STRICT_COMMIT,
                        "package_manifest_sha256": args.expected_candidate_manifest_sha256}
    need(all(key in summary and type(summary[key]) is type(value) and summary[key] == value
             for key, value in expected_summary.items()), "Candidate replay PASS is not bound to this package/scope")
    metadata = {"schema": "strict-flow-candidate-v1", "evidence_commit": STRICT_COMMIT, "scope": SCOPE}
    need(member_json(args.candidate_zip, "STRICT_FLOW_CANDIDATE.json") == metadata and
         member_json(args.final_zip, "STRICT_FLOW_CANDIDATE.json") == metadata, "Strict metadata differs")
    need(set(base["payloads"]) <= set(candidate["payloads"]), "Candidate lost baseline payload")
    equal_payloads(args.baseline_zip, args.candidate_zip, base["payloads"])
    need(PAYLOAD_EXCEPTIONS <= set(candidate["payloads"]) and PAYLOAD_EXCEPTIONS <= set(final["payloads"]),
         "Declared metadata exception missing")
    inherited = set(candidate["payloads"]) - PAYLOAD_EXCEPTIONS
    need(inherited <= set(final["payloads"]), "Final package lost candidate science payload")
    equal_payloads(args.candidate_zip, args.final_zip, inherited)
    need(sum(name.startswith(NATIVE) for name in inherited) >= 25, "Native addendum unexpectedly absent")

    overlay = git_overlay(args.repository, args.expected_commit)
    for name, oid in overlay.items():
        need(name in final["records"] and final["records"][name]["git_blob"] == oid,
             "Final payload differs from trusted Git blob: " + name)
    expected_inventory = (set(base["payloads"]) - PAYLOAD_EXCEPTIONS) | set(overlay) | set(GENERATED)
    need(set(final["payloads"]) == expected_inventory, "Final ZIP scope differs from baseline + exact Git overlay + metadata")
    need(final["records"][SELF]["sha256"] == args.expected_self_sha256,
         "Executed audit source differs from the final committed payload")
    need(final["records"]["README_FINAL_AR.md"]["sha256"] == args.expected_readme_sha256,
         "Unreviewed final README")

    checkpoints = []
    names = ["verified_checkpoint_manifest.csv"] + [f"verified_checkpoint{number:02d}_manifest.csv"
                                                          for number in range(2, args.checkpoint_count + 1)]
    with zipfile.ZipFile(args.final_zip) as archive:
        expected_allowlist = ("\n".join(sorted(final["records"])) + "\n").encode("utf-8")
        need(archive.read("FILE_ALLOWLIST.txt") == expected_allowlist, "Regenerated allowlist differs from full final inventory")
        for name in names:
            path = CHECKPOINT_ROOT + name
            need(path in final["payloads"] and path in overlay, "Checkpoint manifest is not final-Git bound: " + name)
            rows = manifest(archive.read(path), historical=True)
            for relative_name, row in rows.items():
                need(relative_name in final["payloads"] and final["payloads"][relative_name] == row,
                     "Checkpoint payload changed: " + name + ": " + relative_name)
            checkpoints.append({"manifest": name, "payloads": len(rows), "pass": True})
    need(receipt["published_manifest_checks"] == checkpoints and receipt["git_blob_checks"] == len(overlay),
         "Final receipt checkpoint/Git accounting differs")
    provenance = member_json(args.final_zip, "PACKAGE_PROVENANCE.json")
    required_provenance = {"git_commit": args.expected_commit, "not_final_manuscript": True,
                           "committed_research_files": len(overlay), "source_zip_crc_and_manifest_verified": True,
                           "git_blob_equality_checked_for_every_added_or_refreshed_file": True,
                           "inherited_payload_bytes_unchanged": True, "strict_replay_evidence_commit": STRICT_COMMIT,
                           "published_manifest_checks": checkpoints, "active_uncommitted_arms_excluded": []}
    need(all(key in provenance and type(provenance[key]) is type(value) and provenance[key] == value
             for key, value in required_provenance.items()), "Regenerated final provenance differs")
    after = {name: sha(path) for name, path in inputs.items()}
    need(before == after, "Input changed during integrity audit")
    return {
        "status": "INDEPENDENT_FINAL_DELIVERY_INTEGRITY_PASS", "source_sha256": before["audit_source"],
        "input_bindings": {name: {"path": str(path), "sha256": before[name], "bytes": path.stat().st_size}
                           for name, path in inputs.items()},
        "expected_git_commit": args.expected_commit, "local_git_blob_checks": len(overlay),
        "remote_publication": "Externally attested by the root task's exact ls-remote match; no network call by this audit",
        "final_zip_sha256": final["zip_sha256"], "final_zip_bytes": final["zip_bytes"],
        "final_outer_manifest_sha256": final["outer_manifest_sha256"], "final_payloads": len(final["payloads"]),
        "candidate_payloads": len(candidate["payloads"]), "candidate_science_payloads_identical": len(inherited),
        "candidate_metadata_payload_exceptions": sorted(PAYLOAD_EXCEPTIONS),
        "metadata_exception_changes": {name: candidate["payloads"][name] != final["payloads"][name]
                                       for name in sorted(PAYLOAD_EXCEPTIONS)},
        "outer_manifest": "Separately authenticated; not a candidate payload exception",
        "baseline_payloads_preserved_in_candidate": len(base["payloads"]),
        "checkpoint_manifests": checkpoints, "strict_metadata_identical": True,
        "native_and_wrapper_bytes_included_in_identity_check": True, "all_input_files_unchanged": True,
        "integrity_only": True, "mathematical_replay_calls": 0, "optimizer_calls": 0, "network_calls": 0,
        "native_assembly_calls": 0, "extraction_performed": False,
        "interpretation": "Previously reviewed candidate strict evidence is present byte-for-byte in the final archive. "
                          "Additional final payloads receive integrity/Git checks, not a new mathematical verification.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("repository", "baseline-zip", "candidate-zip", "candidate-replay-summary",
                 "final-zip", "final-receipt", "report-dir"):
        parser.add_argument("--" + flag, type=Path, required=True)
    for flag in ("expected-self-sha256", "expected-candidate-sha256", "expected-candidate-manifest-sha256",
                 "expected-candidate-summary-sha256", "expected-receipt-sha256", "expected-readme-sha256"):
        parser.add_argument("--" + flag, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--checkpoint-count", type=int, required=True)
    parser.add_argument("--expected-candidate-payloads", type=int, required=True)
    args = parser.parse_args()
    need(sys.flags.isolated == 1 and sys.flags.no_site == 1, "Run using Python -I -S")
    for key, value in vars(args).items():
        if key.endswith("sha256"):
            need(re.fullmatch(r"[0-9a-f]{64}", value) is not None, "Expected explicit trusted SHA256: " + key)
    need(re.fullmatch(r"[0-9a-f]{40}", args.expected_commit) is not None and args.checkpoint_count >= 18 and
         args.expected_candidate_payloads > BASE_PAYLOADS, "Invalid trusted commit/count arguments")
    no_links(args.repository)
    need(args.repository.is_dir(), "Repository missing")
    no_links(args.report_dir)
    output = args.report_dir.resolve()
    private = (args.repository / ".work/research8h_delivery").resolve()
    need(output != private and output.is_relative_to(private) and not output.exists(),
         "Use a fresh private report directory beneath .work/research8h_delivery")
    for path in (args.baseline_zip, args.candidate_zip, args.candidate_replay_summary, args.final_zip, args.final_receipt):
        need(not path.resolve().is_relative_to(output), "Report directory would contain an input")
    started = time.perf_counter()
    output.mkdir(parents=True, exist_ok=False)
    try:
        report = audit(args)
    except Exception as error:
        report = {"status": "INDEPENDENT_FINAL_DELIVERY_INTEGRITY_FAILED", "error_type": type(error).__name__,
                  "error": str(error), "source_sha256": sha(Path(__file__)), "partial_reports_preserved": True,
                  "optimizer_calls": 0, "mathematical_replay_calls": 0, "network_calls": 0,
                  "native_assembly_calls": 0, "extraction_performed": False}
        code = 1
    else:
        code = 0
    report["created_utc"] = datetime.now(timezone.utc).isoformat()
    report["elapsed_seconds"] = time.perf_counter() - started
    report["invocation"] = vars(args) | {"python_isolated": True, "python_no_site": True}
    with (output / "integrity_review.json").open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False, allow_nan=False, default=str)
        stream.write("\n")
    print(json.dumps({"status": report["status"], "report_path": str(output / "integrity_review.json")}), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
