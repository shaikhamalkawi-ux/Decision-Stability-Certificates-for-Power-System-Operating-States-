"""Independent solver-free eight-model fresh-week target archive gate."""
import csv,importlib.util,json,math,sys,time
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'results/research8h/fresh_january_weeks';OUT=BASE/'targets'
sp=importlib.util.spec_from_file_location('fresh_target_helpers',ROOT/'results/research8h/seasonal_cap_prepared_review.py');a=importlib.util.module_from_spec(sp);sys.modules[sp.name]=a;sp.loader.exec_module(a);v=a.reader
SOURCE='5d89038f53760d8dff1cc521b641636fbbec490ea4842d3d9a524568fcdd36a7';PROTOCOL='00cdcb9fde261660cc78e549e1bfd3426b81b1632ecf20e9f1ab86f23c0b39fd'
SCHEDULE={2:((26093210,26093211),26100210),3:((26093220,26093221),26100220)}
def bits(x,y):return len(x)==len(y) and all(p==q and (not isinstance(p,float) or p.hex()==q.hex()) for p,q in zip(x,y))
def key(x):return x['family'],int(x['hour_0based']),x['uid']
def jq(x):return Q(int(x['numerator']),int(x['denominator']))
def main():
    started=time.perf_counter();freeze=a.js(OUT/'prepared_freeze.json');assert not (OUT/'execution_started.json').exists()
    assert freeze['source_sha256']==SOURCE==v.sha(ROOT/'src/research8h_fresh_january_weeks.py') and freeze['protocol_sha256']==PROTOCOL==v.sha(ROOT/'docs/research8h/FRESH_JANUARY_WEEKS_PROTOCOL.md')
    assert freeze['optimizer_calls_started']==0 and freeze['stage']=='targets' and freeze['intended_ordinary_cases']==4 and freeze['intended_controls']==2
    manifest=v.manifest_check(OUT/'input_manifest.csv',expected=freeze['manifest_sha256'])
    assert freeze['cases']==[f'seed_{s}' for seeds,_ in SCHEDULE.values() for s in seeds]
    prepared=a.js(OUT/'prepared_cases.json');assert [x['case'] for x in prepared]==freeze['cases']
    scheduled=a.js(OUT/'scheduled_cases.json');assert [(x['week'],x['seed'],x['kind'],x['status']) for x in scheduled]==[(w,s,'ordinary' if s in seeds else 'control','SCHEDULED') for w,(seeds,c) in SCHEDULE.items() for s in (*seeds,c)]
    template=v.load_model(ROOT/'results/research8h/hour_of_day/january_identity');templabels=a.labels(ROOT/'results/research8h/hour_of_day/january_identity/row_metadata.csv.gz')
    records=[]
    for week,(seeds,control) in SCHEDULE.items():
        refdir=BASE/'references'/f'week_{week}';replay=a.js(ROOT/f'results/research8h/fresh_reference_postrun_review/week_{week}.json')
        assert replay['status']=='INDEPENDENT_EXPANDED_BINARY_REFERENCE_PASS'
        assert all(v.sha(ROOT/p)==sha for p,sha in replay['replayed_files_sha256'].items())
        refmodel=v.load_model(refdir);refnames=a.labels(refdir/'row_metadata.csv.gz');refmap={key(x):r for r,x in enumerate(refnames)};assert len(refmap)==refmodel.rows
        ref=a.array(refdir/'recovered_vector.npz','vector');mask=a.array(refdir/'integrality.npz','integrality')
        native=v.read_npz(refdir/'native_inputs.npz',('pmin','pmax','net','rows','nodal','source_hour'))
        cap=a.js(OUT/f'week_{week}_cap.json');energy=jq(replay['exact_fossil_MWh']);scaled=energy*Q(101,100);budget=-(-scaled.numerator//scaled.denominator)
        assert cap['budget_MWh']==budget and cap['reference_vector_sha256']==v.sha(refdir/'recovered_vector.npz')
        assert budget>energy and energy==sum((Q(ref[t*41+j]) for t in range(168) for j in range(23)),Q(0))
        for seed in (None,*seeds,control):
            case=f'week_{week}_identity' if seed is None else f'seed_{seed}';d=OUT/case;ordinary=seed in seeds;m=v.load_model(d);names=a.labels(d/'row_metadata.csv.gz');meta=a.js(d/'model_metadata.json')
            assert names==templabels and m.rows==34681 and m.cols==23016
            assert m.indices==template.indices and m.indptr==template.indptr and bits(m.data,template.data)
            assert a.array(d/'integrality.npz','integrality')==mask==(0,)*6888+(1,)*12096+(0,)*4032
            projection=a.projection_audit(m,mask,a.array(d/'projected_integrality.npz','integrality'),meta,names)
            assert all(x==0 for x in a.array(d/'objective.npz','objective'))
            assert meta['budget_MWh']==budget and meta['individual_mean_constraints']==0 and meta['unit_names'][:24]==meta['thermal_unit_names'] and meta['fossil_units']==meta['unit_names'][:23] and meta['unit_names'][23]=='121_NUCLEAR_1'
            inputs=v.read_npz(d/'native_inputs.npz',('pmin','pmax','net','rows','nodal','source_hour'));order=inputs['source_hour'].values
            assert sorted(order)==list(range(168)) and order[:48]==tuple(range(48)) and order[120:]==tuple(range(120,168)) and all(t%24==s%24 for t,s in enumerate(order))
            for field in ('pmin','pmax','net','rows','nodal'):
                before,after=native[field],inputs[field];width=math.prod(before.shape[1:]);assert before.dtype==after.dtype and before.shape==after.shape
                assert bits(after.values,tuple(x for t in order for x in before.values[t*width:(t+1)*width]))
            with (d/'permutation.csv').open(newline='') as f:perm=list(csv.DictReader(f))
            assert [int(x['source_hour_0based']) for x in perm]==list(order) and [int(x['native_row_0based']) for x in perm]==list(inputs['rows'].values)
            point=a.array(d/'constructive_vector.npz','vector');blocks=((0,41),(6888,24),(10920,24),(14952,24),(18984,24))
            for offset,width in (blocks[0],blocks[1],blocks[-1]):assert bits(point[offset:offset+168*width],tuple(x for t in order for x in ref[offset+t*width:offset+(t+1)*width]))
            for t in range(168):
                for j in range(24):
                    change=0 if t==0 else point[6888+t*24+j]-point[6888+(t-1)*24+j]
                    assert point[10920+t*24+j]==max(0,change) and point[14952+t*24+j]==max(0,-change)
            draw=a.js(d/'draw.json');assert draw['redraws']==0
            if seed is None:assert order==tuple(range(168))
            else:
                assert draw['seed']==seed and draw['generator']=='Generator(PCG64)'
                if ordinary:groups={(h,):[48+h,72+h,96+h] for h in range(24)}
                else:
                    groups={}
                    for t in range(48,120):groups.setdefault((t%24,*map(int,ref[6888+t*24:6888+(t+1)*24])),[]).append(t)
                    assert point[6888:10920]==ref[6888:10920]
                assert len(groups)==len(draw['groups'])
                for k,g in zip(sorted(groups),draw['groups']):assert g['key']==list(k) and g['destination']==groups[k] and g['source']==[order[t] for t in groups[k]] and sorted(g['source'])==groups[k]
                assert draw['identity_draw_retained']==(order==tuple(range(168)))
            local={'aggregate_balance','thermal_upper','thermal_lower','nodal_balance','branch_flow'};caps=[]
            for r,label in enumerate(names):
                family,hour,uid=key(label)
                if family=='fossil_energy_cap':
                    assert a.row(m,r)=={t*41+j:1. for t in range(168) for j in range(23)} and m.row_lower[r]==-math.inf and m.row_upper[r]==budget;caps.append(r);continue
                source=order[hour] if family in local else hour;old=refmap[(family,source,uid)];expected=a.row(refmodel,old)
                if family in local:
                    mapped={}
                    for j,value in expected.items():
                        offset,width=next((o,w) for o,w in blocks if o<=j<o+168*w);assert (j-offset)//width==source;mapped[j+(hour-source)*width]=value
                    expected=mapped
                assert a.row(m,r)==expected and m.row_lower[r]==refmodel.row_lower[old] and m.row_upper[r]==refmodel.row_upper[old]
            assert len(caps)==1
            for offset,width in blocks:
                for t,source in enumerate(order):
                    assert bits(m.lower[offset+t*width:offset+(t+1)*width],refmodel.lower[offset+source*width:offset+(source+1)*width]) and bits(m.upper[offset+t*width:offset+(t+1)*width],refmodel.upper[offset+source*width:offset+(source+1)*width])
            check=a.point_audit(m,point,mask,names);stored=a.js(d/'constructive_check.json')
            assert check['static_expanded_pass'] and stored['static_exact']['expanded_pass'] and stored['numerical']['static_network_cap_pass']
            assert check['full_expanded_pass']==stored['full_exact']['expanded_pass'] and check['full_strict_pass']==stored['full_exact']['strict_pass']
            if not ordinary:assert check['full_expanded_pass'] and stored['constructive_expanded_pass'] and stored['numerical']['physical']['pass']
            else:
                assert all(x['family'] in ('minimum_up','minimum_down') for x in check['failed_expanded_rows'])
                for f in ('matrix.npz','bounds.npz','integrality.npz','row_metadata.csv.gz'):assert v.sha(d/f)==v.sha(d/'lp'/f)
                assert not (d/'lp/solver.log').exists() and not (d/'mip').exists()
                item=next(x for x in prepared if x['case']==case);assert item['budget_MWh']==budget and item['constructive_expanded_pass']==stored['constructive_expanded_pass']
            assert energy==sum((Q(point[t*41+j]) for t in range(168) for j in range(23)),Q(0))
            preservation=a.js(d/'preservation.json');continuity=[t for t in range(167) if order[t+1]!=order[t]+1];pairs=[t for t in range(167) if (order[t],order[t+1])!=(t,t+1)]
            assert preservation['source_continuity_breaks_after_destination_hours']==continuity and preservation['literal_changed_adjacent_source_pairs_after_destination_hours']==pairs and preservation['changed_hours']==sum(t!=s for t,s in enumerate(order))
            records.append(dict(week=week,case=case,role='ordinary' if ordinary else 'identity' if seed is None else 'positive_control',budget_MWh=budget,exact_reference_fossil_MWh=v.rat(energy),changed_hours=preservation['changed_hours'],continuity_breaks=len(continuity),literal_changed_adjacent_pairs=len(pairs),projection=projection,point_check=check,model_and_native_package_mapping_exact=True,original_binary_coordinates=12096))
            print(json.dumps({'case':case,'static':check['static_expanded_pass'],'full':check['full_expanded_pass'],'budget':budget}),flush=True)
    assert not (OUT/'execution_started.json').exists();v.manifest_check(OUT/'input_manifest.csv',expected=freeze['manifest_sha256'])
    out=dict(status='INDEPENDENT_FRESH_TARGET_PREPARED_PASS',optimizer_calls=0,manifest_sha256=freeze['manifest_sha256'],frozen_bindings=manifest['entries_checked'],all_hashes_unchanged=True,execution_marker_absent=True,cases=records,review_source_sha256=v.sha(Path(__file__)),scope='Exact dyadic point checks and all mapped model coefficients/bounds plus native package transport; PCG64 source/group/order audited without reimplementing PRNG. Stored native physical reports pass for controls.',elapsed_seconds=time.perf_counter()-started)
    with (OUT/'independent_prepared_review.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'status':out['status'],'bindings':out['frozen_bindings'],'seconds':out['elapsed_seconds']}),flush=True)
if __name__=='__main__':main()
