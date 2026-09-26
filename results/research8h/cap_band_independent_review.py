"""Independent arithmetic replay of cap-band consequences; no model solve/replay."""
import hashlib,json,time
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/research8h/cap_band';BASE=ROOT/'results/research8h/energy_lp_refinement'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def q(x):return F(int(x['numerator']),int(x['denominator']))
def floor(x):return x.numerator//x.denominator
def ceil(x):return divmod(x.numerator,x.denominator)[0]+bool(x.numerator%x.denominator)
def rat(x):return dict(numerator=str(x.numerator),denominator=str(x.denominator),approximate=float(x))
def main():
    started=time.perf_counter();manifest=read(OUT/'input_manifest.json')
    expect={str(p) for p in (ROOT/'src/research8h_cap_band.py',ROOT/'docs/research8h/CAP_BAND_PROTOCOL.md',BASE/'refined_brackets.json',BASE/'independent_review.json')}
    assert len(manifest)==4 and {str(Path(r['path'])) for r in manifest}==expect
    def check():
        for r in manifest:
            p=Path(r['path']);assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
    check();before=read(OUT/'before_arithmetic.json');assert before['input_manifest_sha256']==sha(OUT/'input_manifest.json') and before['optimizer_calls']==0
    saved=read(OUT/'cap_bands.json');inputs=read(BASE/'refined_brackets.json');review=read(BASE/'independent_review.json')
    assert review['status']=='PASS_COMPLETE' and review['all_59_frozen_hashes_and_byte_counts_pass']
    verified={r['case']:r for r in review['cases']}
    tau=F.from_float(1e-5);assert q(saved['tau'])==tau
    result=[]
    for r,s in zip(inputs,saved['results']):
        assert r['case']==s['case']
        ui=q(r['identity_optimum_bounds_MWh']['upper']);li=q(r['identity_optimum_bounds_MWh']['lower'])
        lt=q(r['target_optimum_bounds_MWh']['lower']);ut=q(r['target_optimum_bounds_MWh']['upper'])
        assert 0<li<=ui<lt<=ut
        assert ui==q(verified['january_identity']['unchanged_binary_upper_MWh']) and li==q(verified['january_identity']['best_lower_bound_MWh'])
        assert lt==q(verified[r['case']]['best_lower_bound_MWh']) and ut==q(verified[r['case']]['unchanged_binary_upper_MWh'])
        assert all(verified[c]['binary_upper_point_hash_and_energy_binding_pass'] for c in ('january_identity',r['case']))
        lo=ui-tau;hi=lt-tau;width=lt-ui
        assert q(s['band_left_included_MWh'])==lo and q(s['band_right_excluded_MWh'])==hi
        assert q(s['band_width_MWh'])==width==q(r['optimum_difference_MWh']['lower'])
        assert lo+tau==ui and hi+tau==lt and lo<hi
        assert q(s['order_blind_worst_case_absolute_error_lower_bound_MWh'])==width/2
        lowstr,highstr=s['safe_closed_decimal_subinterval_MWh'];low,high=F(lowstr),F(highstr)
        assert lo<=low<=high<hi and floor(low*10**6)==ceil(lo*10**6) and floor(high*10**6)==ceil(hi*10**6)-1
        assert lo<=F(float(lowstr))<=F(float(highstr))<hi
        first,last=s['first_integer_cap_MWh'],s['last_integer_cap_MWh']
        assert first==ceil(lo) and last==ceil(hi)-1 and s['integer_cap_count']==last-first+1
        assert lo<=first<=last<hi and first-1<lo and last+1>=hi and lo<=23195<hi
        for k in ('band_left_included_MWh','band_right_excluded_MWh','band_width_MWh','order_blind_worst_case_absolute_error_lower_bound_MWh'):
            x=q(s[k]);assert F(s[k]['floor6'])==F(floor(x*10**6),10**6) and F(s[k]['ceiling6'])==F(ceil(x*10**6),10**6)
        result.append(dict(case=r['case'],pass_all=True,exact_bound_and_upper_inheritance_match=True,closed_decimal_band=[lowstr,highstr],binary64_display_endpoints_also_inside=True,integer_cap_range=[first,last],integer_cap_count=last-first+1,half_gap_MWh=rat(width/2),original_cap_in_band=True))
    assert len(inputs)==len(saved['results'])==2 and [x['case'] for x in result]==['seed_26093100','seed_26093101']
    check()
    out=dict(status='INDEPENDENT_CAP_BAND_ARITHMETIC_PASS',optimizer_calls=0,full_matrix_or_point_replays=0,bindings=4,all_hashes_unchanged=True,manifest_sha256=sha(OUT/'input_manifest.json'),review_source_sha256=sha(Path(__file__)),arithmetic_results=result,scope='Derived consequences conditional on separately completed original-model lower-bound and binary-upper-point audits; no new empirical cases',elapsed_seconds=time.perf_counter()-started)
    with (OUT/'independent_arithmetic_review.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(out),flush=True)
if __name__=='__main__':main()
