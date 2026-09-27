"""Independent exact reporting/cap crosscheck after completed matrix replay."""
import csv,hashlib,json
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'results/research8h/fresh_january_energy';OUT=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rat=lambda x:Q(int(x['numerator']),int(x['denominator']))
summary=read(BASE/'summary.json');review=read(OUT/'postrun.json');brackets=read(BASE/'energy_brackets.json');caps=read(BASE/'new_cap_implication.json')
assert review['status']=='INDEPENDENT_FRESH_ENERGY_POSTRUN_PASS'
assert sha(BASE/'summary.json')=='3fc1739e997a0c5179c90a21a816dc55c5583758b9ce154986b884377bdab606'
assert sha(BASE/'READOUT.md')=='26e92e8e46369a2bf51e1deec4059df06ba17e3db979ae9e7474508120a3e31f'
assert sha(BASE/'summarize_postrun.py')==summary['reporting_source_sha256']
assert all(sha(BASE/p)==value for p,value in summary['artifact_sha256'].items())
old={x['case']:x['verdict'] for x in read(BASE/'parent_outcomes_context.json')['outcomes']};new=[]
with (BASE/'summary.csv').open(newline='',encoding='utf-8') as stream:csvrows=list(csv.DictReader(stream))
assert [x['case'] for x in caps]==[x['case'] for x in summary['rows']]==[x['case'] for x in brackets]==[x['case'] for x in csvrows]
for b,c,s,cr in zip(brackets,caps,summary['rows'],csvrows):
    case=b['case'];binding=read(BASE/case/'model_binding.json');B=Q(binding['removed_cap_MWh']);L=rat(b['lower_MWh']);exclusion=L>B+Q.from_float(1e-5)
    assert rat(c['expanded_cap_exact'])==B+Q.from_float(1e-5) and rat(c['lower_MWh'])==L and c['removed_cap_MWh']==B
    assert c['historical_capped_verdict']==old[case] and c['strict_lower_greater_than_expanded_cap']==exclusion
    assert c['new_exclusion_for_historically_UNKNOWN']==(old[case]=='UNKNOWN' and exclusion) and not c['historical_ledger_modified']
    assert s['historical_capped_verdict']==old[case] and s['exact_lower_excludes_old_expanded_cap']==exclusion and s['removed_cap_MWh']==B
    assert s['target_lower_MWh_floor']==b['lower_MWh']['outward_floor_6dp'] and s['target_upper_MWh_ceiling']==b['upper_MWh']['outward_ceiling_6dp']
    for field,bfield in [('optimum_difference_MWh','optimum_difference_MWh'),('optimal_relative_percent','optimal_relative_penalty_percent')]:
        interval='['+b[bfield]['lower']['outward_floor_6dp']+', '+b[bfield]['upper']['outward_ceiling_6dp']+']'
        assert s[field]==cr[field]==interval and interval in (BASE/'READOUT.md').read_text(encoding='utf-8')
    assert s['expanded_original_binary_witness_pass'] and s['native_no_cap_pass'] and not s['strict_nominal_witness_pass']
    assert L>rat(b['identity_reference_upper_MWh'])
    new.append(dict(case=case,historical_cap_verdict=old[case],old_cap_excluded_by_new_bound=exclusion,strictly_positive_optimum_difference=True))
assert [x['old_cap_excluded_by_new_bound'] for x in new]==[True,False,True,True]
assert all(not x['new_exclusion_for_historically_UNKNOWN'] for x in caps)
allocation=read(BASE/'allocation_audit.json')
for observed,saved in zip(review['clock_diagnostics'],allocation['calls']):
    assert (observed['case'],observed['kind'])==(saved['case'],saved['kind'])
    assert observed['observed_consistent']==saved['observed_start_consistent_with_recorded_admission']
    for rk,sk in [('decision_to_start_s','decision_to_actual_start_s'),('actual_UTC_remaining_s','actual_UTC_remaining_s'),('wall_adjusted_phase_estimate_s','estimated_phase_remaining_at_start_s')]:assert observed[rk]==saved[sk]
assert not allocation['observed_admission_start_discrepancies']
assert all(sha(ROOT/p)==x for p,x in review['input_and_result_hashes'].items())
report=dict(status='INDEPENDENT_FRESH_ENERGY_REPORTING_PASS',reviewer_optimizer_calls=0,summary_sha256=sha(BASE/'summary.json'),readout_sha256=sha(BASE/'READOUT.md'),reporting_source_sha256=sha(BASE/'summarize_postrun.py'),checks=new,unknown11_remains_unknown_under_old_cap=True,new_binary_uppers_are_uncapped=True,all_four_true_optimum_difference_intervals_strictly_positive=True,exact_optimality_claim=False,independent_source_sha256=sha(Path(__file__)))
with (OUT/'reporting.json').open('x',encoding='utf-8') as stream:json.dump(report,stream,indent=2);stream.write('\n')
print(json.dumps(report))
