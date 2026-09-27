"""Prospective independent mathematical replay of one CLOSED refinement batch.

No solver/backend/producer arithmetic imports. --self-test uses invented objects only.
Scientific execution requires separately supplied closed-output hashes and parent GO.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter, defaultdict
from datetime import datetime, timezone
import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
import math
import struct
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
ARM = ROOT/'results/research_next/common_refinement_batch'
PRE = ARM/'prepared'
RUN = ARM/'run01'
OUT = ROOT/'results/research_next/common_refinement_math_review'
FREEZE = '7642265df13848db01ad0627381c6e294ddea30569a5dbc2b344e2e952372b85'
MANIFEST = '34311c0d425e453a24781079a007eef2369bb8cbf2e3e75eab13f523498916ef'
PRODUCER = 'f7f79ecca154169832c8739d9c17889c5c5993aa460f6d528d6f115c60018371'
PROTOCOL = 'bc47f198b8a6f711c80ce315418749ef4b1b2b9b1afea38568901bd8e2fd6e0d'
KERNEL = '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
NATIVE_REVIEW = '090aba46d707e01c21cc4713073c41b718d98ca9d2bb3192674e274508f21e98'
NB, START, STOP, NC = 12096, 6888, 18984, 12432
TAU = F.from_float(1e-5)
WEIGHT = F(6004799503160661,144115188075855872)
THERMAL = ('101_CT_1','101_CT_2','101_STEAM_3','101_STEAM_4','102_CT_1','102_CT_2',
 '102_STEAM_3','102_STEAM_4','113_CT_1','113_CT_2','113_CT_3','113_CT_4','115_STEAM_1',
 '115_STEAM_3','116_STEAM_1','118_CC_1','123_STEAM_2','123_STEAM_3','123_CT_1','123_CT_4','123_CT_5')

def need(ok, label):
    if not ok: raise ValueError(label)

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def gz(path):
    with gzip.open(path, 'rt', encoding='utf-8') as stream: return json.load(stream)

def rat(x): return [str(x.numerator),str(x.denominator)]

def frac(value):
    need(type(value) is list and len(value)==2 and all(type(x) is str for x in value),'Rational schema')
    q=F(int(value[0]),int(value[1])); need(rat(q)==value,'Canonical rational'); return q

def scalar(value): return None if value is None else frac(value['exact'])

def save(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value,stream,indent=2,allow_nan=False); stream.write('\n')

def captured_module(path, digest, name):
    source=Path(path).read_bytes(); need(hashlib.sha256(source).hexdigest()==digest,'Reviewed source bytes')
    spec=importlib.util.spec_from_file_location(name,path); module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module; exec(compile(source,str(path),'exec'),module.__dict__); return module

def bind(entry):
    data=Path(entry['path']).read_bytes()
    need(len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256'],'Unchanged binding '+entry['path'])

def check_bindings(entries):
    need(len({str(Path(e['path']).resolve()).casefold() for e in entries})==len(entries),'Unique bindings')
    for entry in entries: bind(entry)

def values(v,path,name,length,members=None,dtype=('<f8',)):
    data=v.read_npz(path,(name,) if members is None else members)
    return tuple(v.vector(data[name],dtype,length,name))

def mask(v,folder,n): return values(v,folder/'integrality.npz','integrality',n,dtype=('|u1',))

def state_digest(bits):
    need(len(bits)==NB and all(type(x) is int and x in (0,1) for x in bits),'Full exact binary state')
    return hashlib.sha256(bytes(bits)).hexdigest()

def exact_cut(m,flags,control,weights,tau=TAU):
    """Independent signed-original-row proof; no imported certificate arithmetic."""
    need(len(flags)==m.cols and len(control)==m.cols,'Complete cut coordinate vectors')
    need(all(type(b) is int and b in (0,1) for b in flags),'Full mask values')
    accum=defaultdict(F); beta=F(); norm=F(); endpoints=[]
    for row,weight in sorted(weights.items()):
        need(type(row) is int and 0<=row<m.rows and weight!=0,'Nonzero unique row support')
        lo,hi=m.row_lower[row],m.row_upper[row]; need(lo<=hi,'Ordered row interval')
        value=lo if weight>0 else hi; need(math.isfinite(value),'Available signed endpoint')
        beta+=weight*F(value); norm+=abs(weight)
        endpoints.append(dict(row=row,side='lower' if weight>0 else 'upper',endpoint_hex=value.hex()))
        for k in range(m.indptr[row],m.indptr[row+1]): accum[m.indices[k]]+=weight*F(m.data[k])
    q={j:a for j,a in accum.items() if a}; support=F(); cn=F(); cv=F(); support_ends=[]
    for j,a in sorted(q.items()):
        need(0<=j<m.cols,'Residual coordinate')
        if flags[j]: cv+=a*F(control[j])
        else:
            value=m.upper[j] if a>0 else m.lower[j]; need(math.isfinite(value),'Finite support box')
            support+=a*F(value); cn+=abs(a)
            support_ends.append(dict(column=j,side='upper' if a>0 else 'lower',endpoint_hex=value.hex()))
    loss=tau*(norm+cn); rhs=beta-support-loss
    return dict(q=q,d=weights,beta=beta,original_row_norm=norm,continuous_support=support,
      continuous_q_norm=cn,tau_loss=loss,cut_rhs=rhs,control_state_value=cv,
      selected_original_endpoints=endpoints,continuous_support_endpoints=support_ends)

def expected_template_maps():
    origins=read(PRE/'joint/row_origins.json')['origins']
    inverse={tuple(item):j for j,item in enumerate(origins)}; need(len(inverse)==len(origins),'Joint row-origin bijection')
    cases=[]
    for wi,world in enumerate(('identity','days_321')):
        with gzip.open(PRE/world/'row_metadata.csv.gz','rt',encoding='utf-8-sig',newline='') as stream: rows=list(csv.DictReader(stream))
        index=defaultdict(list)
        for row,entry in enumerate(rows):
            need(int(entry['row'])==row,'Metadata row order')
            index[(entry['family'],int(entry['hour_0based']),entry['uid'])].append(row)
        for hour in range(168):
            selection=[('aggregate_balance','ALL',1,'lower')]+[('thermal_upper',name,-1,'upper') for name in THERMAL]+[('nodal_balance','107',-1,'upper'),('branch_flow','10',-1,'upper')]
            selected=[]
            for family,uid,sign,side in selection:
                original=index[(family,hour,uid)]; need(len(original)==1,'Unique frozen template key')
                row=original[0]; need((wi,row) in inverse,'Original joint row mapping')
                selected.append(dict(family=family,uid=uid,side=side,sign=sign,original_row=row,joint_row=inverse[(wi,row)]))
            cases.append(dict(world=world,world_index=wi,hour=hour,rows=selected))
    symbolic=read(PRE/'symbolic_seed_maps.json')
    need(symbolic['cases']==cases and frac(symbolic['common_weight'])==WEIGHT,'Complete fixed symbolic maps')
    need(len(cases)==336,'Fixed seed family'); return cases

def compare_seed(proof,calculation,case,m,flags):
    need(proof['case']==case,'Saved seed identity')
    for key,value in [('original_rows',m.rows),('original_columns',m.cols),('full_state_dimension',sum(flags))]: need(proof[key]==value,'Seed dimensions')
    need(proof['omitted_coordinates_exact_zero'] is True and proof['all_selected_row_terms_used'] is True,'Sparse zero semantics')
    need(proof['original_d']==[[r,rat(a)] for r,a in sorted(calculation['d'].items())],'Every seed signed multiplier')
    need(proof['full_q_nonzero']==[[j,rat(a)] for j,a in sorted(calculation['q'].items())],'Every seed residual including exact-zero omission')
    need(proof['state_terms']==[[j,rat(a)] for j,a in sorted(calculation['q'].items()) if flags[j]],'Seed state partition')
    for key in ('beta','original_row_norm','continuous_support','continuous_q_norm','tau_loss','cut_rhs','control_state_value'):
        need(frac(proof[key])==calculation[key],'Seed exact '+key)
    for key in ('selected_original_endpoints','continuous_support_endpoints'): need(proof[key]==calculation[key],'Seed endpoint map '+key)
    holds=calculation['control_state_value']>=calculation['cut_rhs']
    need(proof['control_satisfied'] is holds and holds,'Old exact control consistency')
    need(proof['extra_binary_tau']==proof['derived_extra_tau']==0,'No extra derived tolerance')

def anchor_match(calc,m,old):
    anchor=gz(PRE/'anchor_certificate.json.gz')
    need(len(anchor['original_d'])==m.rows and len(anchor['full_A_transpose_d'])==m.cols,'Anchor complete dimensions')
    need(all(frac(a)==calc['d'].get(r,F()) for r,a in enumerate(anchor['original_d'])),'Anchor full multipliers')
    need(all(frac(a)==calc['q'].get(j,F()) for j,a in enumerate(anchor['full_A_transpose_d'])),'Anchor full residuals')
    for key in ('beta','original_row_norm','continuous_support','continuous_q_norm','tau_loss','cut_rhs','control_state_value'):
        need(frac(anchor[key])==calc[key],'Anchor exact '+key)
    lhs=sum((a*old[j-START] for j,a in calc['q'].items() if START<=j<STOP),F())
    need(frac(anchor['nominee_state_value'])==lhs and frac(anchor['expanded_margin'])==calc['cut_rhs']-lhs>0,'Anchor original nominee exclusion')

def project_duals(m,endpoint_map,raw):
    need(len(endpoint_map)==len(raw) and all(math.isfinite(x) for x in raw),'Complete finite raw dual')
    lo=defaultdict(F); hi=defaultdict(F); projected=[]; seen=set(); beta_raw=F()
    for k,(entry,value) in enumerate(zip(endpoint_map,raw)):
        r=entry['original_row']; side=entry['side']
        need(type(r) is int and 0<=r<m.rows and side in ('lower','upper') and (r,side) not in seen,'Endpoint identity')
        seen.add((r,side)); endpoint=m.row_lower[r] if side=='lower' else m.row_upper[r]
        need(math.isfinite(endpoint),'Finite mapped endpoint'); a=max(F(value) if side=='lower' else -F(value),F())
        if side=='lower':lo[r]=a; beta_raw+=a*F(endpoint)
        else:hi[r]=a; beta_raw-=a*F(endpoint)
        projected.append(dict(phase_row=k,original_row=r,side=side,raw_hex=value.hex(),nonnegative_multiplier=rat(a)))
    need(seen=={(r,s) for r in range(m.rows) for s,e in (('lower',m.row_lower[r]),('upper',m.row_upper[r])) if math.isfinite(e)},'All finite endpoint sides')
    d={r:lo[r]-hi[r] for r in range(m.rows) if lo[r]!=hi[r]}; gain=F(); cancellation=F()
    for r in set(lo)|set(hi):
        overlap=min(lo[r],hi[r])
        if overlap:gain+=overlap*(F(m.row_upper[r])-F(m.row_lower[r])); cancellation+=2*overlap
    return d,projected,dict(beta_raw=beta_raw,canonical_interval_gain=gain,
      unmerged_multiplier_norm=sum(lo.values(),F())+sum(hi.values(),F()),norm_cancellation=cancellation,
      expanded_canonical_gain=gain+TAU*cancellation)

def phase_review(v,folder,m,flags,control,origin):
    certificate=gz(folder/'full_exact_candidate.json.gz')
    endpoint_map=gz(PRE/'endpoint_map.json.gz')
    raw=values(v,folder/'raw_solution.npz','row_dual',len(endpoint_map),('vector','row_value','row_dual','col_dual'))
    d,projection,cancellation=project_duals(m,endpoint_map,raw)
    c=exact_cut(m,flags,control,d)
    need(certificate['raw_endpoint_projection']==projection,'Every raw dual sign projection')
    need(len(certificate['original_d'])==m.rows and all(frac(a)==d.get(r,F()) for r,a in enumerate(certificate['original_d'])),'Phase complete original multiplier vector')
    need(len(certificate['full_A_transpose_d'])==m.cols and all(frac(a)==c['q'].get(j,F()) for j,a in enumerate(certificate['full_A_transpose_d'])),'Phase complete residual vector')
    for key in ('beta','original_row_norm','continuous_support','continuous_q_norm','tau_loss','cut_rhs','control_state_value'):
        need(frac(certificate[key])==c[key],'Phase exact '+key)
    for key,value in cancellation.items():need(frac(certificate[key])==value,'Endpoint cancellation '+key)
    need(c['beta']-cancellation['beta_raw']==cancellation['canonical_interval_gain']>=0,'Canonical endpoint gain')
    need(cancellation['unmerged_multiplier_norm']-c['original_row_norm']==cancellation['norm_cancellation']>=0,'Canonical norm gain')
    need(certificate['selected_original_endpoints']==c['selected_original_endpoints'],'Phase signed endpoint selection')
    expected=[]
    for j,b in enumerate(flags):
        if not b:
            a=c['q'].get(j,F()); e=m.upper[j] if a>=0 else m.lower[j]
            expected.append(dict(column=j,endpoint_side='upper' if a>=0 else 'lower',endpoint_hex=e.hex()))
    need(certificate['continuous_support_endpoints']==expected,'Every continuous box support endpoint including zeros')
    lhs=sum((a*origin[j-START] for j,a in c['q'].items() if flags[j]),F()); gap=c['cut_rhs']-lhs
    need(frac(certificate['nominee_state_value'])==lhs and frac(certificate['expanded_margin'])==gap,'Original nominated margin')
    need(certificate['strictly_positive_expanded_margin'] is (gap>0),'Phase separation flag')
    need(certificate['status']==('VERIFIED_GLOBAL_NECESSARY_CUT_REJECTS_NOMINEE' if gap>0 else 'VALID_NONSEPARATING_CANDIDATE'),'Phase scoped status')
    need(certificate['control_satisfied'] is True and c['control_state_value']>=c['cut_rhs'],'Exact original control consistency')
    need(certificate['extra_binary_tau']==certificate['derived_row_extra_tau']==0 and certificate['old_full_point_replayed'] is False,'Phase tolerance/replay scope')
    need(certificate['all_original_coefficients_retained'] is True and certificate['alternative_multiplier_candidates']==0,'Single complete candidate')
    need(certificate['row_support']==len(d) and certificate['state_support']==sum(flags[j] for j in c['q']) and certificate['continuous_support_count']==sum(not flags[j] for j in c['q']),'Exact support counts')
    compact=gz(folder/'cut.json.gz')
    need(compact['state_terms']==[[j,rat(a)] for j,a in sorted(c['q'].items()) if flags[j]] and frac(compact['cut_rhs'])==c['cut_rhs'],'Compact cut matches full proof')
    need(compact['original_rows']==m.rows and compact['original_columns']==m.cols and compact['full_state_dimension']==NB and compact['omitted_coordinates_exact_zero'] is True,'Compact full dimensions')
    bind(compact['full_proof']); need(Path(compact['full_proof']['path']).resolve()==(folder/'full_exact_candidate.json.gz').resolve(),'Compact full-proof path')
    return c,dict(strictly_excludes_origin=gap>0,exact_margin=rat(gap),row_support=len(d),state_support=certificate['state_support'])

def exact_master(model,point):
    need(len(point)==len(model['boxes']),'Complete master point')
    issues=[]
    for j,(x,box) in enumerate(zip(point,model['boxes'])):
        if not scalar(box['lower'])<=x<=scalar(box['upper']) or (box['kind']=='B' and x not in (0,1)):issues.append(dict(column=j))
    for r,row in enumerate(model['rows']):
        lhs=sum((scalar(a)*point[j] for j,a in row['terms']),F()); lo=scalar(row['lower']); hi=scalar(row['upper'])
        if (lo is not None and lhs<lo) or (hi is not None and lhs>hi):issues.append(dict(row=r,family=row['family']))
    return issues

def recover_nomination(raw,model,premises):
    if len(raw)!=NC or not all(math.isfinite(x) for x in raw):return dict(accepted=False,reason='invalid_raw_shape_or_nonfinite'),None
    bits=[]
    for number in raw[:NB]:
        options=[b for b in (0,1) if abs(F(number)-b)<=TAU]
        if len(options)!=1:return dict(accepted=False,reason='nonintegral_state'),None
        bits.append(options[0])
    auxiliary=[]
    need(len(premises['worlds'])==2,'Two premise worlds')
    for world in premises['worlds']:
        fi=world['fossil_indices']; ni=world['nuclear_index']
        need(len(fi)==len(set(fi))==23 and ni not in fi and set(fi)|{ni}==set(range(24)),'Frozen fossil/nuclear roster')
        need(len(world['hours'])==168,'Full native week')
        for t,h in enumerate(world['hours']):
            a=list(map(frac,h['a'])); b=list(map(frac,h['b'])); u=bits[24*t:24*t+24]
            need(len(a)==len(b)==24,'Capacity roster')
            auxiliary.append(max(frac(h['box_lower']),frac(h['rho'])-b[ni]*u[ni],sum((a[j]*u[j] for j in fi),F())-23*TAU))
    point=list(map(F,bits))+auxiliary; issues=exact_master(model,point)
    return dict(accepted=not issues,issues=issues,original_shared_state_values=bits,auxiliary_exact=list(map(rat,auxiliary)),
      auxiliary_rule='deterministic componentwise minimum, not physical redispatch',no_extra_tau=True),bits if not issues else None

def appended_master(model,base,cuts):
    need({k:v for k,v in model.items() if k!='rows'}=={k:v for k,v in base.items() if k!='rows'},'Unchanged base master metadata and boxes')
    need(model['rows'][:len(base['rows'])]==base['rows'] and len(model['rows'])==len(base['rows'])+len(cuts),'Base rows and full appended denominator')
    for row,(proofpath,calculation,kind) in zip(model['rows'][len(base['rows']):],cuts):
        provenance=row['provenance']; bind(provenance['proof']); bind(provenance['encoding'])
        need(Path(provenance['proof']['path']).resolve()==proofpath.resolve(),'Appended chronological cut provenance')
        encoding=gz(provenance['encoding']['path']); scale=frac(encoding['scale']); need(scale>0,'Positive row scale')
        terms=[(j-START,a/scale) for j,a in sorted(calculation['q'].items()) if START<=j<STOP]
        actual=[(j,scalar(a)) for j,a in row['terms']]
        need(actual==terms and scalar(row['lower'])==calculation['cut_rhs']/scale and row['upper'] is None,'Every exact appended master coefficient and endpoint')
        need(row['family']==('network_seed' if kind=='seed' else 'new_phase1_cut'),'Appended family')
        need(provenance['exact_scaled_original_row'] is True and provenance['no_extra_tau'] is True,'Exact new-row scope')

def exact_point(m,flags,raw,tau=TAU):
    need(len(raw)==m.cols and len(flags)==m.cols and all(math.isfinite(x) for x in raw),'Finite complete point')
    x=list(map(F,raw)); binary=all(not flag or x[j] in (0,1) for j,flag in enumerate(flags))
    col=F(); row=F(); badcols=badrows=0
    for j,value in enumerate(x):
        gap=max(F(m.lower[j])-value,value-F(m.upper[j]),F()); col=max(col,gap); badcols+=gap>tau
    for r in range(m.rows):
        lhs=sum((F(m.data[k])*x[m.indices[k]] for k in range(m.indptr[r],m.indptr[r+1])),F())
        for bound,lower in ((m.row_lower[r],True),(m.row_upper[r],False)):
            if math.isfinite(bound):
                gap=max(F(bound)-lhs if lower else lhs-F(bound),F()); row=max(row,gap); badrows+=gap>tau
    return dict(expanded_pass=binary and not badcols and not badrows,strict_pass=binary and col==row==0,
      original_binary_coordinates_exact=binary,maximum_column_violation=rat(col),maximum_row_violation=rat(row),
      expanded_violated_column_count=badcols,expanded_violated_row_side_count=badrows,rows=m.rows,columns=m.cols,binary_coordinates=sum(flags))

def packed(seq): return b''.join(struct.pack('<d',x) for x in seq)

def positive_review(v,folder,m,flags,origin,native_module):
    raw=values(v,folder/'raw_solution.npz','vector',m.cols)
    candidate=values(v,folder/'candidate_vector.npz','vector',m.cols)
    need(all(math.isfinite(x) for x in raw),'Complete finite recourse raw values')
    for j,b in enumerate(flags):
        if b:need(candidate[j]==origin[j-START] and abs(F(raw[j])-origin[j-START])<=TAU,'Only prescribed near states restored')
    need(packed([x for j,x in enumerate(candidate) if not flags[j]])==packed([x for j,x in enumerate(raw) if not flags[j]]),'Every continuous raw byte unchanged')
    joint=exact_point(m,flags,candidate); saved=read(folder/'exact_candidate_checks.json')
    need(joint['expanded_pass']==saved['joint']['expanded_pass'] and joint['strict_pass']==saved['joint']['strict_pass'],'Joint new-point agreement')
    maps=read(PRE/'joint/column_maps.json'); need(maps['worlds']==['identity','days_321'],'Original world map')
    worlds=[]; shared=[]
    for wi,world in enumerate(maps['worlds']):
        directory=PRE/world; wm=v.load_model(directory); wb=mask(v,directory,wm.cols)
        mapping=maps['original_to_joint'][wi];need(len(mapping)==wm.cols and len(set(mapping))==wm.cols,'Full world coordinate injection')
        point=[candidate[j] for j in mapping]
        stored=values(v,folder/(world+'_vector.npz'),'vector',wm.cols);need(packed(point)==packed(stored),'Saved world point is exact projection')
        check=exact_point(wm,wb,point); direct=native_module.native(v,point,directory)
        old=saved['worlds'][wi];need(old['world']==world and old['original']['expanded_pass']==check['expanded_pass'],'Original-world new-point admission')
        need(old['native']['expanded_pass']==direct['expanded_pass'] and old['native']['violations']==direct['violations'],'Independent native verdict/count')
        for key in ('maximum_violation','exact_fossil_energy'):
            a,b=old['native'][key],direct[key];need(F(int(a['numerator']),int(a['denominator']))==F(int(b['numerator']),int(b['denominator'])),'Independent native exact '+key)
        states=[int(point[j]) for j,b in enumerate(wb) if b];need(len(states)==NB and states==origin,'Every shared original bit')
        shared.append(states);worlds.append(dict(world=world,matrix=check,native=direct))
    accepted=joint['expanded_pass'] and all(w['matrix']['expanded_pass'] and w['native']['expanded_pass'] for w in worlds)
    need(saved['accepted'] is accepted and saved['common_all12096_bits'] is True,'Full combined positive scope')
    return dict(accepted=accepted,joint=joint,worlds=worlds,continuous_bytes_unchanged=True,all_common_bits=NB)

def main_review(args):
    started=time.perf_counter(); need(args.expected_freeze_sha256==FREEZE,'Externally supplied original freeze')
    report_dir=OUT/'review01';need(not report_dir.exists(),'One separately authorized independent execution')
    need(sha(__file__)==args.expected_reviewer_sha256,'Reviewed checker source')
    need(sha(PRE/'prepared_freeze.json')==FREEZE and sha(PRE/'input_manifest.json')==MANIFEST,'Original freeze/manifest unchanged')
    freeze=read(PRE/'prepared_freeze.json');need(freeze['source_sha256']==PRODUCER and freeze['protocol_sha256']==PROTOCOL and freeze['manifest_sha256']==MANIFEST,'Frozen scientific source identity')
    need(sha(ROOT/'src/researchnext_common_refinement_batch.py')==PRODUCER and sha(ROOT/'docs/research_next/COMMON_REFINEMENT_BATCH_PROTOCOL.md')==PROTOCOL,'Frozen source/protocol bytes')
    inputs=read(PRE/'input_manifest.json')['files'];need(len(inputs)==355,'Complete original input denominator');check_bindings(inputs)
    inventory_path=ARM/'producer_output_inventory.csv'
    need(sha(RUN/'completion.json')==args.expected_completion_sha256 and sha(inventory_path)==args.expected_inventory_sha256,'Externally supplied producer closure')
    with inventory_path.open(encoding='utf-8-sig',newline='') as stream: public_rows=list(csv.DictReader(stream))
    public=[]
    for entry in public_rows:
        path=(ROOT/entry['path']).resolve();need(path.is_relative_to(ARM.resolve()),'Public inventory confined to arm')
        public.append(dict(path=str(path),bytes=int(entry['bytes']),sha256=entry['sha256']))
    need(len(public)==688,'Stable closed public payload denominator');check_bindings(public)
    outputs=read(RUN/'producer_files.json')['files'];check_bindings(outputs)
    need(all(Path(e['path']).resolve().is_relative_to(RUN.resolve()) for e in outputs),'Confined producer artifacts')
    snapshot={p.resolve():sha(p) for p in RUN.rglob('*') if p.is_file()}
    need(set(snapshot)=={Path(e['path']).resolve() for e in outputs}|{(RUN/'producer_files.json').resolve()},'Complete closed run-file inventory')
    need(set(snapshot)=={Path(e['path']).resolve() for e in public if Path(e['path']).resolve().is_relative_to(RUN.resolve())},'External inventory covers every run artifact')
    report_dir.mkdir(parents=True)
    save(report_dir/'started.json',dict(utc=datetime.now(timezone.utc).isoformat(),source_sha256=args.expected_reviewer_sha256,
      freeze_sha256=FREEZE,manifest_sha256=MANIFEST,completion_sha256=args.expected_completion_sha256,producer_inventory_sha256=args.expected_inventory_sha256))
    try:
        v=captured_module(ROOT/'src/research8h_standalone_verify.py',KERNEL,'refinement_independent_npz')
        m=v.load_model(PRE/'joint');flags=mask(v,PRE/'joint',m.cols)
        need((m.rows,m.cols,len(m.data),sum(flags))==(69362,33936,291176,NB),'Original joint model dimensions')
        need(flags==tuple(int(START<=j<STOP) for j in range(m.cols)),'Original full binary block')
        control=values(v,PRE/'control_raw_solution.npz','vector',m.cols,('vector','row_value','row_dual','col_dual'))
        need(all(math.isfinite(x) for x in control),'Finite inherited unrounded control')
        old_fixed=read(PRE/'inherited_fixed_schedule.json')['fixed_columns']
        need([e['column'] for e in old_fixed]==list(range(START,STOP)),'Inherited nominee coordinates')
        old=[e['value'] for e in old_fixed];old_hash=state_digest(old)
        column_maps=read(PRE/'joint/column_maps.json')
        need(column_maps['worlds']==['identity','days_321'],'Frozen world order')
        inverse_columns=[{j:k for k,j in enumerate(mapping)} for mapping in column_maps['original_to_joint']]
        cases=expected_template_maps();cuts=[];seed_records=[];gap_started=False;anchor=False
        for case in cases:
            path=RUN/'seeds'/f"{case['world']}_{case['hour']:03d}_proof.json.gz"
            if not path.exists():gap_started=True;continue
            need(not gap_started,'Seed proof files form fixed lexicographic prefix')
            weights={e['joint_row']:WEIGHT*e['sign'] for e in case['rows']};need(len(weights)==24,'All selected seed rows')
            proof=gz(path);calc=exact_cut(m,flags,control,weights);compare_seed(proof,calc,case,m,flags)
            if case['world']=='identity' and case['hour']==80:anchor_match(calc,m,old);anchor=True
            state_blocks=dict(U=0,Y=0,Z=0);continuous_classes=dict(P=0,theta=0)
            inverse=inverse_columns[case['world_index']]
            for j in calc['q']:
                if flags[j]:state_blocks[('U','Y','Z')[(j-START)//4032]]+=1
                else:
                    need(j in inverse,'Private residual belongs to selected source world')
                    original=inverse[j]
                    need(original<START or original>=STOP,'Continuous residual partition')
                    continuous_classes['P' if original<START else 'theta']+=1
            cuts.append((path,calc,'seed'));seed_records.append(dict(world=case['world'],hour=case['hour'],rhs=rat(calc['cut_rhs']),control_activity=rat(calc['control_state_value']),row_support=len(weights),residual_support=len(calc['q']),state_blocks=state_blocks,continuous_classes=continuous_classes))
        need(len(seed_records)==len(list((RUN/'seeds').glob('*_proof.json.gz'))),'Every actual seed proof retained')
        complete_seed=(RUN/'seeds/completion.json').exists()
        if complete_seed:
            seed_completion=read(RUN/'seeds/completion.json');need(len(seed_records)==336 and anchor and seed_completion['cases']==seed_completion['controls_passed']==336 and seed_completion['anchor_full_identity'] is True,'Complete seeded family admission')
        base=gz(PRE/'master.json.gz');premises=read(PRE/'premises.json')
        need(len(base['rows'])==17212 and len(base['boxes'])==NC and base['binary_columns']==NB,'Inherited exact master')
        seen=[(old_hash,old)];rounds=[];positive=None;terminal=False;native_module=None
        if complete_seed:
            need(read(RUN/'initial_duplicate_set.json')==dict(states=[dict(sha256=old_hash,values=old,origin='closed_initial_nominee')],initialized_before_first_master=True),'Inherited nominee actually initializes duplicate set')
        folders=sorted(RUN.glob('round_*'));need(len(folders)<=8,'Finite mathematical trajectory')
        for number,folder in enumerate(folders,1):
            need(folder.name==f'round_{number:02d}' and not terminal and complete_seed,'Contiguous trajectory after complete seeds')
            model=gz(folder/'search_master.json.gz');appended_master(model,base,cuts)
            master=folder/'master'; rawpath=master/'raw_solution.npz';record=dict(round=number,nominee_accepted=False)
            if not rawpath.exists():record['status']='NO_SAVED_MASTER_VECTOR';rounds.append(record);terminal=True;continue
            raw=v.read_npz(rawpath,('vector',))['vector'];need(raw.dtype=='<f8' and len(raw.shape)==1,'Raw master vector schema')
            admission,origin=recover_nomination(raw.values,model,premises)
            need(read(master/'exact_master_admission.json')==admission,'Independent exact master recovery/admission')
            if origin is None:record['status']='RAW_MASTER_NOT_EXACTLY_ADMITTED';rounds.append(record);terminal=True;continue
            record['nominee_accepted']=True;digest=state_digest(origin);duplicate=any(digest==h or origin==b for h,b in seen)
            need(all((digest==h)==(origin==b) for h,b in seen),'Hash/value duplicate agreement')
            if duplicate:
                need((folder/'duplicate_stop.json').exists() and not (folder/'recourse').exists() and not (folder/'phase1').exists(),'Duplicate stops without more scientific calls')
                record['status']='DUPLICATE_STOP';rounds.append(record);terminal=True;continue
            nominee=read(folder/'novel_nominee.json');need(nominee==dict(sha256=digest,values=origin,origin=number),'Novel nominee exact identity')
            seen.append((digest,origin)); record['state_sha256']=digest
            for kind in ('recourse','phase1'):
                fixed=folder/kind/'fixed_schedule.json'
                if fixed.exists():need(read(fixed)['fixed_columns']==[dict(column=START+j,value=x) for j,x in enumerate(origin)] and read(fixed)['state_sha256']==digest,'Same full prescribed state '+kind)
            recourse=folder/'recourse'
            if (recourse/'candidate_vector.npz').exists():
                if native_module is None:native_module=captured_module(ROOT/'results/research_next/common_scip/INDEPENDENT_POSTRUN_REVIEW.py',NATIVE_REVIEW,'refinement_independent_native')
                check=positive_review(v,recourse,m,flags,origin,native_module);record['point_review']=check
                if check['accepted']:
                    need(not (folder/'phase1').exists(),'No cut solve after a full positive')
                    positive=dict(round=number,point=check);record['status']='FULL_EXPANDED_COMMON_POSITIVE';rounds.append(record);terminal=True;continue
            phase=folder/'phase1'
            if (phase/'full_exact_candidate.json.gz').exists():
                calc,detail=phase_review(v,phase,m,flags,control,origin);record['phase1']=detail
                if (folder/'next_cut.json').exists():
                    need(detail['strictly_excludes_origin'],'Only a strictly excluding next cut');nxt=read(folder/'next_cut.json')
                    need(nxt['kind']=='refinement' and nxt['round']==number and Path(nxt['proof']['path']).resolve()==(phase/'cut.json.gz').resolve(),'Next-cut trajectory identity')
                    bind(nxt['proof']);bind(nxt['encoding']);cuts.append((phase/'cut.json.gz',calc,'refinement'))
                    record['status']='EXACT_PROGRESSING_CUT'
                else:record['status']='NO_ADMITTED_NEXT_CUT';terminal=True
            else:record['status']='NO_COMPLETE_NEW_PHASE1_PROOF';terminal=True
            if (folder/'terminal_master.json.gz').exists():
                need(number==8,'Terminal transport only at round ceiling');appended_master(gz(folder/'terminal_master.json.gz'),base,cuts)
            rounds.append(record)
        result=read(RUN/'result.json');done=read(RUN/'completion.json');claimed=done['final_admission']['accepted_common']
        if args.seed_only_closure:
            need(complete_seed and len(seed_records)==336 and anchor,'Required complete seed-only proof family')
            forbidden=('optimizer_attempt.json','optimizer_returned.json','master_backend_readback.json.gz',
                       'raw_solution.npz','candidate_vector.npz','novel_nominee.json','full_exact_candidate.json.gz')
            need(not any(list(RUN.glob('round_*/**/'+name)) for name in forbidden),'Seed-only closure has no optimizer/readback/nomination evidence')
            need(not claimed and positive is None and len(rounds)==1 and rounds[0]['status']=='NO_SAVED_MASTER_VECTOR','Unresolved first-master infrastructure closure')
        need(result['no_global_infeasibility_claim'] is True and result['one_adaptive_trajectory'] is True,'No universal negative claim')
        if claimed:need(positive is not None and done['final_admission']['phase_deadline_met'] is True,'Positive has independently admitted point and timely producer flag')
        need(done['final_admission']['common_verdict']==('VERIFIED_EXPANDED_COMMON_COMMITMENT' if claimed else 'UNKNOWN'),'Final scoped verdict')
        check_bindings(inputs);check_bindings(outputs);check_bindings(public)
        need({p.resolve():sha(p) for p in RUN.rglob('*') if p.is_file()}==snapshot,'Producer output snapshot unchanged')
        need(sha(PRE/'prepared_freeze.json')==FREEZE and sha(PRE/'input_manifest.json')==MANIFEST and sha(__file__)==args.expected_reviewer_sha256 and sha(inventory_path)==args.expected_inventory_sha256,'Final trust pins unchanged')
        need(not any(n in sys.modules for n in ('numpy','scipy','highspy','pyscipopt','batch_encoding','batch_phase')),'No scientific/backend/producer imports')
        report=dict(status='PASS_INDEPENDENT_NEW_MATHEMATICS',source_sha256=args.expected_reviewer_sha256,
          freeze_sha256=FREEZE,manifest_sha256=MANIFEST,completion_sha256=args.expected_completion_sha256,
          producer_inventory_sha256=args.expected_inventory_sha256,input_bindings=355,closed_public_files=len(public),closed_run_payloads=len(outputs),
          actual_saved_seed_proof_count=len(seed_records),complete_seed_family_independently_verified=complete_seed,
          anchor_matched=anchor,seed_records=seed_records,rounds=rounds,new_phase1_proofs=sum('phase1' in r for r in rounds),
          new_exact_nominees=sum(r['nominee_accepted'] for r in rounds),positive=positive,producer_final_common_verdict=done['final_admission']['common_verdict'],
          mathematical_positive_exists=positive is not None,backend_encoding_lifecycle_review='SEPARATE_REQUIRED_GATE',
          seed_only_closure=args.seed_only_closure,
          support_census=[dict(signature=json.loads(key),count=count) for key,count in sorted(Counter(json.dumps(dict(row_support=r['row_support'],residual_support=r['residual_support'],state_blocks=r['state_blocks'],continuous_classes=r['continuous_classes']),sort_keys=True) for r in seed_records).items())],
          reused_decoder_sha256=KERNEL,reused_historical_independent_native_source_sha256=NATIVE_REVIEW if native_module else None,
          old_full_point_or_proof_replays=0,producer_arithmetic_imports=0,encoding_helper_imports=0,optimizer_calls=0,
          all_input_output_bytes_unchanged=True,elapsed_seconds=time.perf_counter()-started,
          scope='Only new exact seed/cut/nomination/point mathematics; fixed expanded pair. Full publication additionally requires separate backend/encoding/lifecycle gate. No new case, discovery, integer-infeasibility or regret claim.')
        save(report_dir/'review.json',report);print(json.dumps(dict(status=report['status'],report_sha256=sha(report_dir/'review.json'),seed_proofs=len(seed_records),rounds=len(rounds),elapsed_seconds=report['elapsed_seconds'])))
    except BaseException as error:
        save(report_dir/'failure.json',dict(error_type=type(error).__name__,message=str(error),source_sha256=args.expected_reviewer_sha256,
          scientific_replay_attempted=True,optimizer_calls=0,no_retry=True));raise

def self_test():
    """No repository scientific inputs, native helpers or prepared data opened."""
    class Toy:
        rows=2;cols=3;indptr=(0,2,4);indices=(0,1,0,2);data=(1.,1.,1.,-1.)
        row_lower=(2.,-math.inf);row_upper=(3.,1.);lower=(0.,-1.,-2.);upper=(1.,2.,3.)
    c=exact_cut(Toy(),(1,0,0),(0.5,0.,0.),{0:F(2),1:F(-1)},F(1,8))
    need(c['q']=={0:F(1),1:F(2),2:F(1)},'Signed exact full residual')
    need(c['beta']==3 and c['continuous_support']==7 and c['tau_loss']==F(3,4) and c['cut_rhs']==F(-19,4),'Signed support and both norm losses')
    d,projection,gains=project_duals(Toy(),[dict(original_row=0,side='lower'),dict(original_row=0,side='upper'),dict(original_row=1,side='upper')],[2.,-1.,-1.])
    need(d=={0:F(1),1:F(-1)} and gains['canonical_interval_gain']==1 and gains['norm_cancellation']==2,'Endpoint sign projection/cancellation')
    small=dict(boxes=[dict(lower={'exact':['0','1']},upper={'exact':['1','1']},kind='B')],rows=[dict(family='toy',terms=[[0,{'exact':['2','1']}]],lower={'exact':['1','1']},upper=None)])
    need(not exact_master(small,[F(1)]) and exact_master(small,[F(0)])==[dict(row=0,family='toy')],'Exact necessary row admission')
    need(not exact_point(Toy(),(1,0,0),(0.,0.,0.),F(0))['expanded_pass'],'Rejected full raw point')
    need(not exact_point(Toy(),(1,0,0),(0.5,1.5,0.),F(1))['original_binary_coordinates_exact'],'Never waive original integrality')
    OUT.mkdir(parents=True,exist_ok=True);report=OUT/'INVENTED_CONTROLS.json'
    save(report,dict(status='PASS_INVENTED_ONLY',source_sha256=sha(__file__),groups=5,scientific_inputs_read=0,
      scientific_replays=0,optimizer_calls=0,backend_imports=0,producer_imports=0,helper_imports=0))
    print(json.dumps(dict(status='PASS_INVENTED_ONLY',source_sha256=sha(__file__),receipt_sha256=sha(report))))

def main():
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--self-test',action='store_true');group.add_argument('--run-closed',action='store_true')
    parser.add_argument('--seed-only-closure',action='store_true')
    parser.add_argument('--expected-freeze-sha256');parser.add_argument('--expected-completion-sha256')
    parser.add_argument('--expected-inventory-sha256');parser.add_argument('--expected-reviewer-sha256');args=parser.parse_args()
    if args.self_test:self_test()
    else:
        need(all((args.expected_freeze_sha256,args.expected_completion_sha256,args.expected_inventory_sha256,args.expected_reviewer_sha256)),'Explicit closed input/output/source pins required')
        need(args.seed_only_closure,'Current reviewed execution scope is the closed seed-only arm; future full trajectories need a separate source gate')
        main_review(args)

if __name__=='__main__':main()
