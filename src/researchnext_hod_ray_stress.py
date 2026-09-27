"""Fixed-ray exact HOD extrema; no solver, refit, or positive-witness search."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from dataclasses import replace
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/research_next/hod_ray_stress"
SOURCE = "src/researchnext_hod_ray_stress.py"
PROTOCOL = "docs/research_next/HOD_RAY_STRESS_PROTOCOL.md"
AUDIT = "src/researchnext_observation_audit.py"
READER = "src/research8h_standalone_verify.py"
KERNEL = "src/researchnext_ray_assignment.py"
GEN = "reproducibility/native_sources/rts_inputs/raw/RTS-GMLC_v0.2.3/gen.csv"
PRIOR_FREEZE = "results/research_next/observation_audit/prepared/input_freeze.json"
TRAIN = "results/research8h/hour_of_day/seed_26093200/lp"
CERT = TRAIN + "/dual_certificate.json"
PINS = {
    AUDIT: "7a0bf951b4fc0c500d35c3f4729bf9a6b74bb6bb7f48ece673225c0eea991432",
    READER: "708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f",
    KERNEL: "298545b19768bd9c08f70ef303449edb26703f3e465a538204b80daa0f027091",
    GEN: "988466f29132b73739de60c9204dd4a2a9ceb0adf572e5966c086611272f4068",
    PRIOR_FREEZE: "9ba6a4b70cc5572ec53493597c693092e6877aad8127d711dc3922900a075636",
    CERT: "8e8ebecfa75e1fee98ff615525e17ec22bc5dd280ab24a6dbe5fa6d4a206320a",
    "docs/research_next/CERTIFICATE_GUIDED_CHRONOLOGY_PROPOSAL.md": "ade6f7ba94e7db87857198dd18a26b67a5dd494106a6d0fba3d229911df337a2",
    "src/temporal_lp_certificate.py": "6191c5760811cab0ec22b2fb1376a5be3aa47cb548e1260c4a17e2563d9802e4",
    "src/research8h_service_network.py": "1cdfa891e4b83e685bb38021709b99066aae6daa994e3c4500e815357f156a41",
    "src/research8h_service_network_mip.py": "a8c9c73b9f85b10afbb7aa93672ca595ccff6f30a1584faefeea5599a775c760",
    "reproducibility/native_sources/rts_inputs/code/dscgrid_model.py": "01d3e67440b1380b62ed68da07e61ac6895b930ada583ffa8af09a370850be78",
}
TAU = Q.from_float(1e-5)
CAPS = {1: 23195, 2: 26532, 3: 48319}
GROUPS = tuple((48+h, 72+h, 96+h) for h in range(24))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            require(k not in result, "duplicate JSON key")
            result[k] = v
        return result
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=unique,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))


def serial(value):
    if isinstance(value, Q):
        return {"numerator": str(value.numerator), "denominator": str(value.denominator)}
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serial(v) for v in value]
    return value


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(serial(value), f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")


def utc():
    return datetime.now(timezone.utc).isoformat()


def file_binding(rel):
    p = ROOT / rel
    require(not Path(rel).is_absolute() and ".." not in Path(rel).parts and p.is_file()
            and not p.is_symlink(), "unsafe/missing input: " + rel)
    return {"path": rel, "sha256": sha(p), "bytes": p.stat().st_size}


def check_pins():
    for rel, digest in PINS.items():
        require(sha(ROOT / rel) == digest, "pinned input changed: " + rel)


def prepare():
    p = OUT / "prepared"
    p.mkdir(parents=True, exist_ok=False)
    save(p / "STARTED.json", {"utc": utc(), "mode": "hash-only", "optimizer_calls": 0})
    check_pins()
    prior = read(ROOT / PRIOR_FREEZE)
    bindings = {}
    for entry in prior["bindings"]:
        require(file_binding(entry["path"]) == entry, "prior observation binding changed")
        bindings[entry["path"]] = entry
    for rel in (*PINS, SOURCE, PROTOCOL, *(TRAIN + "/" + n for n in
                                        ("matrix.npz", "bounds.npz", "row_metadata.csv.gz", "raw_solver_ray.npz"))):
        bindings[rel] = file_binding(rel)
    certificate = read(ROOT / CERT)
    for name, expected in certificate["model_artifacts"].items():
        require(name in ("matrix.npz", "bounds.npz") and sha(ROOT / TRAIN / name) == expected, "trained model binding")
    require(sha(ROOT / TRAIN / "row_metadata.csv.gz") == certificate["row_metadata_sha256"]
            and sha(ROOT / TRAIN / "raw_solver_ray.npz") == certificate["raw_solver_ray_sha256"], "trained ray provenance")
    save(p / "input_freeze.json", {"utc": utc(), "schema": "hod-ray-stress-v1", "bindings": sorted(bindings.values(), key=lambda e: e["path"]),
                                  "extremizer_roles": 6, "context_roles": 12, "ray_refits": 0, "optimizer_calls": 0,
                                  "scientific_margins_evaluated": 0})
    print(json.dumps({"prepared_bindings": len(bindings), "freeze_sha256": sha(p / "input_freeze.json")}))


def verify_freeze():
    check_pins()
    freeze = read(OUT / "prepared/input_freeze.json")
    seen = set()
    for entry in freeze["bindings"]:
        require(entry["path"] not in seen and file_binding(entry["path"]) == entry, "frozen input changed")
        seen.add(entry["path"])
    require(set(PINS) | {SOURCE, PROTOCOL} <= seen, "incomplete frozen sources")
    return freeze


def module(path, name):
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def row_dict(model, row):
    return {model.indices[k]: model.data[k] for k in range(model.indptr[row], model.indptr[row+1]) if model.data[k]}


def native_roster(metadata):
    with (ROOT / GEN).open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    by_name = {r["GEN UID"]: r for r in rows}
    require(len(by_name) == len(rows), "duplicate native UID")
    selected = [by_name[name] for name in metadata["unit_names"]]
    decision = [r["GEN UID"] for r in rows if int(r["Bus ID"]) in metadata["bus_ids"]
                and float(r["PMax MW"]) > 0 and r["Category"] != "Solar RTPV"]
    require(decision == metadata["unit_names"], "native decision roster order")
    thermal = [j for j, r in enumerate(selected) if float(r["PMin MW"]) > 0 and r["Category"] not in ("Hydro", "Solar PV", "Wind")]
    require(thermal == list(range(24)) and metadata["thermal_unit_names"] == metadata["unit_names"][:24], "thermal coordinate roster")
    return selected


def family_gate(case, gen, week):
    """All unit rows and hourly network blocks; source pins justify the family."""
    m, meta, physical = case["model"], case["metadata"], case["rows"]
    require(meta["budget_MWh"] == CAPS[week] and meta["individual_mean_constraints"] == 0, "fixed native cap/model")
    fossil = [j for j in range(24) if gen[j]["GEN UID"] != "121_NUCLEAR_1"]
    require(len(fossil) == 23 and meta["fossil_units"] == [gen[j]["GEN UID"] for j in fossil]
            and all(gen[j]["Fuel"] in ("Coal", "Oil", "NG") for j in fossil), "fossil roster")
    hydro = tuple(j for j, g in enumerate(gen) if g["Category"] == "Hydro")
    names = {uid: j for j, uid in enumerate(meta["unit_names"])}
    buses = {str(bus): j for j, bus in enumerate(meta["bus_ids"])}
    for j in range(24):
        low, high = float(gen[j]["PMin MW"]), float(gen[j]["PMax MW"])
        require(all(r[j] == low and r[41+j] == high for r in physical), "thermal bounds are not native constants")
        require(Q(float(gen[j]["Ramp Rate MW/Min"])*60) >= Q(high)-Q(low), "native on/on ramp not redundant")
    for t, r in enumerate(physical):
        for j in range(41):
            require(m.upper[t*41+j] == r[41+j] and m.lower[t*41+j] == (r[j] if j in hydro else 0), "native P box relation")
    normalized, family_counts = {}, Counter()
    for i, (family, t, uid) in enumerate(case["keys"]):
        family_counts[family] += 1
        actual = row_dict(m, i)
        lo, hi = m.row_lower[i], m.row_upper[i]
        expected = None
        if family == "aggregate_balance":
            expected = {t*41+j: 1.0 for j in range(41)}
            require((lo, hi) == (physical[t][82],)*2, "aggregate RHS must remain independent")
        elif family in ("thermal_upper", "thermal_lower", "transition", "exclusive_transition", "minimum_up", "minimum_down"):
            j = names[uid]
            require(j < 24 and 0 <= t < 168, "unit row coordinates")
            p, u, y, z = t*41+j, 6888+t*24+j, 10920+t*24+j, 14952+t*24+j
            if family == "thermal_upper":
                expected = {p: 1.0, u: -physical[t][41+j]}
            elif family == "thermal_lower":
                expected = {p: -1.0, u: physical[t][j]}
            elif family == "transition":
                require(t >= 1, "free initial edge changed")
                expected = {u: 1.0, u-24: -1.0, y: -1.0, z: 1.0}
            elif family == "exclusive_transition":
                require(t >= 1, "initial transition row")
                expected = {y: 1.0, z: 1.0}
            else:
                require(t >= 1, "observed residence boundary")
                up = family == "minimum_up"
                dwell = math.ceil(float(gen[j]["Min Up Time Hr" if up else "Min Down Time Hr"]))
                offset = 10920 if up else 14952
                expected = {offset+s*24+j: 1.0 for s in range(max(1, t-dwell+1), t+1)}
                expected[u] = -1.0 if up else 1.0
            expected_bounds = (0.0, 0.0) if family == "transition" else (-math.inf, 1.0 if family in ("exclusive_transition", "minimum_down") else 0.0)
            require((lo, hi) == expected_bounds, "unit row endpoint changed")
        elif family == "fossil_energy_cap":
            require(t == -1 and uid == "23_fossil_units" and (lo, hi) == (-math.inf, CAPS[week]), "global cap endpoint")
            expected = {s*41+j: 1.0 for s in range(168) for j in fossil}
        elif family in ("nodal_balance", "branch_flow"):
            require(0 <= t < 168, "network row hour")
            norm = {}
            for col, value in actual.items():
                if col < 6888:
                    require(family == "nodal_balance" and col//41 == t, "nonlocal network P column")
                    norm[("P", col % 41)] = value
                else:
                    require(18984+t*24 <= col < 18984+(t+1)*24, "nonlocal network theta column")
                    norm[("theta", col-18984-t*24)] = value
            key = (family, uid)
            if key not in normalized:
                normalized[key] = norm
            require(norm == normalized[key], "hour-varying topology coefficients")
            if family == "nodal_balance":
                bus = buses[uid]
                require({j: v for (kind, j), v in norm.items() if kind == "P"} ==
                        {j: 1.0 for j, g in enumerate(gen) if int(g["Bus ID"]) == meta["bus_ids"][bus]}, "native generator incidence")
                require((lo, hi) == (physical[t][83+bus],)*2, "native nodal RHS")
            else:
                vals = list(norm.values())
                require(len(vals) == 2 and vals[0] == -vals[1] and vals[0] != 0 and math.isfinite(hi) and hi > 0 and lo == -hi,
                        "branch coefficient/bound domain")
        else:
            raise ValueError("undeclared row family: " + family)
        if expected is not None:
            require(actual == {j: v for j, v in expected.items() if v}, "actual coefficient row does not match pinned builder: " + str(i))
    require(dict(family_counts) == {"aggregate_balance":168, "thermal_upper":4032, "thermal_lower":4032,
            "transition":4008, "exclusive_transition":4008, "minimum_up":4008, "minimum_down":4008,
            "fossil_energy_cap":1, "nodal_balance":4032, "branch_flow":6384}, "complete family denominator")
    require(len(normalized) == 62, "all24bus/38branch blocks")
    lookup = {k: i for i, k in enumerate(case["keys"])}
    for i, (family, t, uid) in enumerate(case["keys"]):
        if family not in ("aggregate_balance", "nodal_balance") and t >= 0:
            anchor = 0 if family in ("thermal_upper", "thermal_lower", "branch_flow") else 1
            k = lookup[(family, anchor, uid)]
            require((m.row_lower[i], m.row_upper[i]) == (m.row_lower[k], m.row_upper[k]), "unmodeled varying static row endpoint")
    # Original free-edge state boxes and angle boxes must stay unchanged.
    for j in range(6888, 18984):
        require(m.lower[j] == 0 and m.upper[j] == (0 if 10920 <= j < 10944 or 14952 <= j < 14976 else 1), "state box/boundary")
    angle0 = tuple(zip(m.lower[18984:19008], m.upper[18984:19008]))
    require(sum(a == b == 0 for a, b in angle0) == 1 and all((a == b == 0) or (a == -math.pi and b == math.pi) for a, b in angle0), "native angle boxes/pin")
    require(all(tuple(zip(m.lower[18984+t*24:18984+(t+1)*24], m.upper[18984+t*24:18984+(t+1)*24])) == angle0 for t in range(168)), "hour-varying angle boxes")
    return {"family_row_counts": dict(family_counts), "thermal_native_constants":24, "hydro_indices":hydro,
            "normalized_network_blocks":62, "full_binary_mask":12096, "all_family_coefficients_invariant":True}


def combined_columns(model, ray):
    q = [Q(0)]*model.cols
    for i, d in ray.items():
        for k in range(model.indptr[i], model.indptr[i+1]):
            q[model.indices[k]] += d*Q(model.data[k])
    return tuple(q)


def endpoint(model, kind, index, coefficient):
    value = ((model.row_lower if coefficient > 0 else model.row_upper)[index] if kind == "row" else
             (model.upper if coefficient < 0 else model.lower)[index])
    require(math.isfinite(value), "selected infinite endpoint")
    return Q(value)


def selected_terms(case, ray, q, kernel):
    m, keys = case["model"], case["keys"]
    lookup = {key: i for i, key in enumerate(keys)}
    row_norm, col_norm = sum(map(abs, ray.values()), Q(0)), sum(map(abs, q), Q(0))
    constant = -TAU*(row_norm+col_norm)
    terms, catalogue = [], []
    contributions = [("row", i, d) for i, d in sorted(ray.items())] + [("column", j, -v) for j, v in enumerate(q) if v]
    for kind, i, coefficient in contributions:
        t = None
        if kind == "row" and keys[i][0] in ("aggregate_balance", "nodal_balance"):
            t = keys[i][1]
        elif kind == "column" and i < 6888:
            t = i//41
        value = endpoint(m, kind, i, coefficient)
        entry = {"kind":kind, "index":i, "coefficient":coefficient, "identity_endpoint":value, "hour":t}
        if t is not None and 48 <= t < 120:
            group, destination = t % 24, (t-48)//24
            source_indices = [lookup[(keys[i][0], s, keys[i][2])] for s in GROUPS[group]] if kind == "row" else [s*41+i%41 for s in GROUPS[group]]
            values = tuple(endpoint(m, kind, j, coefficient) for j in source_indices)
            terms.append(kernel.EndpointTerm(group, destination, coefficient, values))
            entry.update(ownership="assignment", group=group, destination=destination, source_indices=source_indices, source_values=values)
        else:
            constant += coefficient*value
            entry["ownership"] = "fixed"
        catalogue.append(entry)
    require(len(terms) <= len(contributions), "endpoint ownership duplication")
    return constant, terms, catalogue, row_norm, col_norm


def direct_margin(model, ray, q):
    return sum((d*endpoint(model, "row", i, d) for i, d in ray.items()), Q(0)) + sum(
        (-v*endpoint(model, "column", j, -v) for j, v in enumerate(q) if v), Q(0)) - TAU*(sum(map(abs, ray.values()), Q(0))+sum(map(abs, q), Q(0)))


def table_margin(solution, order):
    value = solution["constant"]
    for hours, group in zip(GROUPS, solution["groups"]):
        for local, t in enumerate(hours):
            require(order[t] in hours, "order escaped clock group")
            value += group["table"][local][hours.index(order[t])]
    return value


def extremal_order(solution, which):
    order = list(range(168))
    for hours, group in zip(GROUPS, solution["groups"]):
        for t, s in zip(hours, group["argmin" if which == "minimum" else "argmax"]):
            order[t] = hours[s]
    return tuple(order)


def physical_model(identity, order, gen):
    """Build all varying bounds from complete input packages, not weight tables."""
    m = identity["model"]
    physical = tuple(identity["rows"][s] for s in order)
    lower, upper = list(m.lower), list(m.upper)
    for t, row in enumerate(physical):
        for j in range(41):
            lower[t*41+j] = row[j] if gen[j]["Category"] == "Hydro" else 0.0
            upper[t*41+j] = row[41+j]
    rl, ru = list(m.row_lower), list(m.row_upper)
    buses = {str(b): j for j, b in enumerate(identity["metadata"]["bus_ids"])}
    for i, (family, t, uid) in enumerate(identity["keys"]):
        if family == "aggregate_balance":
            rl[i] = ru[i] = physical[t][82]
        elif family == "nodal_balance":
            rl[i] = ru[i] = physical[t][83+buses[uid]]
    return replace(m, lower=tuple(lower), upper=tuple(upper), row_lower=tuple(rl), row_upper=tuple(ru)), physical


def npz_write(path, arrays):
    """Small deterministic NPZ writer; scientific coefficients remain binary64."""
    with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, (dtype, shape, values) in sorted(arrays.items()):
            require(dtype in ("<f8", "<i8") and len(values) == math.prod(shape), "NPZ output shape/type")
            header = repr({"descr":dtype, "fortran_order":False, "shape":tuple(shape)})
            padding = (-(10+len(header)+1)) % 64
            raw_header = (header+" "*padding+"\n").encode("latin1")
            payload = b"\x93NUMPY\x01\x00"+struct.pack("<H", len(raw_header))+raw_header
            payload += struct.pack("<"+("d" if dtype == "<f8" else "q")*len(values), *values)
            info = zipfile.ZipInfo(name+".npy", date_time=(1980,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, payload)


def write_extremizer(directory, original, model, physical, order, week):
    directory.mkdir(parents=True, exist_ok=False)
    for name in ("matrix.npz", "integrality.npz", "row_metadata.csv.gz", "model_metadata.json"):
        shutil.copyfile(original / name, directory / name)
    npz_write(directory / "bounds.npz", {k:("<f8", (len(v),), v) for k, v in (
        ("column_lower",model.lower),("column_upper",model.upper),("row_lower",model.row_lower),("row_upper",model.row_upper))})
    arrays = {"pmin":("<f8",(168,41),tuple(v for row in physical for v in row[:41])),
              "pmax":("<f8",(168,41),tuple(v for row in physical for v in row[41:82])),
              "net":("<f8",(168,),tuple(row[82] for row in physical)),
              "nodal":("<f8",(168,24),tuple(v for row in physical for v in row[83:])),
              "rows":("<i8",(168,),tuple((week-1)*168+s for s in order)),
              "source_hour":("<i8",(168,),order)}
    npz_write(directory / "native_inputs.npz", arrays)
    with (directory / "permutation.csv").open("x", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(("new_hour_0based","source_hour_0based","source_native_row","hour_of_day_0based"))
        writer.writerows((t,s,(week-1)*168+s,t%24) for t,s in enumerate(order))


class PhaseLimit(RuntimeError):
    pass


def guard(start):
    if time.perf_counter()-start >= 600:
        raise PhaseLimit("600-second soft arithmetic phase exhausted")


def rat(record):
    return Q(int(record["numerator"]), int(record["denominator"]))


def run():
    entered = time.perf_counter()
    freeze = verify_freeze()
    out = OUT / "run01"
    out.mkdir(exist_ok=False)
    save(out / "STARTED.json", {"utc":utc(), "python":sys.version, "freeze_sha256":sha(OUT/"prepared/input_freeze.json"),
                               "optimizer_calls":0, "ray_refits":0})
    reader = module(ROOT/READER, "hod_stress_reader")
    audit = module(ROOT/AUDIT, "hod_stress_audit")
    kernel = module(ROOT/KERNEL, "hod_stress_kernel")
    contexts = [{"week":w[0],"case":case,"role":role,"status":"NOT_EVALUATED"} for w in audit.WEEKS for case,role in audit.roles(w)]
    extrema = [{"week":w[0],"which":kind,"status":"NOT_EVALUATED"} for w in audit.WEEKS for kind in ("minimum","maximum")]
    phase = time.perf_counter()
    error = None
    try:
        certificate = read(ROOT/CERT)
        reference_model = reader.load_model(ROOT/TRAIN)
        ray = reader.parse_multipliers(certificate, reference_model.rows)
        q = combined_columns(reference_model, ray)
        save(out/"fixed_ray_and_q.json", {"source_certificate_sha256":PINS[CERT], "multipliers":certificate["multipliers"],
                                        "combined_columns":[{"column":j,"coefficient":v} for j,v in enumerate(q) if v], "tau":TAU})
        reference_case = None
        for week in audit.WEEKS:
            guard(phase)
            w, base, identity_name, ordinary, control = week
            path = ROOT/base/identity_name
            identity = audit.read_case(reader, path, w)
            require(identity["order"] == tuple(range(168)), "identity source order")
            require((identity["model"].data,identity["model"].indices,identity["model"].indptr) ==
                    (reference_model.data,reference_model.indices,reference_model.indptr), "cross-week exact A mismatch")
            if reference_case is None:
                reference_case = identity
            require(identity["labels"] == reference_case["labels"] and all(identity["metadata"][k] == reference_case["metadata"][k]
                    for k in ("unit_names","thermal_unit_names","bus_ids","offsets","column_order","rows","columns")), "cross-week row/column coordinates")
            gen = native_roster(identity["metadata"])
            gate = family_gate(identity, gen, w)
            constant, terms, catalogue, row_norm, col_norm = selected_terms(identity, ray, q, kernel)
            solution = kernel.exact_assignment_margin((3,)*24, terms, constant)
            distinct = all(len({audit.token(identity["rows"][s]) for s in hours}) == 3 for hours in GROUPS)
            save(out/f"week_{w}_family.json", {"gate":gate, "selected_endpoint_catalogue":catalogue,
                 "row_norm":row_norm,"column_norm":col_norm,"tau":TAU,"solution":solution,
                 "full_107_packages_distinct_within_all_groups":distinct,
                 "physical_family_size":solution["labeled_family_size"] if distinct else None})
            known_orders = {}
            for name, role in audit.roles(week):
                guard(phase)
                record = next(r for r in contexts if r["week"] == w and r["case"] == name)
                record["status"] = "IN_PROGRESS"
                case = identity if name == identity_name else audit.read_case(reader, ROOT/base/name, w)
                mapping = audit.prove_package_mapping(identity, case)
                recreated, _ = physical_model(identity, case["order"], gen)
                require(recreated == case["model"], "all-bound physical reconstruction differs from archived context")
                margin = direct_margin(case["model"], ray, q)
                require(margin == table_margin(solution, case["order"]) and solution["minimum"] <= margin <= solution["maximum"], "context/group margin identity")
                if name == "seed_26093200":
                    require(case["model"] == reference_model, "trained LP is not parent continuous relaxation")
                    v = certificate["verification"]
                    require(margin == Q(int(v["exact_robust_gap_numerator"]),int(v["exact_robust_gap_denominator"]))
                            and margin+TAU*(row_norm+col_norm) == Q(int(v["exact_gap_numerator"]),int(v["exact_gap_denominator"])), "trained gap exact replay")
                if role in ("identity_self","class_control"):
                    require(margin <= 0, "ray separates an inherited expanded positive control; review required")
                known_orders[name] = case["order"]
                record.update(status="EVALUATED", expanded_margin=margin, mapping=mapping)
                save(out/f"context_{name}.json", record)
            for which in ("minimum","maximum"):
                guard(phase)
                record = next(r for r in extrema if r["week"] == w and r["which"] == which)
                record["status"] = "IN_PROGRESS"
                order = extremal_order(solution, which)
                full, physical = physical_model(identity, order, gen)
                target = out/f"week_{w}_{which}"
                write_extremizer(target, path, full, physical, order, w)
                reread = audit.read_case(reader, target, w)
                require(reread["model"] == full, "written full model differs")
                mapping = audit.prove_package_mapping(identity, reread)
                tokens = {v:i for i,v in enumerate(sorted(set(map(audit.token,identity["rows"]))))}
                before = audit.observe(tuple(tokens[audit.token(row)] for row in identity["rows"]))
                after = audit.observe(tuple(tokens[audit.token(row)] for row in physical))
                require(before["hod"] == after["hod"] and before["edges"] == after["edges"], "complete HOD observation changed")
                checked = reader.check_ray(reread["model"], ray, TAU)
                require(rat(checked["expanded_separation_gap"]) == solution[which]
                        and rat(checked["separation_gap"]) == solution[which]+TAU*(row_norm+col_norm), "full checker/assignment exact margin mismatch")
                bound_certificate = {"multipliers":certificate["multipliers"],"source_certificate_sha256":PINS[CERT],
                    "model_artifacts":{n:sha(target/n) for n in ("matrix.npz","bounds.npz")},
                    "row_metadata_sha256":sha(target/"row_metadata.csv.gz"),"input_freeze_sha256":sha(OUT/"prepared/input_freeze.json"),"verification":checked}
                save(target/"dual_certificate.json", bound_certificate)
                duplicates = [name for name, old in known_orders.items() if old == order]
                record.update(status=checked["status"],expanded_margin=solution[which],mapping=mapping,
                              duplicate_old_orders=duplicates,certificate=f"{target.name}/dual_certificate.json")
                save(target/"result.json", record)
        save(out/"all_outcomes.json", {"contexts":contexts,"extrema":extrema})
    except Exception as e:
        error = {"type":type(e).__name__,"message":str(e)}
    elapsed = time.perf_counter()-phase
    for record in contexts+extrema:
        if record["status"] == "IN_PROGRESS":
            record["status"] = "ERROR"
        elif record["status"] == "NOT_EVALUATED":
            record["status"] = "NOT_EVALUATED_PHASE_LIMIT" if error and error["type"] == "PhaseLimit" else "NOT_EVALUATED_AFTER_ERROR"
    verify_freeze()
    save(out/"completion.json", {"status":"COMPLETE" if error is None else "INCOMPLETE", "utc":utc(), "error":error,
         "contexts":contexts,"extrema":extrema,"context_denominator":12,"extremizer_denominator":6,
         "phase_seconds":elapsed,"soft_phase_limit_seconds":600,"initial_validation_import_seconds":phase-entered,
         "elapsed_before_closeout_seconds":time.perf_counter()-entered,"input_bindings":len(freeze["bindings"]),
         "optimizer_calls":0,"ray_refits":0,"binary_witness_replays":0,"claim":"Fixed trained-ray extrema only; nonseparation is not feasibility."})
    print(json.dumps({"status":"COMPLETE" if error is None else "INCOMPLETE","phase_seconds":elapsed,"error":error}))
    return 0 if error is None else 1


def fixtures():
    require(sha(ROOT/READER) == PINS[READER] and sha(ROOT/KERNEL) == PINS[KERNEL], "fixture helper hash")
    reader = module(ROOT/READER,"stress_fixture_reader")
    kernel = module(ROOT/KERNEL,"stress_fixture_kernel")
    # Invented two-row model: signed row endpoints and negative q box endpoint.
    m = reader.Model(2,2,(1.0,-1.0),(0,1),(0,1,2),(0.0,-2.0),(3.0,4.0),(1.0,-math.inf),(1.0,2.0))
    ray = {0:Q(2),1:Q(-3)}
    q = combined_columns(m,ray)
    require(q == (Q(2),Q(3)) and endpoint(m,"row",1,Q(-3)) == 2 and endpoint(m,"column",0,Q(-2)) == 3, "signed row/box endpoint")
    require(endpoint(m,"column",1,Q(3)) == -2, "negative q selects lower box")
    direct = direct_margin(m,ray,q)
    checked = reader.check_ray(m,ray,TAU)
    require(direct == rat(checked["expanded_separation_gap"]), "full tau and signed formula")
    terms = (kernel.EndpointTerm(0,0,Q(2),(Q(1),Q(5))),kernel.EndpointTerm(0,1,Q(-3),(Q(2),Q(4))))
    solved = kernel.exact_assignment_margin((2,),terms,Q(-7)-TAU*10)
    require(solved["minimum"] == Q(-17)-TAU*10 and solved["maximum"] == Q(-3)-TAU*10, "fixed cap/penalty retained")
    zero = reader.Model(1,1,(1.0,),(0,),(0,1),(0.0,),(0.0,),(0.0,),(0.0,))
    require(reader.check_ray(zero,{0:Q(1)},Q(0))["status"] == "VALID_NONSEPARATING_RAY", "zero incorrectly separates")
    with tempfile.TemporaryDirectory(prefix="hod-ray-fixture-") as temp:
        path = Path(temp)/"invented.npz"
        npz_write(path,{"a":("<f8",(2,2),(0.0,-0.0,1.25,-2.5)),"idx":("<i8",(2,),(1,0))})
        arrays = reader.read_npz(path,("a","idx"))
        require(arrays["a"].shape == (2,2) and struct.pack("<4d",*arrays["a"].values) == struct.pack("<4d",0.0,-0.0,1.25,-2.5)
                and arrays["idx"].values == (1,0), "lossless NPZ fixture")
    save(OUT/"implementation_fixtures.json",{"status":"PASS","source_sha256":sha(Path(__file__)),"utc":utc(),
         "checks":["signed_row_endpoint","upper_box_support","negative_q_lower_box","full_tau_formula","fixed_cap_constant","zero_nonseparation","lossless_NPZ"],
         "scientific_arrays_read":0,"optimizer_calls":0,"old_fixture_suites_repeated":0})
    print(json.dumps({"status":"PASS","focused_checks":7}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--fixtures-only",action="store_true")
    modes.add_argument("--prepare-only",action="store_true")
    modes.add_argument("--run-prepared",action="store_true")
    args = parser.parse_args()
    if args.fixtures_only:
        fixtures()
    elif args.prepare_only:
        prepare()
    else:
        sys.exit(run())
