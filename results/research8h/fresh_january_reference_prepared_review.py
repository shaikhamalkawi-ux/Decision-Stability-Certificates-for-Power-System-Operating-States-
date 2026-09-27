"""Independent solver-free fresh-week reference archive/native-table review."""
import csv,datetime,importlib.util,json,math,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/research8h/fresh_january_weeks/references'
sp=importlib.util.spec_from_file_location('fresh_review_helpers',ROOT/'results/research8h/seasonal_cap_prepared_review.py');a=importlib.util.module_from_spec(sp);sys.modules[sp.name]=a;sp.loader.exec_module(a);v=a.reader
SRC='5d89038f53760d8dff1cc521b641636fbbec490ea4842d3d9a524568fcdd36a7';PRO='00cdcb9fde261660cc78e549e1bfd3426b81b1632ecf20e9f1ab86f23c0b39fd'
def csvread(p,limit=None):
    out=[]
    with p.open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f):
            out.append(r)
            if limit and len(out)>=limit:break
    return out

def main():
    started=time.perf_counter();freeze=a.js(OUT/'prepared_freeze.json')
    assert freeze['source_sha256']==SRC==v.sha(ROOT/'src/research8h_fresh_january_weeks.py')
    assert freeze['protocol_sha256']==PRO==v.sha(ROOT/'docs/research8h/FRESH_JANUARY_WEEKS_PROTOCOL.md')
    assert freeze['stage']=='references' and freeze['cases']==['week_2','week_3'] and freeze['optimizer_calls_started']==0
    assert freeze['seconds_per_case']==600 and freeze['phase_seconds']==1800 and freeze['start_guard_seconds']==605
    assert not (OUT/'execution_started.json').exists()
    check=v.manifest_check(OUT/'input_manifest.csv',expected=freeze['manifest_sha256'])
    frozen=csvread(OUT/'input_manifest.csv');paths={str(Path(x['path']).resolve()) for x in frozen}
    baseline=ROOT/'results/research8h/seasonal_reference/month_01';bm=v.load_model(baseline);bnames=a.labels(baseline/'row_metadata.csv.gz');bmeta=a.js(baseline/'model_metadata.json')
    assert (bm.rows,bm.cols)==(34680,23016)
    basehash={f:v.sha(baseline/f) for f in ('matrix.npz','bounds.npz','integrality.npz','objective.npz','row_metadata.csv.gz','model_metadata.json')}
    raw=Path(freeze['source_v3'])/'raw/RTS-GMLC_v0.2.3'
    buses=[x for x in csvread(raw/'bus.csv') if int(x['Area'])==1];busids=[int(x['Bus ID']) for x in buses]
    gens=[x for x in csvread(raw/'gen.csv') if int(x['Bus ID']) in busids]
    dec=[x for x in gens if float(x['PMax MW'])>0 and x['Category']!='Solar RTPV']
    therm=[i for i,x in enumerate(dec) if float(x['PMin MW'])>0 and x['Category'] not in ('Hydro','Solar PV','Wind')]
    fossil=[i for i in therm if dec[i]['Fuel'] in ('Coal','Oil','NG')];hydro=[i for i,x in enumerate(dec) if x['Category']=='Hydro']
    assert len(dec)==41 and len(therm)==24 and len(fossil)==23 and len(busids)==24
    assert [dec[i]['GEN UID'] for i in therm if i not in fossil]==['121_NUCLEAR_1']
    assert all(float(dec[i]['Ramp Rate MW/Min'])*60>=float(dec[i]['PMax MW'])-float(dec[i]['PMin MW']) for i in therm)
    sub=raw/'timeseries_data_files';tablefiles={'load':sub/'Load/DAY_AHEAD_regional_Load.csv','pv':sub/'PV/DAY_AHEAD_pv.csv','wind':sub/'WIND/DAY_AHEAD_wind.csv','hydro':sub/'Hydro/DAY_AHEAD_hydro.csv','rtpv':sub/'RTPV/DAY_AHEAD_rtpv.csv'}
    tables={k:csvread(p,504) for k,p in tablefiles.items()}
    total_load=sum(float(x['MW Load']) for x in buses);props=[float(x['MW Load'])/total_load for x in buses]
    assert all(str(p.resolve()) in paths for p in [*tablefiles.values(),raw/'bus.csv',raw/'gen.csv'])
    records=[]
    for week,start in ((2,168),(3,336)):
        d=OUT/f'week_{week}';m=v.load_model(d);meta=a.js(d/'model_metadata.json');labels=a.labels(d/'row_metadata.csv.gz')
        assert (m.rows,m.cols,m.data,m.indices,m.indptr)==(bm.rows,bm.cols,bm.data,bm.indices,bm.indptr)
        assert labels==bnames
        assert meta['unit_names']==[x['GEN UID'] for x in dec] and meta['thermal_unit_names']==[dec[i]['GEN UID'] for i in therm]
        assert meta['bus_ids']==busids and meta['fossil_units']==[dec[i]['GEN UID'] for i in fossil]
        assert meta['individual_mean_constraints']==0 and meta['energy_cap_constraints']==0
        assert not any('mean' in x['family'] or x['family']=='fossil_energy_cap' for x in labels)
        native=v.read_npz(d/'native_inputs.npz',('pmin','pmax','net','rows','source_hour','nodal'))
        assert native['pmin'].shape==native['pmax'].shape==(168,41) and native['nodal'].shape==(168,24)
        assert native['rows'].values==tuple(range(start,start+168)) and native['source_hour'].values==tuple(range(168))
        mask=a.array(d/'integrality.npz','integrality');projected=a.array(d/'projected_integrality.npz','integrality')
        projection=a.projection_audit(m,mask,projected,meta,labels)
        obj=a.array(d/'objective.npz','objective')
        assert obj==tuple(float(j<6888 and j%41 in fossil) for j in range(23016))
        assert m.lower[6888:]==bm.lower[6888:] and m.upper[6888:]==bm.upper[6888:]
        assert m.upper[:6888]==native['pmax'].values
        assert m.lower[:6888]==tuple(native['pmin'].values[j] if j%41 in hydro else 0. for j in range(6888))
        for r,x in enumerate(labels):
            family=x['family'];hour=int(x['hour_0based'])
            if family=='aggregate_balance':assert m.row_lower[r]==m.row_upper[r]==native['net'].values[hour]
            elif family=='nodal_balance':assert m.row_lower[r]==m.row_upper[r]==native['nodal'].values[hour*24+busids.index(int(x['uid']))]
            else:assert (m.row_lower[r],m.row_upper[r])==(bm.row_lower[r],bm.row_upper[r])
        sourcehours=csvread(d/'source_hours.csv');assert len(sourcehours)==168
        errors=dict(pmin=0.,pmax=0.,net=0.,nodal=0.)
        for t,index in enumerate(range(start,start+168)):
            stamp=datetime.datetime(2020,1,1)+datetime.timedelta(hours=index);cal=(stamp.year,stamp.month,stamp.day,stamp.hour+1)
            assert int(sourcehours[t]['local_hour_0based'])==t and int(sourcehours[t]['native_row_0based'])==index and datetime.datetime.fromisoformat(sourcehours[t]['timestamp'])==stamp
            for tb in tables.values():assert tuple(int(tb[index][f]) for f in ('Year','Month','Day','Period'))==cal
            rtpv=[0.]*24
            for g in gens:
                if g['Category']=='Solar RTPV':rtpv[busids.index(int(g['Bus ID']))]+=float(tables['rtpv'][index][g['GEN UID']])
            load=float(tables['load'][index]['1']);net=load-sum(rtpv)
            errors['net']=max(errors['net'],abs(net-native['net'].values[t]))
            for q,p in enumerate(props):errors['nodal']=max(errors['nodal'],abs(p*load-rtpv[q]-native['nodal'].values[t*24+q]))
            for j,g in enumerate(dec):
                lo,hi=float(g['PMin MW']),float(g['PMax MW']);cat=g['Category'];uid=g['GEN UID']
                if cat in ('Solar PV','Wind'):
                    lo=0.;hi=float(tables['pv' if cat=='Solar PV' else 'wind'][index][uid])
                elif cat=='Hydro':lo=hi=float(tables['hydro'][index][uid])
                errors['pmin']=max(errors['pmin'],abs(lo-native['pmin'].values[t*41+j]))
                errors['pmax']=max(errors['pmax'],abs(hi-native['pmax'].values[t*41+j]))
        assert max(errors.values())<=1e-9
        for f in ('matrix.npz','bounds.npz','integrality.npz','projected_integrality.npz','objective.npz','row_metadata.csv.gz','model_metadata.json','native_inputs.npz','source_hours.csv'):
            assert str((d/f).resolve()) in paths
        assert not (d/'result.json').exists() and not (d/'solver.log').exists()
        record=dict(week=week,native_rows=[start,start+167],matrix_exactly_matches_established_reference_template=True,all_hourly_and_static_bounds_exactly_checked=True,original_binary_mask=12096,U_only_mask=4032,objective_native_fossil_coordinates=3864,calendar_tables_checked=5,native_CSV_adapter_max_abs_differences_MW=errors,native_parser_scope='Independent stdlib decimal parsing and sequential summation; comparison within 1e-9 handles parser/reduction rounding. Archived matrix/bounds comparisons above are exact binary64 equality.',projection=projection)
        records.append(record);print(json.dumps(record),flush=True)
    assert not (OUT/'execution_started.json').exists()
    v.manifest_check(OUT/'input_manifest.csv',expected=freeze['manifest_sha256'])
    assert all(v.sha(baseline/f)==h for f,h in basehash.items())
    out=dict(status='INDEPENDENT_FRESH_REFERENCE_PREPARED_PASS',optimizer_calls=0,execution_marker_absent=True,frozen_bindings=check['entries_checked'],manifest_sha256=freeze['manifest_sha256'],all_hashes_unchanged=True,cases=records,baseline_template_hashes=basehash,review_source_sha256=v.sha(Path(__file__)),reader_sha256=v.sha(ROOT/'src/research8h_standalone_verify.py'),helper_sha256=v.sha(ROOT/'results/research8h/seasonal_cap_prepared_review.py'),elapsed_seconds=time.perf_counter()-started)
    with (OUT/'independent_prepared_review.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'status':out['status'],'seconds':out['elapsed_seconds']}),flush=True)
if __name__=='__main__':main()
