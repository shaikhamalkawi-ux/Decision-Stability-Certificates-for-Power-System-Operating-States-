"""Exact scope diagnostic: on/on ramp dominance from frozen thermal boxes."""
from pathlib import Path
from fractions import Fraction as Q
from datetime import datetime, timezone
import csv, gzip, hashlib, importlib.util, json, sys, time
sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parents[1]
PRE=ROOT/'results/research_next/common_commitment/prepared'
OUT=ROOT/'results/research_next/ramp_scope'
PROTO=ROOT/'docs/research_next/RAMP_SCOPE_PROTOCOL.md'
MANIFEST_SHA='8ff99b1f4450ac15e91b26a261a85c98d574bbbdac3f7fe149efd9fd07204a5c'
KERNEL=ROOT/'src/research8h_standalone_verify.py'
KERNEL_SHA='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
TAU=Q.from_float(1e-5)
def sha(b): return hashlib.sha256(b).hexdigest()
def rat(x): return {'numerator':str(x.numerator),'denominator':str(x.denominator),'approximate':float(x)}
def main():
    start=time.perf_counter()
    assert not OUT.exists(), 'One scope audit; preserve prior output'
    data=(PRE/'input_manifest.json').read_bytes()
    assert sha(data)==MANIFEST_SHA
    roster={str(Path(r['path']).resolve()).casefold():r for r in json.loads(data)['files']}
    bindings=[]
    def captured(p):
        b=p.read_bytes(); r=roster[str(p.resolve()).casefold()]
        assert len(b)==r['bytes'] and sha(b)==r['sha256']
        bindings.append(r); return b
    assert sha(KERNEL.read_bytes())==KERNEL_SHA
    s=importlib.util.spec_from_file_location('ramp_scope_readonly_kernel',KERNEL)
    v=importlib.util.module_from_spec(s); sys.modules[s.name]=v; s.loader.exec_module(v)
    cases=[]; worlds=[]
    for world in ('identity','days_321'):
        folder=PRE/world
        files={n:captured(folder/n) for n in ('native_inputs.npz','model_metadata.json','native_spec.json','row_metadata.csv.gz')}
        meta=json.loads(files['model_metadata.json']); specs=json.loads(files['native_spec.json'])
        assert [r['uid'] for r in specs]==meta['unit_names']
        arrays=v.read_npz(folder/'native_inputs.npz',('pmin','pmax','net','rows','source_hour','nodal'))
        assert arrays['pmin'].shape==arrays['pmax'].shape==(168,41)
        labels=list(csv.DictReader(gzip.decompress(files['row_metadata.csv.gz']).decode('utf-8-sig').splitlines()))
        families={}
        for r in labels: families[r['family']]=families.get(r['family'],0)+1
        assert len(labels)==34681
        current=[]
        for j,r in enumerate(specs):
            if not r['thermal']: continue
            rate=Q(int(r['hourly_rational']['numerator']),int(r['hourly_rational']['denominator']))
            for t in range(1,168):
                lo,prevlo=(Q(arrays['pmin'].values[41*h+j]) for h in (t,t-1))
                hi,prevhi=(Q(arrays['pmax'].values[41*h+j]) for h in (t,t-1))
                assert lo<=hi and prevlo<=prevhi
                d=max(hi-prevlo,prevhi-lo); margin=rate-d
                row={'world':world,'unit':r['uid'],'hour_0based':t,'nominal_change_envelope':rat(d),
                     'hourly_rate':rat(rate),'margin':rat(margin),'nominal_implied':margin>=0,
                     'expanded_native_check_implied':margin>=TAU}
                cases.append(row); current.append(margin)
        assert len(current)==24*167
        worlds.append({'world':world,'adjacent_on_on_cases':len(current),'row_families':families,
                       'minimum_nominal_margin':rat(min(current)),
                       'all_expanded_native_ramp_checks_implied':all(x>=TAU for x in current)})
    for r in bindings:
        b=Path(r['path']).read_bytes()
        assert len(b)==r['bytes'] and sha(b)==r['sha256']
    OUT.mkdir()
    evidence={'cases':cases,'note':'Conditional on exact binary on/on states; no startup/shutdown ramp claim.'}
    (OUT/'cases.json').write_text(json.dumps(evidence,indent=2,allow_nan=False)+'\n',encoding='utf8')
    result={'status':'CLOSED_STRUCTURAL_SCOPE_AUDIT','utc':datetime.now(timezone.utc).isoformat(),
            'source_sha256':sha(Path(__file__).read_bytes()),'protocol_sha256':sha(PROTO.read_bytes()),
            'old_manifest_sha256':MANIFEST_SHA,'kernel_sha256':KERNEL_SHA,'input_bindings':bindings,
            'cases':len(cases),'worlds':worlds,'exact_tau':rat(TAU),
            'failures':sum(not x['expanded_native_check_implied'] for x in cases),
            'all_inputs_unchanged':True,'optimizer_calls':0,'model_builds':0,
            'cases_sha256':sha((OUT/'cases.json').read_bytes()),'elapsed_seconds':time.perf_counter()-start}
    (OUT/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps({k:result[k] for k in ('status','cases','failures','elapsed_seconds')}))
if __name__=='__main__': main()
