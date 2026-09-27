"""Verify archived CSR points and signed Farkas rays using Python's stdlib only.

No optimization, native model reconstruction, NumPy, SciPy, or pickle loading.
All mathematical arithmetic is exact for the supplied binary64 numbers.
"""
from __future__ import annotations

import argparse
import ast
import csv
from dataclasses import dataclass
from fractions import Fraction as Q
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import sys
import tempfile
import time
import zipfile


class InvalidInput(ValueError):
    pass


class UnsupportedFormat(InvalidInput):
    pass


def require(condition, message):
    if not condition:
        raise InvalidInput(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def json_read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result

    def bad_constant(value):
        raise InvalidInput("nonfinite JSON number: " + value)

    return json.loads(Path(path).read_text(encoding="utf-8-sig"),
                      object_pairs_hook=unique, parse_constant=bad_constant)


@dataclass(frozen=True)
class Array:
    dtype: str
    shape: tuple
    values: tuple


def parse_npy(blob):
    require(len(blob) >= 10 and blob[:6] == b"\x93NUMPY", "invalid NPY magic/header")
    version = tuple(blob[6:8])
    if version == (1, 0):
        start, length = 10, struct.unpack_from("<H", blob, 8)[0]
        encoding = "latin1"
    elif version in ((2, 0), (3, 0)):
        require(len(blob) >= 12, "truncated NPY header")
        start, length = 12, struct.unpack_from("<I", blob, 8)[0]
        encoding = "utf-8" if version == (3, 0) else "latin1"
    else:
        raise UnsupportedFormat("unsupported NPY version")
    require(0 < length <= 65536 and start + length <= len(blob), "invalid NPY header length")
    try:
        header = ast.literal_eval(blob[start:start + length].decode(encoding).strip())
    except (ValueError, SyntaxError, UnicodeError) as error:
        raise InvalidInput("invalid NPY literal header") from error
    require(isinstance(header, dict) and set(header) == {"descr", "fortran_order", "shape"},
            "unexpected NPY header fields")
    if header["fortran_order"] is not False:
        raise UnsupportedFormat("Fortran-order arrays are unsupported")
    dtype, shape = header["descr"], header["shape"]
    require(isinstance(shape, tuple) and len(shape) <= 2
            and all(type(x) is int and 0 <= x <= 100000000 for x in shape), "invalid NPY shape")
    allowed = {"<f8": ("<d", 8), "<i4": ("<i", 4), "<i8": ("<q", 8),
               "|u1": ("B", 1), "|S3": ("3s", 3)}
    if not isinstance(dtype, str) or dtype not in allowed:
        raise UnsupportedFormat("unsupported NPY dtype; object/structured arrays are forbidden")
    count = math.prod(shape)
    require(count <= 100000000, "NPY array exceeds supported size")
    fmt, width = allowed[dtype]
    payload = blob[start + length:]
    require(len(payload) == count * width, "NPY payload length disagrees with shape/dtype")
    return Array(dtype, shape, tuple(value[0] for value in struct.iter_unpack(fmt, payload)))


def read_npz(path, members):
    expected = {key + ".npy" for key in members}
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        require(len(names) == len(set(names)), "duplicate NPZ members")
        require(set(names) == expected, "unexpected, missing, or unsafe NPZ member")
        require(all(not entry.is_dir() and not entry.flag_bits & 1 for entry in entries),
                "directory/encrypted NPZ member")
        if any(entry.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED) for entry in entries):
            raise UnsupportedFormat("unsupported ZIP compression")
        require(sum(entry.file_size for entry in entries) <= 512 * 1024 * 1024,
                "NPZ exceeds supported uncompressed size")
        return {key: parse_npy(archive.read(key + ".npy")) for key in members}


def vector(array, dtype, length, label):
    require(array.dtype in dtype and array.shape == (length,), "invalid " + label + " dtype/shape")
    return array.values


@dataclass(frozen=True)
class Model:
    rows: int
    cols: int
    data: tuple
    indices: tuple
    indptr: tuple
    lower: tuple
    upper: tuple
    row_lower: tuple
    row_upper: tuple


def validate_model(model):
    m = model
    require(type(m.rows) is int and type(m.cols) is int and m.rows >= 0 and m.cols > 0,
            "invalid model dimensions")
    require(len(m.indices) == len(m.data) and len(m.indptr) == m.rows + 1, "CSR lengths disagree")
    require(all(type(i) is int for i in (*m.indices, *m.indptr)), "CSR indices must be integers")
    require(m.indptr[0] == 0 and m.indptr[-1] == len(m.data), "CSR pointer endpoints disagree")
    require(all(0 <= a <= b <= len(m.data) for a, b in zip(m.indptr, m.indptr[1:])),
            "CSR row pointers are not monotone/in range")
    require(all(math.isfinite(x) for x in m.data), "nonfinite matrix coefficient")
    require(all(0 <= j < m.cols for j in m.indices), "CSR column out of range")
    for row in range(m.rows):
        js = m.indices[m.indptr[row]:m.indptr[row + 1]]
        require(len(js) == len(set(js)), "duplicate CSR column within row")
    require(len(m.lower) == len(m.upper) == m.cols
            and len(m.row_lower) == len(m.row_upper) == m.rows, "bound dimensions disagree")
    require(all(math.isfinite(x) for x in (*m.lower, *m.upper)),
            "current supported scope requires finite column bounds")
    require(all(a <= b for a, b in zip(m.lower, m.upper)), "inverted column bounds")
    require(all(not math.isnan(a) and not math.isnan(b) and a != math.inf and b != -math.inf and a <= b
                for a, b in zip(m.row_lower, m.row_upper)), "invalid row bound interval")
    return m


def load_model(directory):
    directory = Path(directory)
    a = read_npz(directory / "matrix.npz", ("data", "indices", "indptr", "shape", "format"))
    require(a["format"] == Array("|S3", (), (b"csr",)), "only CSR matrices are supported")
    shape = vector(a["shape"], ("<i4", "<i8"), 2, "matrix shape")
    rows, cols = shape
    require(a["data"].dtype == "<f8" and len(a["data"].shape) == 1, "matrix data must be float64 vector")
    nnz = len(a["data"].values)
    indices = vector(a["indices"], ("<i4", "<i8"), nnz, "CSR indices")
    indptr = vector(a["indptr"], ("<i4", "<i8"), rows + 1, "CSR pointers")
    b = read_npz(directory / "bounds.npz", ("column_lower", "column_upper", "row_lower", "row_upper"))
    return validate_model(Model(rows, cols, a["data"].values, indices, indptr,
        vector(b["column_lower"], ("<f8",), cols, "column lower bounds"),
        vector(b["column_upper"], ("<f8",), cols, "column upper bounds"),
        vector(b["row_lower"], ("<f8",), rows, "row lower bounds"),
        vector(b["row_upper"], ("<f8",), rows, "row upper bounds")))


def q(value):
    require(type(value) in (int, float) and math.isfinite(value), "nonfinite/non-numeric exact input")
    return Q(value)  # Exact binary64 conversion, not decimal rounding.


def tau_value(value):
    try:
        number = float.fromhex(value) if isinstance(value, str) and "0x" in value.lower() else float(value)
    except (ValueError, TypeError, OverflowError) as error:
        raise InvalidInput("invalid tau") from error
    require(math.isfinite(number) and number >= 0, "tau must be finite and nonnegative")
    return q(number)


def rat(value):
    try:
        approximate = float(value)
    except OverflowError:
        approximate = None
    if approximate is not None and not math.isfinite(approximate):
        approximate = None
    return {"numerator": str(value.numerator), "denominator": str(value.denominator), "float": approximate}


def check_point(model, values, integer_mask, tau):
    m = validate_model(model)
    require(len(values) == m.cols and all(math.isfinite(x) for x in values), "invalid/nonfinite point")
    require(len(integer_mask) == m.cols and all(type(flag) is int and flag in (0, 1) for flag in integer_mask),
            "invalid original binary mask")
    require(isinstance(tau, Q) and tau >= 0, "tau must be a nonnegative Fraction")
    point = tuple(map(q, values))
    binary = all(not flag or point[j] in (0, 1) for j, flag in enumerate(integer_mask))
    colmax = rowmax = Q(0)
    colworst = rowworst = None
    for j, value in enumerate(point):
        for side, violation in (("lower", q(m.lower[j]) - value), ("upper", value - q(m.upper[j]))):
            if violation > colmax:
                colmax, colworst = violation, {"column": j, "side": side}
    for row in range(m.rows):
        lhs = sum((q(m.data[e]) * point[m.indices[e]] for e in range(m.indptr[row], m.indptr[row + 1])), Q(0))
        for side, bound in (("lower", m.row_lower[row]), ("upper", m.row_upper[row])):
            if math.isfinite(bound):
                violation = q(bound) - lhs if side == "lower" else lhs - q(bound)
                if violation > rowmax:
                    rowmax, rowworst = violation, {"row": row, "side": side}
    strict = binary and colmax <= 0 and rowmax <= 0
    expanded = binary and colmax <= tau and rowmax <= tau
    status = "CERTIFIED_STRICT_POINT" if strict else "CERTIFIED_EXPANDED_ONLY_POINT" if expanded else "POINT_NOT_FEASIBLE"
    return {"status": status, "strict_pass": strict, "expanded_pass": expanded,
            "original_binary_coordinates_exact": binary, "binary_coordinates": sum(integer_mask),
            "tau": rat(tau), "maximum_column_violation": rat(colmax), "worst_column": colworst,
            "maximum_row_violation": rat(rowmax), "worst_row": rowworst}


def parse_multipliers(certificate, rows):
    require(isinstance(certificate, dict) and isinstance(certificate.get("multipliers"), list),
            "certificate must contain a sparse multipliers list")
    result = {}
    for entry in certificate["multipliers"]:
        require(isinstance(entry, dict) and set(entry) == {"row", "value_hex"}, "invalid multiplier record")
        row, text = entry["row"], entry["value_hex"]
        require(type(row) is int and 0 <= row < rows and row not in result, "duplicate/out-of-range multiplier row")
        require(isinstance(text, str) and text.lower().lstrip("+-").startswith("0x"), "multiplier must be binary64 hex")
        try:
            value = float.fromhex(text)
        except (ValueError, OverflowError) as error:
            raise InvalidInput("invalid hex multiplier") from error
        require(math.isfinite(value) and value != 0, "sparse multiplier must be finite and nonzero")
        result[row] = q(value)
    return result


def check_ray(model, multipliers, tau):
    m = validate_model(model)
    require(isinstance(tau, Q) and tau >= 0, "tau must be a nonnegative Fraction")
    require(isinstance(multipliers, dict), "multipliers must be indexed by row")
    combined = [Q(0) for _ in range(m.cols)]
    beta = expanded_beta = row_norm = Q(0)
    for row, multiplier in multipliers.items():
        require(type(row) is int and 0 <= row < m.rows and isinstance(multiplier, Q) and multiplier != 0,
                "invalid sparse multiplier")
        selected = m.row_lower[row] if multiplier > 0 else m.row_upper[row]
        require(math.isfinite(selected), "multiplier sign selects infinite row endpoint at row " + str(row))
        bound = q(selected)
        beta += multiplier * bound
        expanded_beta += multiplier * (bound - tau if multiplier > 0 else bound + tau)
        row_norm += abs(multiplier)
        for entry in range(m.indptr[row], m.indptr[row + 1]):
            combined[m.indices[entry]] += multiplier * q(m.data[entry])
    maximum = expanded_maximum = column_norm = Q(0)
    for column, coefficient in enumerate(combined):
        if not coefficient:
            continue
        bound = q(m.upper[column] if coefficient > 0 else m.lower[column])
        maximum += coefficient * bound
        expanded_maximum += coefficient * (bound + tau if coefficient > 0 else bound - tau)
        column_norm += abs(coefficient)
    gap = beta - maximum
    expanded_gap = expanded_beta - expanded_maximum
    formula_gap = gap - tau * (row_norm + column_norm)
    require(expanded_gap == formula_gap, "internal widened-endpoint/norm identity mismatch")
    strict, expanded = gap > 0, expanded_gap > 0
    status = "CERTIFIED_EXPANDED_INFEASIBLE" if expanded else "CERTIFIED_STRICT_INFEASIBLE_ONLY" if strict else "VALID_NONSEPARATING_RAY"
    return {"status": status, "strict_pass": strict, "expanded_pass": expanded,
            "tau": rat(tau), "row_multiplier_nonzeros": len(multipliers),
            "combined_column_nonzeros": sum(bool(x) for x in combined), "beta": rat(beta),
            "box_maximum": rat(maximum), "separation_gap": rat(gap),
            "expanded_beta": rat(expanded_beta), "expanded_box_maximum": rat(expanded_maximum),
            "expanded_separation_gap": rat(expanded_gap), "norm_formula_gap": rat(formula_gap),
            "row_multiplier_l1": rat(row_norm), "combined_column_l1": rat(column_norm),
            "independent_widened_endpoint_identity": True}


def checked_hash(path, expected, size=None):
    require(isinstance(expected, str) and len(expected) == 64
            and all(c in "0123456789abcdef" for c in expected), "invalid SHA-256 value")
    path = Path(path)
    require(size is None or path.stat().st_size == size, "file size mismatch: " + str(path))
    actual = sha(path)
    require(actual == expected, "SHA-256 mismatch: " + str(path))
    return {"path": str(path), "sha256": actual, "bytes": path.stat().st_size}


def manifest_check(path, mappings=(), expected=None, required_hashes=()):
    path = Path(path)
    digest = sha(path)
    require(expected is None or digest == expected, "manifest SHA-256 mismatch")
    count, seen, verified_digests = 0, set(), set()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames == ["path", "sha256", "bytes"], "unsupported manifest columns")
        for record in reader:
            require(set(record) == {"path", "sha256", "bytes"}, "malformed manifest row")
            original = record["path"]
            require(isinstance(original, str) and original not in seen, "duplicate/invalid manifest path")
            seen.add(original)
            name = original.replace("\\", "/")
            for prefix, replacement in mappings:
                prefix = prefix.replace("\\", "/").rstrip("/")
                if name == prefix or name.startswith(prefix + "/"):
                    name = replacement.rstrip("/\\") + name[len(prefix):]
                    break
            target = Path(name)
            if not target.is_absolute():
                require(not (len(name) >= 2 and name[1] == ":"), "Windows manifest path needs --path-map on this host")
                target = path.parent / target
            try:
                size = int(record["bytes"])
            except (TypeError, ValueError) as error:
                raise InvalidInput("invalid manifest byte count") from error
            require(size >= 0, "negative manifest byte count")
            checked_hash(target, record["sha256"], size)
            verified_digests.add(record["sha256"])
            count += 1
    require(set(required_hashes) <= verified_digests,
            "supplied manifest does not bind all required mathematical input file contents")
    return {"path": str(path), "sha256": digest, "entries_checked": count,
            "required_input_digests_covered": len(set(required_hashes))}


def ray_bindings(directory, certificate, manifest, mappings):
    require(isinstance(certificate.get("model_artifacts"), dict)
            and set(certificate["model_artifacts"]) == {"matrix.npz", "bounds.npz"},
            "ray certificate must bind exactly matrix.npz and bounds.npz")
    bindings = [checked_hash(Path(directory) / name, value)
                for name, value in certificate["model_artifacts"].items()]
    for key, name in (("row_metadata_sha256", "row_metadata.csv.gz"),
                      ("raw_solver_ray_sha256", "raw_solver_ray.npz")):
        if key in certificate:
            bindings.append(checked_hash(Path(directory) / name, certificate[key]))
    expected = certificate.get("experiment_manifest_sha256")
    manifest_result = manifest_check(manifest, mappings, expected,
                                     certificate["model_artifacts"].values()) if manifest else None
    return {"verified_files": bindings, "manifest": manifest_result,
            "unverified_manifest_digest_without_supplied_manifest": expected if not manifest else None}


def archived_ray_comparison(certificate, result):
    claimed = certificate.get("verification", {})
    pairs = (("exact_gap", "separation_gap"), ("exact_robust_gap", "expanded_separation_gap"))
    comparison = {}
    for prefix, field in pairs:
        if prefix + "_numerator" in claimed or prefix + "_denominator" in claimed:
            try:
                value = Q(int(claimed[prefix + "_numerator"]), int(claimed[prefix + "_denominator"]))
            except (ValueError, KeyError, ZeroDivisionError, TypeError) as error:
                raise InvalidInput("invalid archived claimed fraction") from error
            actual = result[field]
            comparison[prefix] = value == Q(int(actual["numerator"]), int(actual["denominator"]))
    return comparison


def _toy(lower=0., upper=1., row_lower=2., row_upper=math.inf, coefficient=1.):
    return Model(1, 1, (coefficient,), (0,), (0, 1), (lower,), (upper,), (row_lower,), (row_upper,))


def _npy(dtype, shape, payload, fortran=False):
    header = repr({"descr": dtype, "fortran_order": fortran, "shape": shape}).encode("latin1")
    header += b" " * ((-10 - len(header) - 1) % 64) + b"\n"
    return b"\x93NUMPY\x01\x00" + struct.pack("<H", len(header)) + header + payload


def self_test():
    """Hand-derived boundary and malformed-input tests, with no solver oracle."""
    records = []
    def case(name, action, reject=False, unsupported=False):
        try:
            value = action()
        except UnsupportedFormat:
            if not (reject and unsupported):
                raise
            records.append({"name": name, "pass": True, "expected": "UNSUPPORTED_FORMAT"})
        except InvalidInput:
            if not (reject and not unsupported):
                raise
            records.append({"name": name, "pass": True, "expected": "INVALID_INPUT"})
        else:
            if reject or value is not True:
                raise AssertionError("self-test did not meet expectation: " + name)
            records.append({"name": name, "pass": True})
    def result_q(record, key):
        return Q(int(record[key]["numerator"]), int(record[key]["denominator"]))
    case("lower_only_separation_and_widening", lambda: result_q(check_ray(_toy(), {0: Q(1)}, Q(1, 4)), "expanded_separation_gap") == Q(1, 2))
    case("wrong_sign_cannot_select_infinite_upper", lambda: check_ray(_toy(), {0: Q(-1)}, Q(0)), reject=True)
    case("upper_only_negative_multiplier", lambda: check_ray(_toy(row_lower=-math.inf, row_upper=-1.), {0: Q(-1)}, Q(0))["expanded_pass"])
    case("valid_nonseparating_ray_is_not_infeasibility", lambda: check_ray(_toy(row_lower=0.), {0: Q(1)}, Q(0))["status"] == "VALID_NONSEPARATING_RAY")
    case("zero_ray_is_valid_but_nonseparating", lambda: check_ray(_toy(), {}, Q(0))["status"] == "VALID_NONSEPARATING_RAY")
    case("strict_gap_but_expanded_exact_boundary_zero", lambda: check_ray(_toy(), {0: Q(1)}, Q(1, 2))["status"] == "CERTIFIED_STRICT_INFEASIBLE_ONLY")
    case("one_binary64_below_ray_tau_boundary", lambda: check_ray(_toy(), {0: Q(1)}, q(math.nextafter(.5, 0.)))["expanded_pass"])
    cancel = Model(2, 1, (1., 1.), (0, 0), (0, 1, 2), (-100.,), (100.,), (2., -math.inf), (math.inf, 1.))
    case("column_cancellation_still_retains_row_widening", lambda: result_q(check_ray(cancel, {0: Q(1), 1: Q(-1)}, Q(1, 4)), "expanded_separation_gap") == Q(1, 2))
    point_model = _toy(lower=0., upper=0., row_lower=0., row_upper=0.)
    tau = q(1e-5)
    case("point_at_exact_binary64_tau_boundary", lambda: check_point(point_model, (1e-5,), (0,), tau)["status"] == "CERTIFIED_EXPANDED_ONLY_POINT")
    case("point_one_binary64_above_tau_boundary", lambda: check_point(point_model, (math.nextafter(1e-5, math.inf),), (0,), tau)["status"] == "POINT_NOT_FEASIBLE")
    case("fractional_binary_rejected_despite_linear_feasibility", lambda: check_point(_toy(row_lower=0.), (.5,), (1,), Q(0))["status"] == "POINT_NOT_FEASIBLE")
    case("strict_binary_point", lambda: check_point(_toy(row_lower=0.), (1.,), (1,), Q(0))["strict_pass"])
    case("invalid_binary_mask_value", lambda: check_point(_toy(), (0.,), (2,), Q(0)), reject=True)
    case("invalid_binary_mask_shape", lambda: check_point(_toy(), (0.,), (), Q(0)), reject=True)
    case("nonfinite_point", lambda: check_point(_toy(), (math.nan,), (1,), Q(0)), reject=True)
    case("infinite_column_box_unsupported_scope", lambda: check_ray(_toy(upper=math.inf), {0: Q(1)}, Q(0)), reject=True)
    case("nonfinite_matrix", lambda: validate_model(_toy(coefficient=math.nan)), reject=True)
    case("inverted_bounds", lambda: validate_model(_toy(lower=2., upper=1.)), reject=True)
    case("duplicate_multiplier_rows", lambda: parse_multipliers({"multipliers": [{"row": 0, "value_hex": "0x1p0"}, {"row": 0, "value_hex": "-0x1p0"}]}, 1), reject=True)
    case("overflowing_multiplier_hex", lambda: parse_multipliers({"multipliers": [{"row": 0, "value_hex": "0x1p+999999"}]}, 1), reject=True)
    case("duplicate_CSR_indices", lambda: validate_model(Model(1, 1, (1., -1.), (0, 0), (0, 2), (0.,), (1.,), (0.,), (1.,))), reject=True)
    case("out_of_range_CSR_column", lambda: validate_model(Model(1, 1, (1.,), (1,), (0, 1), (0.,), (1.,), (0.,), (1.,))), reject=True)
    case("corrupt_CSR_pointer_end", lambda: validate_model(Model(1, 1, (1.,), (0,), (0, 2), (0.,), (1.,), (0.,), (1.,))), reject=True)
    case("nonmonotone_CSR_pointers", lambda: validate_model(Model(3, 1, (1.,), (0,), (0, 1, 0, 1), (0.,), (1.,), (0.,)*3, (1.,)*3)), reject=True)
    case("object_NPY_forbidden", lambda: parse_npy(_npy("|O", (1,), b"x")), reject=True, unsupported=True)
    case("Fortran_NPY_forbidden", lambda: parse_npy(_npy("<f8", (1,), struct.pack("<d", 1.), True)), reject=True, unsupported=True)
    case("NPY_shape_payload_disagreement", lambda: parse_npy(_npy("<f8", (2,), struct.pack("<d", 1.))), reject=True)
    case("binary64_not_decimal_rational", lambda: q(parse_npy(_npy("<f8", (1,), struct.pack("<d", .1))).values[0]) != Q(1, 10))
    case("negative_tau", lambda: tau_value("-1"), reject=True)
    case("nonfinite_tau", lambda: tau_value("nan"), reject=True)
    with tempfile.TemporaryDirectory(prefix="standalone-verifier-tests-") as tmp:
        tmp = Path(tmp)
        badzip = tmp / "unsafe.npz"
        with zipfile.ZipFile(badzip, "w") as z:
            z.writestr("../vector.npy", _npy("<f8", (1,), struct.pack("<d", 0.)))
        case("unsafe_NPZ_member", lambda: read_npz(badzip, ("vector",)), reject=True)
        import warnings
        duplicate_zip = tmp / "duplicate.npz"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(duplicate_zip, "w") as z:
                for unused in range(2):
                    z.writestr("vector.npy", _npy("<f8", (1,), struct.pack("<d", 0.)))
        case("duplicate_NPZ_member", lambda: read_npz(duplicate_zip, ("vector",)), reject=True)
        altered = tmp / "bound.bin"
        altered.write_bytes(b"altered")
        case("supplied_hash_mismatch", lambda: checked_hash(altered, "0"*64), reject=True)
        unrelated = tmp / "unrelated_manifest.csv"
        with unrelated.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["path", "sha256", "bytes"])
            writer.writerow([str(altered), sha(altered), altered.stat().st_size])
        case("valid_unrelated_manifest_does_not_bind_input", lambda: manifest_check(
            unrelated, required_hashes=("0"*64,)), reject=True)
        duplicated = tmp / "duplicate.json"
        duplicated.write_text('{"x":1,"x":2}', encoding="utf-8")
        case("duplicate_JSON_key", lambda: json_read(duplicated), reject=True)
    return {"status": "SELF_TESTS_PASS", "tests": len(records), "results": records}


def cli(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("self-test").add_argument("--output", type=Path)
    for name in ("point", "ray"):
        p = sub.add_parser(name)
        p.add_argument("--model-dir", required=True, type=Path)
        p.add_argument("--tau", default="1e-5", help="decimal/hex binary64 value, then exact Fraction")
        p.add_argument("--manifest", type=Path, help="optional full CSV hash/size verification")
        p.add_argument("--path-map", action="append", default=[], metavar="OLD=NEW")
        p.add_argument("--output", type=Path)
        if name == "point":
            p.add_argument("--vector", required=True, type=Path)
            p.add_argument("--integrality", required=True, type=Path, help="original full binary mask, not U-only mask")
        else:
            p.add_argument("--certificate", required=True, type=Path)
    args = parser.parse_args(argv)
    started = time.perf_counter()
    try:
        if args.command == "self-test":
            report = self_test()
        else:
            mappings = []
            for text in args.path_map:
                require("=" in text, "path map requires OLD=NEW")
                old, new = text.split("=", 1)
                require(bool(old) and bool(new), "empty path map")
                mappings.append((old, new))
            model = load_model(args.model_dir)
            tau = tau_value(args.tau)
            files = [args.model_dir / "matrix.npz", args.model_dir / "bounds.npz"]
            if args.command == "point":
                values = vector(read_npz(args.vector, ("vector",))["vector"], ("<f8",), model.cols, "point")
                mask = vector(read_npz(args.integrality, ("integrality",))["integrality"], ("|u1",), model.cols, "binary mask")
                report = check_point(model, values, mask, tau)
                files += [args.vector, args.integrality]
                report["manifest"] = manifest_check(args.manifest, mappings,
                    required_hashes=[sha(path) for path in files]) if args.manifest else None
            else:
                cert = json_read(args.certificate)
                bindings = ray_bindings(args.model_dir, cert, args.manifest, mappings)
                report = check_ray(model, parse_multipliers(cert, model.rows), tau)
                report["bindings"] = bindings
                report["archived_gap_claim_comparison"] = archived_ray_comparison(cert, report)
                files.append(args.certificate)
            report["dimensions"] = {"rows": model.rows, "columns": model.cols, "nonzeros": len(model.data)}
            report["input_hashes"] = {str(path): sha(path) for path in files}
            report["scope"] = "Exact archived binary64 linear model; uniform outward expansion of every finite row/column bound. Binary coordinates remain exact. No native physical-data or field validation."
        code = 0 if report["status"].startswith(("CERTIFIED_", "SELF_TESTS_PASS")) else 1
    except UnsupportedFormat as error:
        report, code = {"status": "UNSUPPORTED_FORMAT", "reason": str(error)}, 2
    except (InvalidInput, OSError, ValueError, TypeError, KeyError, struct.error, zipfile.BadZipFile) as error:
        report, code = {"status": "INVALID_INPUT", "reason": str(error)}, 2
    report.update(elapsed_s=time.perf_counter() - started, verifier_sha256=sha(Path(__file__)),
                  python_version=sys.version, optimization_calls=0)
    text = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        # Refuse replacement: historical evidence must not be silently overwritten.
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(text)
    print(text, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(cli())
