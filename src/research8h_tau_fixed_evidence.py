"""Fixed-evidence numerical tau sensitivity: prepare, then separately authorized replay.

No solver, network, data selection, multiplier search or native-model import.
"""
from __future__ import annotations
import argparse
import csv
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
from datetime import datetime, timezone
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/research8h/tau_fixed_evidence"
PROTOCOL = "docs/research8h/TAU_FIXED_EVIDENCE_PROTOCOL.md"
KERNEL = "src/research8h_standalone_verify.py"
KERNEL_SHA = "708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f"
HELPER = "reproducibility/replay_closed_research.py"
HELPER_SHA = "c6cf226ac82ecb5551dee2241e89b2fd1c990fdde3e27878758331b3f998fb85"
R = "results/research8h/"
HOD = R + "hour_of_day"
FRESH = R + "fresh_january_weeks/targets"
ENERGY = R + "fresh_january_energy"
HOD_ENERGY = R + "hour_of_day_uncapped"
GEN = "reproducibility/native_sources/rts_inputs/raw/RTS-GMLC_v0.2.3/gen.csv"
TAU0 = Q.from_float(1e-5)
MASK = (0,)*6888 + (1,)*12096 + (0,)*4032
CAPS = {1: 23195, 2: 26532, 3: 48319}
NEGATIVE_CASES = ("seed_26093200", "seed_26093201", "seed_26093210", "seed_26093220", "seed_26093221")
ENERGY_CASES = ("seed_26093200", "seed_26093201", "seed_26093210", "seed_26093211", "seed_26093220", "seed_26093221")
WEEK = dict(zip(ENERGY_CASES, (1, 1, 2, 2, 3, 3)))
MANIFESTS = {
 HOD + "/input_manifest.csv": "078082667f83322d3540ad3ac215ebcc996d0d31b04fd52bfa75c1d2fd814fcc",
 R + "fresh_january_weeks/targets/input_manifest.csv": "56c5240486a8274ecb076b3aca49db236db4a7d72b865392016868119f7938dd",
 HOD_ENERGY + "/input_manifest.csv": "b0ffca41db74d7278c001c776ae3b8656272994d083c8fc215ecbbf665020f8a",
 ENERGY + "/input_manifest.csv": "44b382d30a30b8485beda0cf080d22cd991b55a9f37491939f633d147bc14f2a"}
REVIEWS = {
 R + "hour_of_day_uncapped/independent_postrun_review.json": "INDEPENDENT_HOD_UNCAPPED_POSTRUN_PASS",
 R + "fresh_energy_review/postrun.json": "INDEPENDENT_FRESH_ENERGY_POSTRUN_PASS",
 R + "fresh_targets_postrun_review/final_ledger.json": "INDEPENDENT_FRESH_TARGET_FINAL_REVIEW_PASS"}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def js(path):
    def reject(x): raise ValueError("Nonfinite JSON: " + x)
    def unique(pairs):
        d = {}
        for k, v in pairs:
            require(k not in d, "Duplicate JSON key")
            d[k] = v
        return d
    return json.loads(path.read_text(encoding="utf-8-sig"), parse_constant=reject, object_pairs_hook=unique)


def frac(record):
    return Q(int(record["numerator"]), int(record["denominator"]))


def pack(x):
    return dict(numerator=str(x.numerator), denominator=str(x.denominator), approximate=float(x))


def save(path, data):
    with path.open("x", encoding="utf-8") as f:
        json.dump(data, f, indent=2, allow_nan=False); f.write("\n")


def bit_equal(x, y):
    return len(x) == len(y) and all(a == b and (not isinstance(a, float) or a.hex() == b.hex()) for a, b in zip(x, y))


def point_descriptor(role, week, model, mask, vector, metadata):
    return dict(role=role, week=week, model=model, mask=mask, vector=vector, metadata=metadata)


def descriptor():
    points = []
    for week in (1, 2, 3):
        identity = HOD + "/january_identity" if week == 1 else FRESH + f"/week_{week}_identity"
        control = HOD + "/seed_26100200" if week == 1 else FRESH + ("/seed_26100210" if week == 2 else "/seed_26100220")
        for kind, directory in (("identity", identity), ("control", control)):
            points.append(point_descriptor(f"cap_{kind}_w{week}", week, directory, directory + "/integrality.npz",
                directory + "/constructive_vector.npz", directory + "/model_metadata.json"))
        energy = R + "energy_lp_refinement/january_identity" if week == 1 else ENERGY + f"/week_{week}_identity"
        vector = HOD + "/january_identity/constructive_vector.npz" if week == 1 else energy + "/reference_upper_vector.npz"
        points.append(point_descriptor(f"energy_identity_w{week}", week, energy, energy + "/original_integrality.npz", vector,
            identity + "/model_metadata.json" if week == 1 else energy + "/model_metadata.json"))
    targets = []
    for case in ENERGY_CASES:
        week = WEEK[case]; directory = (HOD_ENERGY if week == 1 else ENERGY) + "/" + case
        points.append(point_descriptor("energy_" + case, week, directory, directory + "/original_integrality.npz",
            directory + "/mip/recovered_vector.npz", directory + "/model_metadata.json"))
        targets.append(dict(case=case, week=week, model=directory, parent=(HOD if week == 1 else FRESH) + "/" + case,
            identity_role=f"energy_identity_w{week}", target_role="energy_" + case))
    negatives = [dict(case=case, week=WEEK[case], parent=(HOD if WEEK[case] == 1 else FRESH) + "/" + case,
        model=(HOD if WEEK[case] == 1 else FRESH) + "/" + case + "/lp",
        identity_role=f"cap_identity_w{WEEK[case]}", control_role=f"cap_control_w{WEEK[case]}") for case in NEGATIVE_CASES]
    return dict(points=points, energy=targets, negatives=negatives, capped_ordinary_denominator=6,
        capped_certificate_denominator=5, capped_unknown="seed_26093211", energy_denominator=6,
        capped_point_roles=6, uncapped_point_roles=9, multiplier_selection="one fixed archived vector per claim")


def input_paths(plan):
    names = {str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), PROTOCOL, KERNEL, HELPER, GEN, *MANIFESTS, *REVIEWS,
        FRESH + "/outcomes.json", HOD_ENERGY + "/energy_brackets.json", HOD_ENERGY + "/reused_identity_bounds.json",
        ENERGY + "/energy_brackets.json", ENERGY + "/identity_energy_bounds.json"}
    for point in plan["points"]:
        names.update((point["mask"], point["vector"], point["metadata"]))
        names.update(point["model"] + "/" + x for x in ("matrix.npz", "bounds.npz", "row_metadata.csv.gz"))
        if point["role"].startswith("energy"):
            names.add(point["model"] + "/objective.npz")
    for negative in plan["negatives"]:
        names.update(negative["model"] + "/" + x for x in ("matrix.npz", "bounds.npz", "row_metadata.csv.gz", "dual_certificate.json", "raw_solver_ray.npz"))
        names.update(negative["parent"] + "/" + x for x in ("matrix.npz", "bounds.npz", "integrality.npz", "model_metadata.json", "row_metadata.csv.gz"))
    for item in plan["energy"]:
        names.update(item["model"] + "/lp/" + x for x in ("projected_row_dual.npz", "raw_duals.npz", "exact_lower_bound.json", "exact_stationarity_residual.json", "result.json"))
        names.update(item["model"] + "/mip/" + x for x in ("result.json", "exact_point_check.json"))
        names.update(item["parent"] + "/" + x for x in ("matrix.npz", "bounds.npz", "integrality.npz", "row_metadata.csv.gz", "model_metadata.json"))
    return sorted(names)


def review_statuses():
    for name, digest in MANIFESTS.items():
        require(sha(ROOT/name) == digest, "Changed historical manifest: " + name)
    for name, status in REVIEWS.items():
        require(js(ROOT/name)["status"] == status, "Closed independent gate mismatch: " + name)


def prepare():
    require(not OUT.exists(), "Sensitivity output directory already exists")
    plan = descriptor(); review_statuses()
    require(sha(ROOT/KERNEL) == KERNEL_SHA and sha(ROOT/HELPER) == HELPER_SHA, "Changed exact helper/kernel")
    entries = []
    for name in input_paths(plan):
        p = (ROOT/name).resolve(); require(p.is_relative_to(ROOT) and p.is_file(), "Missing selected input: " + name)
        entries.append(dict(path=name, sha256=sha(p), bytes=p.stat().st_size))
    OUT.mkdir(parents=True)
    save(OUT/"cases.json", plan)
    with (OUT/"input_manifest.csv").open("x", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "sha256", "bytes"], lineterminator="\n"); writer.writeheader(); writer.writerows(entries)
    save(OUT/"prepared_freeze.json", dict(status="TAU_FIXED_EVIDENCE_PREPARED_ONLY", prepared_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=sha(Path(__file__)), protocol_sha256=sha(ROOT/PROTOCOL), descriptor_sha256=sha(OUT/"cases.json"),
        manifest_sha256=sha(OUT/"input_manifest.csv"), selected_input_files=len(entries), selected_input_bytes=sum(x["bytes"] for x in entries),
        tau0=pack(TAU0), safe_display_decimal_places=18, optimizer_calls=0, arithmetic_calls=0, independent_prepared_gate_required=True,
        path_scope="explicit repository-relative exact-computation closure; historical manifests pinned, no host prefix fallback"))
    print(json.dumps(dict(status="TAU_FIXED_EVIDENCE_PREPARED_ONLY", manifest_sha256=sha(OUT/"input_manifest.csv"), files=len(entries))))


def upper_threshold(numerator, slope):
    require(slope >= 0, "Negative proof slope")
    if slope == 0:
        return dict(kind="unbounded" if numerator > 0 else "empty", upper=None, numerator=numerator, slope=slope)
    return dict(kind="finite" if numerator > 0 else "empty", upper=numerator/slope, numerator=numerator, slope=slope)


def decimal18(x, upward):
    scaled = x*10**18; n = -((-scaled).__floor__()) if upward else scaled.__floor__()
    whole, decimal = divmod(abs(n), 10**18)
    return ("-" if n < 0 else "") + f"{whole}.{decimal:018d}"


def intersection(points, proofs):
    require(points and proofs and all(x >= 0 for x in points.values()), "Empty/negative point-threshold group")
    lower = max(points.values()); lower_active = [name for name, x in points.items() if x == lower]
    empty = [name for name, t in proofs.items() if t["kind"] == "empty"]
    finite = {name: t["upper"] for name, t in proofs.items() if t["upper"] is not None}
    upper = min(finite.values()) if finite else None
    upper_active = [name for name, x in finite.items() if x == upper]
    valid = not empty and (upper is None or lower < upper)
    kind = ("unbounded" if upper is None else "finite") if valid else "empty"
    contains = valid and lower <= TAU0 and (upper is None or TAU0 < upper)
    low_display = decimal18(lower, True); up_display = decimal18(upper, False) if upper is not None else None
    display_nonempty = valid and (upper is None or Q(low_display) < Q(up_display))
    return dict(kind=kind, lower=pack(lower), upper=pack(upper) if upper is not None else None,
        lower_included=True, upper_included=False, active_lower_roles=lower_active, active_upper_proofs=upper_active,
        empty_proof_conditions=empty, exact_tau0_membership=contains,
        certified_values_strictly_below_tau0=contains and lower < TAU0,
        certified_values_strictly_above_tau0=contains and (upper is None or upper > TAU0),
        safe_decimal_subset=dict(lower=low_display, upper=up_display, lower_included=True, upper_included=False,
            nonempty=display_nonempty, rounding="lower upward, upper downward; upper remains open"),
        lower_over_tau0=pack(lower/TAU0), upper_over_tau0=pack(upper/TAU0) if upper is not None else None)


def synthetic_checks():
    records = []
    for label, n, s, expected in (("zero_slope_positive", Q(1), Q(0), "unbounded"), ("zero_slope_zero", Q(0), Q(0), "empty"),
            ("zero_slope_negative", Q(-1), Q(0), "empty"), ("positive_slope_nonpositive", Q(0), Q(2), "empty")):
        require(upper_threshold(n, s)["kind"] == expected, label); records.append(label)
    try:
        upper_threshold(Q(1), Q(-1))
    except ValueError:
        records.append("negative_slope_rejected")
    else:
        raise ValueError("Negative slope accepted")
    r = intersection({"a": TAU0, "b": TAU0}, {"x": upper_threshold(2*TAU0, Q(1)), "y": upper_threshold(2*TAU0, Q(1))})
    require(r["exact_tau0_membership"] and r["active_lower_roles"] == ["a", "b"] and r["active_upper_proofs"] == ["x", "y"], "Closed lower/tie semantics")
    records.append("closed_lower_and_tied_limits")
    r = intersection({"a": Q(0)}, {"x": upper_threshold(TAU0, Q(1))})
    require(not r["exact_tau0_membership"], "Strict upper treated as closed"); records.append("open_upper_at_tau0")
    r = intersection({"a": Q(1)}, {"x": upper_threshold(Q(1), Q(1))})
    require(r["kind"] == "empty", "Equal endpoints accepted"); records.append("equal_endpoint_empty")
    r = intersection({"a": Q(1, 3*10**18)}, {"x": upper_threshold(Q(2, 3*10**18), Q(1))})
    require(r["kind"] == "finite" and not r["safe_decimal_subset"]["nonempty"], "Rounded collapse changed exact interval")
    require(Q(r["safe_decimal_subset"]["lower"]) >= frac(r["lower"]) and Q(r["safe_decimal_subset"]["upper"]) <= frac(r["upper"]), "Validity rounding is outward")
    records.append("inward_display_can_collapse_nonempty_exact_range")
    return dict(status="TAU_SYNTHETIC_ENDPOINT_CHECKS_PASS", tests=records, optimizer_calls=0)


class Audit:
    def __init__(self, freeze):
        self.freeze = freeze; self.plan = js(OUT/"cases.json"); require(self.plan == descriptor(), "Case selection changed")
        self.check_manifest(); review_statuses(); sys.dont_write_bytecode = True
        self.v = self.import_pinned(KERNEL, KERNEL_SHA, "tau_fixed_kernel")
        self.h = self.import_pinned(HELPER, HELPER_SHA, "tau_fixed_bound_helpers")
        self.points = {}; self.models = {}; self.point_records = []
        with (ROOT/GEN).open(encoding="utf-8-sig", newline="") as f:
            roster = list(csv.DictReader(f))
        require(len({x["GEN UID"] for x in roster}) == len(roster), "Duplicate native generator")
        self.fuels = {x["GEN UID"]: x["Fuel"] for x in roster}

    def import_pinned(self, name, digest, module):
        require(sha(ROOT/name) == digest, "Changed math dependency")
        spec = importlib.util.spec_from_file_location(module, ROOT/name)
        obj = importlib.util.module_from_spec(spec); sys.modules[spec.name] = obj; spec.loader.exec_module(obj)
        return obj

    def check_manifest(self):
        require(sha(Path(__file__)) == self.freeze["source_sha256"] and sha(ROOT/PROTOCOL) == self.freeze["protocol_sha256"] and
            sha(OUT/"cases.json") == self.freeze["descriptor_sha256"] and sha(OUT/"input_manifest.csv") == self.freeze["manifest_sha256"], "Prepared source/descriptor changed")
        with (OUT/"input_manifest.csv").open(encoding="utf-8-sig", newline="") as f: entries = list(csv.DictReader(f))
        require(len(entries) == self.freeze["selected_input_files"] and [x["path"] for x in entries] == input_paths(self.plan), "Prepared input set changed")
        for entry in entries:
            p = (ROOT/entry["path"]).resolve(); require(p.is_relative_to(ROOT) and p.stat().st_size == int(entry["bytes"]) and sha(p) == entry["sha256"], "Changed exact input: " + entry["path"])

    def model(self, directory):
        if directory not in self.models: self.models[directory] = self.v.load_model(ROOT/directory)
        return self.models[directory]

    def array(self, name, key):
        return self.v.read_npz(ROOT/name, (key,))[key].values

    def labels(self, directory):
        with gzip.open(ROOT/directory/"row_metadata.csv.gz", "rt", encoding="utf-8", newline="") as f:return list(csv.DictReader(f))

    def mask(self, name):
        x = self.array(name, "integrality"); require(x == MASK, "Original 12096-coordinate binary mask required"); return x

    def cost(self, model, meta):
        require(model.cols == 23016 and meta["offsets"] == dict(P=0,U=6888,Y=10920,Z=14952,theta=18984), "Wrong column layout")
        units = meta["unit_names"]; require(len(units) == len(set(units)) == 41, "Wrong unit roster")
        fossil = [j for j, uid in enumerate(units) if self.fuels[uid] in ("Coal", "Oil", "NG")]
        require(len(fossil) == 23 and set(units[j] for j in fossil) == set(meta["fossil_units"]) and "121_NUCLEAR_1" not in meta["fossil_units"], "Wrong fossil roster")
        support = {t*41+j for t in range(168) for j in fossil}
        return tuple(1. if j in support else 0. for j in range(model.cols))

    def cap(self, directory, week, cost):
        model = self.model(directory); names = self.labels(directory)
        rows = [i for i,x in enumerate(names) if x["family"] == "fossil_energy_cap"]
        require(len(rows) == 1 and not any("mean" in x["family"] for x in names), "Wrong cap/mean background")
        index = rows[0]; require(model.row_lower[index] == -math.inf and model.row_upper[index] == float(CAPS[week]), "Nominal cap changed")
        terms = {model.indices[e]: model.data[e] for e in range(model.indptr[index],model.indptr[index+1]) if model.data[e]}
        require(terms == {j:x for j,x in enumerate(cost) if x}, "Cap/fossil objective support differs")
        return index

    def point_thresholds(self):
        for item in self.plan["points"]:
            directory = item["model"]; model = self.model(directory); mask = self.mask(item["mask"])
            point = self.array(item["vector"], "vector"); meta = js(ROOT/item["metadata"]); cost = self.cost(model, meta)
            report = self.v.check_point(model, point, mask, Q(0))
            require(report["original_binary_coordinates_exact"] and report["binary_coordinates"] == 12096, "Tau cannot repair nonbinary point")
            threshold = max(Q(0), frac(report["maximum_column_violation"]), frac(report["maximum_row_violation"]))
            require(threshold <= TAU0, "Closed witness not feasible at stored tau0")
            if item["role"].startswith("cap_"):
                self.cap(directory, item["week"], cost)
            else:
                require(not any(x["family"] == "fossil_energy_cap" or "mean" in x["family"] for x in self.labels(directory)), "Uncapped witness model retains cap/means")
                require(bit_equal(cost, self.array(directory+"/objective.npz", "objective")), "Uncapped point objective differs")
                if item["role"].startswith("energy_identity_"):
                    capped_identity = next(x for x in self.plan["points"] if x["role"] == f"cap_identity_w{item['week']}")
                    self.cap_only(directory, capped_identity["model"], item["week"], cost)
            energy = sum((Q(c)*Q(x) for c,x in zip(cost,point)), Q(0))
            self.points[item["role"]] = dict(p=threshold, energy=energy, descriptor=item)
            rec = dict(role=item["role"], week=item["week"], tau_min=pack(threshold), threshold_included=True,
                original_binary_coordinates=12096, strict_nominal_membership=report["strict_pass"], exact_point_scan=report,
                fixed_fossil_MWh=pack(energy), model=directory, matrix_sha256=sha(ROOT/directory/"matrix.npz"),
                bounds_sha256=sha(ROOT/directory/"bounds.npz"), mask_sha256=sha(ROOT/item["mask"]), vector_sha256=sha(ROOT/item["vector"]))
            self.point_records.append(rec)
        require(len(self.points) == 15, "Point-role denominator changed")
        save(OUT/"point_thresholds.json", dict(status="FIFTEEN_FIXED_POINT_ROLES_SCANNED", capped_roles=6, uncapped_roles=9, records=self.point_records))

    def rays(self):
        proofs = {}; records = []
        for item in self.plan["negatives"]:
            directory, parent = item["model"], item["parent"]; model = self.model(directory)
            require(all(sha(ROOT/directory/name) == sha(ROOT/parent/name) for name in ("matrix.npz","bounds.npz")), "LP/original capped model mismatch")
            self.mask(parent+"/integrality.npz"); meta = js(ROOT/parent/"model_metadata.json")
            self.cap(parent,item["week"],self.cost(model,meta))
            cert = js(ROOT/directory/"dual_certificate.json"); self.v.ray_bindings(ROOT/directory,cert,None,())
            raw = self.array(directory+"/raw_solver_ray.npz", "multipliers")
            require(len(raw) == model.rows and all(math.isfinite(x) for x in raw) and cert["orientation"] in (-1,1), "Invalid raw ray")
            signed = tuple(Q(x)*cert["orientation"] for x in raw)
            require(cert["candidate"] in ("raw","projected_to_row_sign_cone"), "Unknown archived ray selection")
            expected = {i:x for i,x in enumerate(signed) if x and not (cert["candidate"] == "projected_to_row_sign_cone" and
                ((x>0 and not math.isfinite(model.row_lower[i])) or (x<0 and not math.isfinite(model.row_upper[i]))))}
            multipliers = self.v.parse_multipliers(cert, model.rows); require(multipliers == expected, "Archived raw/projected ray mismatch")
            check = self.v.check_ray(model,multipliers,TAU0); comparison = self.v.archived_ray_comparison(cert,check)
            require(check["expanded_pass"] and comparison and all(comparison.values()), "Existing capped proof not reproduced at tau0")
            delta = frac(check["separation_gap"]); slope = frac(check["row_multiplier_l1"])+frac(check["combined_column_l1"])
            threshold = upper_threshold(delta,slope); proofs[item["case"]] = threshold
            pair = intersection({item["identity_role"]:self.points[item["identity_role"]]["p"]},{item["case"]:threshold})
            control_pair = intersection({r:self.points[r]["p"] for r in (item["identity_role"],item["control_role"])},{item["case"]:threshold})
            require(pair["exact_tau0_membership"] and control_pair["exact_tau0_membership"], "Existing capped pair sensitivity disagrees at tau0")
            records.append(dict(case=item["case"],week=item["week"],delta0=pack(delta),slope=pack(slope),
                strict_upper=pack(threshold["upper"]) if threshold["upper"] is not None else None,degenerate_kind=threshold["kind"],
                pair_range=pair,with_class_control_range=control_pair,exact_ray_at_tau0=check,
                existing_floating_ray_threshold=cert.get("verification",{}).get("maximum_uniform_bound_relaxation"),
                existing_diagnostic_is_not_the_exact_endpoint=True))
        save(OUT/"capped_ray_ranges.json",dict(status="FIVE_FIXED_RAY_RANGES",records=records,capped_denominator=6,certified_negative_denominator=5,unchanged_unknown="seed_26093211"))
        return proofs

    def cap_only(self,directory,parent,week,cost):
        model, full = self.model(directory),self.model(parent); cap = self.cap(parent,week,cost)
        require(model.rows+1 == full.rows and model.cols == full.cols and bit_equal(model.lower,full.lower) and bit_equal(model.upper,full.upper), "Cap deletion changed shape/box")
        keep = [r for r in range(full.rows) if r!=cap]
        for r,old in enumerate(keep):
            lo,hi=model.indptr[r:r+2];a,b=full.indptr[old:old+2]
            require(model.indices[lo:hi] == full.indices[a:b] and bit_equal(model.data[lo:hi],full.data[a:b]) and
                bit_equal((model.row_lower[r],model.row_upper[r]),(full.row_lower[old],full.row_upper[old])), "Noncap row changed")
        self.mask(parent+"/integrality.npz")

    def energy(self):
        records=[];proofs={}
        archived={x["case"]:x for x in js(ROOT/HOD_ENERGY/"energy_brackets.json")+js(ROOT/ENERGY/"energy_brackets.json")}
        require(set(archived)==set(ENERGY_CASES), "Archived energy denominator differs")
        for item in self.plan["energy"]:
            directory=item["model"];model=self.model(directory);cost=self.array(directory+"/objective.npz","objective")
            require(bit_equal(cost,self.cost(model,js(ROOT/directory/"model_metadata.json"))),"Target fossil objective differs")
            self.cap_only(directory,item["parent"],item["week"],cost)
            raw_arrays=self.v.read_npz(ROOT/directory/"lp/raw_duals.npz",("row_dual","column_dual"));raw=raw_arrays["row_dual"].values
            projected=self.array(directory+"/lp/projected_row_dual.npz","row_dual")
            require(len(raw)==len(projected)==model.rows and all(math.isfinite(x) for x in raw),"Invalid fixed energy dual")
            expected=tuple(0. if ((x>0 and not math.isfinite(model.row_lower[r])) or (x<0 and not math.isfinite(model.row_upper[r]))) else x for r,x in enumerate(raw))
            require(bit_equal(projected,expected),"Energy raw/projection differs")
            bound,residual=self.h.objective_lower(model,cost,projected,TAU0);saved=js(ROOT/directory/"lp/exact_lower_bound.json")
            require(all(frac(saved[k])==frac(v) for k,v in bound.items()),"Archived objective bound differs")
            require(sum(a!=b for a,b in zip(raw,projected))==saved["projected_entries"],"Energy projection count differs")
            sparse=js(ROOT/directory/"lp/exact_stationarity_residual.json")
            require([(int(x["column"]),frac(x)) for x in sparse]==[(j,x) for j,x in enumerate(residual) if x],"Exact stationarity residual differs")
            nominal=frac(bound["nominal_lower_bound_MWh"]);slope=frac(bound["row_dual_l1"])+frac(bound["stationarity_residual_l1"])
            identity,target=self.points[item["identity_role"]],self.points[item["target_role"]]
            ui,ut=identity["energy"],target["energy"];closed=archived[item["case"]]
            require(ui==frac(closed["identity_reference_upper_MWh"]) and ut==frac(closed["upper_MWh"]),"Energy witness/archived upper mismatch")
            fixed_at_tau0=nominal-TAU0*slope
            require(fixed_at_tau0==frac(bound["expanded_lower_bound_MWh"])==frac(closed["lower_MWh"]),"Fixed dual differs from archived selected bound at tau0")
            threshold=upper_threshold(nominal-ui,slope);proofs[item["case"]]=threshold
            pair=intersection({item["identity_role"]:identity["p"],item["target_role"]:target["p"]},{item["case"]:threshold})
            require(pair["exact_tau0_membership"],"Existing energy gap not certified by its fixed evidence at tau0")
            records.append(dict(case=item["case"],week=item["week"],nominal_target_lower=pack(nominal),slope=pack(slope),
                fixed_identity_upper=pack(ui),fixed_target_upper=pack(ut),energy_numerator=pack(nominal-ui),
                fixed_gap_lower_at_tau0=pack(fixed_at_tau0-ui),strict_upper=pack(threshold["upper"]) if threshold["upper"] is not None else None,
                degenerate_kind=threshold["kind"],pair_range=pair,identity_lower_bound_not_required=True,
                objective_dual_at_tau0=bound,no_alternative_dual_or_zero_baseline_selection=True))
        save(OUT/"energy_ranges.json",dict(status="SIX_FIXED_POSITIVE_ENERGY_PROOF_RANGES",records=records,denominator=6,
            capped_26093211_still_unknown=True))
        return proofs


def run_prepared():
    require(OUT.is_dir() and not (OUT/"execution_started.json").exists(),"Prepare first; execution already started is never retried")
    freeze=js(OUT/"prepared_freeze.json")
    require(freeze["status"]=="TAU_FIXED_EVIDENCE_PREPARED_ONLY", "Wrong prepared record")
    started=time.perf_counter()
    save(OUT/"execution_started.json",dict(started_utc=datetime.now(timezone.utc).isoformat(),optimizer_calls=0,source_sha256=sha(Path(__file__))))
    try:
        audit=Audit(freeze);save(OUT/"synthetic_checks.json",synthetic_checks())
        audit.h.fresh_ledger(js(ROOT/FRESH/"outcomes.json"))
        audit.point_thresholds();rays=audit.rays();energy=audit.energy()
        capped_points={name:x["p"] for name,x in audit.points.items() if name.startswith("cap_")}
        energy_points={name:x["p"] for name,x in audit.points.items() if name.startswith("energy_")}
        common_cap=intersection(capped_points,{"ray_"+k:v for k,v in rays.items()})
        common_energy=intersection(energy_points,{"energy_"+k:v for k,v in energy.items()})
        joint=intersection({**capped_points,**energy_points},{**{"ray_"+k:v for k,v in rays.items()},**{"energy_"+k:v for k,v in energy.items()}})
        require(all(x["exact_tau0_membership"] for x in (common_cap,common_energy,joint)),"Closed common tau0 evidence discrepancy")
        audit.check_manifest()
        save(OUT/"common_ranges.json",dict(status="EXACT_FIXED_EVIDENCE_COMMON_TAU_RANGES",tau0=pack(TAU0),
            capped=common_cap,energy=common_energy,joint=joint,numerical_mixed_unit_convention=True,
            normalization_caveat="Ranges depend on row/column units and normalization. Fixed-ray positive rescaling invariance is not model-row rescaling invariance.",
            outside_range="This fixed evidence stops certifying; no reversal or absence of other proofs is established."))
        save(OUT/"completion.json",dict(status="TAU_FIXED_EVIDENCE_EXACT_REPLAY_COMPLETE",completed_utc=datetime.now(timezone.utc).isoformat(),
            five_fixed_negative_rays=5,six_fixed_energy_duals=6,capped_point_roles=6,uncapped_point_roles=9,
            all_frozen_hashes_unchanged=True,manifest_sha256=freeze["manifest_sha256"],optimizer_calls=0,network_calls=0,
            elapsed_s=time.perf_counter()-started,independent_postrun_review_required=True))
    except Exception as error:
        save(OUT/"failure.json",dict(status="TAU_FIXED_EVIDENCE_REPLAY_FAILED",error_type=type(error).__name__,error=str(error),
            partial_outputs_preserved=True,optimizer_calls=0,elapsed_s=time.perf_counter()-started))
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare",action="store_true");group.add_argument("--run-prepared",action="store_true")
    args=parser.parse_args()
    if args.prepare:prepare()
    else:run_prepared()


if __name__=="__main__":main()
