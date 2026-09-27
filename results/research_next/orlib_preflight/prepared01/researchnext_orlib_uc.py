"""Source-only OR-LIB10 UC adapter and exact checker; no optimizer or network.

The selected target is the converted benchmark under UC.jl v0.4.0's default
formulation, not a claim of equivalence to the original Pisa quadratic model.
Scientific preparation is a separate reviewed action. --self-test uses only a
handwritten synthetic fixture, never the selected data or target permutations.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

COMMIT = "4f04f0dd6641b071fd7556346c3d7190c2ffdfe5"
CASE_URL = "https://axavier.org/UnitCommitment.jl/0.4/instances/or-lib/10_0_1_w.json.gz"
GZIP_SHA = "6ef95ef5a1966914306da848f2ffa4bd835c49d520e30b1dcbcfa948eee85cbe"
JSON_SHA = "3cfa5d6f0135e732edd7cb08f887cda0c7e56b0b8e766185d05b52e0ee1f3308"
SOURCE_SHA = {
    "src/instance/read.jl": "4ac605833da6c283b20ea536c3da874c6a42b8c2923301abf874f536fa4b6ec2",
    "src/instance/migrate.jl": "cef1c7575185ad4350e00962ce0d4af27514cf287e266439dc8679c99e33cf60",
    "src/validation/repair.jl": "8f918bb6bd9074ba56ad98fcc5e04de397ac6d153a6e498cb79800f32fd02b2f",
    "src/validation/validate.jl": "74fe665dd1e0b64569b8c0000bdd279cfaf524738b15519a2d05cea7c74c1337",
    "src/model/formulations/base/unit.jl": "fdfff2b655cef6bfa9fcd7f17a78e5636e5c9c3c41f179b9fe6774d44da4158b",
    "src/model/formulations/Gar1962/status.jl": "59049061a26d8223915061a7dc7b3c08907885bdeb5e9df6db897b6946181e7c",
    "src/model/formulations/Gar1962/prod.jl": "278790c87ca41f7bc4ec89d3d9b9ab22ef0d554fa6c8638e5a2726ab76db5d8e",
    "src/model/formulations/KnuOstWat2018/pwlcosts.jl": "53697ddd610c649ad1e1b65b1061146e391f0695d8d65da8670fd00864d5f367",
    "src/model/formulations/MorLatRam2013/scosts.jl": "db8c3c5410aa6a122a6bf61ca6d399c7c93d25f5fcf30a096f02940ab13f92b8",
    "src/model/formulations/base/bus.jl": "a7efa482f3c3b09576015717cfc90fea91c6bb3c5717be6afee7729240cbbb8c",
    "src/model/formulations/base/system.jl": "10ca02e32608a359f124115e420dddd15c425963050afa0e0e313cb64c14ae67",
    "src/model/formulations/base/structs.jl": "5a90e3738a898d6a5be31f0cb8f4a809e78ca255f47d033df72717f533667216",
    "src/model/formulations/MorLatRam2013/ramp.jl": "fd8f6f982993f9b33ecb348178b68c9dc9eee284f0ab2e37b149ca3730952916",
    "LICENSE.md": "1c50672dd60074aa0d516c1c61834f47fb6002f4d70e707523d57bda5f0f136c",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def finite(value):
    require(type(value) in (int, float) and math.isfinite(value), "Expected finite real, not bool")
    return float(value)


def frac(value):
    return Fraction.from_float(finite(value))


def rational(value):
    return {"numerator": str(value.numerator), "denominator": str(value.denominator),
            "approximate": float(value)}


def parse_selected(raw):
    """Normalize exactly these immutable bytes, also used as the archived copy."""
    require(len(raw) == 2419 and sha(raw) == GZIP_SHA, "Selected compressed case hash mismatch")
    data = gzip.decompress(raw)
    require(len(data) == 6811 and sha(data) == JSON_SHA, "Selected JSON hash mismatch")
    case = normalize(json.loads(data))
    require(case["horizon"] == 24 and len(case["units"]) == 10, "Unexpected selected dimensions")
    require([g["name"] for g in case["units"]] == ["g" + str(i) for i in range(10)], "Unit order mismatch")
    require(all(v == 0 for v in case["reserve"]), "Selected reserve requirements changed")
    case["case_json_sha256"] = JSON_SHA
    case["synthetic_fixture"] = False
    return case


def read_selected(path):
    return parse_selected(Path(path).read_bytes())


def normalize(data):
    """Explicit restricted schema; unsupported features fail rather than vanish."""
    require(set(data) <= {"Parameters", "Buses", "Generators", "Reserves", "SOURCE", "LICENSE"},
            "Unsupported top-level feature")
    p = data["Parameters"]
    require(set(p) <= {"Version", "Time horizon (h)", "Time (h)", "Time step (min)",
                       "Power balance penalty ($/MW)"}, "Unsupported parameter")
    require(p["Version"] in ("0.3", "0.4"), "Unsupported schema version")
    t = p.get("Time horizon (h)", p.get("Time (h)"))
    require(type(t) is int and t > 0 and p.get("Time step (min)", 60) == 60, "Require hourly horizon")
    require(len(data["Buses"]) == 1 and len(data["Reserves"]) == 1, "Require one bus and reserve product")
    bn, bus = next(iter(data["Buses"].items()))
    rn, reserve = next(iter(data["Reserves"].items()))
    require(set(bus) == {"Load (MW)"}, "Unsupported bus field")
    require(set(reserve) <= {"Type", "Amount (MW)", "Shortfall penalty ($/MW)"}, "Unsupported reserve field")
    require(reserve["Type"].lower() == "spinning" and reserve.get("Shortfall penalty ($/MW)", -1) < 0,
            "Only hard spinning-reserve requirement admitted")

    def series(value):
        v = value if isinstance(value, list) else [value] * t
        require(len(v) == t, "Time series length mismatch")
        return [finite(x) for x in v]

    load, req = series(bus["Load (MW)"]), series(reserve["Amount (MW)"])
    penalty = series(p.get("Power balance penalty ($/MW)", 1000.0))
    require(all(x >= 0 for x in load + req + penalty), "Require nonnegative load/reserve/penalty")
    units = []
    allowed = {"Bus", "Type", "Production cost curve (MW)", "Production cost curve ($)",
               "Startup costs ($)", "Startup delays (h)", "Minimum uptime (h)", "Minimum downtime (h)",
               "Ramp up limit (MW)", "Ramp down limit (MW)", "Startup limit (MW)", "Shutdown limit (MW)",
               "Initial status (h)", "Initial power (MW)", "Must run?", "Reserve eligibility"}
    for name, g in data["Generators"].items():
        require(set(g) <= allowed, "Unsupported generator field: " + name)
        require(g["Bus"] == bn and g.get("Type", "Thermal").lower() == "thermal", "Nonthermal unit")
        require(g.get("Must run?", False) is False, "Must-run case outside selected adapter")
        require(g.get("Reserve eligibility") == [rn], "Require eligibility for exactly selected reserve")
        mw = [finite(x) for x in g["Production cost curve (MW)"]]
        cost = [finite(x) for x in g["Production cost curve ($)"]]
        require(len(mw) == len(cost) == 5, "Require selected four constant cost segments")
        widths = [float(mw[k + 1] - mw[k]) for k in range(4)]
        require(all(w > 0 for w in widths) and mw[0] >= 0, "Nonpositive segment width")
        slopes = [float((cost[k + 1] - cost[k]) / widths[k]) for k in range(4)]
        require(all(x >= 0 for x in cost + slopes) and all(slopes[k + 1] >= slopes[k] for k in range(3)),
                "Cost repair would be required; no silent repair")
        up, down, age = g["Minimum uptime (h)"], g["Minimum downtime (h)"], g["Initial status (h)"]
        require(all(type(x) is int for x in (up, down, age)) and up > 1 and down > 0 and age != 0,
                "Require integer dwell/age and minimum-up>1")
        startup_cost = g.get("Startup costs ($)", [0.0])
        delays = g.get("Startup delays (h)", [1])
        require(len(startup_cost) == len(delays) == 1 and delays[0] == down,
                "Only the selected single native startup category is admitted")
        su, sd = finite(g.get("Startup limit (MW)", 1e6)), finite(g.get("Shutdown limit (MW)", 1e6))
        require(su >= mw[-1] and sd >= mw[-1], "Nonzero Knu startup/shutdown correction requires new review")
        initial = finite(g["Initial power (MW)"])
        require((age < 0 and initial == 0) or (age > 0 and mw[0] <= initial <= mw[-1]), "Initial power/status mismatch")
        ru, rd = finite(g["Ramp up limit (MW)"]), finite(g["Ramp down limit (MW)"])
        require(ru >= 0 and rd >= 0, "Negative ramp")
        units.append({"name": name, "pmin": mw[0], "pmax": mw[-1], "widths": widths,
                      "slopes": slopes, "min_cost": cost[0], "up": up, "down": down,
                      "age": age, "initial_power": initial, "ru": ru, "rd": rd,
                      "su": su, "sd": sd, "startup_cost": finite(startup_cost[0]),
                      "startup_delay": delays[0], "original_mw": mw, "original_cost": cost})
    require(units and all(g["startup_cost"] >= 0 for g in units), "Negative startup cost")
    return {"horizon": t, "bus": bn, "reserve_name": rn, "load": load, "reserve": req,
            "penalty": penalty, "units": units, "migration": "Add Thermal type if absent",
            "numeric_repairs": [], "source_software_commit": COMMIT, "synthetic_fixture": True}


def column_name(family, g, t, k=None):
    return ":".join(str(v) for v in (family, g, t) + (() if k is None else (k,)))


def build(case, variant, order):
    """Build the declared source-derived encoding; never call a solver."""
    require(variant in ("native_penalized", "hard_service"), "Unknown service convention")
    tmax = case["horizon"]
    require(all(type(x) is int for x in order) and sorted(order) == list(range(tmax)), "Not a permutation")
    columns, rows, indices = [], [], {}

    def col(family, g, t, lo, hi, objective=0, binary=False, k=None):
        name = column_name(family, g, t, k)
        require(name not in indices, "Duplicate column")
        indices[name] = len(columns)
        columns.append({"name": name, "lower": finite(lo), "upper": finite(hi),
                        "objective": finite(objective), "binary": bool(binary)})

    def ix(family, g, t, k=None):
        return indices[column_name(family, g, t, k)]

    def row(name, terms, lower=None, upper=None):
        acc = {}
        for j, value in terms:
            acc[j] = float(acc.get(j, 0.0) + finite(value))
        rows.append({"name": name, "coefficients": [[j, a] for j, a in sorted(acc.items()) if a != 0],
                     "lower": None if lower is None else finite(lower),
                     "upper": None if upper is None else finite(upper)})

    for g in case["units"]:
        n, width = g["name"], float(g["pmax"] - g["pmin"])
        require(width >= 1e-7, "Degenerate production range unsupported")
        for t in range(tmax):
            for f in ("U", "Y", "Z", "D"):
                cost = g["min_cost"] if f == "U" else g["startup_cost"] if f == "D" else 0.0
                col(f, n, t, 0, 1, cost, True)
            col("Q", n, t, 0, width)
            col("R", n, t, 0, width)
            for k in range(4):
                col("S", n, t, 0, g["widths"][k], g["slopes"][k], k=k)
    for t, src in enumerate(order):
        col("C", "system", t, 0, case["load"][src] if variant == "native_penalized" else 0,
            case["penalty"][src])
        col("F", "system", t, 0, 0)
        col("N", "system", t, 0, 0)

    for g in case["units"]:
        n, width = g["name"], float(g["pmax"] - g["pmin"])
        for t in range(tmax):
            u, y, z, d, q, r = (ix(f, n, t) for f in ("U", "Y", "Z", "D", "Q", "R"))
            link = [(u, 1), (y, -1), (z, 1)]
            initial_on = float(g["age"] > 0) if t == 0 else 0.0
            if t:
                link.append((ix("U", n, t - 1), -1))
            row(f"link:{n}:{t}", link, initial_on, initial_on)
            row(f"exclusive:{n}:{t}", [(y, 1), (z, 1)], upper=1)
            row(f"startup_category:{n}:{t}", [(y, 1), (d, -1)], 0, 0)
            row(f"minup:{n}:{t}", [(ix("Y", n, i), 1) for i in range(max(0, t - g["up"] + 1), t + 1)] + [(u, -1)], upper=0)
            row(f"mindown:{n}:{t}", [(ix("Z", n, i), 1) for i in range(max(0, t - g["down"] + 1), t + 1)] + [(u, 1)], upper=1)
            row(f"production_limit:{n}:{t}", [(q, 1), (r, 1), (u, -width)], upper=0)
            for k in range(4):
                row(f"segment_limit:{n}:{t}:{k}", [(ix("S", n, t, k), 1), (u, -g["widths"][k])], upper=0)
                # The native equality is inserted once per segment inside its k-loop.
                row(f"production_definition:{n}:{t}:{k}", [(q, 1)] + [(ix("S", n, t, j), -1) for j in range(4)], 0, 0)
            row(f"startup_limit:{n}:{t}", [(q, 1), (r, 1), (u, -width)], upper=0)
            if t + 1 < tmax:
                row(f"shutdown_limit:{n}:{t}", [(q, 1), (u, -width)], upper=0)
            if t:
                row(f"ramp_up:{n}:{t}", [(q, 1), (r, 1), (ix("Q", n, t - 1), -1)], upper=g["ru"])
                row(f"ramp_down:{n}:{t}", [(ix("Q", n, t - 1), 1), (ix("R", n, t - 1), 1), (q, -1)], upper=g["rd"])
            elif g["age"] > 0:
                # Preserve the native initial expression Pmin+Q, even when U=0.
                up_rhs = float(float(g["initial_power"] + g["ru"]) - g["pmin"])
                down_rhs = float(g["rd"] - float(g["initial_power"] - g["pmin"]))
                row(f"initial_ramp_up:{n}", [(q, 1), (r, 1)], upper=up_rhs)
                row(f"initial_ramp_down:{n}", [(q, -1)], upper=down_rhs)
        family = "Z" if g["age"] > 0 else "Y"
        remaining = g["up"] - g["age"] if g["age"] > 0 else g["down"] + g["age"]
        row(f"initial_dwell:{n}", [(ix(family, n, t), 1) for t in range(max(0, min(remaining, tmax)))], 0, 0)

    for t, src in enumerate(order):
        terms = [(ix("C", "system", t), 1), (ix("N", "system", t), -1)]
        for g in case["units"]:
            terms += [(ix("Q", g["name"], t), 1), (ix("U", g["name"], t), g["pmin"])]
        row(f"net_injection:{t}", terms, case["load"][src], case["load"][src])
        row(f"balance:{t}", [(ix("N", "system", t), 1)], 0, 0)
        row(f"reserve:{t}", [(ix("R", g["name"], t), 1) for g in case["units"]] + [(ix("F", "system", t), 1)], lower=case["reserve"][src])
    return {"schema": "orlib-uc-source-derived-binary64-v1", "source_commit": COMMIT,
            "case_json_sha256": case.get("case_json_sha256"), "synthetic_fixture": case["synthetic_fixture"],
            "variant": variant, "order": order, "horizon": tmax, "columns": columns, "rows": rows,
            "binary_count": sum(c["binary"] for c in columns),
            "omitted_auxiliaries": "mfg>=0 only: no selected-formulation constraint/objective reference; lift to0",
            "added_implied_boxes": "0<=Q,R<=Pmax-Pmin; N=0. Equivalent at nominal rows, expansion defined on this encoding only.",
            "native_runtime_export_equality": "NOT_TESTED; source-derived normalization is explicit"}


def exact_matrix_check(model, vector, tau=0.0):
    require(len(vector) == len(model["columns"]), "Vector dimension mismatch")
    x, tolerance = [frac(v) for v in vector], frac(tau)
    require(tolerance >= 0, "Negative tolerance")
    failures, nominal_max = [], Fraction(0)
    for j, c in enumerate(model["columns"]):
        violation = max(frac(c["lower"]) - x[j], x[j] - frac(c["upper"]), Fraction(0))
        nominal_max = max(nominal_max, violation)
        if violation > tolerance:
            failures.append("box:" + c["name"])
        if c["binary"] and x[j] not in (0, 1):
            failures.append("binary:" + c["name"])
    for row in model["rows"]:
        v = sum((frac(a) * x[j] for j, a in row["coefficients"]), Fraction(0))
        violation = max(Fraction(0),
                        Fraction(0) if row["lower"] is None else frac(row["lower"]) - v,
                        Fraction(0) if row["upper"] is None else v - frac(row["upper"]))
        nominal_max = max(nominal_max, violation)
        if violation > tolerance:
            failures.append("row:" + row["name"])
    obj = sum((frac(c["objective"]) * v for c, v in zip(model["columns"], x)), Fraction(0))
    return {"accepted": not failures, "tau": rational(tolerance), "nominal_max_violation": rational(nominal_max),
            "exact_objective": rational(obj), "failures": failures}


def direct_check(case, model, vector, tau=0.0):
    """Equation-level audit from case and named vector; never reads row coefficients."""
    require(len(vector) == len(model["columns"]), "Direct vector dimension mismatch")
    values = {c["name"]: frac(v) for c, v in zip(model["columns"], vector)}
    require(len(values) == len(vector), "Duplicate column names")
    tolerance, failures, worst = frac(tau), [], Fraction(0)
    require(tolerance >= 0, "Negative tolerance")

    def get(f, g, t, k=None):
        return values[column_name(f, g, t, k)]

    def bounded(label, value, lo, hi):
        nonlocal worst
        violation = max(Fraction(0), value - hi, lo - value)
        worst = max(worst, violation)
        if violation > tolerance:
            failures.append(label)

    def le(label, value, bound):
        nonlocal worst
        violation = max(Fraction(0), value - bound)
        worst = max(worst, violation)
        if violation > tolerance:
            failures.append(label)

    def equal(label, a, b):
        bounded(label, a, b, b)

    total_cost, canonical_cost = Fraction(0), Fraction(0)
    canonical_domain_failures = []
    horizon, order = case["horizon"], model["order"]
    require(sorted(order) == list(range(horizon)), "Invalid direct-check order")
    for g in case["units"]:
        n, width = g["name"], frac(float(g["pmax"] - g["pmin"]))
        for t in range(horizon):
            u, y, z, d, q, r = [get(f, n, t) for f in ("U", "Y", "Z", "D", "Q", "R")]
            for f, value in zip(("U", "Y", "Z", "D"), (u, y, z, d)):
                if value not in (0, 1):
                    failures.append(f"binary:{f}:{n}:{t}")
            bounded(f"q:{n}:{t}", q, Fraction(0), width)
            bounded(f"r:{n}:{t}", r, Fraction(0), width)
            previous = Fraction(g["age"] > 0) if t == 0 else get("U", n, t - 1)
            equal(f"link:{n}:{t}", u - previous, y - z)
            le(f"exclusive:{n}:{t}", y + z, Fraction(1))
            equal(f"category:{n}:{t}", d, y)
            le(f"minup:{n}:{t}", sum((get("Y", n, s) for s in range(max(0, t - g["up"] + 1), t + 1)), Fraction(0)), u)
            le(f"mindown:{n}:{t}", sum((get("Z", n, s) for s in range(max(0, t - g["down"] + 1), t + 1)), Fraction(0)), 1 - u)
            le(f"headroom:{n}:{t}", q + r, width * u)
            seg = [get("S", n, t, k) for k in range(4)]
            for k in range(4):
                bounded(f"segment_box:{n}:{t}:{k}", seg[k], Fraction(0), frac(g["widths"][k]))
                le(f"segment_on:{n}:{t}:{k}", seg[k], frac(g["widths"][k]) * u)
            equal(f"production_definition:{n}:{t}", sum(seg, Fraction(0)), q)
            # Nonbinding SU/SD corrections are zero, but these native rows remain.
            le(f"startup_limit:{n}:{t}", q + r, width * u)
            if t + 1 < horizon:
                le(f"shutdown_limit:{n}:{t}", q, width * u)
            if t:
                le(f"ramp_up:{n}:{t}", q + r - get("Q", n, t - 1), frac(g["ru"]))
                le(f"ramp_down:{n}:{t}", get("Q", n, t - 1) + get("R", n, t - 1) - q, frac(g["rd"]))
            elif g["age"] > 0:
                le(f"initial_ramp_up:{n}", q + r, frac(float(float(g["initial_power"] + g["ru"]) - g["pmin"])))
                le(f"initial_ramp_down:{n}", -q, frac(float(g["rd"] - float(g["initial_power"] - g["pmin"]))))
            total_cost += frac(g["min_cost"]) * u + frac(g["startup_cost"]) * d
            total_cost += sum((frac(s) * v for s, v in zip(g["slopes"], seg)), Fraction(0))
            # Diagnostic canonical production cost; never replace saved segment objective.
            canonical_cost += frac(g["min_cost"]) * u + frac(g["startup_cost"]) * d
            nominal_capacity = sum((frac(w) for w in g["widths"]), Fraction(0)) * u
            if u not in (0, 1) or q < 0 or q > nominal_capacity:
                canonical_domain_failures.append(f"outside_nominal_PWL_domain:{n}:{t}")
            else:
                remaining = q
                for k in range(4):
                    amount = min(remaining, frac(g["widths"][k]) * u)
                    canonical_cost += amount * frac(g["slopes"][k])
                    remaining -= amount
        residual = g["up"] - g["age"] if g["age"] > 0 else g["down"] + g["age"]
        forbidden = "Z" if g["age"] > 0 else "Y"
        equal(f"initial_dwell:{n}", sum((get(forbidden, n, t) for t in range(max(0, min(residual, horizon)))), Fraction(0)), Fraction(0))
    for t, src in enumerate(order):
        curtail, shortfall, injection = (get(f, "system", t) for f in ("C", "F", "N"))
        maximum = frac(case["load"][src]) if model["variant"] == "native_penalized" else Fraction(0)
        bounded(f"curtail:{t}", curtail, Fraction(0), maximum)
        bounded(f"shortfall:{t}", shortfall, Fraction(0), Fraction(0))
        bounded(f"injection_box:{t}", injection, Fraction(0), Fraction(0))
        production = sum((frac(g["pmin"]) * get("U", g["name"], t) + get("Q", g["name"], t) for g in case["units"]), Fraction(0))
        equal(f"nodal:{t}", production + curtail - injection, frac(case["load"][src]))
        equal(f"balance:{t}", injection, Fraction(0))
        available_reserve = shortfall + sum((get("R", g["name"], t) for g in case["units"]), Fraction(0))
        le(f"reserve:{t}", frac(case["reserve"][src]), available_reserve)
        total_cost += curtail * frac(case["penalty"][src])
        canonical_cost += curtail * frac(case["penalty"][src])
    matrix_cost = sum((frac(c["objective"]) * values[c["name"]] for c in model["columns"]), Fraction(0))
    if matrix_cost != total_cost:
        failures.append("objective_coefficients_disagree_with_native_cost")
    return {"accepted": not failures, "tau": rational(tolerance), "nominal_max_violation": rational(worst),
            "exact_saved_segment_objective": rational(total_cost),
            "canonical_greedy_cost_diagnostic": None if canonical_domain_failures else rational(canonical_cost),
            "canonical_domain_failures": canonical_domain_failures,
            "canonical_cost_is_not_substituted_for_saved_objective": True, "failures": failures}


def prospective_orders():
    """Called only by separately authorized scientific preparation."""
    identity = list(range(24))
    reversal = identity[:4] + list(reversed(identity[4:20])) + identity[20:]
    rotation = identity[:4] + identity[5:20] + identity[4:5] + identity[20:]
    return {"identity": identity, "reverse_4_19": reversal, "rotate_left1_4_19": rotation}


def prepare(case_path, source_root, protocol_path, output):
    case_path, protocol_path = Path(case_path), Path(protocol_path)
    raw_case = case_path.read_bytes()
    script = Path(__file__).read_bytes()
    protocol = protocol_path.read_bytes()
    case = parse_selected(raw_case)
    source_root, output = Path(source_root), Path(output)
    require(not output.exists(), "Preparation output must be new")
    source_bytes = {}
    for rel, expected in SOURCE_SHA.items():
        b = (source_root / rel).read_bytes()
        require(sha(b) == expected, "Upstream source mismatch: " + rel)
        source_bytes[rel] = b
    require(protocol_path.name == "ORLIB_TRANSFER_PROTOCOL.md", "Wrong protocol")
    output.mkdir(parents=True, exist_ok=False)
    (output / "selected_case.json.gz").write_bytes(raw_case)
    (output / "normalized_case.json").write_bytes(encode(case))
    (output / "ORLIB_TRANSFER_PROTOCOL.md").write_bytes(protocol)
    (output / "researchnext_orlib_uc.py").write_bytes(script)
    for rel, b in source_bytes.items():
        dest = output / "upstream" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b)
    records = []
    for name, order in prospective_orders().items():
        require(order[:4] == list(range(4)) and order[20:] == list(range(20, 24)), "Endpoint contract")
        for variant in ("native_penalized", "hard_service"):
            model = build(case, variant, order)
            path = name + "__" + variant + ".json"
            (output / path).write_bytes(encode(model))
            records.append({"case": name, "variant": variant, "file": path,
                            "rows": len(model["rows"]), "columns": len(model["columns"]),
                            "binary_columns": model["binary_count"]})
    descriptor = {"status": "PREPARED_NOT_SOLVED", "source_commit": COMMIT,
                  "case_url": CASE_URL, "case_sha256": GZIP_SHA, "models": records,
                  "positive_control": "identity input and subsequently accepted identity witness; no extra optimization",
                  "solver_calls": 0, "runtime_JuMP_matrix_equivalence": "NOT_TESTED"}
    # The normalized case and archive derive from the same captured bytes.
    # Check every original input again before declaring the preparation closed.
    require(case_path.read_bytes() == raw_case, "Case changed during preparation")
    require(protocol_path.read_bytes() == protocol, "Protocol changed during preparation")
    require(Path(__file__).read_bytes() == script, "Adapter changed during preparation")
    for rel, b in source_bytes.items():
        require((source_root / rel).read_bytes() == b, "Upstream source changed during preparation: " + rel)
    descriptor["immutable_input_snapshots_and_final_recheck"] = True
    descriptor["snapshot_sha256"] = {"case_gzip": sha(raw_case), "adapter": sha(script), "protocol": sha(protocol)}
    (output / "descriptor.json").write_bytes(encode(descriptor))
    files = [{"path": p.relative_to(output).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p.read_bytes())}
             for p in sorted(output.rglob("*")) if p.is_file()]
    (output / "manifest.json").write_bytes(encode({"schema": "orlib-prepared-manifest-v1", "files": files}))
    return descriptor


def synthetic_fixture():
    return normalize({"Parameters": {"Version": "0.3", "Time horizon (h)": 4},
                      "Buses": {"b": {"Load (MW)": [10, 10, 10, 10]}},
                      "Reserves": {"r": {"Type": "spinning", "Amount (MW)": [0, 0, 0, 0]}},
                      "Generators": {"g": {"Bus": "b", "Production cost curve (MW)": [5, 10, 15, 20, 25],
                                            "Production cost curve ($)": [10, 15, 25, 40, 60],
                                            "Startup costs ($)": [100], "Startup delays (h)": [2],
                                            "Minimum uptime (h)": 2, "Minimum downtime (h)": 2,
                                            "Ramp up limit (MW)": 100, "Ramp down limit (MW)": 100,
                                            "Initial status (h)": 3, "Initial power (MW)": 10,
                                            "Reserve eligibility": ["r"]}}})


def self_test():
    """Synthetic adversarial checks only; not a native scientific case run."""
    case = synthetic_fixture()
    model = build(case, "native_penalized", list(range(4)))
    index = {c["name"]: j for j, c in enumerate(model["columns"])}
    vector = [0.0] * len(index)
    for t in range(4):
        vector[index[column_name("U", "g", t)]] = 1.0
        vector[index[column_name("Q", "g", t)]] = 5.0
        vector[index[column_name("S", "g", t, 3)]] = 5.0
    checks = []

    def expect(label, candidate_case, candidate_model, candidate_vector, expected, contains=None):
        m = exact_matrix_check(candidate_model, candidate_vector)
        d = direct_check(candidate_case, candidate_model, candidate_vector)
        require(m["accepted"] == expected and d["accepted"] == expected, "Synthetic test failed: " + label)
        if contains:
            require(any(contains in s for s in m["failures"]), "Missing matrix failure: " + label)
            require(any(contains in s for s in d["failures"]), "Missing semantic failure: " + label)
        checks.append({"name": label, "matrix_accepted": m["accepted"], "direct_accepted": d["accepted"]})
        return m, d

    _, direct = expect("noncanonical_segments_are_valid_but_cost_more", case, model, vector, True)
    require(direct["exact_saved_segment_objective"]["numerator"] == "120", "Segment objective lost")
    require(direct["canonical_greedy_cost_diagnostic"]["numerator"] == "60", "Canonical diagnostic wrong")
    changed = vector[:]
    changed[index[column_name("D", "g", 0)]] = 0.5
    expect("fractional_startup_category_rejected", case, model, changed, False, "binary")
    off = [0.0] * len(index)
    off[index[column_name("Z", "g", 0)]] = 1.0
    for t in range(4):
        off[index[column_name("C", "system", t)]] = 10.0
    expect("native_curtailment_is_a_real_feasible_variable", case, model, off, True)
    hard = build(case, "hard_service", list(range(4)))
    expect("same_curtailment_point_fails_hard_service", case, hard, off, False)
    initial = copy.deepcopy(case)
    initial["units"][0]["initial_power"] = 14.0
    initial["units"][0]["rd"] = 4.0
    initial_model = build(initial, "native_penalized", list(range(4)))
    expect("initially_on_shutdown_respects_native_above_minimum_row", initial, initial_model, off, False, "initial_ramp_down")
    dwell = copy.deepcopy(case)
    dwell["units"][0]["age"] = 1
    dwell["units"][0]["up"] = 3
    dwell_model = build(dwell, "native_penalized", list(range(4)))
    expect("residual_initial_dwell_not_reset", dwell, dwell_model, off, False, "initial_dwell")
    mutated = copy.deepcopy(model)
    mutated["columns"][index[column_name("S", "g", 0, 3)]]["objective"] += 1.0
    require(not direct_check(case, mutated, vector)["accepted"], "Objective tampering not detected")
    checks.append({"name": "semantic_cost_detects_objective_tampering", "accepted_tamper": False})
    # A separate initial-model mutation demonstrates direct checks do not read rows.
    mutated = copy.deepcopy(initial_model)
    mutated["rows"] = [r for r in mutated["rows"] if not r["name"].startswith("initial_ramp_down")]
    require(exact_matrix_check(mutated, off)["accepted"] and not direct_check(initial, mutated, off)["accepted"],
            "Direct checker failed to catch deleted initial ramp")
    checks.append({"name": "deleted_initial_ramp_caught_independently", "accepted_tamper": False})
    out_of_domain = vector[:]
    out_of_domain[index[column_name("Q", "g", 0)]] = -1e-6
    diagnostic = direct_check(case, model, out_of_domain, 1e-5)
    require(diagnostic["canonical_greedy_cost_diagnostic"] is None and diagnostic["canonical_domain_failures"],
            "Outside-domain PWL diagnostic must be null, never clipped")
    checks.append({"name": "outside_nominal_PWL_domain_returns_null_without_clipping", "diagnostic": None})
    return {"status": "PASS_SYNTHETIC_ONLY", "tests": checks, "scientific_models_built": 0,
            "scientific_permutations_generated": 0, "solver_calls": 0, "network_calls": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    test = sub.add_parser("self-test")
    test.add_argument("--report", required=True)
    inspection = sub.add_parser("inspect")
    inspection.add_argument("--case-gzip", required=True)
    prep = sub.add_parser("prepare")
    for flag in ("case-gzip", "source-root", "protocol", "output"):
        prep.add_argument("--" + flag, required=True)
    check = sub.add_parser("check")
    for flag in ("case-gzip", "model", "vector", "report"):
        check.add_argument("--" + flag, required=True)
    check.add_argument("--tau", type=float, default=0.0)
    args = parser.parse_args()
    if args.command == "inspect":
        result = read_selected(args.case_gzip)
    elif args.command == "prepare":
        result = prepare(args.case_gzip, args.source_root, args.protocol, args.output)
    elif args.command == "self-test":
        result = self_test()
    else:
        case = read_selected(args.case_gzip)
        model = json.loads(Path(args.model).read_text(encoding="utf-8"))
        require(model == build(case, model["variant"], model["order"]), "Model does not equal declared source-derived encoding")
        vector = json.loads(Path(args.vector).read_text(encoding="utf-8"))
        result = {"matrix": exact_matrix_check(model, vector, args.tau), "direct": direct_check(case, model, vector, args.tau),
                  "model_sha256": sha(Path(args.model).read_bytes()), "vector_sha256": sha(Path(args.vector).read_bytes())}
        result["accepted"] = result["matrix"]["accepted"] and result["direct"]["accepted"]
    if hasattr(args, "report"):
        report = Path(args.report)
        report.parent.mkdir(parents=True, exist_ok=True)
        with report.open("xb") as f:
            f.write(encode(result))
    print(json.dumps({"command": args.command, "status": result.get("status", result.get("accepted", "SOURCE_INSPECTION"))}))


if __name__ == "__main__":
    main()
