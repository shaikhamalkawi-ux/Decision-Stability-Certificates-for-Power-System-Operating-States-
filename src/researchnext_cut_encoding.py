"""Exact outward binary-cut transport. Pure APIs; optional invented controls only."""
from __future__ import annotations

import argparse
from collections.abc import Mapping
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

SCHEMA = 'exact_binary_cut_transport_v1'
MAX_RATIONAL_BITS = 8192
MAX_COORDINATES = 12096
MAX_COORDINATE_ID = 2**31 - 1


class CutEncodingError(ValueError):
    """Unsupported input or encoding; no alternate scale/repair is attempted."""
    def __init__(self, code, message):
        super().__init__(code + ': ' + message)
        self.code = code


def _need(ok, code, message):
    if not ok:
        raise CutEncodingError(code, message)


def _guard(q):
    _need(q.numerator.bit_length() <= MAX_RATIONAL_BITS and q.denominator.bit_length() <= MAX_RATIONAL_BITS,
          'RATIONAL_LIMIT', 'Exact stored/accumulated rational exceeds fixed bit limit')
    return q


def _exact(x):
    _need(type(x) in (int, F), 'EXACT_INPUT_REQUIRED', 'Use Fraction or int, not floats or booleans')
    return _guard(F(x))


def _pair(q):
    return [str(q.numerator), str(q.denominator)]


def _parse(pair):
    _need(isinstance(pair, list) and len(pair) == 2 and all(type(x) is str for x in pair), 'RECORD_SCHEMA', 'Expected a canonical rational pair')
    try:
        q = _guard(F(int(pair[0]), int(pair[1])))
    except (ValueError, ZeroDivisionError) as exc:
        raise CutEncodingError('RECORD_SCHEMA', 'Invalid rational pair') from exc
    _need(pair == _pair(q), 'RECORD_SCHEMA', 'Noncanonical rational pair')
    return q


def _sum(values):
    total = F(0)
    for value in values:
        total = _guard(total + _guard(value))
    return total


def _dot(a, z):
    return _sum(_guard(x*y) for x, y in zip(a, z))


def _power_two(exponent):
    return _guard(F(1 << exponent) if exponent >= 0 else F(1, 1 << -exponent))


def dyadic_scale(coefficients):
    """Return (integer exponent, exact scale); zero support uses exponent0/scale1."""
    coefficients = tuple(_exact(x) for x in coefficients)
    _need(len(coefficients) <= MAX_COORDINATES, 'COORDINATE_LIMIT', 'Unsupported coordinate denominator')
    maximum = max(map(abs, coefficients), default=F(0))
    if not maximum:
        return 0, F(1)
    numerator, denominator = maximum.numerator, maximum.denominator
    exponent = numerator.bit_length() - denominator.bit_length()
    at_most = numerator <= (denominator << exponent) if exponent >= 0 else (numerator << -exponent) <= denominator
    if not at_most:
        exponent += 1
    scale = _power_two(exponent)
    _need(scale / 2 < maximum <= scale, 'INTERNAL_SCALE', 'Scale is not the smallest enclosing power of two')
    return exponent, scale


def _nearest_finite(q):
    try:
        value = float(q)
    except (OverflowError, ValueError) as exc:
        raise CutEncodingError('BINARY64_OVERFLOW', 'No finite nearest binary64 encoding') from exc
    _need(math.isfinite(value), 'BINARY64_OVERFLOW', 'Nonfinite binary64 encoding')
    _need(q == 0 or value != 0., 'BINARY64_UNDERFLOW', 'Nonzero exact value rounds to zero')
    return value


def _downward(q):
    nearest = _nearest_finite(q)
    step = F(nearest) > q
    value = math.nextafter(nearest, -math.inf) if step else nearest
    _need(math.isfinite(value), 'BINARY64_OVERFLOW', 'Downward endpoint is not finite')
    _need(q == 0 or value != 0., 'BINARY64_UNDERFLOW', 'Downward endpoint loses a nonzero value to zero')
    _need(F(value) <= q, 'INTERNAL_ENDPOINT', 'Downward encoding failed exact comparison')
    return value, nearest, step


def _origin(origin, n, require_exclusion):
    _need(type(require_exclusion) is bool, 'EXCLUSION_MODE', 'require_exclusion must be explicit bool')
    if origin is None:
        _need(not require_exclusion, 'ORIGIN_REQUIRED', 'Refinement requires one exact binary origin')
        return None
    z = tuple(origin)
    _need(len(z) == n and all(type(x) is int and x in (0, 1) for x in z), 'BINARY_ORIGIN_REQUIRED', 'Origin must contain exactly the declared binary coordinates')
    return z


def encode_binary_cut(coefficients, rhs, *, coordinates=None, full_dimension=None, origin=None, require_exclusion=True):
    """Encode a*z>=b outward on [0,1]^n; does not access a backend or any file.

    Pass require_exclusion=False for seed validity only. A refinement requires
    original and requested encoded strict exclusion. A constant row is recorded
    but never approved for insertion or treated here as a global proof.
    """
    _need((sys.float_info.radix,sys.float_info.mant_dig,sys.float_info.max_exp,sys.float_info.min_exp)==(2,53,1024,-1021),
          'UNSUPPORTED_FLOAT', 'Runtime must use IEEE binary64 Python floats')
    a = tuple(_exact(x) for x in coefficients)
    dimension = len(a) if full_dimension is None else full_dimension
    _need(type(dimension) is int and 0 < dimension <= MAX_COORDINATES and len(a) <= dimension,
          'COORDINATE_LIMIT', 'Unsupported full dimension or explicit coordinate denominator')
    b = _exact(rhs)
    ids = tuple(range(len(a))) if coordinates is None else tuple(coordinates)
    _need(len(ids) == len(a) and all(type(j) is int and 0 <= j < dimension and j <= MAX_COORDINATE_ID for j in ids)
          and ids == tuple(sorted(set(ids))), 'COORDINATE_MAP', 'Coordinates must be unique increasing nonnegative integer IDs')
    z = _origin(origin, dimension, require_exclusion)
    support_z = tuple(z[j] for j in ids) if z is not None else None
    exponent, scale = dyadic_scale(a)
    alpha = tuple(_guard(x / scale) for x in a)
    beta = _guard(b / scale)
    encoded = tuple(_nearest_finite(x) for x in alpha)
    errors = tuple(_guard(F(y)-x) for x, y in zip(alpha, encoded))
    correction = _sum(min(x, F(0)) for x in errors)
    bound = _guard(beta + correction)
    lower, nearest, stepped = _downward(bound)
    original_gap = _guard(b-_dot(a,support_z)) if z is not None else None
    scaled_gap = _guard(beta-_dot(alpha,support_z)) if z is not None else None
    requested_gap = _guard(F(lower)-_dot(tuple(F(x) for x in encoded),support_z)) if z is not None else None
    constant = not any(a)
    if constant:
        disposition = 'CONSTANT_CONTRADICTION_REQUIRES_SEPARATE_PROOF' if b > 0 else 'CONSTANT_NONRESTRICTING_ROW'
    elif require_exclusion and original_gap <= 0:
        disposition = 'NONEXCLUDING_ORIGINAL_ROW'
    elif require_exclusion and requested_gap <= 0:
        disposition = 'NONPROGRESSING_ENCODING'
    else:
        disposition = 'READY_FOR_BACKEND_READBACK'
    return {
        'schema': SCHEMA, 'coordinate_count': len(a), 'full_dimension': dimension, 'require_exclusion': require_exclusion,
        'implicit_exact_zeros': dict(count=dimension-len(ids), coordinates='range(full_dimension) minus explicit coordinates',
                                     source_completeness='caller must prove every omitted original coefficient exactly zero; helper does not reconstruct original model'),
        'origin_scope': 'complete full_dimension binary state vector',
        'origin': list(z) if z is not None else None, 'source_rhs': _pair(b),
        'scale_exponent_2': exponent, 'scale': _pair(scale), 'scaled_rhs': _pair(beta),
        'coefficients': [dict(coordinate=j, source=_pair(x), scaled=_pair(y), encoded_hex=f.hex(), error=_pair(e))
                         for j,x,y,f,e in zip(ids,a,alpha,encoded,errors)],
        'residual_box_lower': _pair(correction), 'requested_endpoint_target': _pair(bound),
        'lower': dict(nearest_hex=nearest.hex(), nextafter_negative_infinity=stepped, encoded_hex=lower.hex(),
                      error=_pair(F(lower)-bound)), 'upper': 'positive_infinity',
        'original_origin_gap': _pair(original_gap) if z is not None else None,
        'scaled_origin_gap': _pair(scaled_gap) if z is not None else None,
        'requested_origin_gap': _pair(requested_gap) if z is not None else None,
        'constant_row': constant, 'disposition': disposition,
        'eligible_for_backend': disposition == 'READY_FOR_BACKEND_READBACK',
        'extra_binary_tau': 0, 'alternative_scales': 0,
        'policy': dict(max_rational_bits=MAX_RATIONAL_BITS, max_coordinates=MAX_COORDINATES,
                       nonzero_to_zero='reject', finite_nonzero_subnormals='allow', overflow='reject',
                       endpoint_rounding='nearest_then_at_most_one_downward_nextafter'),
    }


def verify_actual_binary_cut(encoding, actual_coefficients, actual_lower, actual_upper):
    """Check a saved actual backend row without importing or calling its solver.

    Supply actual coefficients as a mapping or iterable of (coordinate,float)
    pairs. Omitted expected coordinates become exact zeros. Nonzero actual
    coefficients outside supplied source support and out-of-range IDs fail.
    """
    _need(type(encoding) is dict and encoding.get('schema') == SCHEMA, 'RECORD_SCHEMA', 'Unsupported encoding record')
    rows = encoding.get('coefficients')
    _need(type(rows) is list, 'RECORD_SCHEMA', 'Missing explicit source coordinate record')
    a = tuple(_parse(x['source']) for x in rows); ids = tuple(x['coordinate'] for x in rows)
    b = _parse(encoding['source_rhs'])
    regenerated = encode_binary_cut(a,b,coordinates=ids,full_dimension=encoding['full_dimension'],origin=encoding['origin'],require_exclusion=encoding['require_exclusion'])
    _need(regenerated == encoding, 'RECORD_MISMATCH', 'Encoding record does not exactly reproduce the frozen recipe')
    _need(type(actual_lower) is float and math.isfinite(actual_lower), 'ACTUAL_ENDPOINT', 'Actual lower endpoint must be finite binary64')
    _need(type(actual_upper) is float and actual_upper == math.inf, 'ACTUAL_ENDPOINT', 'Actual upper endpoint must be positive infinity')
    supplied = list(actual_coefficients.items()) if isinstance(actual_coefficients, Mapping) else list(actual_coefficients)
    coordinates = set(ids); values = {}; present = set(); implicit_backend_zeros=[]
    for item in supplied:
        _need(isinstance(item,(tuple,list)) and len(item)==2, 'ACTUAL_COORDINATE', 'Expected coordinate/value pair')
        j,value=item
        _need(type(j) is int and 0 <= j < encoding['full_dimension'] and j not in present, 'ACTUAL_COORDINATE', 'Out-of-range or duplicate actual coordinate')
        _need(type(value) is float and math.isfinite(value), 'ACTUAL_COEFFICIENT', 'Actual coefficient must be finite binary64')
        _need(j in coordinates or value == 0., 'ACTUAL_COORDINATE', 'Nonzero backend term outside caller-proved exact source support')
        present.add(j)
        if j in coordinates: values[j]=value
        else: implicit_backend_zeros.append(dict(coordinate=j,actual_hex=value.hex()))
    actual = tuple(values.get(j,0.) for j in ids)
    alpha = tuple(_parse(x['scaled']) for x in rows); beta = _parse(encoding['scaled_rhs'])
    errors = tuple(_guard(F(f)-x) for f,x in zip(actual,alpha))
    correction = _sum(min(x,F(0)) for x in errors)
    bound = _guard(beta+correction)
    outward = F(actual_lower) <= bound
    z = tuple(encoding['origin']) if encoding['origin'] is not None else None
    support_z = tuple(z[j] for j in ids) if z is not None else None
    original_gap = _guard(b-_dot(a,support_z)) if z is not None else None
    actual_gap = _guard(F(actual_lower)-_dot(tuple(F(f) for f in actual),support_z)) if z is not None else None
    exclusion = not encoding['require_exclusion'] or (original_gap > 0 and actual_gap > 0)
    if not outward:
        status = 'REJECTED_ACTUAL_OUTWARD_IMPLICATION'
    elif not encoding['eligible_for_backend']:
        status = 'ORIGINAL_ENCODING_NOT_ADMISSIBLE'
    elif not exclusion:
        status = 'NONPROGRESSING_ACTUAL_ROW'
    else:
        status = 'ADMITTED_ACTUAL_BINARY_ROW'
    return dict(schema=SCHEMA, status=status, admitted=status=='ADMITTED_ACTUAL_BINARY_ROW', require_exclusion=encoding['require_exclusion'],full_dimension=encoding['full_dimension'],
                actual_lower_hex=actual_lower.hex(), actual_upper='positive_infinity',
                actual_coefficients=[dict(coordinate=j,actual_hex=f.hex(),omitted=j not in present,error=_pair(e)) for j,f,e in zip(ids,actual,errors)],
                actual_residual_box_lower=_pair(correction), actual_outward_lower_limit=_pair(bound),
                outward_slack=_pair(bound-F(actual_lower)), outward_valid=outward,
                original_origin_gap=_pair(original_gap) if z is not None else None,
                actual_origin_gap=_pair(actual_gap) if z is not None else None,
                original_strict_exclusion=(original_gap>0) if z is not None else None,
                actual_strict_exclusion=(actual_gap>0) if z is not None else None,
                omitted_coordinate_count=len(coordinates-present), implicit_exact_zero_count=encoding['full_dimension']-len(ids),
                explicit_backend_zeros_on_implicit_source=implicit_backend_zeros,extra_binary_tau=0, changed_backend_row_repaired=False,
                validity_domain='full declared [0,1]^n box conditional on caller-proved exact source-zero completion; hence exact binary states',
                fractional_control_evaluated=False)


def synthetic_controls():
    """Invented inputs only; finite enumeration checks the implication itself."""
    groups=[]; assertions=0; enumerated=0
    def check(condition,message):
        nonlocal assertions
        assertions+=1
        if not condition: raise AssertionError(message)
    def rejected(fn,code):
        try: fn()
        except CutEncodingError as exc: check(exc.code==code,'Expected error '+code+', got '+exc.code)
        else: raise AssertionError('Unsupported case accepted: '+code)
    def actual(record):
        return [(e['coordinate'],float.fromhex(e['encoded_hex'])) for e in record['coefficients']]
    def enumerate_implication(record,coefs,lower):
        nonlocal enumerated
        source=[_parse(e['source']) for e in record['coefficients']]; b=_parse(record['source_rhs'])
        for z in itertools.product((0,1),repeat=len(source)):
            enumerated+=1
            if _dot(source,z)>=b:check(_dot(tuple(F(f) for f in coefs),z)>=F(lower),'Outward implication failed on enumerated binary state')

    for a,k in (([F(3),F(-1,3)],2),([F(1,8),F(-1,16)],-3),([F(1,3)],-1),([F(1,2)],-1),([F(2)],1),([F(1<<2000)],2000),([F(1,1<<2000)],-2000)):
        ex,scale=dyadic_scale(a);check(ex==k and scale/2<max(map(abs,a))<=scale,'Exact integer exponent')
    check(dyadic_scale([F(0),F(0)])==(0,F(1)),'Constant scale1')
    groups.append('integer-comparison smallest dyadic scale: signed support, positive/negative/extreme exponents and constant scale')

    r=encode_binary_cut([F(1),F(1,3),F(-1,3),F(0)],F(1,7),origin=[0,0,0,0])
    errors=[_parse(e['error']) for e in r['coefficients']]
    check(errors[1]<0<errors[2] and errors[0]==errors[3]==0,'Both signed coefficient errors and explicit exact zeros')
    check(_parse(r['residual_box_lower'])==errors[1],'Only negative residual support')
    g=verify_actual_binary_cut(r,actual(r),float.fromhex(r['lower']['encoded_hex']),math.inf)
    check(g['admitted'] and g['original_strict_exclusion'] and g['actual_strict_exclusion'],'Nominee excluded before and after transport')
    enumerate_implication(r,[f for j,f in actual(r)],float.fromhex(r['lower']['encoded_hex']))
    groups.append('both coefficient signs, complete zero entries, exact residual support and exhaustive binary implication')

    down=encode_binary_cut([F(1)],F(1,10),origin=[0]); floor=float.fromhex(down['lower']['encoded_hex'])
    check(down['lower']['nextafter_negative_infinity'] and floor==math.nextafter(float(F(1,10)),-math.inf) and F(floor)<=F(1,10),'Exactly one downward endpoint step')
    below=encode_binary_cut([F(1)],F(1,3),origin=[0]);check(not below['lower']['nextafter_negative_infinity'],'Nearest already below needs no step')
    groups.append('positive endpoint rounding above/below target; no extra step or tolerance')

    omit=encode_binary_cut([F(1)],F(1),origin=[0])
    bad=verify_actual_binary_cut(omit,[],1.,math.inf)
    check(not bad['admitted'] and not bad['outward_valid'] and bad['omitted_coordinate_count']==1,'Omission with old endpoint is unsound')
    check(_dot([F(1)],[1])>=1 and _dot([F(0)],[1])<1,'Concrete feasible binary state lost by uncorrected omission')
    null=verify_actual_binary_cut(omit,[],0.,math.inf)
    check(null['outward_valid'] and not null['admitted'] and null['status']=='NONPROGRESSING_ACTUAL_ROW','Sound omitted row can still be nonprogressing')
    groups.append('actual omitted coefficient counterexample; recomputed implication versus strict progress')

    for rhs,status in ((F(-1),'CONSTANT_NONRESTRICTING_ROW'),(F(0),'CONSTANT_NONRESTRICTING_ROW'),(F(1),'CONSTANT_CONTRADICTION_REQUIRES_SEPARATE_PROOF')):
        c=encode_binary_cut([F(0),F(0)],rhs,origin=[0,1],require_exclusion=False)
        check(c['scale_exponent_2']==0 and c['scale']==['1','1'] and c['disposition']==status and not c['eligible_for_backend'],'Constant disposition, not global proof')
        check(not verify_actual_binary_cut(c,[],float.fromhex(c['lower']['encoded_hex']),math.inf)['admitted'],'Constant not inserted')
    groups.append('constant nonrestricting and contradictory rows remain separate non-insertion dispositions')

    seed=encode_binary_cut([F(1)],F(0),require_exclusion=False)
    check(verify_actual_binary_cut(seed,[(0,1.)],0.,math.inf)['admitted'],'Seed validity does not require an excluded training origin')
    seed_with_origin=encode_binary_cut([F(1)],F(0),origin=[1],require_exclusion=False)
    check(verify_actual_binary_cut(seed_with_origin,[(0,1.)],0.,math.inf)['admitted'],'Optional seed origin can satisfy cut')
    ref=encode_binary_cut([F(1)],F(0),origin=[1],require_exclusion=True)
    check(not ref['eligible_for_backend'],'Identical nonexcluding row cannot be a refinement')
    rejected(lambda:encode_binary_cut([F(1)],F(0)), 'ORIGIN_REQUIRED')
    groups.append('explicit seed/refinement modes; optional seed origin and required strict refinement origin')

    out=encode_binary_cut([F(1)]*5,F(3),origin=[0]*5)
    actual_out=[-1.,1.,1.,1.,1.]
    vr=verify_actual_binary_cut(out,list(enumerate(actual_out)),1.,math.inf)
    check(vr['admitted'],'Actual altered row still has independently valid outward bound and strict origin exclusion')
    enumerate_implication(out,actual_out,1.)
    fractional=(F(7,2),F(0),F(0),F(0),F(0))
    check(_dot([F(1)]*5,fractional)>=3 and _dot(tuple(F(x) for x in actual_out),fractional)<1,'Transport need not hold outside [0,1]')
    rejected(lambda:encode_binary_cut([F(1)]*5,F(3),origin=fractional), 'BINARY_ORIGIN_REQUIRED')
    groups.append('explicit out-of-box fractional counterexample despite valid/progressing binary transport; no fractional-control inference')

    mapped=encode_binary_cut([F(1),F(0)],F(1,2),coordinates=[4,9],full_dimension=10,origin=[0]*10)
    check(verify_actual_binary_cut(mapped,[(4,1.)],.5,math.inf)['admitted'],'Declared zero may be omitted and is recorded')
    rejected(lambda:verify_actual_binary_cut(mapped,[(4,1.),(4,1.)],.5,math.inf),'ACTUAL_COORDINATE')
    rejected(lambda:verify_actual_binary_cut(mapped,[(4,1.),(7,.1)],.5,math.inf),'ACTUAL_COORDINATE')
    rejected(lambda:verify_actual_binary_cut(mapped,[(4,1.),(10,0.)],.5,math.inf),'ACTUAL_COORDINATE')
    explicit_zero=verify_actual_binary_cut(mapped,[(4,1.),(7,0.)],.5,math.inf)
    check(explicit_zero['admitted'] and explicit_zero['implicit_exact_zero_count']==8 and explicit_zero['explicit_backend_zeros_on_implicit_source']==[dict(coordinate=7,actual_hex=0.0.hex())],'Actual zero on implicit exact source coordinate is explicitly recorded')
    rejected(lambda:verify_actual_binary_cut(mapped,[(4,1.)],.5,1e20),'ACTUAL_ENDPOINT')
    rejected(lambda:verify_actual_binary_cut(mapped,[(4,math.nan)],.5,math.inf),'ACTUAL_COEFFICIENT')
    rejected(lambda:verify_actual_binary_cut(mapped,[(4,1.)],-math.inf,math.inf),'ACTUAL_ENDPOINT')
    groups.append('noncontiguous exact maps, expected zero omission, duplicate/unexpected coordinates and finite/upper-infinity gates')

    sparse=encode_binary_cut([F(2),F(-1,3)],F(1),coordinates=[1,4],full_dimension=6,origin=[0]*6)
    sparse_row=verify_actual_binary_cut(sparse,actual(sparse),float.fromhex(sparse['lower']['encoded_hex']),math.inf)
    check(sparse_row['admitted'] and sparse['implicit_exact_zeros']['count']==4,'Sparse exact support/full-dimension contract')
    dense_source=[F(0),F(2),F(0),F(0),F(-1,3),F(0)];dense_actual=[F(0)]*6
    for j,x in actual(sparse):dense_actual[j]=F(x)
    for z in itertools.product((0,1),repeat=6):
        enumerated+=1
        if _dot(dense_source,z)>=1:check(_dot(dense_actual,z)>=F(float.fromhex(sparse['lower']['encoded_hex'])),'Sparse completion exhaustive implication')
    rejected(lambda:encode_binary_cut([F(2),F(-1,3)],F(1),coordinates=[1,4],full_dimension=6,origin=[0,0]),'BINARY_ORIGIN_REQUIRED')
    rejected(lambda:verify_actual_binary_cut(sparse,actual(sparse)+[(2,.001)],float.fromhex(sparse['lower']['encoded_hex']),math.inf),'ACTUAL_COORDINATE')
    empty=encode_binary_cut([],F(0),coordinates=[],full_dimension=6,require_exclusion=False)
    check(empty['scale']==['1','1'] and empty['implicit_exact_zeros']['count']==6 and not empty['eligible_for_backend'],'Empty support constant-zero completion')
    groups.append('sparse gap/full-dimension zero completion, full origin scope, outside-support actual nonzero rejection and empty constant support')

    rejected(lambda:encode_binary_cut([F(1),F(1,1<<1075)],F(1),origin=[0,0]),'BINARY64_UNDERFLOW')
    rejected(lambda:encode_binary_cut([F(1)],F(1,1<<1075),origin=[0]),'BINARY64_UNDERFLOW')
    rejected(lambda:encode_binary_cut([F(1)],F(1<<1024),origin=[0]),'BINARY64_OVERFLOW')
    sub=encode_binary_cut([F(1),F(1,1<<1074)],F(1,2),origin=[0,0])
    check(float.fromhex(sub['coefficients'][1]['encoded_hex'])==math.ulp(0.),'Finite nonzero subnormal is supported')
    rejected(lambda:encode_binary_cut([F(1,1<<8192)],F(1),origin=[0]),'RATIONAL_LIMIT')
    rejected(lambda:encode_binary_cut([1.],F(1),origin=[0]),'EXACT_INPUT_REQUIRED')
    groups.append('frozen overflow/underflow/bit/type policy, while finite nonzero subnormal survives')

    # A real representable nonzero row can lose strict exclusion solely at the
    # permitted outward endpoint rounding, without any underflow or retry.
    small_gap=F(1)+F(1,1<<54)
    np=encode_binary_cut([F(1)],small_gap,origin=[1])
    check(_parse(np['original_origin_gap'])>0 and _parse(np['requested_origin_gap'])==0 and np['disposition']=='NONPROGRESSING_ENCODING','Strict original gap can vanish numerically')
    check(not verify_actual_binary_cut(np,[(0,1.)],1.,math.inf)['admitted'],'No alternate scale or tolerance used to salvage progress')
    groups.append('finite strict original exclusion lost by outward rounding becomes explicit nonprogress, not a rescale')

    tampered=json.loads(json.dumps(r));tampered['coefficients'][1]['error']=['0','1']
    rejected(lambda:verify_actual_binary_cut(tampered,actual(r),float.fromhex(r['lower']['encoded_hex']),math.inf),'RECORD_MISMATCH')
    for source,rhs in (([F(3,7),F(-2,5)],F(1,4)),([F(-1),F(2),F(1,11)],F(1,3)),([F(1,8),F(-3,16),F(1,32)],F(-1,9))):
        e=encode_binary_cut(source,rhs,require_exclusion=False)
        rr=verify_actual_binary_cut(e,actual(e),float.fromhex(e['lower']['encoded_hex']),math.inf)
        check(rr['admitted'],'Mixed-sign seed transport')
        enumerate_implication(e,[f for j,f in actual(e)],float.fromhex(e['lower']['encoded_hex']))
    groups.append('tampered exact record rejection and independent exhaustive mixed-sign binary implication families')
    return dict(status='PASS_SYNTHETIC_ONLY',groups=groups,assertions=assertions,enumerated_binary_states=enumerated,
                scientific_inputs_read=0,optimizer_calls=0,backend_imports=0,scientific_cut_evaluations=0,
                selected_invented_records=dict(signed_rounding=r,omission_failure=bad,out_of_box_transport=vr,nonprogress=np))


def _cli():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test',action='store_true',required=True)
    parser.add_argument('--report-dir',type=Path,required=True)
    parser.add_argument('--protocol',type=Path,required=True)
    args=parser.parse_args()
    _need(not args.report_dir.exists(), 'OUTPUT_EXISTS', 'Use one fresh invented-control output directory')
    source_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    protocol_hash=hashlib.sha256(args.protocol.read_bytes()).hexdigest()
    args.report_dir.mkdir(parents=True)
    try:
        result=synthetic_controls()
    except BaseException as exc:
        with (args.report_dir/'synthetic_failure.json').open('x',encoding='utf-8') as stream:
            json.dump(dict(source_sha256=source_hash,protocol_sha256=protocol_hash,error_type=type(exc).__name__,message=str(exc),scientific_inputs_read=0,optimizer_calls=0),stream,indent=2)
        raise
    _need(source_hash==hashlib.sha256(Path(__file__).read_bytes()).hexdigest() and protocol_hash==hashlib.sha256(args.protocol.read_bytes()).hexdigest(), 'SOURCE_CHANGED', 'Source/protocol changed during controls')
    result.update(utc=datetime.now(timezone.utc).isoformat(),source_sha256=source_hash,protocol_sha256=protocol_hash,python=sys.version)
    with (args.report_dir/'synthetic_receipt.json').open('x',encoding='utf-8') as stream:
        json.dump(result,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({'status':result['status'],'groups':len(result['groups']),'assertions':result['assertions'],'enumerated_binary_states':result['enumerated_binary_states']}))


if __name__=='__main__':
    _cli()
