"""Prospective independent mathematical replay of one CLOSED ownership-recovery trajectory.

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
ARM = ROOT/'results/research_next/common_refinement_jobs'
PRE = ARM/'prepared'
RUN = ARM/'run01'
OUT = ROOT/'results/research_next/common_refinement_jobs_math_review'
FREEZE = '8053a3795c9ed14d53c84df5dddefa355fb29572be9ce213758bf75a3922347c'
MANIFEST = '4478c4637b2b81256cc31e9cdc2516b2112309c30096176d5df42ba205dd09a6'
PRODUCER = 'fa1548f4d7765ac84e2f74a06df2fde640c713b85a1c27bdc29c99f3bb1b2973'
PROTOCOL = '14f9a4f2fb11966eec851e1c69187945f2daa523f1d5fd1a5b389900ecdf7b1f'
KERNEL = '708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
NATIVE_REVIEW = '090aba46d707e01c21cc4713073c41b718d98ca9d2bb3192674e274508f21e98'
NB, START, STOP, NC = 12096, 6888, 18984, 12432
TAU = F.from_float(1e-5)
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
    compact_path=folder/'cut.json.gz'
    if not compact_path.exists():
        return c,dict(strictly_excludes_origin=gap>0,exact_margin=rat(gap),row_support=len(d),state_support=certificate['state_support'],compact_present=False)
    compact=gz(compact_path)
    need(compact['state_terms']==[[j,rat(a)] for j,a in sorted(c['q'].items()) if flags[j]] and frac(compact['cut_rhs'])==c['cut_rhs'],'Compact cut matches full proof')
    need(compact['original_rows']==m.rows and compact['original_columns']==m.cols and compact['full_state_dimension']==NB and compact['omitted_coordinates_exact_zero'] is True,'Compact full dimensions')
    bind(compact['full_proof']); need(Path(compact['full_proof']['path']).resolve()==(folder/'full_exact_candidate.json.gz').resolve(),'Compact full-proof path')
    return c,dict(strictly_excludes_origin=gap>0,exact_margin=rat(gap),row_support=len(d),state_support=certificate['state_support'],compact_present=True)

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
        need(Path(provenance['encoding']['path']).resolve()==calculation['encoding_path'].resolve(),'Pinned requested encoding identity')
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

# Closed evidence is inherited as a premise, never reevaluated against an old point.
SEED_REVIEW = '205b8118a0a01d5cb63a1435b5b8dbdc0089ca1aad7e2cbb153b9117ac63738a'
OLD_INVENTORY = '8c0faa1048a6b5d232feb58a75d921fb287abc87c607d71f492d7824739b7f83'
OLD_COMPLETION = 'b445ba6868a2ee044a9dbe1c019bcf2e17dd7ed0d947ef6b08e1b117a0f3886f'
ENCODING_REVIEW = 'fa336a6b919b50df691f4ec01b8ef70cadd63e7f800f0fb4b3298c783c642a0f'
MATH_NAMES = {'search_master.json.gz','terminal_master.json.gz','raw_solution.npz',
 'exact_master_admission.json','novel_nominee.json','duplicate_stop.json','fixed_schedule.json',
 'candidate_vector.npz','identity_vector.npz','days_321_vector.npz','exact_candidate_checks.json',
 'prescribed_restoration.json','full_exact_candidate.json.gz','cut.json.gz','next_cut.json'}

def consume(path,seen):
    path=Path(path)
    if path.is_file(): seen.add(path.resolve());return True
    return False

def optional(path,seen):
    return read(path) if consume(path,seen) else None

def check_partial_dependencies(kind,names):
    """A saved prefix may stop anywhere; a downstream file cannot lack its inputs."""
    rules={
      'master':{'exact_master_admission.json':{'raw_solution.npz'}},
      'recourse':{'candidate_vector.npz':{'raw_solution.npz'},
        'identity_vector.npz':{'candidate_vector.npz'},'days_321_vector.npz':{'identity_vector.npz'},
        'exact_candidate_checks.json':{'identity_vector.npz','days_321_vector.npz'},
        'prescribed_restoration.json':{'exact_candidate_checks.json'}},
      'phase1':{'full_exact_candidate.json.gz':{'raw_solution.npz'},
        'cut.json.gz':{'full_exact_candidate.json.gz'},'encoding.json.gz':{'cut.json.gz'}}}
    for later,earlier in rules[kind].items():
        need(later not in names or earlier<=names,'Saved mathematical dependency missing: '+kind+'/'+later)

def producer_point_agreement(saved,computed,label):
    for key in ('expanded_pass','strict_pass','original_binary_coordinates_exact','binary_coordinates'):
        need(saved[key]==computed[key],label+' '+key)
    for key in ('maximum_column_violation','maximum_row_violation'):
        q=saved[key];actual=F(int(q['numerator']),int(q['denominator']))
        need(actual==frac(computed[key]),label+' exact '+key)

def positive_review(v,folder,m,flags,origin,native_module,seen):
    """Check a SAVED new candidate even if the producer stopped mid-check/write.

    Missing producer derivative files are recorded, not synthesized or required for
    independent mathematics. They prevent claiming complete producer admission.
    """
    raw=values(v,folder/'raw_solution.npz','vector',m.cols)
    candidate=values(v,folder/'candidate_vector.npz','vector',m.cols)
    seen.update((folder/name).resolve() for name in ('raw_solution.npz','candidate_vector.npz'))
    need(all(math.isfinite(x) for x in raw+candidate),'Finite complete recourse vectors')
    for j,b in enumerate(flags):
        if b:need(candidate[j]==origin[j-START] and abs(F(raw[j])-origin[j-START])<=TAU,'Only prescribed near states restored')
    need(packed([x for j,x in enumerate(candidate) if not flags[j]])==packed([x for j,x in enumerate(raw) if not flags[j]]),'Every raw continuous byte unchanged')
    joint=exact_point(m,flags,candidate);saved=optional(folder/'exact_candidate_checks.json',seen)
    maps=read(PRE/'joint/column_maps.json');need(maps['worlds']==['identity','days_321'],'Two original world maps')
    worlds=[];missing=[]
    for wi,world in enumerate(maps['worlds']):
        directory=PRE/world;wm=v.load_model(directory);wb=mask(v,directory,wm.cols)
        mapping=maps['original_to_joint'][wi]
        need(len(mapping)==len(set(mapping))==wm.cols and all(type(j)is int and 0<=j<m.cols for j in mapping),'Full original coordinate injection')
        need(sum(wb)==NB and mapping[START:STOP]==list(range(START,STOP)),'Complete shared original mask mapping')
        point=[candidate[j] for j in mapping];path=folder/(world+'_vector.npz')
        if consume(path,seen):need(packed(point)==packed(values(v,path,'vector',wm.cols)),'Saved projection is exact original-world point')
        else:missing.append(path.name)
        check=exact_point(wm,wb,point);direct=native_module.native(v,point,directory)
        states=[int(point[j]) for j,b in enumerate(wb) if b]
        need(states==origin,'Every original bit common to both worlds')
        if saved is not None:
            item=saved['worlds'][wi];need(item['world']==world,'Saved world order')
            producer_point_agreement(item['original'],check,world)
            for key in ('expanded_pass','violations'):need(item['native'][key]==direct[key],'Native '+key)
            for key in ('maximum_violation','exact_fossil_energy'):
                a,b=item['native'][key],direct[key]
                need(F(int(a['numerator']),int(a['denominator']))==F(int(b['numerator']),int(b['denominator'])),'Native exact '+key)
        worlds.append(dict(world=world,matrix=check,native=direct))
    accepted=joint['expanded_pass'] and all(w['matrix']['expanded_pass'] and w['native']['expanded_pass'] for w in worlds)
    if saved is not None:
        producer_point_agreement(saved['joint'],joint,'joint')
        need(saved['accepted'] is accepted and saved['common_all12096_bits'] is True and saved['continuous_bytes_unchanged'] is True,'Combined producer point claims')
    else:missing.append('exact_candidate_checks.json')
    restore=optional(folder/'prescribed_restoration.json',seen)
    if restore is not None:need(restore==dict(continuous_raw_bytes_unchanged=True,all12096_prescribed_bits=True,prescribed_within_exact_tau=True),'Restoration claim')
    else:missing.append('prescribed_restoration.json')
    return dict(accepted_mathematically=accepted,joint=joint,worlds=worlds,
      continuous_bytes_unchanged=True,all_common_bits=NB,missing_producer_derivatives=missing,
      complete_producer_point_records=not missing,strict_nominal_claim=False)

def inherited_cuts(inputs):
    expected={
      ROOT/'results/research_next/common_refinement_math_review/review01/review.json':SEED_REVIEW,
      ROOT/'results/research_next/common_refinement_batch/producer_output_inventory.csv':OLD_INVENTORY,
      ROOT/'results/research_next/common_refinement_batch/run01/completion.json':OLD_COMPLETION,
      ROOT/'results/research_next/common_refinement_batch_independent_review/postrun_failure_review.json':ENCODING_REVIEW}
    bound={Path(e['path']).resolve():e for e in inputs}
    for path,digest in expected.items():
        need(path.resolve() in bound and bound[path.resolve()]['sha256']==digest and sha(path)==digest,'Closed historical premise')
    index=read(PRE/'inherited_seed_index.json')
    need(index['mathematical_review_sha256']==SEED_REVIEW and index['encoding_review_sha256']==ENCODING_REVIEW,'Inherited review references')
    records=index['records'];need(index['cases']==len(records)==336 and index['no_seed_arithmetic'] is True,'Inherited denominator')
    need([(r['world'],r['hour']) for r in records]==[(w,t) for w in ('identity','days_321') for t in range(168)],'Inherited seed order')
    copies=read(PRE/'copy_provenance.json')['copies'];copy_map={Path(x['copy']['path']).resolve():x for x in copies}
    cuts=[]
    for entry in records:
        for kind in ('proof','encoding'):
            desc=entry[kind];bind(desc);p=Path(desc['path']).resolve()
            need(p.is_relative_to((PRE/'seeds').resolve()) and copy_map[p]['copy']==desc,'Inherited copied payload identity')
            original=copy_map[p]['original'];need(original['sha256']==desc['sha256'] and original['bytes']==desc['bytes'],'No seed payload change')
            need(Path(original['path']).resolve() in bound and bound[Path(original['path']).resolve()]==original,'Historical payload bound in original inventory chain')
        proof=gz(entry['proof']['path'])
        terms={j:frac(a) for j,a in proof['state_terms']}
        need(len(terms)==len(proof['state_terms']) and all(START<=j<STOP and a for j,a in terms.items()),'Inherited state coordinate schema')
        # This only deserializes admitted terms. No d/q/support/control or anchor calculation.
        cuts.append((Path(entry['proof']['path']),dict(q=terms,cut_rhs=frac(proof['cut_rhs']),encoding_path=Path(entry['encoding']['path'])),'seed'))
    return cuts

def finish_phase(v,folder,m,flags,control,origin,seen):
    rawpath=folder/'raw_solution.npz';full=folder/'full_exact_candidate.json.gz';compact=folder/'cut.json.gz'
    if consume(rawpath,seen):
        # A raw-only record is not a producer certificate. Do not invent its missing proof.
        if not full.exists():
            need(not compact.exists(),'No compact proof without full proof')
            return None,dict(status='RAW_DUAL_ONLY_NO_SAVED_CERTIFICATE',scientific_proof_reconstruction=False)
    else:
        need(not full.exists() and not compact.exists(),'Proof cannot precede raw dual')
        return None,dict(status='NO_SAVED_PHASE_VECTOR_OR_PROOF',scientific_proof_reconstruction=False)
    consume(full,seen);consume(compact,seen)
    calculation,detail=phase_review(v,folder,m,flags,control,origin)
    detail['status']='EXACT_NOMINEE_REJECTION' if detail['strictly_excludes_origin'] else 'VALID_NONSEPARATING_PROOF'
    detail['scientific_proof_reconstruction']=True
    calculation['encoding_path']=folder/'encoding.json.gz'
    return calculation,detail

def review_trajectory(v,m,flags,control,cuts,seen_math):
    base=gz(PRE/'master.json.gz');premises=read(PRE/'premises.json')
    need(len(base['rows'])==17212 and len(base['boxes'])==NC and base['binary_columns']==NB,'Inherited necessary master')
    inherited=read(PRE/'inherited_initial_duplicate_set.json');states=inherited['states']
    need(inherited['initialized_before_first_master'] and len(states)==1,'Closed old duplicate')
    previous=states[0];old=previous['values'];need(previous['sha256']==state_digest(old) and previous['origin']=='closed_initial_nominee','Inherited bit identity')
    duplicatepath=RUN/'initial_duplicate_set.json'
    if duplicatepath.exists():need(read(duplicatepath)==inherited,'Same initial duplicate set, no old feasibility replay')
    folders=sorted(RUN.glob('round_*'));need(len(folders)<=8,'Fixed round ceiling')
    if folders:need(duplicatepath.exists(),'Duplicate exclusion initialized before rounds')
    allseen=[(previous['sha256'],old)];rounds=[];positive=[];terminal=False;native=None
    for number,folder in enumerate(folders,1):
        need(folder.is_dir() and folder.name==f'round_{number:02d}' and not terminal,'Contiguous finite trajectory')
        for kind in ('master','recourse','phase1'):
            check_partial_dependencies(kind,{p.name for p in (folder/kind).iterdir() if p.is_file()} if (folder/kind).is_dir() else set())
        record=dict(round=number,raw_master_present=False,exact_master_admission=False,producer_nomination=False)
        search=folder/'search_master.json.gz'
        if not consume(search,seen_math):
            need(not any(p.is_file() for p in folder.rglob('*')),'Missing search model only allowed for an empty interrupted round')
            record['status']='EMPTY_ROUND_INTERRUPTED';rounds.append(record);terminal=True;continue
        model=gz(search);appended_master(model,base,cuts)
        master=folder/'master';rawpath=master/'raw_solution.npz'
        if not consume(rawpath,seen_math):
            record['status']='NO_SAVED_MASTER_VECTOR';rounds.append(record);terminal=True;continue
        record['raw_master_present']=True
        raw=v.read_npz(rawpath,('vector',))['vector'];need(raw.dtype=='<f8' and len(raw.shape)==1,'Raw master vector schema')
        admission,origin=recover_nomination(raw.values,model,premises)
        recorded=optional(master/'exact_master_admission.json',seen_math)
        if recorded is not None:need(recorded==admission,'Complete independent master recovery including rejection details')
        record['exact_master_admission']=origin is not None
        record['producer_master_admission_present']=recorded is not None
        if origin is None:
            record['status']='RAW_MASTER_NOT_EXACTLY_ADMITTED';rounds.append(record);terminal=True;continue
        digest=state_digest(origin);duplicate=any(digest==h or origin==b for h,b in allseen)
        need(all((digest==h)==(origin==b) for h,b in allseen),'Digest/full-bit equality agreement')
        record['state_sha256']=digest;record['duplicates_prior_state']=duplicate
        stop=optional(folder/'duplicate_stop.json',seen_math)
        if duplicate:
            if stop is not None:need(stop==dict(state_sha256=digest,no_additional_solver=True),'Duplicate stop identity')
            record['status']='DUPLICATE_STATE_TERMINAL';rounds.append(record);terminal=True;continue
        need(stop is None,'No false duplicate stop')
        nominee=optional(folder/'novel_nominee.json',seen_math)
        if nominee is None:
            record['status']='EXACT_MASTER_POINT_WITHOUT_PUBLISHED_NOMINEE';rounds.append(record);terminal=True;continue
        need(recorded is not None and nominee==dict(sha256=digest,values=origin,origin=number),'New nominee follows recorded exact admission')
        allseen.append((digest,origin));record['producer_nomination']=True
        for kind in ('recourse','phase1'):
            fixed=optional(folder/kind/'fixed_schedule.json',seen_math)
            if fixed is not None:need(fixed==dict(fixed_columns=[dict(column=START+j,value=x) for j,x in enumerate(origin)],state_sha256=digest),'Unchanged all-bit prescription '+kind)
            req=folder/kind/'request.json'
            if req.exists():
                q=read(req);need(q['state_values']==origin and Path(q['nominee']['path']).resolve()==(folder/'novel_nominee.json').resolve(),'Actual worker request mathematical identity')
                bind(q['nominee'])
        recourse=folder/'recourse';candidate=recourse/'candidate_vector.npz'
        if consume(candidate,seen_math):
            if native is None:native=captured_module(ROOT/'results/research_next/common_scip/INDEPENDENT_POSTRUN_REVIEW.py',NATIVE_REVIEW,'jobs_new_candidate_independent_native')
            point=positive_review(v,recourse,m,flags,origin,native,seen_math);record['point_review']=point
            if point['accepted_mathematically']:positive.append(dict(round=number,point=point))
        elif consume(recourse/'raw_solution.npz',seen_math):
            # Restore no vector and certify no point which was not actually saved.
            record['recourse_status']='RAW_RECOURSE_ONLY_NO_SAVED_CANDIDATE'
        phase=folder/'phase1'
        calc,detail=finish_phase(v,phase,m,flags,control,origin,seen_math);record['phase1']=detail
        nxt=optional(folder/'next_cut.json',seen_math)
        if nxt is not None:
            need(calc is not None and detail['strictly_excludes_origin'] and detail['compact_present'],'Only a full, compact, strictly excluding saved cut may continue')
            need(nxt['kind']=='refinement' and nxt['round']==number and Path(nxt['proof']['path']).resolve()==(phase/'cut.json.gz').resolve() and Path(nxt['encoding']['path']).resolve()==(phase/'encoding.json.gz').resolve(),'New cut chronology/provenance')
            bind(nxt['proof']);bind(nxt['encoding']);cuts.append((phase/'cut.json.gz',calc,'refinement'))
            record['status']='EXACT_PROGRESSING_CUT';terminal=number==8
        else:
            record['status']='TERMINAL_NO_PROPAGATED_NEW_CUT';terminal=True
        terminalpath=folder/'terminal_master.json.gz'
        if consume(terminalpath,seen_math):
            need(number==8 and nxt is not None,'Only one final ceiling transport model')
            appended_master(gz(terminalpath),base,cuts)
        rounds.append(record)
    return rounds,positive,native is not None

def worker_math_claims(rounds):
    """Only crosscheck mathematical claims; timing/process/backend admission is separate."""
    for record in rounds:
        folder=RUN/f"round_{record['round']:02d}"
        path=folder/'master/completion.json'
        if path.exists():
            final=read(path)['final_admission']
            need(final.get('nominee_accepted',False)==record['exact_master_admission'],'Completed master nominee claim')
            if final.get('nominee_accepted',False):
                need(record.get('producer_master_admission_present',False),'Completed master requires saved admission')
                need(state_digest(final['state_values'])==record['state_sha256'],'Worker returned the reviewed complete nominee')
        path=folder/'phase1/completion.json'
        if path.exists():
            final=read(path)['final_admission'];proof=record.get('phase1',{})
            need(final.get('strict_exact_nominee_exclusion',False)==proof.get('strictly_excludes_origin',False),'Completed PhaseI exact exclusion claim')
        path=folder/'recourse/completion.json'
        if path.exists() and read(path)['final_admission']['accepted_common']:
            point=record.get('point_review',{})
            need(point.get('accepted_mathematically',False) and point.get('complete_producer_point_records',False),'Completed recourse positive has full saved mathematical evidence')

def final_claim(done,rounds,positive):
    final=done['final_admission'];claimed=final['accepted_common']
    need(type(claimed)is bool and final['common_verdict']==('VERIFIED_EXPANDED_COMMON_COMMITMENT' if claimed else 'UNKNOWN'),'No finite-rejection/global-infeasibility promotion')
    if claimed:
        eligible=[p for p in positive if p['point']['complete_producer_point_records']]
        need(len(eligible)==1 and eligible[0]['round']==len(rounds) and final['phase_deadline_met'] is True,'Final positive requires full checked point and authoritative timely record')
        worker=RUN/f"round_{eligible[0]['round']:02d}/recourse/completion.json"
        need(worker.exists() and read(worker)['final_admission']['accepted_common'] is True,'Authoritative recourse positive record')
        need(not (worker.parent.parent/'phase1').exists(),'No PhaseI after admitted common point')
    # A late/partially saved mathematically good point remains separate from admission.
    return dict(producer_common_verdict=final['common_verdict'],mathematical_positive_saved=bool(positive),
                authoritative_common_positive=claimed,global_infeasibility_proved=False)

def main_review(args):
    started=time.perf_counter();report_dir=OUT/'review01'
    need(not report_dir.exists(),'One explicitly authorized closed scientific review')
    need(args.expected_freeze_sha256==FREEZE and sha(__file__)==args.expected_reviewer_sha256,'External freeze/reviewer pins')
    need(sha(PRE/'prepared_freeze.json')==FREEZE and sha(PRE/'input_manifest.json')==MANIFEST,'Prepared files pinned')
    freeze=read(PRE/'prepared_freeze.json')
    need((freeze['source_sha256'],freeze['protocol_sha256'],freeze['manifest_sha256'],freeze['bindings'])==(PRODUCER,PROTOCOL,MANIFEST,1769),'Frozen source/protocol/manifest')
    source=ROOT/'src/researchnext_common_refinement_jobs.py';protocol=ROOT/'docs/research_next/COMMON_REFINEMENT_JOBS_PROTOCOL.md'
    need(sha(source)==PRODUCER and sha(protocol)==PROTOCOL,'Producer source/protocol bytes')
    inputs=read(PRE/'input_manifest.json')['files'];need(len(inputs)==1769,'Complete preparation input count');check_bindings(inputs)
    inventory=ARM/'producer_output_inventory.csv'
    need(sha(RUN/'completion.json')==args.expected_completion_sha256 and sha(inventory)==args.expected_inventory_sha256,'Externally bound closure')
    with inventory.open(encoding='utf-8-sig',newline='') as f:entries=list(csv.DictReader(f))
    public=[]
    for e in entries:
        p=(ROOT/e['path']).resolve();need(p.is_relative_to(ARM.resolve()),'Public payload confined to recovery arm')
        public.append(dict(path=str(p),bytes=int(e['bytes']),sha256=e['sha256']))
    need(len(public)==args.expected_public_count,'External public inventory denominator');check_bindings(public)
    outputs=read(RUN/'producer_files.json')['files'];check_bindings(outputs)
    need(all(Path(e['path']).resolve().is_relative_to(RUN.resolve()) for e in outputs),'Closed run outputs confined')
    snapshot={p.resolve():sha(p) for p in RUN.rglob('*') if p.is_file()}
    need(set(snapshot)=={Path(e['path']).resolve() for e in outputs}|{(RUN/'producer_files.json').resolve()},'Complete run-file inventory')
    need(set(snapshot)=={Path(e['path']).resolve() for e in public if Path(e['path']).resolve().is_relative_to(RUN.resolve())},'External inventory covers full run')
    report_dir.mkdir(parents=True)
    save(report_dir/'started.json',dict(utc=datetime.now(timezone.utc).isoformat(),source_sha256=args.expected_reviewer_sha256,
      freeze_sha256=FREEZE,manifest_sha256=MANIFEST,completion_sha256=args.expected_completion_sha256,inventory_sha256=args.expected_inventory_sha256))
    try:
        cuts=inherited_cuts(inputs)
        v=captured_module(ROOT/'src/research8h_standalone_verify.py',KERNEL,'jobs_review_stdlib_decoder')
        m=v.load_model(PRE/'joint');flags=mask(v,PRE/'joint',m.cols)
        need((m.rows,m.cols,len(m.data),sum(flags))==(69362,33936,291176,NB),'Original joint dimensions')
        need(flags==tuple(int(START<=j<STOP) for j in range(m.cols)),'All original binary coordinates')
        control=values(v,PRE/'control_raw_solution.npz','vector',m.cols,('vector','row_value','row_dual','col_dual'))
        need(all(math.isfinite(x) for x in control),'Inherited unrounded control finite; no membership replay')
        seen=set();rounds,positive,used_native=review_trajectory(v,m,flags,control,cuts,seen)
        actual={p.resolve() for p in RUN.glob('round_*/**/*') if p.is_file() and p.name in MATH_NAMES}
        need(seen==actual,'Every generated mathematical artifact handled; no silent partial/output omission: '+str(sorted(map(str,actual-seen))))
        result=read(RUN/'result.json');done=read(RUN/'completion.json')
        need(result['no_global_infeasibility_claim'] is True and result['one_adaptive_trajectory'] is True,'Scope not promoted')
        worker_math_claims(rounds)
        claim=final_claim(done,rounds,positive)
        check_bindings(inputs);check_bindings(outputs);check_bindings(public)
        need(snapshot=={p.resolve():sha(p) for p in RUN.rglob('*') if p.is_file()},'Closed producer files unchanged')
        for p,h in ((PRE/'prepared_freeze.json',FREEZE),(PRE/'input_manifest.json',MANIFEST),(source,PRODUCER),(protocol,PROTOCOL),
                    (Path(__file__),args.expected_reviewer_sha256),(inventory,args.expected_inventory_sha256)):
            need(sha(p)==h,'Final source/transport pins')
        if used_native:need(sha(ROOT/'results/research_next/common_scip/INDEPENDENT_POSTRUN_REVIEW.py')==NATIVE_REVIEW,'Pure historical native source unchanged')
        need(not any(n in sys.modules for n in ('numpy','scipy','highspy','pyscipopt','batch_encoding','batch_phase')),'No backend/producer arithmetic imports')
        report=dict(status='PASS_INDEPENDENT_RECOVERY_MATHEMATICS',source_sha256=args.expected_reviewer_sha256,
          freeze_sha256=FREEZE,manifest_sha256=MANIFEST,completion_sha256=args.expected_completion_sha256,inventory_sha256=args.expected_inventory_sha256,
          input_bindings=len(inputs),closed_public_files=len(public),closed_run_payloads=len(outputs),inherited_seed_count=336,
          inherited_seed_mathematics_review_sha256=SEED_REVIEW,inherited_seed_math_replays=0,new_seed_evaluations=0,
          rounds=rounds,new_saved_full_phase_proofs=sum(r.get('phase1',{}).get('scientific_proof_reconstruction',False) for r in rounds),
          exact_master_points=sum(r['exact_master_admission'] for r in rounds),published_new_nominees=sum(r['producer_nomination'] for r in rounds),
          positive=positive,claim=claim,all_mathematical_files_accounted=len(seen),
          separate_backend_encoding_lifecycle_review='REQUIRED; not replaced by mathematical admission',
          decoder_source_sha256=KERNEL,historical_native_pure_function_source_sha256=NATIVE_REVIEW if used_native else None,
          old_full_point_replays=0,optimizer_calls=0,producer_arithmetic_imports=0,encoding_helper_imports=0,
          all_input_output_bytes_unchanged=True,elapsed_seconds=time.perf_counter()-started,
          scope='Only new saved trajectory mathematics for this fixed expanded pair. Exact cut rejection excludes its nominated state, not all common commitments. Missing producer derivatives cannot be promoted to authoritative admission.')
        save(report_dir/'review.json',report)
        print(json.dumps(dict(status=report['status'],report_sha256=sha(report_dir/'review.json'),rounds=len(rounds),elapsed_seconds=report['elapsed_seconds'])))
    except BaseException as e:
        save(report_dir/'failure.json',dict(error_type=type(e).__name__,message=str(e),source_sha256=args.expected_reviewer_sha256,
          scientific_review_attempted=True,optimizer_calls=0,no_automatic_retry=True));raise

def self_test():
    """Invented only: no prepared archive, old point or scientific helper opened."""
    class Toy:
        rows=2;cols=3;indptr=(0,2,4);indices=(0,1,0,2);data=(1.,1.,1.,-1.)
        row_lower=(2.,-math.inf);row_upper=(3.,1.);lower=(0.,-1.,-2.);upper=(1.,2.,3.)
    checks=[]
    def check(name,ok):need(ok,name);checks.append(name)
    c=exact_cut(Toy(),(1,0,0),(0.5,0.,0.),{0:F(2),1:F(-1)},F(1,8))
    check('signed_full_residual',c['q']=={0:F(1),1:F(2),2:F(1)})
    check('all_support_and_tau_terms',c['beta']==3 and c['continuous_support']==7 and c['tau_loss']==F(3,4) and c['cut_rhs']==F(-19,4))
    d,p,g=project_duals(Toy(),[dict(original_row=0,side='lower'),dict(original_row=0,side='upper'),dict(original_row=1,side='upper')],[2.,-1.,-1.])
    check('both_signs_and_cancellation',d=={0:F(1),1:F(-1)} and g['canonical_interval_gain']==1 and g['norm_cancellation']==2)
    d,_,_=project_duals(Toy(),[dict(original_row=0,side='lower'),dict(original_row=0,side='upper'),dict(original_row=1,side='upper')],[-2.,1.,-1.])
    check('wrong_dual_sign_projected_to_zero',d=={1:F(-1)})
    model=dict(boxes=[dict(lower={'exact':['0','1']},upper={'exact':['1','1']},kind='B')],rows=[dict(family='toy',terms=[[0,{'exact':['2','1']}]],lower={'exact':['1','1']},upper=None)])
    check('nomination_row_rejection',exact_master(model,[F(0)])==[dict(row=0,family='toy')] and not exact_master(model,[F(1)]))
    check('no_integrality_waiver',not exact_point(Toy(),(1,0,0),(0.5,1.5,0.),F(1))['original_binary_coordinates_exact'])
    check('bad_complete_candidate_rejected',not exact_point(Toy(),(1,0,0),(0.,0.,0.),F(0))['expanded_pass'])
    check('invalid_raw_nominee_rejected',recover_nomination([math.nan],{}, {})[0]['accepted'] is False)
    for kind,names in [('master',{'raw_solution.npz'}),('recourse',{'raw_solution.npz','candidate_vector.npz'}),
                       ('phase1',{'raw_solution.npz','full_exact_candidate.json.gz'})]:
        check_partial_dependencies(kind,names);checks.append('valid_partial_'+kind)
    for kind,names in [('master',{'exact_master_admission.json'}),('recourse',{'raw_solution.npz','candidate_vector.npz','exact_candidate_checks.json'}),
                       ('phase1',{'raw_solution.npz','cut.json.gz'})]:
        try:check_partial_dependencies(kind,names)
        except ValueError:checks.append('missing_dependency_rejected_'+kind)
        else:raise ValueError('Invented incomplete dependency accepted')
    # Pure final-claim logic: mathematical positive and producer admission differ.
    done=dict(final_admission=dict(accepted_common=False,common_verdict='UNKNOWN',phase_deadline_met=False))
    q=final_claim(done,[],[dict(point=dict(complete_producer_point_records=False))])
    check('late_or_partial_positive_stays_unknown',q['mathematical_positive_saved'] and not q['authoritative_common_positive'])
    try:final_claim(dict(final_admission=dict(accepted_common=True,common_verdict='VERIFIED_EXPANDED_COMMON_COMMITMENT',phase_deadline_met=True)),[],[])
    except ValueError:checks.append('empty_positive_claim_rejected')
    else:raise ValueError('Invented unsupported positive accepted')
    OUT.mkdir(parents=True,exist_ok=True);path=OUT/'INVENTED_CONTROLS.json'
    save(path,dict(status='PASS_INVENTED_ONLY',source_sha256=sha(__file__),groups=len(checks),checks=checks,
      scientific_inputs_read=0,scientific_replays=0,optimizer_calls=0,backend_imports=0,producer_imports=0,helper_imports=0))
    print(json.dumps(dict(status='PASS_INVENTED_ONLY',source_sha256=sha(__file__),receipt_sha256=sha(path))))

def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--self-test',action='store_true');g.add_argument('--run-closed',action='store_true')
    for name in ('freeze','completion','inventory','reviewer'):p.add_argument('--expected-'+name+'-sha256')
    p.add_argument('--expected-public-count',type=int);a=p.parse_args()
    if a.self_test:self_test()
    else:
        need(all((a.expected_freeze_sha256,a.expected_completion_sha256,a.expected_inventory_sha256,a.expected_reviewer_sha256,a.expected_public_count)), 'External closed input/output/source hashes/count required')
        main_review(a)

if __name__=='__main__':main()
