"""Pure, selected-input transport for the frozen OR-LIB reverse target.

Only self_test performs file I/O, and it uses invented data.  transform accepts
three byte strings; it neither reads files nor imports an adapter or solver.
This admission checks hourly transport and schema, not native model equivalence.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import io
import json
import math
import struct
from pathlib import Path

COMMIT = "4f04f0dd6641b071fd7556346c3d7190c2ffdfe5"
SOURCE_GZIP_SHA256 = "6ef95ef5a1966914306da848f2ffa4bd835c49d520e30b1dcbcfa948eee85cbe"
SOURCE_JSON_SHA256 = "3cfa5d6f0135e732edd7cb08f887cda0c7e56b0b8e766185d05b52e0ee1f3308"
FIXED_ORDER = (0, 1, 2, 3, 19, 18, 17, 16, 15, 14, 13, 12,
               11, 10, 9, 8, 7, 6, 5, 4, 20, 21, 22, 23)
MODEL_SCHEMA = "orlib-uc-source-derived-binary64-v1"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")


def canonical(value):
    # Preserves JSON numeric type and binary64 round-trip values, including -0.0.
    return json.dumps(value, ensure_ascii=False, allow_nan=False,
                      sort_keys=True, separators=(",", ":")).encode("utf-8")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def parse(payload):
    require(type(payload) is bytes, "Inputs must be immutable bytes")
    def reject(value):
        raise ValueError("Nonfinite JSON constant: " + value)
    result = json.loads(payload, object_pairs_hook=unique_object, parse_constant=reject)
    require(type(result) is dict, "Expected top-level JSON object")
    return result


def number(value):
    require(type(value) in (int, float), "Expected numeric scalar, not bool/list")
    value = float(value)
    require(math.isfinite(value), "Nonfinite binary64 value")
    return value


def bits(value):
    return struct.pack(">d", number(value)).hex()


def equal_number(actual, expected, label):
    require(bits(actual) == bits(expected), "Binary64 mismatch: " + label)


def series(value, horizon, label):
    values = value if type(value) is list else [value] * horizon
    require(len(values) == horizon, "Wrong series length: " + label)
    require(all(number(v) >= 0 for v in values), "Negative series: " + label)
    return values


def deterministic_gzip(payload):
    sink = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=sink,
                       compresslevel=9, mtime=0) as stream:
        stream.write(payload)
    return sink.getvalue()


def _raw_schema(raw, normal, horizon, unit_names, bus, reserve):
    require(set(raw) <= {"Parameters", "Buses", "Generators", "Reserves", "SOURCE", "LICENSE"},
            "Unexpected top-level source field")
    require({"Parameters", "Buses", "Generators", "Reserves", "SOURCE", "LICENSE"} <= set(raw),
            "Missing source structure or attribution")
    params = raw["Parameters"]
    require(type(params) is dict and set(params) <= {
        "Version", "Time horizon (h)", "Time (h)", "Time step (min)", "Power balance penalty ($/MW)"},
        "Unexpected Parameters field")
    require(params.get("Version") in ("0.3", "0.4"), "Unsupported source version")
    for key in ("Time horizon (h)", "Time (h)"):
        if key in params:
            require(type(params[key]) is int and params[key] == horizon, "Wrong source horizon")
    require("Time horizon (h)" in params or "Time (h)" in params, "Missing horizon")
    require(type(params.get("Time step (min)", 60)) is int and params.get("Time step (min)", 60) == 60,
            "Require one-hour steps")
    require(type(raw["Buses"]) is dict and list(raw["Buses"]) == [bus], "Wrong bus")
    require(type(raw["Reserves"]) is dict and list(raw["Reserves"]) == [reserve], "Wrong reserve")
    b, r = raw["Buses"][bus], raw["Reserves"][reserve]
    require(type(b) is dict and set(b) == {"Load (MW)"}, "Unsupported bus fields")
    require(type(r) is dict and set(r) <= {"Type", "Amount (MW)", "Shortfall penalty ($/MW)"}
            and {"Type", "Amount (MW)"} <= set(r), "Unsupported reserve fields")
    require(type(r["Type"]) is str and r["Type"].lower() == "spinning", "Wrong reserve type")
    require(number(r.get("Shortfall penalty ($/MW)", -1)) < 0, "Reserve shortfall must be disabled")
    require(type(b["Load (MW)"]) is list, "Require explicit hourly load")
    load = series(b["Load (MW)"], horizon, "load")
    reserve_values = series(r["Amount (MW)"], horizon, "reserve")
    # This selected input has an omitted scalar default; no unreviewed varying
    # penalty field is silently left at its original hour.
    penalty_scalar = number(params.get("Power balance penalty ($/MW)", 1000.0))
    penalty = series(penalty_scalar, horizon, "penalty")
    require(type(normal.get("horizon")) is int and normal["horizon"] == horizon
            and normal.get("bus") == bus and normal.get("reserve_name") == reserve,
            "Normalized dimensions or names changed")
    for key, source in (("load", load), ("reserve", reserve_values), ("penalty", penalty)):
        require(type(normal.get(key)) is list and len(normal[key]) == horizon, "Wrong normalized " + key)
        for t, value in enumerate(source):
            equal_number(normal[key][t], value, "normalized " + key + ":" + str(t))
    generators = raw["Generators"]
    require(type(generators) is dict and list(generators) == unit_names, "Generator roster/order changed")
    require(type(normal.get("units")) is list and [g.get("name") for g in normal["units"]] == unit_names,
            "Normalized roster changed")
    allowed = {"Bus", "Type", "Production cost curve (MW)", "Production cost curve ($)",
               "Startup costs ($)", "Startup delays (h)", "Minimum uptime (h)", "Minimum downtime (h)",
               "Ramp up limit (MW)", "Ramp down limit (MW)", "Startup limit (MW)", "Shutdown limit (MW)",
               "Initial status (h)", "Initial power (MW)", "Must run?", "Reserve eligibility"}
    for name, unit in zip(unit_names, normal["units"]):
        g = generators[name]
        require(type(g) is dict and set(g) <= allowed, "Unexpected generator/time-varying field: " + name)
        require(g.get("Bus") == bus and g.get("Type", "Thermal").lower() == "thermal"
                and g.get("Must run?", False) is False and g.get("Reserve eligibility") == [reserve],
                "Unsupported generator identity/features")
        mw, cost = g["Production cost curve (MW)"], g["Production cost curve ($)"]
        require(type(mw) is list and type(cost) is list and len(mw) == len(cost) == 5,
                "Require four constant scalar cost segments")
        mw, cost = [number(v) for v in mw], [number(v) for v in cost]
        widths = [mw[k + 1] - mw[k] for k in range(4)]
        require(all(w > 0 for w in widths), "Nonpositive segment width")
        slopes = [(cost[k + 1] - cost[k]) / widths[k] for k in range(4)]
        require(all(v >= 0 for v in mw + cost + slopes)
                and all(slopes[k] <= slopes[k + 1] for k in range(3)), "Cost repair would be required")
        require(type(g.get("Startup costs ($)")) is list and len(g["Startup costs ($)"]) == 1
                and type(g.get("Startup delays (h)")) is list and len(g["Startup delays (h)"]) == 1,
                "Require one scalar startup category")
        for key, nk in (("Minimum uptime (h)", "up"), ("Minimum downtime (h)", "down"),
                        ("Initial status (h)", "age")):
            require(type(g[key]) is int and type(unit.get(nk)) is int and g[key] == unit[nk],
                    "Initial/dwell mismatch")
        require(g["Minimum uptime (h)"] > 1 and g["Minimum downtime (h)"] > 0
                and g["Initial status (h)"] != 0, "Unsupported initial/dwell values")
        delay = g["Startup delays (h)"][0]
        require(type(delay) is int and delay == g["Minimum downtime (h)"]
                and type(unit.get("startup_delay")) is int and unit["startup_delay"] == delay,
                "Startup delay mismatch")
        for nk, value in (("pmin", mw[0]), ("pmax", mw[-1]), ("min_cost", cost[0]),
                          ("startup_cost", g["Startup costs ($)"][0]),
                          ("initial_power", g["Initial power (MW)"]),
                          ("ru", g["Ramp up limit (MW)"]), ("rd", g["Ramp down limit (MW)"]),
                          ("su", g.get("Startup limit (MW)", 1e6)),
                          ("sd", g.get("Shutdown limit (MW)", 1e6))):
            equal_number(unit[nk], value, name + ":" + nk)
        for nk, values in (("widths", widths), ("slopes", slopes), ("original_mw", mw), ("original_cost", cost)):
            require(type(unit.get(nk)) is list and len(unit[nk]) == len(values), "Normalized curve length")
            for actual, value in zip(unit[nk], values):
                equal_number(actual, value, name + ":" + nk)
        require(number(unit["su"]) >= mw[-1] and number(unit["sd"]) >= mw[-1], "Nonzero startup corrections")
    return load, reserve_values, penalty


def _transport(raw_gzip_bytes, model_json_bytes, normal_json_bytes, *, horizon, unit_names,
               bus, reserve, expected_order, production):
    require(all(type(b) is bytes for b in (raw_gzip_bytes, model_json_bytes, normal_json_bytes)),
            "Inputs must be bytes")
    original_json = gzip.decompress(raw_gzip_bytes)
    raw, model, normal = parse(original_json), parse(model_json_bytes), parse(normal_json_bytes)
    source_json_sha = sha(original_json)
    require(model.get("schema") == MODEL_SCHEMA and model.get("variant") == "native_penalized",
            "Wrong model schema/service variant")
    require(model.get("source_commit") == COMMIT and normal.get("source_software_commit") == COMMIT,
            "Wrong native source revision")
    require(model.get("case_json_sha256") == source_json_sha == normal.get("case_json_sha256"),
            "Original source-to-normal/model hash mismatch")
    require(model.get("synthetic_fixture") is (not production)
            and normal.get("synthetic_fixture") is (not production), "Wrong scientific/fixture admission")
    require(type(model.get("horizon")) is int and model["horizon"] == horizon, "Wrong model horizon")
    order = model.get("order")
    require(type(order) is list and all(type(v) is int for v in order)
            and order == list(expected_order) and sorted(order) == list(range(horizon)), "Wrong frozen order")
    load, reserves, penalty = _raw_schema(raw, normal, horizon, unit_names, bus, reserve)
    columns, rows = model.get("columns"), model.get("rows")
    require(type(columns) is list and type(rows) is list, "Missing model arrays")
    expected_names = []
    expected_binary = set()
    for name in unit_names:
        for t in range(horizon):
            for family in ("U", "Y", "Z", "D", "Q", "R"):
                cn = f"{family}:{name}:{t}"
                expected_names.append(cn)
                if family in ("U", "Y", "Z", "D"):
                    expected_binary.add(cn)
            expected_names.extend(f"S:{name}:{t}:{k}" for k in range(4))
    expected_names.extend(f"{family}:system:{t}" for t in range(horizon) for family in ("C", "F", "N"))
    require([c.get("name") for c in columns] == expected_names, "Column dimension/order/name mismatch")
    index = {c["name"]: j for j, c in enumerate(columns)}
    for col in columns:
        require(set(col) == {"name", "lower", "upper", "objective", "binary"}, "Unexpected column schema")
        require(type(col["binary"]) is bool and col["binary"] == (col["name"] in expected_binary),
                "Original binary mask mismatch")
        require(number(col["lower"]) <= number(col["upper"]), "Invalid finite column bounds")
        number(col["objective"])
        if col["binary"]:
            equal_number(col["lower"], 0.0, "binary lower")
            equal_number(col["upper"], 1.0, "binary upper")
    require(type(model.get("binary_count")) is int and model["binary_count"] == len(expected_binary),
            "Binary count mismatch")
    row_index = {}
    for row in rows:
        require(type(row) is dict and set(row) == {"name", "coefficients", "lower", "upper"}
                and type(row["name"]) is str and row["name"] not in row_index, "Duplicate/invalid row schema")
        require(type(row["coefficients"]) is list, "Invalid coefficients")
        previous = -1
        for pair in row["coefficients"]:
            require(type(pair) is list and len(pair) == 2 and type(pair[0]) is int
                    and previous < pair[0] < len(columns), "Unordered/duplicate/invalid coefficient index")
            require(number(pair[1]) != 0, "Explicit zero coefficient")
            previous = pair[0]
        for side in ("lower", "upper"):
            if row[side] is not None:
                number(row[side])
        require(row["lower"] is None or row["upper"] is None
                or number(row["lower"]) <= number(row["upper"]), "Invalid row interval")
        row_index[row["name"]] = row

    def check_row(name, coefficients, lower, upper):
        require(name in row_index, "Missing hourly row: " + name)
        row = row_index[name]
        actual = {j: bits(a) for j, a in row["coefficients"]}
        expect = {index[k]: bits(v) for k, v in coefficients.items() if number(v) != 0}
        require(actual == expect, "Hourly coefficient mismatch: " + name)
        for side, value in (("lower", lower), ("upper", upper)):
            if value is None:
                require(row[side] is None, "Unexpected finite row side: " + name)
            else:
                equal_number(row[side], value, name + ":" + side)

    hourly_audit = []
    for t, src in enumerate(order):
        cn, fn, nn = (f"{f}:system:{t}" for f in ("C", "F", "N"))
        for name, upper, objective in ((cn, load[src], penalty[src]), (fn, 0.0, 0.0), (nn, 0.0, 0.0)):
            col = columns[index[name]]
            for key, value in (("lower", 0.0), ("upper", upper), ("objective", objective)):
                equal_number(col[key], value, name + ":" + key)
        injection = {cn: 1.0, nn: -1.0}
        reserve_coeff = {fn: 1.0}
        for g in normal["units"]:
            injection[f"Q:{g['name']}:{t}"] = 1.0
            injection[f"U:{g['name']}:{t}"] = g["pmin"]
            reserve_coeff[f"R:{g['name']}:{t}"] = 1.0
        check_row(f"net_injection:{t}", injection, load[src], load[src])
        check_row(f"balance:{t}", {nn: 1.0}, 0.0, 0.0)
        check_row(f"reserve:{t}", reserve_coeff, reserves[src], None)
        hourly_audit.append({"destination_hour": t, "source_hour": src,
            "load_binary64_hex": bits(load[src]), "reserve_binary64_hex": bits(reserves[src]),
            "penalty_binary64_hex": bits(penalty[src]),
            "checked_rows": [f"net_injection:{t}", f"balance:{t}", f"reserve:{t}"],
            "curtailment_column_index": index[cn]})
    if production:
        require(len(columns) == 2472 and len(rows) == 4384 and len(expected_binary) == 960,
                "Selected model dimension mismatch")
        require(all(number(v) == 0 for v in reserves), "Selected reserve requirements changed")

    target = copy.deepcopy(raw)
    target["Buses"][bus]["Load (MW)"] = [copy.deepcopy(load[s]) for s in order]
    amount = raw["Reserves"][reserve]["Amount (MW)"]
    if type(amount) is list:
        target["Reserves"][reserve]["Amount (MW)"] = [copy.deepcopy(amount[s]) for s in order]
    before, after = copy.deepcopy(raw), copy.deepcopy(target)
    for obj in (before, after):
        obj["Buses"][bus]["Load (MW)"] = "<transported load>"
        obj["Reserves"][reserve]["Amount (MW)"] = "<transported reserve>"
    require(canonical(before) == canonical(after), "Nontransport JSON subtree changed")
    target_json = encode(target)
    require(canonical(parse(target_json)) == canonical(target), "Target JSON round-trip changed a value/type")
    target_gzip = deterministic_gzip(target_json)
    require(gzip.decompress(target_gzip) == target_json, "Target gzip round-trip mismatch")
    audit = {"schema": "native-reverse-input-transport-v1", "status": "TRANSPORT_ONLY_PASS",
        "case": "reverse_4_19__native_penalized" if production else "INVENTED_FIXTURE",
        "production": production, "order_destination_to_source": order,
        "source_software_commit": COMMIT,
        "inputs": {"source_gzip": {"bytes": len(raw_gzip_bytes), "sha256": sha(raw_gzip_bytes)},
                   "source_json": {"bytes": len(original_json), "sha256": source_json_sha},
                   "old_target_model": {"bytes": len(model_json_bytes), "sha256": sha(model_json_bytes)},
                   "original_normalized_case": {"bytes": len(normal_json_bytes), "sha256": sha(normal_json_bytes)}},
        "outputs": {"target_json": {"bytes": len(target_json), "sha256": sha(target_json)},
                    "target_gzip": {"bytes": len(target_gzip), "sha256": sha(target_gzip)}},
        "unchanged_subtrees": {k: {"canonical_sha256": sha(canonical(raw[k])),
                                  "exact_json_types_and_values_preserved": True}
                               for k in ("Parameters", "Generators", "SOURCE", "LICENSE")},
        "nontransport_structure_sha256": sha(canonical(before)),
        "penalty_field_present": "Power balance penalty ($/MW)" in raw["Parameters"],
        "reserve_representation_preserved": "list" if type(amount) is list else "scalar",
        "binary_count": len(expected_binary), "columns": len(columns), "rows": len(rows),
        "binary_mask_sha256": sha(canonical([j for j, c in enumerate(columns) if c["binary"]])),
        "hourly_transport": hourly_audit, "gzip_mtime": 0,
        "source_files_read": 0, "adapter_models_generated": 0, "candidate_or_dual_transforms": 0,
        "solver_calls": 0, "native_reads": 0, "native_builds": 0,
        "native_model_correspondence": "NOT_TESTED_BY_TRANSPORT"}
    return target_json, target_gzip, audit


def transform(raw_gzip_bytes, model_json_bytes, normal_json_bytes):
    """Return (target_json_bytes, target_gzip_bytes, audit) for the one pinned case.

    The caller owns source/preparation/output bindings and subsequent native
    comparison.  No paths or external state are consulted by this function.
    """
    require(type(raw_gzip_bytes) is bytes and len(raw_gzip_bytes) == 2419
            and sha(raw_gzip_bytes) == SOURCE_GZIP_SHA256, "Wrong selected source gzip")
    original = gzip.decompress(raw_gzip_bytes)
    require(len(original) == 6811 and sha(original) == SOURCE_JSON_SHA256, "Wrong selected source JSON")
    return _transport(raw_gzip_bytes, model_json_bytes, normal_json_bytes, horizon=24,
                      unit_names=["g" + str(i) for i in range(10)], bus="b1", reserve="r1",
                      expected_order=FIXED_ORDER, production=True)


def _invented_fixture():
    # Four-hour one-unit handwritten fixture; deliberately distinct binary64
    # decimals, mixed JSON int/float types, signed zero and nonzero reserves.
    raw = {"Parameters": {"Version": "0.3", "Time horizon (h)": 4},
        "Buses": {"b": {"Load (MW)": [1, 0.1, 0.10000000000000002, 4.0]}},
        "Reserves": {"r": {"Type": "spinning", "Amount (MW)": [-0.0, 0.2, 0.3, 0]}},
        "Generators": {"g": {"Bus": "b", "Production cost curve (MW)": [1, 2, 3, 4, 5],
            "Production cost curve ($)": [2, 4, 7, 11, 16], "Startup costs ($)": [3],
            "Startup delays (h)": [2], "Minimum uptime (h)": 2, "Minimum downtime (h)": 2,
            "Ramp up limit (MW)": 2.0, "Ramp down limit (MW)": 2.0,
            "Initial status (h)": -2, "Initial power (MW)": 0, "Reserve eligibility": ["r"]}},
        "SOURCE": {"label": "invented", "retain": [1, 1.0, -0.0]}, "LICENSE": "Invented test attribution"}
    order = [0, 2, 1, 3]
    unit = {"name": "g", "pmin": 1.0, "pmax": 5.0, "widths": [1.0] * 4,
        "slopes": [2.0, 3.0, 4.0, 5.0], "min_cost": 2.0, "startup_cost": 3.0,
        "up": 2, "down": 2, "age": -2, "initial_power": 0.0, "ru": 2.0, "rd": 2.0,
        "su": 1e6, "sd": 1e6, "startup_delay": 2,
        "original_mw": [1.0, 2.0, 3.0, 4.0, 5.0], "original_cost": [2.0, 4.0, 7.0, 11.0, 16.0]}
    raw_json = encode(raw)
    normal = {"horizon": 4, "bus": "b", "reserve_name": "r",
        "load": [float(v) for v in raw["Buses"]["b"]["Load (MW)"]],
        "reserve": [float(v) for v in raw["Reserves"]["r"]["Amount (MW)"]],
        "penalty": [1000.0] * 4, "units": [unit], "source_software_commit": COMMIT,
        "case_json_sha256": sha(raw_json), "synthetic_fixture": True}
    columns, rows = [], []
    for t in range(4):
        for family in ("U", "Y", "Z", "D", "Q", "R"):
            columns.append({"name": f"{family}:g:{t}", "lower": 0.0, "upper": 1.0 if family in "UYZD" else 4.0,
                            "objective": 0.0, "binary": family in "UYZD"})
        for k in range(4):
            columns.append({"name": f"S:g:{t}:{k}", "lower": 0.0, "upper": 1.0, "objective": 0.0, "binary": False})
    for t, s in enumerate(order):
        for family in ("C", "F", "N"):
            columns.append({"name": f"{family}:system:{t}", "lower": 0.0,
                            "upper": normal["load"][s] if family == "C" else 0.0,
                            "objective": 1000.0 if family == "C" else 0.0, "binary": False})
    ix = {c["name"]: j for j, c in enumerate(columns)}
    for t, s in enumerate(order):
        for name, terms, lower, upper in (
            (f"net_injection:{t}", {f"C:system:{t}": 1.0, f"N:system:{t}": -1.0,
                                    f"Q:g:{t}": 1.0, f"U:g:{t}": 1.0}, normal["load"][s], normal["load"][s]),
            (f"balance:{t}", {f"N:system:{t}": 1.0}, 0.0, 0.0),
            (f"reserve:{t}", {f"R:g:{t}": 1.0, f"F:system:{t}": 1.0}, normal["reserve"][s], None)):
            rows.append({"name": name, "coefficients": sorted([[ix[k], v] for k, v in terms.items()]),
                         "lower": lower, "upper": upper})
    model = {"schema": MODEL_SCHEMA, "source_commit": COMMIT, "case_json_sha256": sha(raw_json),
        "synthetic_fixture": True, "variant": "native_penalized", "order": order, "horizon": 4,
        "columns": columns, "rows": rows, "binary_count": 16}
    return raw, model, normal


def self_test(output_path):
    """Exercise only invented four-hour data, writing one new synthetic receipt."""
    output = Path(output_path)
    require(not output.exists(), "Synthetic receipt already exists")
    raw, model, normal = _invented_fixture()
    original_snapshots = tuple(canonical(x) for x in (raw, model, normal))
    def invoke(r=raw, m=model, n=normal):
        return _transport(deterministic_gzip(encode(r)), encode(m), encode(n), horizon=4,
                          unit_names=["g"], bus="b", reserve="r", expected_order=(0, 2, 1, 3), production=False)
    payload, compressed, audit = invoke()
    target = parse(payload)
    require(target["Buses"]["b"]["Load (MW)"] == [1, 0.10000000000000002, 0.1, 4.0], "Order applied once")
    require("Power balance penalty ($/MW)" not in target["Parameters"], "Omitted default materialized")
    require(target["Generators"] == raw["Generators"] and canonical(target["SOURCE"]) == canonical(raw["SOURCE"]),
            "Unchanged fields changed")
    require(bits(target["Reserves"]["r"]["Amount (MW)"][0]) == "8000000000000000", "Signed zero lost")
    require(tuple(canonical(x) for x in (raw, model, normal)) == original_snapshots, "Input mutation")
    require(invoke() == (payload, compressed, audit), "Nondeterministic transport")
    require(compressed[4:8] == b"\x00" * 4 and gzip.decompress(compressed) == payload, "Gzip metadata/round-trip")
    passed = ["order_applied_once", "omitted_default_preserved", "unchanged_generator_history_attribution",
              "mixed_numeric_types_and_binary64_roundtrip", "signed_zero_preserved", "input_nonmutation", "deterministic_gzip"]
    def reject(label, r=raw, m=model, n=normal):
        try:
            invoke(r, m, n)
        except (ValueError, TypeError, KeyError):
            passed.append(label)
            return
        raise AssertionError("Invalid fixture accepted: " + label)
    wrong = copy.deepcopy(model); wrong["order"] = [0, 1, 2, 3]
    reject("wrong_order_rejected", m=wrong)
    wrong = copy.deepcopy(model); wrong["rows"][3]["upper"] = 99.0
    reject("wrong_model_endpoint_rejected", m=wrong)
    wrong = copy.deepcopy(model); wrong["columns"][0]["binary"] = False
    reject("wrong_binary_mask_rejected", m=wrong)
    wrong = copy.deepcopy(model); wrong["columns"][40]["objective"] = 999.0
    reject("wrong_penalty_coefficient_rejected", m=wrong)
    wrong = copy.deepcopy(normal); wrong["load"][1] = 0.10000000000000002
    reject("one_ulp_source_normal_mismatch_rejected", n=wrong)
    # A second application cannot reuse the original source-to-model binding.
    reject("already_transported_input_rejected", r=target)
    wrong_raw = copy.deepcopy(raw); wrong_raw["Generators"]["g"]["Production cost curve (MW)"][1] = [2.0] * 4
    wrong_model, wrong_normal = copy.deepcopy(model), copy.deepcopy(normal)
    wrong_model["case_json_sha256"] = wrong_normal["case_json_sha256"] = sha(encode(wrong_raw))
    reject("time_varying_generator_curve_rejected", r=wrong_raw, m=wrong_model, n=wrong_normal)
    try:
        transform(deterministic_gzip(encode(raw)), encode(model), encode(normal))
    except ValueError:
        passed.append("invented_input_rejected_by_production_wrapper")
    else:
        raise AssertionError("Production wrapper accepted invented fixture")
    result = {"status": "PASS_INVENTED_ONLY", "source_sha256": sha(Path(__file__).read_bytes()),
        "checks": passed, "check_count": len(passed), "fixture_horizon": 4, "fixture_units": 1,
        "scientific_inputs_read": 0, "scientific_transforms": 0, "scientific_models_generated": 0,
        "optimizer_calls": 0, "native_reads": 0, "native_builds": 0}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(encode(result))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", required=True, metavar="NEW_RECEIPT")
    args = parser.parse_args()
    print(json.dumps(self_test(args.self_test), sort_keys=True))
