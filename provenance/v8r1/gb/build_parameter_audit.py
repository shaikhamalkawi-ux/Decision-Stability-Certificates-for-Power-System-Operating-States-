"""Rebuild a read-only provenance audit; no optimization or network reconstruction."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re

COMMIT = "8e084afe4fb2d4be86f270d3f12ad3315eee2a3a"
ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / ".work/gb_upstream"
OUT = Path(__file__).resolve().parent
BASE = f"https://github.com/andrewlyden/PyPSA-GB/blob/{COMMIT}/"


def write_csv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata-root", type=Path, required=True)
    args = parser.parse_args()
    default_lines = (RAW / "config/defaults.yaml").read_text(encoding="utf-8").splitlines()
    params = {}
    current = None
    in_parameters = False
    for number, line in enumerate(default_lines, 1):
        if line == "      carrier_parameters:":
            in_parameters = True
            continue
        if not in_parameters:
            continue
        if line.strip() and not line.lstrip().startswith("#") and len(line) - len(line.lstrip()) < 8:
            break
        carrier_match = re.fullmatch(r"        (\w+):", line)
        value_match = re.fullmatch(r"          (\w+):\s*([^#]+?)(?:\s*#.*)?", line)
        if carrier_match:
            current = carrier_match[1]
            params[current] = {}
        elif value_match:
            key, value = value_match.groups()
            params[current][key] = (value.strip(), number)
    assert set(params) == {"CCGT", "OCGT", "coal", "oil"}, params.keys()
    carrier_rows = []
    admissions = []
    for carrier, values in params.items():
        row = {"carrier": carrier, "admission": "KEEP", "scope": "source-defined optional sensitivity only", "min_p_nom_mw": 50}
        for key, (value, line) in values.items():
            row[key] = value
            if key == "enabled":
                units = "boolean; carrier selection"
            elif key == "p_min_pu":
                units = "fraction of p_nom while status=1"
            elif key in {"min_up_time", "min_down_time"}:
                units = "PyPSA snapshot count; hours only at 60-minute resolution"
            elif key.startswith("ramp_limit"):
                units = "fraction of p_nom per snapshot; no snapshot-weight scaling"
            else:
                units = "model currency/MW per transition; multiplied by p_nom to get currency"
            admissions.append({"route": "wholesale_overlay", "carrier": carrier, "parameter": key,
                "source_value": value, "effective_value": value, "units": units, "admission": "KEEP",
                "scope": "upstream-defined optional sensitivity; not observed 2020 plant parameter",
                "reason": "Exact pinned configuration and assignment recovered; no individual literature calibration established.",
                "source": BASE + f"config/defaults.yaml#L{line}",
                "implementation": BASE + "scripts/market/solve_wholesale.py#L376-L420"})
        row.update({"ramp_limit_start_up": 1.0, "ramp_limit_shut_down": 1.0,
                    "initial_status": "off", "up_time_before": 0,
                    "down_time_before": max(int(values["min_down_time"][0]), 1),
                    "eligible_active": "must be verified", "eligible_extendable": "must be false",
                    "source": BASE + "config/defaults.yaml#L330-L385"})
        carrier_rows.append(row)
    write_csv("wholesale_overlay_carriers.csv", carrier_rows)

    controls = [
        ("committable", "True for exact carrier + p_nom>=50 + active + not extendable", "KEEP", "sensitivity definition", "Exact eligibility rule, not derivable in full from frozen metadata", "365-L374"),
        ("initial_status", "off; up_time_before=0; down_time_before=max(min_down_time,1)", "KEEP", "explicit synthetic initial state", "Prior minimum downtime is already satisfied; no evidence this was actual historical state", "253-L276"),
        ("alternative_initial_status", "on; up_time_before=max(min_up_time,1); down_time_before=0", "KEEP", "declared boundary sensitivity", "Explicit native alternative; do not silently substitute preserve without prior state", "253-L276"),
        ("ramp_limit_start_up/shut_down", "1.0/1.0", "KEEP", "sensitivity definition", "Pinned defaults permit full-nameplate transition; preserve separately from normal ramps", "320-L342"),
        ("snapshot_resolution", "60 minutes", "KEEP", "frozen/default temporal convention", "PyPSA min times and ramps ignore snapshot weights; half-hour use requires explicit conversion policy", "376-L399"),
        ("full_generator_eligibility", "active and p_nom_extendable unavailable in frozen metadata", "HOLD", "claim of exact upstream candidate set", "Carrier/nameplate matching alone cannot establish both missing eligibility flags", "348-L374"),
        ("complete_native_network_feasibility", "no full network/time-varying model admitted", "HOLD", "native network UC/chronology conclusion", "Generator metadata omits full network, availability series and boundary states", "279-L287"),
        ("wholesale_main_network", "copperplate relaxation before UC", "HOLD", "claim of Reduced-network-constrained chronology", "Full wholesale entrypoint changes line/transformer limits; parameter helper alone must be labelled extracted overlay", "699-L725"),
        ("rolling_window_commitment", "24h copies; SoC explicitly carried", "HOLD", "multi-window continuous UC", "No commitment status/dwell carry in inspected loop; prefer one declared 168h horizon", "503-L579"),
        ("remove_must_run", "if true, resets all p_min_pu to0 after overlay", "HOLD", "p_min-preserving run without resolved config", "Must explicitly establish false for any experiment depending on p_min", "726-L730"),
        ("terminal_minimum_times", "truncated to remaining modeled snapshots", "KEEP", "PyPSA1.0.7 finite-horizon semantics", "Not cyclic chronology and not proof of feasibility after the final snapshot", "376-L399"),
    ]
    for parameter, value, decision, scope, reason, lines in controls:
        admissions.append({"route": "wholesale_overlay", "carrier": "ALL", "parameter": parameter,
            "source_value": value, "effective_value": value, "units": "see reason and audit report", "admission": decision,
            "scope": scope, "reason": reason,
            "source": BASE + "scripts/market/solve_wholesale.py#L" + lines,
            "implementation": "PyPSA v1.0.7 component_attrs/generators.csv and unit-commitment.md"})

    raw_rows = []
    fuel_rows = read_csv(RAW / "data/generators/generator_data_by_fuel.csv")
    for source_line, item in enumerate(fuel_rows, 2):
        for parameter in ("committable", "min_up_time", "min_down_time", "ramp_limit_up", "ramp_limit_down", "p_min_pu", "up_time_before", "start_up_cost", "p_max_pu"):
            raw = item[parameter]
            if parameter in {"min_up_time", "min_down_time"}:
                effective = str(int(float(raw)))
                reason = "Thermal MILP code casts directly to int snapshots; CSV has no unit labels or time conversion; fractional part is truncated."
            elif parameter.startswith("ramp_limit"):
                effective = str(float(raw)/100 if float(raw)<=100 else 1.0)
                reason = "Thermal code comment calls raw value %/hr and divides by100; independent raw-source unit/calibration mapping unresolved."
            elif parameter == "committable":
                effective = raw + " only if exact normalized carrier key matches and thermal solve_mode is MILP"
                reason = "LP explicitly disables UC; key normalization can prevent lookup; root config path differs from defaults."
            else:
                effective = "not assigned by add_thermal_generators from this CSV field"
                reason = "CSV presence does not prove use: p_min/p_max, initial uptime and startup cost are not copied by this thermal function."
            raw_rows.append({"fuel": item["fuel"], "source_line": source_line, "parameter": parameter,
                "raw_value": raw, "code_effect_if_exact_fuel_lookup": effective, "admission": "HOLD",
                "scope": "native historical chronology parameter", "reason": reason,
                "source": BASE + f"data/generators/generator_data_by_fuel.csv#L{source_line}",
                "implementation": BASE + "scripts/generators/integrate_thermal_generators.py#L1594-L1655"})
    write_csv("raw_fuel_parameter_audit.csv", raw_rows)
    write_csv("parameter_admission.csv", admissions)

    candidates = []
    summary = []
    metadata_manifest = []
    for month in ("january", "july"):
        path = args.metadata_root / f"{month}_generator_metadata.csv"
        metadata = read_csv(path)
        metadata_manifest.append({"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size})
        for carrier in params:
            group = [row for row in metadata if row["carrier"] == carrier and float(row["p_nom"]) >= 50]
            summary.append({"month": month, "carrier": carrier, "carrier_nameplate_candidates": len(group),
                "candidate_capacity_mw": sum(float(row["p_nom"]) for row in group),
                "full_eligibility": "HOLD: active and p_nom_extendable not exported"})
            for item in group:
                candidates.append({"month": month, "name": item["name"], "bus": item["bus"], "carrier": carrier,
                    "p_nom_mw": item["p_nom"], "frozen_p_min_pu": item["p_min_pu"],
                    "frozen_p_max_pu_static": item["p_max_pu"], "active": "NOT_EXPORTED",
                    "p_nom_extendable": "NOT_EXPORTED", "admission": "KEEP", "scope": "carrier/nameplate candidate mapping only",
                    "full_eligibility": "HOLD pending active/nonextendable validation",
                    "source_file_sha256": metadata_manifest[-1]["sha256"]})
    assert len(candidates) == 104, len(candidates)
    write_csv("wholesale_overlay_candidates.csv", candidates)
    write_csv("wholesale_overlay_candidate_summary.csv", summary)
    write_csv("frozen_metadata_manifest.csv", metadata_manifest)
    manifest = []
    for path in sorted(RAW.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(RAW).as_posix()
        if relative.startswith("PyPSA_v1.0.7/"):
            repository = "PyPSA/PyPSA"
            revision = "v1.0.7"
            source_path = relative.removeprefix("PyPSA_v1.0.7/")
        else:
            repository = "andrewlyden/PyPSA-GB"
            revision = COMMIT
            source_path = relative.removeprefix("docs/").replace("__", "/") if relative.startswith("docs/") else relative
        manifest.append({"raw_path": relative, "repository": repository, "revision": revision,
            "source_path": source_path, "url": f"https://raw.githubusercontent.com/{repository}/{revision}/{source_path}",
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size})
    write_csv("source_manifest.csv", manifest)
    print(json.dumps({"upstream_commit": COMMIT, "parameter_admission_rows": len(admissions),
        "raw_fuel_audit_rows": len(raw_rows), "candidate_rows": len(candidates), "source_files": len(manifest),
        "native_network_uc_conclusion": "HOLD", "optional_overlay_parameter_definition": "KEEP"}, indent=2))


if __name__ == "__main__":
    main()
