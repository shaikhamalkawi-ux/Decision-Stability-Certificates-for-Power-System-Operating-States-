"""Exact finite assignment kernel for a prospective fixed-certificate stress test.

No model importer, solver, scientific input selection or experiment is run here.
The caller must establish the fixed-matrix and endpoint-ownership hypotheses.
See docs/research_next/CERTIFICATE_GUIDED_CHRONOLOGY_PROPOSAL.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import permutations, product


@dataclass(frozen=True)
class EndpointTerm:
    """One selected endpoint's weighted contribution to the separation margin.

    Row terms use coefficient d_i; box terms use coefficient -q_j. Values
    contain that same selected endpoint for every allowed source package.
    Indices are local positions in exactly one disjoint assignment group.
    """
    group: int
    destination: int
    coefficient: Q
    source_values: tuple[Q, ...]


def exact_assignment_margin(group_sizes, terms, constant):
    """Return exact group tables/extremizers; zero never means feasibility.

    ``constant`` includes fixed endpoints and the FULL row/column tau penalty.
    The input contract is checked before evaluating any finite assignment.
    Groups are bounded at size8 to prevent an accidental factorial explosion.
    No numeric coercion to binary float, tolerant comparison, or hash equality.
    """
    if not isinstance(constant, Q):
        raise ValueError("constant must be an exact Fraction")
    sizes = tuple(group_sizes)
    if not sizes or any(type(n) is not int or not 1 <= n <= 8 for n in sizes):
        raise ValueError("group sizes must be integers from1to8")
    tables = [[[Q(0) for _ in range(n)] for _ in range(n)] for n in sizes]
    for term in terms:
        if not isinstance(term, EndpointTerm):
            raise ValueError("invalid endpoint term")
        if type(term.group) is not int or not 0 <= term.group < len(sizes):
            raise ValueError("invalid group index")
        n = sizes[term.group]
        if type(term.destination) is not int or not 0 <= term.destination < n:
            raise ValueError("invalid destination index")
        if not isinstance(term.coefficient, Q):
            raise ValueError("endpoint coefficient must be exact")
        if not isinstance(term.source_values, tuple) or len(term.source_values) != n:
            raise ValueError("endpoint source values do not match group")
        if any(not isinstance(x, Q) for x in term.source_values):
            raise ValueError("endpoint values must be exact")
        for s, value in enumerate(term.source_values):
            tables[term.group][term.destination][s] += term.coefficient * value
    records = []
    for table in tables:
        values = tuple((p, sum((table[t][s] for t, s in enumerate(p)), Q(0)))
                       for p in permutations(range(len(table))))
        low = min(v for _, v in values)
        high = max(v for _, v in values)
        # permutations(range(n)) is lexicographic, so this is explicit tie policy.
        records.append(dict(table=tuple(tuple(row) for row in table),
                            assignments=values,
                            minimum=low, maximum=high,
                            argmin=next(p for p, v in values if v == low),
                            argmax=next(p for p, v in values if v == high),
                            minimum_ties=sum(v == low for _, v in values),
                            maximum_ties=sum(v == high for _, v in values)))
    return dict(constant=constant, groups=tuple(records),
                minimum=constant + sum((r['minimum'] for r in records), Q(0)),
                maximum=constant + sum((r['maximum'] for r in records), Q(0)),
                labeled_family_size=_family_size(records))


def _family_size(records):
    value = 1
    for record in records:
        value *= len(record['assignments'])
    return value


def synthetic_fixtures():
    """Hand-derived signed-endpoint cases plus exhaustive tiny-family oracle.

    These invented values exercise row/box signs, exact zero, nonzero residual
    widening, independent factors and deterministic ties. They are unrelated
    to the archived power-system arrays. This is not a solver benchmark.
    """
    # Two destination balances require x0=b0,x1=b1; column boxes x0<=3,x1<=1.
    # d=(1,2), A=I, so q=(1,2). tau=1/4 widens both rows AND both columns.
    # Constant = -(3+2*1) - (1/4)*(3+3) = -13/2.
    # Source row endpoints (1,3) give identity margin7-13/2=1/2 and swap5-13/2=-3/2.
    terms = (EndpointTerm(0, 0, Q(1), (Q(1), Q(3))),
             EndpointTerm(0, 1, Q(2), (Q(1), Q(3))))
    result = exact_assignment_margin((2,), terms, Q(-13, 2))
    assert result['maximum'] == Q(1, 2) and result['minimum'] == Q(-3, 2)
    assert result['groups'][0]['argmax'] == (0, 1)
    # Direct expanded endpoint formula (independent of grouping kernel).
    for p, _ in result['groups'][0]['assignments']:
        endpoints = (Q(1), Q(3))
        direct = sum(Q(d) * (endpoints[p[t]] - Q(1, 4))
                     for t, d in enumerate((1, 2)))
        direct -= Q(1) * (Q(3) + Q(1, 4)) + Q(2) * (Q(1) + Q(1, 4))
        table_value = result['constant'] + sum(result['groups'][0]['table'][t][s]
                                              for t, s in enumerate(p))
        assert direct == table_value
    # Upper-row endpoints carry negative d; lower-column endpoints carry -q>0.
    signed = (EndpointTerm(0, 0, Q(-2), (Q(-3), Q(1))),
              EndpointTerm(0, 1, Q(3), (Q(2), Q(5))))
    sign_result = exact_assignment_margin((2,), signed, Q(0))
    assert sign_result['maximum'] == Q(21) and sign_result['minimum'] == Q(4)
    # Two disjoint groups: brute force4complete choices independently checks extrema.
    combined = terms + tuple(EndpointTerm(1, t.destination, t.coefficient, t.source_values)
                             for t in signed)
    two = exact_assignment_margin((2, 2), combined, Q(-13, 2))
    brute = []
    for p0, p1 in product(permutations(range(2)), repeat=2):
        choices = (p0, p1)
        brute.append(Q(-13, 2) + sum(t.coefficient * t.source_values[choices[t.group][t.destination]]
                                     for t in combined))
    assert two['maximum'] == max(brute) and two['minimum'] == min(brute)
    assert two['labeled_family_size'] == 4
    # A proof at exact zero cannot reject. Equal values produce6ties, not6distinct inputs.
    tied = exact_assignment_margin((3,), (), Q(0))
    assert tied['maximum'] == 0 and tied['minimum'] == 0
    assert tied['groups'][0]['maximum_ties'] == 6
    assert tied['groups'][0]['argmax'] == (0, 1, 2)
    # Reject silent float conversion or indexing/schema loss before evaluating.
    invalid = (lambda: exact_assignment_margin((2,), (), 0.0),
               lambda: exact_assignment_margin((9,), (), Q(0)),
               lambda: exact_assignment_margin((2,), (EndpointTerm(1, 0, Q(1), (Q(1), Q(2))),), Q(0)),
               lambda: exact_assignment_margin((2,), (EndpointTerm(0, 0, Q(1), (Q(1),)),), Q(0)),
               lambda: exact_assignment_margin((2,), (EndpointTerm(0, 0, Q(1), (Q(1), 2.)),), Q(0)))
    for reject in invalid:
        try:
            reject()
        except ValueError:
            pass
        else:
            raise AssertionError("invalid exact-assignment input accepted")
    return dict(status='SYNTHETIC_KERNEL_FIXTURES_PASS',
                scientific_inputs_read=0, model_solve_calls=0,
                claims='Conditional assignment kernel only; no UC/novelty/empirical result')


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--synthetic-fixtures', action='store_true', required=True)
    parser.parse_args()
    print(json.dumps(synthetic_fixtures(), sort_keys=True))
