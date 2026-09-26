"""Compare the four fixed standalone reports with existing exact archive checks.

This script reads completed reports; it does not rerun checks or optimization.
"""
import ast
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "src/research8h_standalone_verify.py"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rational(value):
    return Fraction(int(value["numerator"]), int(value["denominator"]))


source_sha = digest(SOURCE)
imports = sorted({node.module.split(".")[0] if isinstance(node, ast.ImportFrom)
                  else name.name.split(".")[0]
                  for node in ast.walk(ast.parse(SOURCE.read_text(encoding="utf-8")))
                  if isinstance(node, (ast.Import, ast.ImportFrom))
                  for name in (node.names if isinstance(node, ast.Import) else [None])})
assert set(imports) <= sys.stdlib_module_names
self_tests = read(HERE / "final/self_tests.json")
assert self_tests["status"] == "SELF_TESTS_PASS" and self_tests["tests"] == 35
assert all(case["pass"] for case in self_tests["results"])
assert self_tests["verifier_sha256"] == source_sha and self_tests["optimization_calls"] == 0
comparisons = []
for seed in (26093100, 26093101):
    result_file = HERE / f"final/january_seed_{seed}_ray.json"
    result = read(result_file)
    certificate_file = ROOT / f"results/research8h/seasonal_transfer/seed_{seed}/lp/dual_certificate.json"
    certificate = read(certificate_file)
    old = certificate["verification"]
    assert result["status"] == "CERTIFIED_EXPANDED_INFEASIBLE"
    assert result["verifier_sha256"] == source_sha and result["optimization_calls"] == 0
    nominal = Fraction(int(old["exact_gap_numerator"]), int(old["exact_gap_denominator"]))
    expanded = Fraction(int(old["exact_robust_gap_numerator"]), int(old["exact_robust_gap_denominator"]))
    assert rational(result["separation_gap"]) == nominal > 0
    assert rational(result["expanded_separation_gap"]) == expanded > 0
    assert rational(result["norm_formula_gap"]) == expanded
    assert result["row_multiplier_nonzeros"] == old["row_multiplier_nonzeros"]
    assert result["combined_column_nonzeros"] == old["combined_column_nonzeros"]
    assert all(result["archived_gap_claim_comparison"].values())
    comparisons.append({"fixture": f"january_seed_{seed}", "kind": "ray", "pass": True,
                        "nominal_and_expanded_fractions_exactly_match": True,
                        "result_sha256": digest(result_file), "old_certificate_sha256": digest(certificate_file)})

day_root = ROOT / "results/research8h/day_blocks"
point_expectations = [
    ("january_identity", day_root / "exact_positive_controls.json", "january_identity"),
    ("day_312", day_root / "days_312/constructive_check.json", "full_exact"),
]
for name, old_file, key in point_expectations:
    result_file = HERE / f"final/{name}_point.json"
    result, old = read(result_file), read(old_file)[key]
    assert result["status"] == "CERTIFIED_EXPANDED_ONLY_POINT"
    assert result["verifier_sha256"] == source_sha and result["optimization_calls"] == 0
    for field in ("strict_pass", "expanded_pass", "original_binary_coordinates_exact", "worst_column", "worst_row"):
        assert result[field] == old[field]
    for field in ("tau", "maximum_column_violation", "maximum_row_violation"):
        assert rational(result[field]) == rational(old[field])
    assert result["binary_coordinates"] == 12096
    comparisons.append({"fixture": name, "kind": "point", "pass": True,
                        "exact_maximum_residuals_and_locations_match": True,
                        "result_sha256": digest(result_file), "old_check_sha256": digest(old_file)})

report = {"status": "SELECTED_FIXTURES_MATCH", "fixtures": comparisons,
          "self_tests": 35, "all_imports_standard_library": True, "imported_modules": imports,
          "verifier_sha256": source_sha, "optimization_calls": 0,
          "scope": "Four preselected fixtures; no new native model reconstruction, corpus expansion, or optimization."}
with (HERE / "selected_fixture_comparison.json").open("x", encoding="utf-8") as stream:
    json.dump(report, stream, indent=2)
    stream.write("\n")
print(json.dumps(report, indent=2))
