"""Exact necessary energy floors for one previously frozen common schedule."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction as Q

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PRE = ROOT / 'results/research_next/common_union/prepared'
OUT = ROOT / 'results/research_next/union_energy_floor'
PROTOCOL = ROOT / 'docs/research_next/UNION_ENERGY_FLOOR_PROTOCOL.md'
KERNEL = ROOT / 'src/research8h_standalone_verify.py'
TAU = Q.from_float(1e-5)
FREEZE = '8d5e348d91db8ae082a1a036d2359ac382891b25849e9e682fb833e9ae52d0a2'
MANIFEST = '1337e9674d15fc52023733b8c72b1140c20d01a472a287fd43a90cd5719d3a2d'
KERNEL_SHA = '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def need(ok, message):
    if not ok: raise ValueError(message)
def save(p, x):
    with Path(p).open('x', encoding='utf-8') as f:
        json.dump(x, f, indent=2, allow_nan=False); f.write('\n')
def rat(x): return dict(numerator=str(x.numerator), denominator=str(x.denominator), approximate=float(x))

def main():
    started = time.perf_counter()
    def budget(): need(time.perf_counter()-started < 120, 'Soft phase budget exceeded')
    need(not OUT.exists(), 'One fresh diagnostic only')
    need(sha(PRE/'prepared_freeze.json') == FREEZE, 'Freeze pin')
    need(sha(PRE/'input_manifest.json') == MANIFEST, 'Manifest pin')
    need(sha(KERNEL) == KERNEL_SHA, 'Decoder pin')
    old = {str(Path(x['path']).resolve()).casefold(): x for x in read(PRE/'input_manifest.json')['files']}
    paths = [PRE/'candidate_schedule.json']
    for world in ('identity', 'days_321'):
        paths += [PRE/world/name for name in ('matrix.npz','bounds.npz','integrality.npz','model_metadata.json')]
    bindings = []
    for p in paths:
        x = old[str(p.resolve()).casefold()]
        need(p.stat().st_size == x['bytes'] and sha(p) == x['sha256'], 'Selected input changed')
        bindings.append(x)
    for p in (Path(__file__), PROTOCOL, KERNEL, PRE/'prepared_freeze.json', PRE/'input_manifest.json'):
        bindings.append(dict(path=str(p.resolve()), bytes=p.stat().st_size, sha256=sha(p)))
    OUT.mkdir()
    save(OUT/'started.json', dict(utc=datetime.now(timezone.utc).isoformat(), inputs=bindings,
        optimizer_calls=0, source_sha256=sha(__file__), protocol_sha256=sha(PROTOCOL)))
    spec = importlib.util.spec_from_file_location('floor_npz_decoder', KERNEL)
    v = importlib.util.module_from_spec(spec); sys.modules[spec.name] = v; spec.loader.exec_module(v)
    schedule = read(PRE/'candidate_schedule.json')['fixed_columns']
    fixed = {x['column']: Q(x['value']) for x in schedule}
    need(len(fixed) == 12096 and set(fixed) == set(range(6888,18984)), 'Complete fixed states')
    need(all(x in (0,1) for x in fixed.values()), 'Exact bits')
    summaries = []
    for world in ('identity','days_321'):
        budget(); folder = PRE/world; m = v.load_model(folder); meta = read(folder/'model_metadata.json')
        need((m.rows,m.cols) == (34681,23016), 'Original dimensions')
        bits = v.vector(v.read_npz(folder/'integrality.npz', ('integrality',))['integrality'], ('|u1',), m.cols, 'original bits')
        need(set(fixed) == {j for j,b in enumerate(bits) if b}, 'Original mask')
        need(meta['hours']==168 and meta['units']==41 and len(meta['fossil_units'])==23, 'Original roster')
        fossil = {meta['unit_names'].index(n) for n in meta['fossil_units']}
        cap_columns = {41*t+j for t in range(168) for j in fossil}
        low=[]; high=[]; low_from=[]; high_from=[]
        for j in range(6888):
            need(math.isfinite(m.lower[j]) and math.isfinite(m.upper[j]), 'Finite original P boxes')
            low.append(Q(m.lower[j])-TAU); high.append(Q(m.upper[j])+TAU)
            low_from.append(dict(box=j,side='lower')); high_from.append(dict(box=j,side='upper'))
        balances={}; cap=None; single_rows=0
        for i in range(m.rows):
            if i % 512 == 0: budget()
            entries=[(m.indices[k],Q(m.data[k])) for k in range(m.indptr[i],m.indptr[i+1])]
            nonstate=[(j,a) for j,a in entries if j not in fixed]
            if len(nonstate)==1 and nonstate[0][0]<6888:
                j,a=nonstate[0]; need(a!=0,'Zero stored coefficient')
                constant=sum((a*fixed[j] for j,a in entries if j in fixed),Q(0)); single_rows+=1
                for value, side in ((m.row_lower[i],'lower'),(m.row_upper[i],'upper')):
                    if not math.isfinite(value): continue
                    bound=(Q(value)+(-TAU if side=='lower' else TAU)-constant)/a
                    islower=(side=='lower')==(a>0)
                    if islower and bound>low[j]: low[j]=bound; low_from[j]=dict(row=i,side=side)
                    if not islower and bound<high[j]: high[j]=bound; high_from[j]=dict(row=i,side=side)
            if len(entries)==41 and all(a==1 and j<6888 for j,a in entries):
                hours={j//41 for j,a in entries}
                if len(hours)==1:
                    t=next(iter(hours))
                    if {j for j,a in entries}==set(range(41*t,41*(t+1))):
                        need(t not in balances,'Duplicate aggregate row')
                        need(math.isfinite(m.row_lower[i]) and math.isfinite(m.row_upper[i]),'Finite aggregate')
                        balances[t]=(i,Q(m.row_lower[i])-TAU,Q(m.row_upper[i])+TAU)
            if len(entries)==len(cap_columns) and {j for j,a in entries}==cap_columns and all(a==1 for j,a in entries):
                need(cap is None and m.row_upper[i]==23195,'Unique original cap')
                cap=(i,Q(m.row_upper[i])+TAU)
        need(len(balances)==168 and cap is not None,'Complete aggregate/cap roster')
        empty=[j for j in range(6888) if low[j]>high[j]]
        hourly=[]; total=Q(0); bad_hours=[]
        for t in range(168):
            row,bal_low,bal_high=balances[t]
            direct=sum((low[41*t+j] for j in fossil),Q(0))
            other_upper=sum((high[41*t+j] for j in range(41) if j not in fossil),Q(0))
            balance_floor=bal_low-other_upper; bound=max(direct,balance_floor); total+=bound
            interval_low=sum(low[41*t:41*(t+1)],Q(0)); interval_high=sum(high[41*t:41*(t+1)],Q(0))
            if interval_low>bal_high or interval_high<bal_low: bad_hours.append(t)
            hourly.append(dict(hour=t,aggregate_row=row,direct_fossil_floor=rat(direct),
                balance_minus_nonfossil_upper=rat(balance_floor),selected_floor=rat(bound),
                active='individual_lower_sum' if direct>=balance_floor else 'balance_minus_other_upper',
                total_interval_lower=rat(interval_low),total_interval_upper=rat(interval_high),
                balance_lower=rat(bal_low),balance_upper=rat(bal_high)))
        save(OUT/(world+'_derivations.json'),dict(world=world,variables=[dict(column=j,lower=rat(low[j]),
            upper=rat(high[j]),lower_source=low_from[j],upper_source=high_from[j]) for j in range(6888)],hourly=hourly))
        summaries.append(dict(world=world,single_generation_rows=single_rows,empty_generation_intervals=empty,
            disjoint_hourly_aggregate_intervals=bad_hours,necessary_fossil_energy_floor=rat(total),cap_row=cap[0],
            expanded_cap=rat(cap[1]),floor_minus_cap=rat(total-cap[1]),strict_floor_excess=total>cap[1],
            fixed_schedule_obstruction_pending_independent_review=bool(empty or bad_hours or total>cap[1])))
    for x in bindings:
        p=Path(x['path']); need(p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],'Input changed at close')
    budget()
    save(OUT/'result.json',dict(status='CLOSED_PENDING_INDEPENDENT_REVIEW',worlds=summaries,
        optimizer_calls=0,scientific_candidates=1,new_candidates_generated=0,all_inputs_unchanged=True,
        elapsed_seconds=time.perf_counter()-started,not_complete_dispatch_test=True,
        unrestricted_common_verdict='UNKNOWN',tau=rat(TAU)))
    print(json.dumps(summaries),flush=True)

if __name__=='__main__':
    try: main()
    except BaseException as exc:
        if OUT.exists() and not (OUT/'failure.json').exists():
            save(OUT/'failure.json',dict(error_type=type(exc).__name__,message=str(exc),optimizer_calls=0,no_retry=True))
        raise
