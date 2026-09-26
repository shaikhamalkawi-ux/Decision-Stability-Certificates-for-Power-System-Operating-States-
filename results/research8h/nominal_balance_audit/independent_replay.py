"""Solver-free independent integer-dyadic replay of the completed balance audit.

No imports from the audited runner or its Fraction checker. All arithmetic below
uses a single power-of-two denominator per archived model and integer products.
"""
from __future__ import annotations

import ast
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import time
import zipfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_npz(path, expected):
    with zipfile.ZipFile(path) as archive:
        assert len(archive.namelist()) == len(expected)
        assert set(archive.namelist()) == {name + ".npy" for name in expected}
        result = {}
        for name in expected:
            raw = archive.read(name + ".npy")
            assert raw[:6] == b"\x93NUMPY"
            version = tuple(raw[6:8])
            assert version in {(1, 0), (2, 0), (3, 0)}
            width = 2 if version == (1, 0) else 4
            n = int.from_bytes(raw[8:8 + width], "little")
            start = 8 + width
            header = ast.literal_eval(raw[start:start+n].decode("utf8"))
            assert not header["fortran_order"]
            shape = header["shape"]
            assert isinstance(shape, tuple) and all(type(v) is int and v >= 0 for v in shape)
            count = math.prod(shape)
            dtype = header["descr"]
            formats = {"<f8": "d", "<i4": "i", "<i8": "q", "|u1": "B", "|S3": "3s"}
            assert dtype in formats, dtype
            fmt = "<" + formats[dtype]
            data = raw[start+n:]
            assert len(data) == count * struct.calcsize(fmt)
            values = tuple(v[0] for v in struct.iter_unpack(fmt, data))
            result[name] = (shape, values)
    return result


def record(numerator, denominator):
    divisor = math.gcd(numerator, denominator)
    return {"numerator": str(numerator // divisor), "denominator": str(denominator // divisor)}


def same(recorded, numerator, denominator):
    return int(recorded["numerator"]) * denominator == numerator * int(recorded["denominator"])


def main():
    begun = time.perf_counter()
    summary = json.loads((HERE / "summary.json").read_text())
    assert summary["all_frozen_inputs_unchanged"] and summary["optimization_calls"] == 0
    assert [r["month"] for r in summary["months"]] == [1, 4, 7, 10]
    freeze = json.loads((HERE / "freeze.json").read_text())
    assert freeze["months"] == [1, 4, 7, 10]
    for item in freeze["inputs"]:
        p = Path(item["path"])
        assert p.stat().st_size == item["bytes"] and digest(p) == item["sha256"]
    outputs = []
    for month, expected_summary in zip((1, 4, 7, 10), summary["months"]):
        directory = ROOT / f"results/research8h/seasonal_reference/month_{month:02d}"
        sparse = read_npz(directory / "matrix.npz", ("data", "indices", "indptr", "shape", "format"))
        assert sparse["format"][1] == (b"csr",)
        nrows, ncols = sparse["shape"][1]
        data, indices, indptr = (sparse[name][1] for name in ("data", "indices", "indptr"))
        assert len(indptr) == nrows + 1 and indptr[0] == 0 and indptr[-1] == len(data) == len(indices)
        assert all(0 <= a <= b <= len(data) for a, b in zip(indptr, indptr[1:]))
        assert all(0 <= j < ncols for j in indices) and all(math.isfinite(v) for v in data)
        bounds = read_npz(directory / "bounds.npz", ("column_lower", "column_upper", "row_lower", "row_upper"))
        lower, upper, rlower, rupper = (bounds[name][1] for name in ("column_lower", "column_upper", "row_lower", "row_upper"))
        assert len(lower) == len(upper) == ncols and len(rlower) == len(rupper) == nrows
        assert all(math.isfinite(v) for v in (*lower, *upper))
        assert all(a <= b for a, b in zip(lower, upper))
        with gzip.open(directory / "row_metadata.csv.gz", "rt", newline="") as stream:
            labels = list(csv.DictReader(stream))
        assert len(labels) == nrows and all(int(r["row"]) == j for j, r in enumerate(labels))
        selected = [[] for _ in range(168)]
        for row in labels:
            if row["family"] in {"aggregate_balance", "nodal_balance"}:
                selected[int(row["hour_0based"])].append((int(row["row"]), 1 if row["family"] == "aggregate_balance" else -1))
        selected_values = [rlower[r] for hour in selected for r, sign in hour]
        assert all(math.isfinite(v) for v in selected_values)
        exponent = max(v.as_integer_ratio()[1].bit_length() - 1 for v in (*data, *lower, *upper, *selected_values, 1e-5))
        scale = 1 << exponent
        square = scale * scale

        def integer(value):
            n, d = value.as_integer_ratio()
            assert scale % d == 0
            return n * (scale // d)

        coefficients_integer = tuple(integer(v) for v in data)
        box_lower = tuple(integer(v) for v in lower)
        box_upper = tuple(integer(v) for v in upper)
        tau = integer(1e-5)
        archived = json.loads((HERE / f"month_{month:02d}.json").read_text())
        assert len(archived) == 168
        fresh = []
        for hour, choices in enumerate(selected):
            assert len(choices) == 25 and sum(sign > 0 for _, sign in choices) == 1
            assert len({r for r, _ in choices}) == 25
            row_rhs, combined = 0, {}
            for row, sign in choices:
                assert rlower[row] == rupper[row]
                row_rhs += sign * integer(rlower[row])
                row_indices = indices[indptr[row]:indptr[row + 1]]
                assert len(set(row_indices)) == len(row_indices)
                for entry in range(indptr[row], indptr[row + 1]):
                    column = indices[entry]
                    combined[column] = combined.get(column, 0) + sign * coefficients_integer[entry]
            combined = {column: value for column, value in combined.items() if value}
            minimum = sum(value * (box_lower[column] if value > 0 else box_upper[column]) for column, value in combined.items())
            maximum = sum(value * (box_upper[column] if value > 0 else box_lower[column]) for column, value in combined.items())
            strict_gaps = (row_rhs * scale - maximum, minimum - row_rhs * scale)
            penalty = tau * (25 * scale + sum(abs(v) for v in combined.values()))
            expanded_gaps = tuple(gap - penalty for gap in strict_gaps)
            got = archived[hour]
            assert got["hour_0based"] == hour
            assert same(got["rhs_difference"], row_rhs, scale)
            assert same(got["box_minimum"], minimum, square) and same(got["box_maximum"], maximum, square)
            assert got["strict_separation"] == (max(strict_gaps) > 0)
            assert got["expanded_separation"] == (max(expanded_gaps) > 0)
            assert got["exact_redundancy"] == (not combined and row_rhs == 0)
            assert got["selected_rows"] == [{"row": r, "multiplier": sign} for r, sign in choices]
            stored_coefficients = {r["column"]: r["value"] for r in got["nonzero_difference_coefficients"]}
            assert set(stored_coefficients) == set(combined)
            assert all(same(stored_coefficients[j], value, scale) for j, value in combined.items())
            assert len(got["ray_checks"]) == 2
            for index, sign in enumerate((1, -1)):
                ray = got["ray_checks"][index]
                assert ray["orientation"] == sign
                assert same(ray["check"]["separation_gap"], strict_gaps[index], square)
                assert same(ray["check"]["expanded_separation_gap"], expanded_gaps[index], square)
                assert same(ray["check"]["row_multiplier_l1"], 25, 1)
                assert same(ray["check"]["combined_column_l1"], sum(abs(v) for v in combined.values()), scale)
                assert ray["check"]["strict_pass"] == (strict_gaps[index] > 0)
                assert ray["check"]["expanded_pass"] == (expanded_gaps[index] > 0)
            fresh.append({"hour": hour, "exact_redundancy": not combined and row_rhs == 0,
                          "strict_separation": max(strict_gaps) > 0, "expanded_separation": max(expanded_gaps) > 0,
                          "rhs_integer": row_rhs, "nonzero_coefficients": len(combined),
                          "maximum_strict_gap_integer": max(strict_gaps), "maximum_expanded_gap_integer": max(expanded_gaps)})
        computed = {"month": month, "hours": 168,
                    "exact_redundancy_hours": sum(r["exact_redundancy"] for r in fresh),
                    "strict_separation_hours": sum(r["strict_separation"] for r in fresh),
                    "expanded_separation_hours": sum(r["expanded_separation"] for r in fresh),
                    "maximum_absolute_rhs_difference": record(max(abs(r["rhs_integer"]) for r in fresh), scale)}
        assert {k: v for k, v in expected_summary.items() if k != "maximum_absolute_rhs_difference"} == {k: v for k, v in computed.items() if k != "maximum_absolute_rhs_difference"}
        assert same(expected_summary["maximum_absolute_rhs_difference"], max(abs(r["rhs_integer"]) for r in fresh), scale)
        computed.update(integer_scale_exponent=exponent, every_record_and_both_ray_gaps_match=True,
                        strict_separation_hour_indices=[r["hour"] for r in fresh if r["strict_separation"]],
                        maximum_strict_gap=record(max(r["maximum_strict_gap_integer"] for r in fresh), square),
                        maximum_expanded_gap=record(max(r["maximum_expanded_gap_integer"] for r in fresh), square),
                        distinct_nonzero_coefficient_counts=sorted({r["nonzero_coefficients"] for r in fresh}),
                        archived_month_sha256=digest(HERE / f"month_{month:02d}.json"))
        outputs.append(computed)
        print(json.dumps({"month": month, "independent_replay": "PASS", "strict_separation_hours": computed["strict_separation_hours"], "expanded_separation_hours": computed["expanded_separation_hours"]}), flush=True)
    for item in freeze["inputs"]:
        p = Path(item["path"])
        assert p.stat().st_size == item["bytes"] and digest(p) == item["sha256"]
    result = {"status": "INDEPENDENT_INTEGER_DYADIC_REPLAY_PASS", "months": outputs,
              "hours_checked": 672, "ray_orientations_checked": 1344, "optimization_calls": 0,
              "all_input_freeze_hashes_match": True, "replay_source_sha256": digest(__file__),
              "original_summary_sha256": digest(HERE / "summary.json"), "original_freeze_sha256": digest(HERE / "freeze.json"),
              "python_version": sys.version, "elapsed_s": time.perf_counter() - begun,
              "scope": "Independently decoded CSR/NPY inputs and integer dyadic interval/separation arithmetic; no optimizer, Fraction checker, or native-model reconstruction."}
    with (HERE / "independent_replay.json").open("x", encoding="utf8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
