"""Pure-Python independent checks for the finite-window theorem candidate.

No numerical optimizer or third-party package is used. The model has one unit
with p=u in {0,1}, minimum up two, minimum down one, and mature OFF history;
one curtailable renewable; and Z/F/O hourly input packages.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
ALPHABET = "ZFO"
ALLOWED = {"Z": (0,), "F": (1,), "O": (0, 1)}
LOAD = {"Z": 0, "F": 1, "O": 1}
RENEWABLE_UPPER = {"Z": 0, "F": 0, "O": 1}


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def block(m):
    assert m >= 0
    return "O" + "FO" * m


def construction(k, r=None):
    r = k if r is None else r
    if k < 1 or r < 1:
        raise ValueError("k and r must be positive integers")
    z = "Z" * k
    return z + block(2 * r) + z + block(2 * r) + z, z + block(2 * r - 1) + z + block(2 * r + 1) + z


def grams(word, width):
    return Counter(word[index:index + width] for index in range(len(word) - width + 1))


def minimum_dp(word, minimum_up=2, minimum_down=1):
    """Run-age DP, initial mature OFF, terminal dwell clipped to the horizon."""
    required = (minimum_down, minimum_up)
    caps = tuple(max(1, value) for value in required)
    states = {(0, caps[0]): (0, ())}
    for symbol in word:
        following = {}
        for (old, age), (energy, path) in states.items():
            for new in ALLOWED[symbol]:
                if new != old and age < required[old]:
                    continue
                new_age = 1 if new != old else min(caps[new], age + 1)
                key, candidate = (new, new_age), (energy + new, path + (new,))
                if key not in following or candidate < following[key]:
                    following[key] = candidate
        states = following
    return min(states.values()) if states else (None, None)


def schedule_valid(word, status, minimum_up=2, minimum_down=1):
    """Direct forward dwell checks, independent of the DP's attained ages."""
    if len(word) != len(status):
        return False
    previous = 0
    for hour, (symbol, state) in enumerate(zip(word, status)):
        if state not in ALLOWED[symbol]:
            return False
        if state != previous:
            duration = minimum_up if state else minimum_down
            if any(status[later] != state for later in range(hour, min(len(word), hour + duration))):
                return False
        previous = state
    return True


def exhaustive_minimum(word, minimum_up=2, minimum_down=1):
    """Enumerate every instantaneously admissible binary thermal schedule."""
    best, tested = None, 0
    for status in itertools.product(*(ALLOWED[symbol] for symbol in word)):
        tested += 1
        if schedule_valid(word, status, minimum_up, minimum_down):
            energy = sum(status)
            if best is None or energy < best:
                best = energy
    return best, tested


def block_witness(m):
    # Pair consecutive forced Fs using their shared O; an odd last F uses the
    # final O. Resulting ON runs have lengths three or two, never one.
    status = [int(symbol == "F") for symbol in block(m)]
    for first_forced in range(1, m, 2):
        status[2 * first_forced] = 1
    if m % 2:
        status[-1] = 1
    return status


def matching_lower_bound(word):
    """Disjoint O-pair covers certify the energy lower bound for these blocks."""
    pairs, forced, selected_forced = [], [], []
    offset = 0
    for component in word.split("Z"):
        if component:
            assert component == block(component.count("F"))
            fs = [offset + j for j, symbol in enumerate(component) if symbol == "F"]
            forced.extend(fs)
            for hour in fs[::2]:
                assert word[hour - 1] == word[hour + 1] == "O"
                pairs.append((hour - 1, hour + 1))
                selected_forced.append(hour)
        offset += len(component) + 1
    occupied = [hour for pair in pairs for hour in pair]
    assert len(occupied) == len(set(occupied))
    assert set(forced) == {t for t, symbol in enumerate(word) if symbol == "F"}
    return {"forced_F_hours": forced, "selected_F_hours": selected_forced,
            "disjoint_neighbor_O_pairs": [list(pair) for pair in pairs],
            "forced_energy": len(forced), "optional_energy_lower_bound": len(pairs),
            "energy_lower_bound": len(forced) + len(pairs)}


def exact_cover_algebra(word, certificate, cap):
    """Check local startup inequalities and the global rational contradiction."""
    local_checks = []
    for hour in certificate["selected_F_hours"]:
        # Equality + min-up-next + nonnegative shutdown/startup bounds:
        # (u_t-u_prev-y_t+z_t) + (y_t+y_next-u_next) -z_t-y_next.
        rows = [{f"u{hour}": 1, f"u{hour-1}": -1, f"y{hour}": -1, f"z{hour}": 1},
                {f"y{hour}": 1, f"y{hour+1}": 1, f"u{hour+1}": -1},
                {f"z{hour}": -1}, {f"y{hour+1}": -1}]
        summed = Counter()
        for row in rows:
            summed.update(row)
        summed = {key: value for key, value in summed.items() if value}
        assert summed == {f"u{hour}": 1, f"u{hour-1}": -1, f"u{hour+1}": -1}
        assert word[hour] == "F" and word[hour-1] == word[hour+1] == "O"
        local_checks.append({"forced_hour": hour, "derived_coefficients": summed,
                             "derived_rhs_after_uF_equals_one": -1})

    # Add the cap, negative fixed-F equalities, local negative-cover rows and
    # nonnegativity bounds for every thermal variable not already canceled.
    coefficients = {hour: Fraction(1) for hour in range(len(word))}
    rhs = Fraction(cap)
    for hour in certificate["forced_F_hours"]:
        coefficients[hour] -= 1
        rhs -= 1
    covered = set()
    for left, right in certificate["disjoint_neighbor_O_pairs"]:
        coefficients[left] -= 1
        coefficients[right] -= 1
        covered.update((left, right))
        rhs -= 1
    leftovers = [hour for hour, coefficient in coefficients.items() if coefficient]
    for hour in leftovers:
        assert coefficients[hour] == 1
        coefficients[hour] -= 1
    assert all(coefficient == 0 for coefficient in coefficients.values())
    expected = cap - certificate["energy_lower_bound"]
    assert rhs == expected
    return {"local_cover_derivations": local_checks,
            "remaining_nonnegativity_hours": leftovers,
            "summed_variable_coefficients_identically_zero": True,
            "summed_rhs_numerator": rhs.numerator, "summed_rhs_denominator": rhs.denominator,
            "strict_contradiction": rhs < 0,
            "scope": "Exact integer/rational algebra; lower bound also holds in the usual continuous startup/min-up-two relaxation."}


def construction_check(k, r, exhaustive=False):
    x, y = construction(k, r)
    assert len(x) == len(y) == 8 * r + 2 + 3 * k
    assert x[:k] == y[:k] == x[-k:] == y[-k:] == "Z" * k
    equal_orders = [width for width in range(1, k + 1) if grams(x, width) == grams(y, width)]
    assert len(equal_orders) == k, (k, r, equal_orders)
    ex, wx = minimum_dp(x)
    ey, wy = minimum_dp(y)
    assert ex == 6 * r and ey == 6 * r + 1
    assert schedule_valid(x, wx) and schedule_valid(y, wy)
    cap = Fraction(12 * r + 1, 2)
    assert ex <= cap < ey
    certx, certy = matching_lower_bound(x), matching_lower_bound(y)
    assert certx["energy_lower_bound"] == ex and certy["energy_lower_bound"] == ey
    algebra = exact_cover_algebra(y, certy, cap)
    assert algebra["strict_contradiction"]
    tested = 0
    if exhaustive:
        oracle_x, count_x = exhaustive_minimum(x)
        oracle_y, count_y = exhaustive_minimum(y)
        assert (oracle_x, oracle_y) == (ex, ey)
        tested = count_x + count_y
    one_x, _ = minimum_dp(x, minimum_up=1)
    one_y, _ = minimum_dp(y, minimum_up=1)
    assert one_x == one_y == 4 * r
    return {"k": k, "r": r, "horizon": len(x), "all_orders_1_through_k_equal": True,
            "minimum_thermal_x": ex, "minimum_thermal_y": ey,
            "shared_cap_numerator": cap.numerator, "shared_cap_denominator": cap.denominator,
            "complete_candidate_schedules_enumerated": tested,
            "minimum_up_one_control": [one_x, one_y],
            "exact_continuous_relaxation_lower_bound_verified": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results/research8h/kgram_check")
    args = parser.parse_args()
    if (args.output / "pre_run_freeze.json").exists():
        raise FileExistsError("Preserve previous results; use another output path")
    args.output.mkdir(parents=True, exist_ok=True)
    save(args.output / "pre_run_freeze.json", {"script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "generic_words_max_length": 8, "block_formula_m_max": 40, "block_exhaustive_m_max": 12,
        "safe_family_k_max": 64, "tighter_grid_k_max": 24, "tighter_grid_r_max": 8,
        "first_distinguishing_order_r_max": 16,
        "status": "theorem candidate; independent computational and algebraic checks only, no novelty claim"})
    started = time.perf_counter()
    generic_cases = generic_schedules = 0
    for length in range(9):
        for letters in itertools.product(ALPHABET, repeat=length):
            word = "".join(letters)
            expected, checked = exhaustive_minimum(word)
            actual, witness = minimum_dp(word)
            assert expected == actual, (word, expected, actual)
            assert witness is None or schedule_valid(word, witness)
            generic_cases += 1
            generic_schedules += checked
    block_cases, block_schedules = [], 0
    for m in range(41):
        word = "Z" + block(m) + "Z"
        energy, _ = minimum_dp(word)
        predicted = m + (m + 1) // 2
        constructed = [0, *block_witness(m), 0]
        assert schedule_valid(word, constructed) and sum(constructed) == predicted == energy
        if m <= 12:
            expected, checked = exhaustive_minimum(word)
            assert energy == expected
            block_schedules += checked
        block_cases.append({"m": m, "predicted": predicted, "DP_minimum": energy})
    save(args.output / "block_formula_checks.json", block_cases)
    examples = [construction_check(1, 1, True), construction_check(2, 1, True),
                construction_check(3, 1, True), construction_check(4, 1, True),
                construction_check(2, 2, True), construction_check(3, 3, True)]
    safe = [construction_check(k, k) for k in range(1, 65)]
    tighter = [construction_check(k, r) for r in range(1, 9) for k in range(1, min(24, 4 * r) + 1)]
    sharpness = []
    for r in range(1, 17):
        k = 4 * r + 1
        x, y = construction(k, r)
        differences = [width for width in range(1, k + 1) if grams(x, width) != grams(y, width)]
        assert differences == [4 * r + 1], (k, r, differences)
        sharpness.append({"r": r, "first_distinguishing_order": differences[0]})
    save(args.output / "safe_family_checks.json", safe)
    save(args.output / "tighter_parameter_checks.json", tighter)
    save(args.output / "sharpness_checks.json", sharpness)
    save(args.output / "exhaustive_examples.json", examples)
    x, y = construction(3, 1)
    ex, wx = minimum_dp(x)
    ey, wy = minimum_dp(y)
    cy = matching_lower_bound(y)
    save(args.output / "example_k3_r1.json", {"x": x, "y": y, "k": 3, "r": 1,
        "payload_mapping": {a: {"load": LOAD[a], "renewable_upper": RENEWABLE_UPPER[a]} for a in ALPHABET},
        "thermal_min_up": 2, "thermal_min_down": 1, "thermal_pmin": 1, "thermal_pmax": 1,
        "minimum_thermal_x": ex, "minimum_thermal_y": ey,
        "x_status_witness": wx, "y_minimum_status": wy,
        "x_renewable_dispatch": [LOAD[a] - u for a, u in zip(x, wx)],
        "shared_cap": "13/2", "shared_trigram_counts": dict(sorted(grams(x, 3).items())),
        "negative_lower_bound": cy, "negative_exact_algebra": exact_cover_algebra(y, cy, Fraction(13, 2))})
    summary = {"result": "PASS", "status": "THEOREM_CANDIDATE_CHECKED_NOT_NOVELTY_ASSESSED",
        "generic_DP_vs_exhaustive_words": generic_cases,
        "generic_complete_candidate_schedules": generic_schedules,
        "block_formula_cases": len(block_cases), "block_exhaustive_schedules": block_schedules,
        "exhaustive_construction_examples": len(examples),
        "construction_schedules_enumerated": sum(e["complete_candidate_schedules_enumerated"] for e in examples),
        "safe_family_cases": len(safe), "tighter_parameter_cases": len(tighter), "sharpness_cases": len(sharpness),
        "elapsed_s": time.perf_counter() - started,
        "interpretation": "Fixed finite unordered exogenous k-gram histograms are insufficient over unbounded horizons. This does not rule out finite-state sequential sufficient summaries."}
    save(args.output / "summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
