"""Independent closed phase-I review. No producer/optimizer import or old point replay."""
import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
ARM = ROOT / 'results/research_next/common_phase1'
PRE = ARM / 'prepared'
RUN = ARM / 'run01'
KERNEL = ROOT / 'src/research8h_standalone_verify.py'
KERNEL_SHA = '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
TAU = F.from_float(1e-5)
PINS = {
    ROOT / 'src/researchnext_common_phase1.py': '8af88d286e85f5807ab0bc11cc2450d10596f667e62f4b45c5279c8ebbc2eacb',
    ROOT / 'docs/research_next/COMMON_PHASE1_PROTOCOL.md': '6617c67b1c93339487a41c306217c8770142665b9e35e33f23a09225f1e00583',
    PRE / 'prepared_freeze.json': '9d2a0768eb785277d9b8ddf04483e0e83ed97ba628fff23e2a32b146649e1496',
    PRE / 'input_manifest.json': '9e4640c4bea127601201e3323f43471e2582eb9aab26ed6cb045f566c4f00d70',
    OUT / 'prepared_review.json': '989c84f8e1ede00370d406f811f1ed6123cf3efb3a62615815ddf5f35b38f74d',
    KERNEL: KERNEL_SHA,
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def gz(path):
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        return json.load(stream)


def binding(item):
    p = Path(item['path']); data = p.read_bytes()
    need(len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'], 'Changed binding ' + str(p))


def frac(pair):
    need(isinstance(pair, list) and len(pair) == 2 and all(isinstance(x, str) for x in pair), 'Rational schema')
    q = F(int(pair[0]), int(pair[1]))
    need(pair == [str(q.numerator), str(q.denominator)], 'Canonical rational')
    return q


def pair(q):
    return [str(q.numerator), str(q.denominator)]


def main(args):
    started = time.perf_counter()
    for path, digest in PINS.items():
        need(sha(path) == digest, 'Pinned prepared/source evidence ' + str(path))
    inventory_path = ARM / 'producer_output_inventory.csv'
    need(sha(inventory_path) == args.inventory_sha256, 'Trusted closed inventory')
    need(sha(RUN / 'completion.json') == args.completion_sha256, 'Trusted completed run')
    items = read(PRE / 'input_manifest.json')['files']
    need(len(items) == 292 and len({x['path'].casefold() for x in items}) == 292, '292 unique input bindings')
    for x in items:
        binding(x)
    with inventory_path.open(encoding='utf-8-sig', newline='') as stream:
        entries = list(csv.DictReader(stream))
    outputs = []
    for e in entries:
        p = (ROOT / e['path']).resolve()
        need(p.is_relative_to(ARM.resolve()), 'Public producer output confinement')
        outputs.append({'path': str(p), 'bytes': int(e['bytes']), 'sha256': e['sha256']})
    need(len({x['path'].casefold() for x in outputs}) == len(outputs), 'Unique output paths')
    for x in outputs:
        binding(x)
    run_files = {p.resolve() for p in RUN.rglob('*') if p.is_file()}
    bound_files = {Path(x['path']).resolve() for x in outputs}
    need(run_files <= bound_files, 'All run files in closed inventory')
    need(not (RUN / 'failure.json').exists(), 'This complete-run reviewer does not silently reinterpret a failed run')
    transport = {str(p): sha(p) for p in (*PINS, inventory_path)}

    spec = importlib.util.spec_from_file_location('phase1_postrun_independent_decoder', KERNEL)
    v = importlib.util.module_from_spec(spec); sys.modules[spec.name] = v; spec.loader.exec_module(v)
    members = ('data', 'indices', 'indptr', 'shape', 'column_lower', 'column_upper', 'row_lower', 'row_upper', 'objective', 'integrality')
    phase = v.read_npz(PRE / 'phase_model.npz', members)
    actual = v.read_npz(RUN / 'backend_readback.npz', members)
    nr, nc = v.vector(phase['shape'], ('<i8',), 2, 'prepared phase shape')
    need((nr, nc) == (98546, 33937), 'Fixed phase dimensions')
    for k in ('shape', 'column_lower', 'column_upper', 'row_lower', 'row_upper', 'objective', 'integrality'):
        need(actual[k] == phase[k], 'Complete numerical backend array ' + k)
    pdata = v.vector(phase['data'], ('<f8',), 505786, 'prepared phase coefficients')
    pjs = v.vector(phase['indices'], ('<i8',), len(pdata), 'prepared phase indices')
    pp = v.vector(phase['indptr'], ('<i8',), nr + 1, 'prepared phase pointers')
    adata = v.vector(actual['data'], ('<f8',), len(pdata), 'actual phase coefficients')
    ajs = v.vector(actual['indices'], ('<i8',), len(adata), 'actual phase indices')
    ap = v.vector(actual['indptr'], ('<i8',), nr + 1, 'actual phase pointers')
    need(ap[0] == 0 and ap[-1] == len(adata) and all(a <= b for a,b in zip(ap,ap[1:])), 'Actual CSR consistency')
    for r in range(nr):
        wanted = sorted(zip(pjs[pp[r]:pp[r+1]], pdata[pp[r]:pp[r+1]]))
        got = list(zip(ajs[ap[r]:ap[r+1]], adata[ap[r]:ap[r+1]]))
        need(got == wanted and len({j for j,x in got}) == len(got), 'Every actual numerical row ' + str(r))
    backend = read(RUN / 'backend_readback.json'); plan = read(PRE / 'plan.json')
    need(backend['options'] == plan['options'] == {'time_limit':60., 'threads':1, 'random_seed':0, 'presolve':'on', 'solver':'simplex'}, 'Backend option readback')
    need((backend['rows'], backend['columns'], backend['coefficient_uses']) == (nr,nc,len(adata)), 'Backend counts')
    need(backend['phase_model_sha256'] == sha(PRE/'phase_model.npz') and backend['readback_sha256'] == sha(RUN/'backend_readback.npz'), 'Readback model binding')

    raw = v.read_npz(RUN/'raw_solution.npz', ('vector','row_value','row_dual','col_dual'))
    for name in raw:
        need(raw[name].dtype == '<f8' and len(raw[name].shape) == 1, 'Raw numeric vector schema ' + name)
    returned = read(RUN/'solver_returned.json'); result = read(RUN/'result.json'); completion = read(RUN/'completion.json')
    endpoints = gz(PRE/'endpoint_map.json.gz')
    eligible = bool(returned['dual_valid'] and raw['row_dual'].shape == (nr,) and all(math.isfinite(x) for x in raw['row_dual'].values))
    proof_report = {'eligible_complete_dual': eligible, 'mathematically_separating': False, 'old_full_point_replayed': False}
    cert_path = RUN/'exact_candidate.json.gz'
    if eligible:
        need(cert_path.is_file(), 'Eligible sole exact candidate must be retained')
        cert = gz(cert_path); m = v.load_model(PRE/'joint')
        need((m.rows,m.cols,len(m.data)) == (69362,33936,291176), 'Original source model')
        mask = v.vector(v.read_npz(PRE/'joint/integrality.npz', ('integrality',))['integrality'], ('|u1',), m.cols, 'original state mask')
        need(mask == tuple(int(6888<=j<18984) for j in range(m.cols)), 'Complete original state block')
        se = read(PRE/'fixed_schedule.json')['fixed_columns']; fixed = {x['column']: x['value'] for x in se}
        need(len(se) == len(fixed) == 12096 and set(fixed) == {j for j,b in enumerate(mask) if b} and all(type(x)is int and x in (0,1) for x in fixed.values()), 'Sole immutable exact nominee')
        controls = v.read_npz(PRE/'control_raw_solution.npz', ('vector','row_value','row_dual','col_dual'))
        control = v.vector(controls['vector'], ('<f8',), m.cols, 'old unrounded point coordinates')
        need(all(math.isfinite(x) for x in control), 'Finite inherited control')
        lower = [F(0)]*m.rows; upper = [F(0)]*m.rows
        projection = cert['raw_endpoint_projection']; need(len(projection)==nr, 'Full projection denominator')
        seen = set()
        for i,(e,x,p) in enumerate(zip(endpoints,raw['row_dual'].values,projection)):
            r = e['original_row']; side = e['side']; need((r,side) not in seen and e['phase_row']==i, 'Unique ordered source endpoint'); seen.add((r,side))
            need(p['phase_row']==i and p['original_row']==r and p['side']==side and p['raw_hex']==x.hex(), 'Every raw projected endpoint identity')
            qx = F(x)
            weight = max(qx,F(0)) if side=='lower' else max(-qx,F(0))
            need(frac(p['nonnegative_multiplier']) == weight, 'Prescribed single sign projection')
            if side=='lower':
                need(math.isfinite(m.row_lower[r]), 'Available lower endpoint'); lower[r] = weight
            else:
                need(side=='upper' and math.isfinite(m.row_upper[r]), 'Available upper endpoint'); upper[r] = weight
        need(seen == {(r,s) for r in range(m.rows) for s,b in (('lower',m.row_lower[r]),('upper',m.row_upper[r])) if math.isfinite(b)}, 'Complete available endpoint denominator')
        d = [a-b for a,b in zip(lower,upper)]
        need(len(cert['original_d'])==m.rows and [frac(x) for x in cert['original_d']] == d, 'Every original signed multiplier')
        q = [F(0)]*m.cols; beta=raw_beta=F(0); selected=[]; interval_gain=F(0)
        for r in range(m.rows):
            a,b=lower[r],upper[r]
            need(m.row_lower[r]<=m.row_upper[r], 'Ordered original row')
            if a: raw_beta += a*F(m.row_lower[r])
            if b: raw_beta -= b*F(m.row_upper[r])
            if a and b: interval_gain += min(a,b)*(F(m.row_upper[r])-F(m.row_lower[r]))
            if d[r]:
                side='lower' if d[r]>0 else 'upper'; endpoint=m.row_lower[r] if d[r]>0 else m.row_upper[r]
                need(math.isfinite(endpoint), 'Finite signed selected endpoint'); beta+=d[r]*F(endpoint)
                selected.append({'row':r,'side':side,'endpoint_hex':endpoint.hex()})
                for k in range(m.indptr[r],m.indptr[r+1]):
                    q[m.indices[k]] += d[r]*F(m.data[k])
        need(len(cert['full_A_transpose_d'])==m.cols and [frac(x) for x in cert['full_A_transpose_d']] == q, 'Full original-column vector identity with every residual')
        need(cert['selected_original_endpoints']==selected, 'Every signed endpoint witness')
        row_norm=sum(map(abs,d),F(0)); unmerged=sum(lower,F(0))+sum(upper,F(0)); cancellation=2*sum((min(a,b) for a,b in zip(lower,upper)),F(0))
        need(beta-raw_beta==interval_gain and unmerged-row_norm==cancellation, 'Independent canonical cancellation identities')
        need(interval_gain>=0 and cancellation>=0, 'Nonnegative canonical gains')
        support=F(0); c_norm=F(0); nominee=F(0); ctrl=F(0); support_meta=[]
        for j,a in enumerate(q):
            if mask[j]:
                nominee += a*fixed[j]; ctrl += a*F(control[j])
            else:
                endpoint=m.upper[j] if a>=0 else m.lower[j]
                need(math.isfinite(endpoint), 'Finite original continuous support'); support += a*F(endpoint); c_norm += abs(a)
                support_meta.append({'column':j,'endpoint_side':'upper' if a>=0 else 'lower','endpoint_hex':endpoint.hex()})
        need(cert['continuous_support_endpoints']==support_meta, 'Complete continuous support selection')
        loss=TAU*(row_norm+c_norm); rhs=beta-support-loss; margin=rhs-nominee
        expanded_gain=beta-TAU*row_norm-(raw_beta-TAU*unmerged)
        need(expanded_gain==interval_gain+TAU*cancellation, 'Expanded gain including endpoint tau cancellation')
        numbers={'beta':beta,'beta_raw':raw_beta,'canonical_interval_gain':interval_gain,'unmerged_multiplier_norm':unmerged,'original_row_norm':row_norm,'norm_cancellation':cancellation,
                 'expanded_canonical_gain':expanded_gain,'continuous_support':support,'continuous_q_norm':c_norm,'tau_loss':loss,'cut_rhs':rhs,'nominee_state_value':nominee,'expanded_margin':margin,'control_state_value':ctrl}
        for name,value in numbers.items():
            need(frac(cert[name])==value, 'Exact certificate scalar '+name)
        need(ctrl>=rhs and cert['control_satisfied'] is True, 'Inherited fractional-state consistency control; no membership replay')
        need(cert['strictly_positive_expanded_margin']==(margin>0) and cert['status']==('VERIFIED_GLOBAL_NECESSARY_CUT_REJECTS_NOMINEE' if margin>0 else 'VALID_NONSEPARATING_CANDIDATE'), 'Exact candidate classification')
        need(cert['row_support']==sum(bool(x) for x in d) and cert['state_support']==sum(bool(q[j]) for j,b in enumerate(mask) if b) and cert['continuous_support_count']==sum(bool(q[j]) for j,b in enumerate(mask) if not b), 'Full support counts')
        need(cert['extra_binary_tau']==cert['derived_row_extra_tau']==cert['alternative_multiplier_candidates']==0 and cert['all_original_coefficients_retained'] is True and cert['old_full_point_replayed'] is False, 'Stated certificate scope')
        need(cert['model_bindings']=={n:sha(PRE/'joint'/n) for n in ('matrix.npz','bounds.npz','integrality.npz','column_maps.json','row_origins.json')}, 'Complete certificate model bindings')
        need(cert['nominee_sha256']==sha(PRE/'fixed_schedule.json') and cert['raw_dual_sha256']==sha(RUN/'raw_solution.npz') and cert['control_sha256']==sha(PRE/'control_raw_solution.npz'), 'Raw and point certificate roles')
        need(result['candidate_status']==cert['status'] and result['accepted_nominee_rejection']==(margin>0), 'Provisional result matches exact candidate')
        # Classify this same certificate's support using already bound original labels.
        # This does not construct another certificate or attribute a temporal cause.
        origins=read(PRE/'joint/row_origins.json')['origins']; maps=read(PRE/'joint/column_maps.json')
        metadata=[]
        for world in maps['worlds']:
            p=ROOT/'results/research_next/common_master_bounded/prepared'/world/'row_metadata.csv.gz'
            need(str(p.resolve()) in {x['path'] for x in items}, 'Row metadata frozen before execution')
            with gzip.open(p,'rt',encoding='utf-8-sig',newline='') as stream:
                rows=list(csv.DictReader(stream))
            need(len(rows)==34681 and [int(e['row']) for e in rows]==list(range(34681)), 'Complete inherited row-label map')
            metadata.append(rows)
        support_rows=[]
        for r,weight in enumerate(d):
            if weight:
                wi,sr=origins[r]; e=metadata[wi][sr]
                support_rows.append({'joint_row':r,'world':maps['worlds'][wi],'original_row':sr,'family':e['family'],'hour_0based':int(e['hour_0based']),'uid':e['uid'],'multiplier':pair(weight)})
        thermal=read(PRE/'identity_metadata.json')['thermal_unit_names']
        need(len(thermal)==24, 'State-label thermal roster')
        state_rows=[]
        for j,value in enumerate(q):
            if mask[j] and value:
                offset=j-6888; block,within=divmod(offset,4032); hour,unit=divmod(within,24)
                state_rows.append({'joint_column':j,'state_type':('U','Y','Z')[block],'hour_0based':hour,'uid':thermal[unit],'coefficient':pair(value),'nominee_bit':fixed[j]})
        proof_report.update(mathematically_separating=margin>0, row_support=cert['row_support'], state_support=cert['state_support'], continuous_support=cert['continuous_support_count'], original_rows=m.rows, original_columns=m.cols,
            original_coefficients=len(m.data), candidate_margin=pair(margin), candidate_margin_float=float(margin), cut_rhs=pair(rhs), nominee_value=pair(nominee), control_value=pair(ctrl), control_slack=pair(ctrl-rhs),
            canonical_gain=pair(expanded_gain), all_coefficients_and_scalars_exact=True, nominee_rejected_only=margin>0,
            support_rows=support_rows,support_family_counts=dict(Counter(x['family'] for x in support_rows)),support_hours=sorted({x['hour_0based'] for x in support_rows}),support_worlds=sorted({x['world'] for x in support_rows}),
            state_columns=state_rows,state_type_counts=dict(Counter(x['state_type'] for x in state_rows)),state_hours=sorted({x['hour_0based'] for x in state_rows}),
            temporal_mechanism_claim=False)
    else:
        need(not cert_path.exists() and result['candidate_status']=='NO_VALID_FINITE_COMPLETE_RETURNED_DUAL' and result['accepted_nominee_rejection'] is False, 'Eligible-dual null retained')

    start=read(RUN/'execution_started.json'); ready=read(RUN/'call_ready.json'); ledger=completion['call_ledger']
    need(start['source_sha256']==PINS[ROOT/'src/researchnext_common_phase1.py'] and start['freeze_sha256']==PINS[PRE/'prepared_freeze.json'] and start['phase_seconds']==180., 'Entry source/phase identity')
    need(type(start['pid'])is int and type(start['parent_pid'])is int and start['pid']>0 and start['parent_pid']>0, 'Recorded actual interpreter PID and parent PID')
    need(ready['not_actual_call'] is True and ready['remaining']>=65., 'Initial ready-file guard')
    need(ledger['attempted']==ledger['returned']==1 and math.isfinite(ledger['actual_seconds']) and ledger['actual_seconds']>=0, 'Exactly one returned phase-I call')
    need(result['provisional_until_completion'] is True and result['common_verdict']=='UNKNOWN' and result['no_unrestricted_negative_claim'] is True, 'Provisional scope')
    need(completion['solver_soft_overrun']==max(0,ledger['actual_seconds']-60.) and completion['phase_soft_overrun']==max(0,completion['phase_seconds']-180.), 'Actual soft overrun accounting')
    need(completion['all_frozen_bytes_unchanged'] is True and completion['no_retry'] is True and completion['no_ray_recovery'] is True and completion['alternative_multiplier_candidates']==0 and completion['final_write_cleanup_outside_sample'] is True, 'Closed scope and timings')
    final=completion['final_admission']
    need(final['common_verdict']=='UNKNOWN' and final['phase_deadline_met']==(completion['phase_seconds']<=180.), 'Unrestricted question and deadline snapshot')
    if final['accepted_nominee_rejection']:
        need(proof_report['mathematically_separating'] and final['phase_deadline_met'] and final['status']=='EXACT_CUT_REJECTS_FIXED_NOMINEE', 'Authoritative positive exact rejection gate')
    else:
        need(final['status']=='NO_ACCEPTED_CERTIFICATE', 'Authoritative null classification')
    need(not any('ray' in p.name.lower() for p in run_files), 'No ray-recovery artifact')
    need(read(RUN/'private_log_receipt.json')['raw_logs_public'] is False, 'Private logs are not read or published by reviewer')
    process=read(ARM/'PROCESS_CLOSURE.json')
    need(process['exit_code']==0 and process['optimizer_calls_attempted']==process['optimizer_calls_returned']==1 and process['retries']==process['alternative_multiplier_candidates']==process['new_master_calls']==0, 'Closed one-process one-call ledger')
    need(process['runner_actual_python_pid']==start['pid'] and process['runner_parent_pid']==start['parent_pid'] and process['known_pids_still_present']==[] and process['external_termination_calls']==0, 'Normal known process closure, not a termination experiment')
    need(process['authoritative_producer_nominee_rejection']==final['accepted_nominee_rejection'] and process['unrestricted_common_verdict']=='UNKNOWN', 'Process interpretation matches authoritative result')
    for item in items+outputs:
        binding(item)
    need(all(sha(p)==digest for p,digest in transport.items()), 'All closure/transport pins unchanged')
    need({p.resolve() for p in RUN.rglob('*') if p.is_file()}==run_files, 'No producer file additions during review')
    review=dict(status='PASS_INDEPENDENT_POSTRUN',utc=datetime.now(timezone.utc).isoformat(),reviewer_sha256=sha(__file__),elapsed_seconds=time.perf_counter()-started,
        input_bindings=len(items),producer_outputs=len(outputs),run_files=len(run_files),all_files_unchanged=True,inventory_sha256=args.inventory_sha256,completion_sha256=args.completion_sha256,
        backend_rows=nr,backend_columns=nc,backend_coefficient_uses=len(adata),complete_backend_readback=True,exact_proof=proof_report,
        phase1_calls=1,solver_seconds=ledger['actual_seconds'],phase_seconds=completion['phase_seconds'],solver_soft_overrun=completion['solver_soft_overrun'],phase_soft_overrun=completion['phase_soft_overrun'],
        final_admission=final,common_verdict='UNKNOWN',no_unrestricted_negative=True,solver_imports=0,producer_imports=0,optimizer_calls_by_reviewer=0,old_point_membership_replays=0,
        new_multiplier_candidates=0,private_logs_read=False,decoder_reuse=KERNEL_SHA,
        process_scope='Entry records actual Python and parent PID; this mathematical audit does not establish descendant timeout termination.',
        note='The exact signed endpoint proof is independent of numerical optimality or the positive phase-I objective. Completion final admission is authoritative.')
    with (OUT/'postrun_review.json').open('x',encoding='utf-8') as stream:
        json.dump(review,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({'status':review['status'],'elapsed_seconds':review['elapsed_seconds'],'report_sha256':sha(OUT/'postrun_review.json')}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory-sha256',required=True);parser.add_argument('--completion-sha256',required=True)
    args=parser.parse_args()
    try:
        main(args)
    except BaseException as exc:
        with (OUT/'postrun_review_failure.json').open('x',encoding='utf-8') as stream:
            json.dump({'reviewer_sha256':sha(__file__),'error_type':type(exc).__name__,'message':str(exc),'optimizer_calls':0},stream,indent=2)
        raise
