"""Independent checker for a single unit's sparse temporal explanation.

This module uses attained run ages and explicit sets of online-hour counts.
It intentionally does not import the residence-certificate implementation.
An empty returned set proves that the supplied forced states, dwell times and
online-count interval cannot all hold. A nonempty set only passes this single
unit necessary-condition check; it does not establish dispatch feasibility.
"""

from __future__ import annotations

import argparse
import itertools
import json
import operator
from pathlib import Path
import random


def _integer(value, name):
    """Accept integer objects (including NumPy integer scalars), not fractions."""
    try:
        return operator.index(value)
    except TypeError as exc:
        raise TypeError(f"{name} must be an integer") from exc


def _hours(values, horizon, name):
    hours = {_integer(value, name) for value in values}
    if any(hour < 0 or hour >= horizon for hour in hours):
        raise ValueError(f"{name} contains an index outside the horizon")
    return hours


def compatible_counts(
    horizon, forced_on, forced_off, minimum_up, minimum_down,
    count_lower, count_upper,
):
    """Return feasible integer online counts in the inclusive supplied interval.

    ``forced_on`` and ``forced_off`` contain zero-based hour indices. Dwell
    times count hourly slots. The initial status is freely selectable and its
    pre-horizon minimum dwell is already satisfied. Every observed change at
    hour t >= 1 starts a new minimum dwell; the last run need not extend beyond
    the observed horizon. Minimum times zero and one both allow a change on
    the next hourly slot. An empty horizon has the single online count zero.
    """
    horizon = _integer(horizon, "horizon")
    minimum_up = _integer(minimum_up, "minimum_up")
    minimum_down = _integer(minimum_down, "minimum_down")
    count_lower = _integer(count_lower, "count_lower")
    count_upper = _integer(count_upper, "count_upper")
    if horizon < 0 or minimum_up < 0 or minimum_down < 0:
        raise ValueError("horizon and minimum dwell times must be nonnegative")
    on = _hours(forced_on, horizon, "forced_on")
    off = _hours(forced_off, horizon, "forced_off")
    lower, upper = max(0, count_lower), min(horizon, count_upper)
    if on & off or lower > upper:
        return []
    if horizon == 0:
        return [0]

    # Ages are saturated once the required dwell is attained. Unlike a
    # residual-dwell implementation, a change is permitted by checking the
    # age of the run being left. The first run starts with a satisfied age.
    required = (minimum_down, minimum_up)
    cap = (max(1, minimum_down), max(1, minimum_up))
    states = {}
    for status in (0, 1):
        if (0 in on and status == 0) or (0 in off and status == 1):
            continue
        if status <= upper and status + horizon - 1 >= lower:
            states[(status, cap[status])] = {status}

    for hour in range(1, horizon):
        following = {}
        remaining = horizon - hour - 1
        for (status, age), counts in states.items():
            choices = [(status, min(cap[status], age + 1))]
            if age >= required[status]:
                choices.append((1 - status, 1))
            for new_status, new_age in choices:
                if (hour in on and new_status == 0) or (hour in off and new_status == 1):
                    continue
                attainable = {
                    count + new_status for count in counts
                    if lower - remaining <= count + new_status <= upper
                }
                if attainable:
                    following.setdefault((new_status, new_age), set()).update(attainable)
        states = following
        if not states:
            return []

    return sorted(set().union(*states.values()))


def _exhaustive_counts(horizon, on, off, minimum_up, minimum_down, lower, upper):
    """Enumeration oracle: inspect every changed slot's forward dwell window."""
    accepted = set()
    for sequence in itertools.product((0, 1), repeat=horizon):
        if any(sequence[hour] != 1 for hour in on):
            continue
        if any(sequence[hour] != 0 for hour in off):
            continue
        count = sum(sequence)
        if not lower <= count <= upper:
            continue
        valid = True
        for hour in range(1, horizon):
            if sequence[hour] == sequence[hour - 1]:
                continue
            duration = minimum_up if sequence[hour] else minimum_down
            if any(sequence[later] != sequence[hour]
                   for later in range(hour, min(horizon, hour + duration))):
                valid = False
                break
        if valid:
            accepted.add(count)
    return sorted(accepted)


def validate():
    """Check exact count sets against exhaustive enumeration, deterministically."""
    seed = 260926
    rng = random.Random(seed)
    configurations = 0
    interval_checks = 0
    candidate_sequences = 0
    for horizon in range(1, 10):
        for minimum_up in range(5):
            for minimum_down in range(5):
                for _ in range(5):
                    forced = [rng.choice((-1, 0, 1)) for _ in range(horizon)]
                    on = [hour for hour, state in enumerate(forced) if state == 1]
                    off = [hour for hour, state in enumerate(forced) if state == 0]
                    intervals = [(0, horizon), (rng.randint(0, horizon), rng.randint(0, horizon))]
                    for lower, upper in intervals:
                        actual = compatible_counts(horizon, on, off, minimum_up, minimum_down, lower, upper)
                        expected = _exhaustive_counts(horizon, on, off, minimum_up, minimum_down, lower, upper)
                        if actual != expected:
                            raise AssertionError({"horizon": horizon, "on": on, "off": off,
                                                  "minimum_up": minimum_up, "minimum_down": minimum_down,
                                                  "interval": [lower, upper], "actual": actual, "expected": expected})
                        interval_checks += 1
                        candidate_sequences += 2 ** horizon
                    configurations += 1

    # Explicit boundary cases include dwell longer than the horizon, initially
    # satisfied dwell, a final-slot switch, contradictory states and h = 0.
    boundary_cases = [
        (0, [], [], 0, 0, 0, 0),
        (0, [], [], 4, 5, 1, 1),
        (1, [], [], 20, 20, 0, 1),
        (3, [1], [0], 20, 20, 0, 3),
        (3, [2], [0, 1], 20, 20, 0, 3),
        (3, [0, 2], [1], 20, 20, 0, 3),
        (3, [0, 2], [1], 0, 0, 0, 3),
        (3, [0, 2], [1], 1, 1, 0, 3),
        (5, [0, 1], [1], 2, 3, 0, 5),
        (5, [0, 0], [4, 4], 2, 3, -2, 7),
        (5, [], [], 2, 3, 4, 2),
    ]
    for arguments in boundary_cases:
        actual = compatible_counts(*arguments)
        expected = _exhaustive_counts(*arguments)
        if actual != expected:
            raise AssertionError({"boundary_arguments": arguments, "actual": actual, "expected": expected})
        candidate_sequences += 2 ** arguments[0]

    return {
        "result": "PASS",
        "checker": "independent saturated run-age states with explicit online-count sets",
        "oracle": "exhaustive enumeration of every binary sequence and direct forward dwell windows",
        "seed": seed,
        "horizons": list(range(1, 10)),
        "minimum_times": list(range(5)),
        "randomized_forced_state_configurations": configurations,
        "randomized_configuration_interval_checks": interval_checks,
        "explicit_boundary_checks": len(boundary_cases),
        "total_checks": interval_checks + len(boundary_cases),
        "binary_sequences_enumerated": candidate_sequences,
        "initial_history": "freely selectable initial status with minimum dwell already satisfied",
        "final_history": "no required dwell beyond the observed horizon",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional JSON path for the exhaustive self-test result")
    args = parser.parse_args()
    result = validate()
    report = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    print(report, end="")


if __name__ == "__main__":
    main()
