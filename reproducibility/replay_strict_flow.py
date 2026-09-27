"""Offline strict flow-model evidence replay. Use Python -I -S; see protocol."""
from __future__ import annotations
import argparse
import csv
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import time
from types import SimpleNamespace

sys.dont_write_bytecode=True
SELF='reproducibility/replay_strict_flow.py'
PROTOCOL='docs/research8h/PORTABLE_STRICT_FLOW_REPLAY_PROTOCOL.md'
SCOPE='strict-flow-capped-and-uncapped-v1'
R='results/research8h/'
CAPPED=R+'branch_flow_encoding';ENERGY=R+'branch_flow_strict_energy'
TARGETS=('seed_26093200','seed_26093201');IDENTITY='january_identity';CONTROL='seed_26100200'
OLD_ROOT='C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3'
OLD_NATIVE='C:/Users/gmalkawi/.codex/worktrees/dsc-v8r1-evidence/3/.work/v8r1_rts_inputs'
ADDENDUM='reproducibility/native_sources'
GEN=ADDENDUM+'/rts_inputs/raw/RTS-GMLC_v0.2.3/gen.csv'
GEN_SHA='988466f29132b73739de60c9204dd4a2a9ceb0adf572e5966c086611272f4068'
MASK=(0,)*6888+(1,)*12096+(0,)*10416
TAU=Q.from_float(1e-5)
HELPERS=(
 ('src/research8h_standalone_verify.py','708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f','strict_flow_kernel'),
 ('src/research8h_rational_witness_check.py','9cb836d420308a2ffc5b6e50e78cb565a823d5b65d1223c0f53d98910de5680d','research8h_rational_witness_check'),
 ('src/research8h_branch_flow_check.py','41dab33ed8e013d46fd7ae78974d95cab70e9794a906a7c6a12786bb093d4632','strict_flow_capped'),
 ('src/research8h_branch_flow_energy_check.py','13d1debeb82d76e595c2700554d39a27c5b01259e03b0d35edabe21e8c3175e9','strict_flow_uncapped'))
MANIFESTS=(
 (CAPPED+'/input_manifest.json','0981491f326dbd3f34e2825d501cbff54d74bf18e5c3d924edf420a4950532d4',103,'historical',''),
 (CAPPED+'/artifact_manifest.csv','a86ee29993a253e7018965cf9ce66dc177e220129eba849a4529960a09e237c4',277,'relative',''),
 (ENERGY+'/input_manifest.json','7ffffe82e6046daff5dcd610337c2e8cb333009c38ec9acfcdb9741f8cbadbb7',355,'historical',''),
 (ENERGY+'/artifact_manifest.csv','89475add4fdc688cf7227a201fa870712602cc67269b0ad7bacdfa7f8ef65648',466,'relative',''))


def need(value,message):
    if not value:raise ValueError(message)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    def pairs(items):
        data={}
        for k,v in items:need(k not in data,'Duplicate JSON key: '+k);data[k]=v
        return data
    def invalid(value):raise ValueError('Nonfinite JSON: '+value)
    return json.loads(Path(path).read_text(encoding='utf-8-sig'),object_pairs_hook=pairs,parse_constant=invalid)


def relative(value):
    need(type(value) is str and '\\' not in value,'Expected canonical POSIX relative path')
    p=PurePosixPath(value)
    need(value and not p.is_absolute() and ':' not in value and '..' not in p.parts and str(p)==value and value!='.','Unsafe relative path: '+value)
    return value


def historical(value):
    value=value.replace('\\','/')
    for prefix,target in ((OLD_NATIVE,ADDENDUM+'/rts_inputs'),(OLD_ROOT,'')):
        if value.startswith(prefix+'/'):
            tail=relative(value[len(prefix)+1:]);return relative(target+'/'+tail if target else tail)
    raise ValueError('Unmapped historical path: '+value)


def no_link(path):
    info=path.lstat()
    need(not stat.S_ISLNK(info.st_mode) and not (getattr(info,'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0x400)),'Link/reparse entry prohibited: '+str(path))


def records(path):
    if path.suffix=='.json':data=read(path)
    else:
        with path.open(encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f);need(len(reader.fieldnames or [])==3 and set(reader.fieldnames)=={'path','sha256','bytes'},'Manifest CSV schema');data=list(reader)
    need(type(data) is list and data,'Manifest list required');seen=set()
    for item in data:
        need(type(item) is dict and set(item)=={'path','sha256','bytes'},'Manifest record schema')
        name=item['path'].replace('\\','/');need(name.casefold() not in seen,'Duplicate/case-colliding manifest path');seen.add(name.casefold())
        need(re.fullmatch('[0-9a-f]{64}',item['sha256']) is not None and str(item['bytes']).isdigit(),'Invalid digest/size')
    return data


def exact_lower(model,cost,dual):
    need(len(cost)==model.cols and len(dual)==model.rows,'Objective/dual shape')
    need(all(math.isfinite(x) for x in (*cost,*dual,*model.lower,*model.upper)),'Nonfinite bound input')
    residual=list(map(Q,cost));beta=Q(0)
    for i,y in enumerate(dual):
        if not y:continue
        bound=model.row_lower[i] if y>0 else model.row_upper[i]
        need(math.isfinite(bound),'Selected infinite row endpoint');weight=Q(y);beta+=weight*Q(bound)
        for k in range(model.indptr[i],model.indptr[i+1]):residual[model.indices[k]]-=weight*Q(model.data[k])
    box=sum((r*Q(model.lower[j] if r>=0 else model.upper[j]) for j,r in enumerate(residual)),Q(0))
    return beta+box,beta,box,residual


def candidates(model,raw,zero=False):
    need(len(raw)==model.rows and all(math.isfinite(x) for x in raw),'Finite raw multiplier shape')
    answer=[('zero',[0.]*model.rows)] if zero else []
    for sign in (1,-1):
        values=[sign*x for x in raw]
        projected=[0. if (x>0 and not math.isfinite(model.row_lower[i])) or (x<0 and not math.isfinite(model.row_upper[i])) else x for i,x in enumerate(values)]
        answer.extend(((f'{sign:+d}_raw',values),(f'{sign:+d}_projected',projected)))
    return answer


class Replay:
    def __init__(self,root,output,digest,commit):
        self.root=root;self.output=output;self.used=set();self.manifests={};self.bindings={}
        need(re.fullmatch('[0-9a-f]{64}',digest) is not None and re.fullmatch('[0-9a-f]{40}',commit) is not None,'Explicit trusted hash/commit required')
        no_link(root);manifest=root/'FILE_MANIFEST.csv';no_link(manifest);need(sha(manifest)==digest,'Trusted outer manifest mismatch')
        self.package={relative(x['path']):x for x in records(manifest)}
        self.before=self.snapshot();need(set(self.before)==set(self.package)|{'FILE_MANIFEST.csv'},'Outer file-set mismatch')
        for name,item in self.package.items():need(self.before[name]==(int(item['bytes']),item['sha256']),'Outer payload mismatch: '+name)
        need(sha(Path(__file__))==sha(self.path(SELF)),'Executed wrapper differs from candidate')
        self.path(PROTOCOL)
        candidate=self.js('STRICT_FLOW_CANDIDATE.json')
        need(candidate==dict(schema='strict-flow-candidate-v1',evidence_commit=commit,scope=SCOPE),'Candidate commit/scope does not match trusted argument')
        self.digest=digest;self.commit=commit
        self.check_manifest(ADDENDUM+'/FILE_MANIFEST.csv','8b18311c646c0ae68d85765c57b690e2db5b5ffc071d1ab1b734b2db88d866b8',24,'relative',ADDENDUM)
        mapping=self.js(ADDENDUM+'/path_map.json')
        need(mapping['maps']==[dict(original_prefix=OLD_ROOT,portable_relative_root='.'),dict(original_prefix=OLD_NATIVE,portable_relative_root=ADDENDUM+'/rts_inputs')],'Changed explicit prefix map')
        source=self.js(ADDENDUM+'/source_bindings.json')
        need(source['native_file_count']==len(source['files'])==17 and source['native_bytes']==3734672 and not source['conflicting_provenance'],'Native addendum scope')
        for entry in source['files']:
            name=historical(entry['original_path']);need(name==ADDENDUM+'/'+relative(entry['portable_path']),'Native source mapping');self.check_binding(name,entry)
        for args in MANIFESTS:self.check_manifest(*args)
        # All input manifests discovered in a bound input manifest are followed explicitly.
        while True:
            pending=[name for name in self.bindings if PurePosixPath(name).name in ('input_manifest.json','input_manifest.csv') and name not in self.manifests]
            if not pending:break
            for name in sorted(pending):self.check_manifest(name,self.bindings[name][1],None,'historical','')
        need(sha(self.path(GEN))==GEN_SHA,'Pinned native generator bytes changed')
        modules=[self.import_pinned(*item) for item in HELPERS];self.v,self.primal,self.capped,self.uncapped=modules
        self.q=self.primal.parse_rat;self.enc=self.primal.rat;self.points={};self.energies={}
        self.review_gates()
        self.save('provenance',dict(status='STRICT_FLOW_PACKAGE_AND_PROVENANCE_PASS',payloads=len(self.package),historical_manifests=self.manifests,unique_bindings=len(self.bindings),package_manifest_sha256=digest,package_evidence_commit=commit,scope=SCOPE,native_reconstruction=False,optimizer_calls=0))

    def snapshot(self):
        result={};casefold=set()
        for p in self.root.rglob('*'):
            no_link(p)
            if p.is_file():
                name=relative(p.relative_to(self.root).as_posix());need(name.casefold() not in casefold,'Case-colliding package file');casefold.add(name.casefold());result[name]=(p.stat().st_size,sha(p))
        return result

    def path(self,name):
        name=relative(name);need(name in self.package,'Missing required package input: '+name)
        p=self.root/name;need(p.resolve().is_relative_to(self.root),'Escaping package path');no_link(p);self.used.add(name);return p

    def js(self,name):return read(self.path(name))

    def check_binding(self,name,item):
        p=self.path(name);value=(int(item['bytes']),item['sha256']);need(self.before[name]==value,'Historical hash/size mismatch: '+name)
        need(name not in self.bindings or self.bindings[name]==value,'Conflicting historical binding');self.bindings[name]=value

    def check_manifest(self,name,digest,count,mode,base):
        p=self.path(name);need(sha(p)==digest,'Pinned manifest changed: '+name);data=records(p)
        if count is not None:need(len(data)==count,'Manifest count changed: '+name)
        seen=set()
        for item in data:
            target=historical(item['path']) if mode=='historical' else relative((base+'/' if base else '')+relative(item['path'].replace('\\','/')))
            need(target not in seen,'Duplicate resolved manifest target');seen.add(target);self.check_binding(target,item)
        self.manifests[name]=dict(sha256=digest,entries=len(data),mode=mode,base=base)

    def import_pinned(self,name,digest,module_name):
        p=self.path(name);need(sha(p)==digest,'Unreviewed helper source: '+name)
        spec=importlib.util.spec_from_file_location(module_name,p);module=importlib.util.module_from_spec(spec);sys.modules[module_name]=module;spec.loader.exec_module(module);return module

    def save(self,name,data):
        need(re.fullmatch('[a-zA-Z0-9_]+',name) is not None,'Report basename')
        with (self.output/(name+'.json')).open('x',encoding='utf-8') as f:json.dump(data,f,indent=2,allow_nan=False);f.write('\n')
        print(json.dumps(dict(check=name,status=data.get('status','PASS'))),flush=True)

    def array(self,directory,name,key,size):return self.v.vector(self.v.read_npz(self.path(directory+'/'+name),(key,))[key],('<f8','|u1'),size,key)

    def model(self,directory):
        self.path(directory+'/matrix.npz');self.path(directory+'/bounds.npz');return self.v.load_model(self.root/directory)

    def labels(self,directory):
        with gzip.open(self.path(directory+'/row_metadata.csv.gz'),'rt',encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

    def objective(self,directory):
        meta=self.js(directory+'/model_metadata.json');expected=self.primal.native_spec(self.path(GEN),meta)
        need(self.js(directory+'/native_spec.json')==expected,'Native specification differs from exact pinned generator convention')
        fossil={i for i,x in enumerate(expected) if x['uid'] in meta['fossil_units']};need(len(fossil)==23 and '121_NUCLEAR_1' not in meta['fossil_units'],'Fossil roster')
        with self.path(GEN).open(encoding='utf-8-sig',newline='') as f:raw={x['GEN UID']:x for x in csv.DictReader(f)}
        need(fossil=={j for j,n in enumerate(meta['unit_names']) if raw[n]['Fuel'] in ('Coal','Oil','NG')},'Native fossil objective')
        cost=tuple(float(j<6888 and j%41 in fossil) for j in range(29400));need(self.array(directory,'objective.npz','objective',29400)==cost,'Actual fossil objective');return cost

    def review_gates(self):
        for folder,digest,status,count in ((R+'branch_flow_independent_review','b0820ff52180c1c20b6d34ef6189dce33b2344223dc58936285a72cc3284991b','INDEPENDENT_BRANCH_FLOW_POSTRUN_PASS',103),(R+'branch_flow_energy_independent_review','ccd2bf67e39d985082707f97116276b3534c11dbbbd20430fe3637bc49739985','INDEPENDENT_STRICT_BRANCH_ENERGY_POSTRUN_PASS',355)):
            p=self.path(folder+'/postrun_review.json');need(sha(p)==digest,'Independent postrun record changed');report=read(p)
            need(report['status']==status and report['frozen_bindings']==count and report['all_frozen_inputs_and_outputs_unchanged'],'Independent closure status')

    def point(self,directory,capped):
        model=self.model(directory);need((model.rows,model.cols)==(34513 if capped else 34512,29400),'Point model dimensions')
        mask=self.array(directory,'integrality.npz','integrality',29400);need(mask==MASK,'Complete original binary mask required')
        cost=self.objective(directory);labels=self.labels(directory);caps=[i for i,x in enumerate(labels) if x['family']=='fossil_energy_cap']
        if capped:
            need(len(caps)==1,'Capped row missing');i=caps[0]
            need(model.row_lower[i]==-math.inf and model.row_upper[i]==23195 and {model.indices[k]:model.data[k] for k in range(model.indptr[i],model.indptr[i+1])}=={j:x for j,x in enumerate(cost) if x},'Actual cap row')
        else:need(not caps,'Uncapped model contains cap')
        schedule=CAPPED+'/fixed_schedule.json' if capped else directory+'/fixed_schedule.json'
        self.path(directory+'/native_inputs.npz');self.path(directory+'/graph.json');self.path(schedule);p=self.path(directory+'/rational_point.json')
        helper=self.capped if capped else self.uncapped;result=helper.replay(self.root/directory,p,self.root/schedule)
        key='accepted_strict_capped' if capped else 'accepted_strict_uncapped';need(result[key] and result['tau']==0,'Strict full/native point failed')
        archived=self.js(directory+('/strict_point_check.json' if capped else '/identity_upper.json' if directory.endswith('/'+IDENTITY) else '/strict_uncapped_point_check.json'))
        need(result==archived,'Replayed strict point/native report differs')
        point=self.primal.read_point(self.v,p,self.root/directory);energy=sum((Q(c)*x for c,x in zip(cost,point)),Q(0));need(energy==self.q(result['exact_objective']),'Exact energy mismatch')
        self.points[directory]=point;self.energies[directory]=energy
        self.save(('capped_' if capped else 'uncapped_')+directory.rsplit('/',1)[1],dict(status='STRICT_BINARY_NATIVE_POINT_PASS',tau=0,energy=self.enc(energy),rows=model.rows,columns=model.cols,binary_coordinates=12096,point_sha256=sha(p)))

    def control(self):
        identity=self.points[CAPPED+'/'+IDENTITY];point=self.points[CAPPED+'/'+CONTROL]
        data=self.v.read_npz(self.path(CAPPED+'/'+CONTROL+'/native_inputs.npz'),('pmin','pmax','net','rows','source_hour','nodal'));order=data['source_hour'].values
        need(sorted(order)==list(range(168)) and sum(t!=s for t,s in enumerate(order))==14,'Fixed control permutation')
        with self.path(CAPPED+'/'+CONTROL+'/permutation.csv').open(encoding='utf-8-sig',newline='') as f:csv_order=list(csv.DictReader(f))
        need(tuple(int(x['source_hour_0based']) for x in csv_order)==order and tuple(int(x['new_hour_0based']) for x in csv_order)==tuple(range(168)),'Control CSV map')
        original=self.v.read_npz(self.path(CAPPED+'/'+IDENTITY+'/native_inputs.npz'),('pmin','pmax','net','rows','source_hour','nodal'))
        for name in ('pmin','pmax','net','rows','nodal'):
            width=math.prod(original[name].shape[1:]) if len(original[name].shape)>1 else 1
            need(data[name].values==tuple(x for s in order for x in original[name].values[s*width:(s+1)*width]),'Control native package mapping')
        need(point[6888:18984]==identity[6888:18984],'Control chronological states changed')
        for t,s in enumerate(order):
            for offset,width in ((0,41),(18984,24),(23016,38)):need(point[offset+t*width:offset+(t+1)*width]==identity[offset+s*width:offset+(s+1)*width],'Control point mapping')
        need(self.energies[CAPPED+'/'+CONTROL]==self.energies[CAPPED+'/'+IDENTITY],'Control energy changed');self.save('control_mapping',dict(status='STRICT_CONTROL_MAPPING_PASS',changed_hours=14))

    def cap_deletion(self,case):
        full=self.model(CAPPED+'/'+case);uncapped=self.model(ENERGY+'/'+case);mapping=self.js(ENERGY+'/'+case+'/cap_deletion.json');keep=mapping['parent_rows'];labels=self.labels(CAPPED+'/'+case)
        caps=[i for i,x in enumerate(labels) if x['family']=='fossil_energy_cap'];need(len(caps)==1 and keep==[i for i in range(full.rows) if i!=caps[0]] and mapping['deleted_row']==caps[0],'Only cap deletion map')
        need(mapping['parent_bindings']==self.primal.model_bindings(self.root/CAPPED/case),'Cap parent hash map')
        need(uncapped.rows==34512 and uncapped.cols==full.cols==29400 and uncapped.lower==full.lower and uncapped.upper==full.upper,'Cap deletion boxes/shapes')
        for new,old in enumerate(keep):
            a,b=uncapped.indptr[new:new+2];c,d=full.indptr[old:old+2]
            need(uncapped.indices[a:b]==full.indices[c:d] and uncapped.data[a:b]==full.data[c:d] and uncapped.row_lower[new]==full.row_lower[old] and uncapped.row_upper[new]==full.row_upper[old],'Non-cap row changed')
        for name in ('integrality.npz','objective.npz','native_inputs.npz','permutation.csv','graph.json','native_spec.json'):
            need(sha(self.path(ENERGY+'/'+case+'/'+name))==sha(self.path(CAPPED+'/'+case+'/'+name)),'Cap deletion source copy changed: '+name)

    def rays(self,case):
        directory=CAPPED+'/'+case;model=self.model(directory);raw=self.array(directory,'raw_solver_ray.npz','ray',model.rows)
        original=self.js(directory+'/classification.json');reports=[];select=None
        for (name,values),old in zip(candidates(model,raw),original['ray_candidates']):
            orientation=int(name.split('_')[0]);kind=name.split('_')[1];file='ray_'+name+'.json';certificate=self.js(directory+'/'+file)
            need(old['orientation']==orientation and old['kind']==kind and old['certificate_file']==file,'Ray order')
            need(certificate['orientation']==orientation and certificate['candidate']==kind and certificate['multipliers']==[dict(row=i,value_hex=x.hex()) for i,x in enumerate(values) if x],'Raw sign/projection changed')
            need(certificate['model_artifacts']=={n:sha(self.path(directory+'/'+n)) for n in ('matrix.npz','bounds.npz')} and certificate['raw_solver_ray_sha256']==sha(self.path(directory+'/raw_solver_ray.npz')) and certificate['row_metadata_sha256']==sha(self.path(directory+'/row_metadata.csv.gz')) and certificate['experiment_manifest_sha256']==MANIFESTS[0][1],'Ray artifact binding')
            try:result=self.v.check_ray(model,{i:Q(x) for i,x in enumerate(values) if x},TAU)
            except self.v.InvalidInput as error:
                need(old.get('rejected_reason')==str(error) and 'verification' not in certificate,'Ray rejection differs');reports.append(dict(candidate=name,rejected=True));continue
            need(certificate['verification']==result and old['verification']==result,'Exact ray result differs');reports.append(dict(candidate=name,verification=result))
        need(len(original['ray_candidates'])==len(reports)==4,'All four ray candidates required')
        select=next((x for x in reports if x.get('verification',{}).get('expanded_pass')),None) or next((x for x in reports if x.get('verification',{}).get('strict_pass')),None)
        need(select is not None and select['verification']['strict_pass'] and select['verification']['expanded_pass'] and original['robust_expanded'] is True and original['selected']['certificate_file']=='ray_'+select['candidate']+'.json' and original['binary_status']=='CERTIFIED_VARIANT_NEGATIVE','Ray selection/classification')
        self.save('rays_'+case,dict(status='STRICT_AND_EXPANDED_NEGATIVE_REPLAY_PASS',candidates=reports,selected=select['candidate']))

    def lower(self,case):
        directory=ENERGY+'/'+case;model=self.model(directory);cost=self.objective(directory);raw=self.array(directory,'raw_row_dual.npz','row_dual',model.rows);reports=[];best=None
        for name,dual in candidates(model,raw,True):
            old=self.js(directory+'/lower_'+name+'.json');need(old['candidate']==name and old['model_bindings']==self.primal.model_bindings(self.root/directory) and old['raw_dual_sha256']==sha(self.path(directory+'/raw_row_dual.npz')),'Lower artifact bindings')
            need(old['multipliers']==[dict(row=i,value_hex=x.hex()) for i,x in enumerate(dual) if x],'Lower raw/sign projection')
            try:value,beta,box,residual=exact_lower(model,cost,dual)
            except ValueError as error:
                need(old['valid'] is False and old['reason']==str(error),'Lower rejection mismatch');reports.append(dict(candidate=name,valid=False));continue
            need(old['valid'] is True and old['tau']==0 and self.q(old['lower_bound'])==value and self.q(old['row_term'])==beta and self.q(old['box_term'])==box,'Exact strict objective bound mismatch')
            need(old['residual']==[dict(column=j,value=self.enc(x)) for j,x in enumerate(residual) if x],'Exact residual mismatch')
            reports.append(dict(candidate=name,valid=True,lower=self.enc(value)))
            if best is None or value>best[1]:best=(name,value)
        selected=self.js(directory+'/lower_bound.json');need(best is not None and best[1]>=0 and selected['selected']==dict(candidate=best[0],lower_bound=self.enc(best[1])) and selected['candidates']==[dict(candidate=x['candidate'],valid=x['valid']) for x in reports],'Selected lower bound mismatch')
        self.save('lower_'+case,dict(status='EXACT_STRICT_LOWER_REPLAY_PASS',selected=best[0],lower=self.enc(best[1]),candidates=reports));return best[1]

    def ledger(self):
        capcalls=self.js(CAPPED+'/calls.json');energycalls=self.js(ENERGY+'/calls.json')
        need([x['case'] for x in capcalls]==['identity_proposal',*TARGETS] and len(capcalls)==3 and all(x['optimizer_calls']==1 for x in capcalls),'Capped three-call ledger')
        need([x['case'] for x in energycalls]==[IDENTITY,*TARGETS,*(x+'_proposal' for x in TARGETS)] and len(energycalls)==5 and all(x['optimizer_calls']==1 for x in energycalls),'Energy five-call ledger')
        for base,calls,count in ((CAPPED,capcalls,3),(ENERGY,energycalls,5)):
            complete=self.js(base+'/completion.json');need(complete['optimizer_calls']==count and math.isclose(complete['actual_solve_seconds'],math.fsum(x['actual_seconds'] for x in calls),rel_tol=0.,abs_tol=1e-9),'Call total mismatch')
        cappedhours=self.js(CAPPED+'/identity_proposal/hour_outcomes.json');need(len(cappedhours)==168 and all(x==dict(hour=i,status='EXACT_HOUR_POINT') for i,x in enumerate(cappedhours)),'Capped hour denominator')
        for case in TARGETS:
            path=ENERGY+'/'+case+'_proposal';ledger=self.js(path+'/hour_outcomes.json');need(len(ledger)==168 and all(x==dict(hour=i,status='EXACT_HOUR_POINT') for i,x in enumerate(ledger)),'Target hour denominator')
            point=self.points[ENERGY+'/'+case]
            for t in range(168):
                hour=self.js(path+f'/hour_{t:03d}.json');columns=list(range(41*t,41*(t+1)))+list(range(18984+24*t,18984+24*(t+1)))+list(range(23016+38*t,23016+38*(t+1)))
                need(hour['status']=='EXACT_HOUR_POINT' and hour['exact_hour_pass'] and [r['column'] for r in hour['values']]==columns and all(self.q(r['value'])==point[r['column']] for r in hour['values']),'Hourly candidate/full point mismatch')
        self.save('ledgers',dict(status='FIXED_CALL_AND_HOUR_LEDGER_PASS',historical_solver_calls=8,wrapper_solver_calls=0,energy_target_hours=336,capped_identity_hours=168))

    def run_math(self):
        self.point(CAPPED+'/'+IDENTITY,True);self.point(CAPPED+'/'+CONTROL,True);self.control()
        for case in TARGETS:self.rays(case)
        for case in (IDENTITY,*TARGETS):self.cap_deletion(case);self.point(ENERGY+'/'+case,False)
        lower={case:self.lower(case) for case in (IDENTITY,*TARGETS)};outcomes=self.js(ENERGY+'/outcomes.json')
        li=lower[IDENTITY];ui=self.energies[ENERGY+'/'+IDENTITY];need(li<=ui and self.q(outcomes['identity_lower'])==li and self.q(outcomes['identity_upper'])==ui,'Identity interval')
        result=[];need(outcomes['target_denominator']==2 and outcomes['target_hour_denominator']==336 and len(outcomes['targets'])==2,'Energy denominator')
        for case,old in zip(TARGETS,outcomes['targets']):
            lt=lower[case];ut=self.energies[ENERGY+'/'+case];need(0<=lt<=ut and li>0,'Finite nonnegative energy enclosure')
            need(old['case']==case and old['status']=='FINITE_STRICT_INTERVAL' and self.q(old['lower'])==lt and self.q(old['upper'])==ut,'Target enclosure')
            delta=(lt-ui,ut-li);ratio=(100*(lt/ui-1),100*(ut/li-1))
            need(self.q(old['penalty_lower'])==delta[0] and self.q(old['penalty_upper'])==delta[1] and old['strictly_positive']==(delta[0]>0) and tuple(map(self.q,old['percent_interval']))==ratio,'Penalty/ratio arithmetic')
            result.append(dict(case=case,lower=self.enc(lt),upper=self.enc(ut),penalty=[self.enc(x) for x in delta],percent=[self.enc(x) for x in ratio],strictly_positive=delta[0]>0))
        self.save('intervals',dict(status='FINITE_STRICT_ENERGY_INTERVALS_PASS',targets=result));self.ledger()

    def finish(self,start):
        after=self.snapshot();need(after==self.before,'Package files/bytes changed during replay')
        self.save('summary',dict(status='PORTABLE_STRICT_FLOW_REPLAY_PASS',scope=SCOPE,strict_points=5,selected_negative_certificates=2,ray_candidates=8,selected_lower_bounds=3,lower_candidates=15,penalty_intervals=2,optimizer_calls=0,network_calls=0,native_reconstruction=False,package_files_unchanged=True,package_manifest_sha256=self.digest,package_evidence_commit=self.commit,used_package_files=len(self.used),elapsed_seconds=time.perf_counter()-start,python=sys.version,platform=sys.platform,second_machine_claim=False))


def focused():
    for bad in ('../x','/x','a/../x','C:/x','a//b','a\\b'):
        try:relative(bad)
        except ValueError:pass
        else:raise ValueError('Unsafe path accepted')
    m=SimpleNamespace(rows=1,cols=1,lower=(0.,),upper=(10.,),row_lower=(3.,),row_upper=(math.inf,),indptr=(0,1),indices=(0,),data=(1.,))
    need(exact_lower(m,(2.,),(1.,))[0]==3,'Residual bound fixture');need(exact_lower(m,(-1.,),(0.,))[0]==-10,'Upper-box fixture')
    need([name for name,_ in candidates(m,(-1.,),True)]==['zero','+1_raw','+1_projected','-1_raw','-1_projected'],'Candidate order fixture')
    need(candidates(m,(-1.,),True)[2][1]==[0.],'Sign-only projection fixture')
    return dict(status='FOCUSED_STRICT_FLOW_CHECKS_PASS',path_rejections=6,arithmetic_checks=4,old_kernel_tests_repeated=False)


def main():
    need(sys.flags.isolated==1 and sys.flags.no_site==1,'Run with Python -I -S')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root',required=True,type=Path);parser.add_argument('--report-dir',required=True,type=Path)
    parser.add_argument('--expected-package-manifest-sha256',required=True);parser.add_argument('--package-evidence-commit',required=True);args=parser.parse_args()
    no_link(args.package_root);root=args.package_root.resolve();output=args.report_dir.resolve()
    need(root.is_dir() and not output.exists() and not output.is_relative_to(root) and not root.is_relative_to(output),'Fresh report directory must be outside package')
    for parent in (args.report_dir,*args.report_dir.parents):
        if parent.exists():no_link(parent)
    output.mkdir(parents=True,exist_ok=False);start=time.perf_counter()
    try:
        replay=Replay(root,output,args.expected_package_manifest_sha256,args.package_evidence_commit)
        replay.save('focused_checks',focused());replay.run_math();replay.finish(start)
    except Exception as error:
        report=dict(status='PORTABLE_STRICT_FLOW_REPLAY_FAILED',error_type=type(error).__name__,error=str(error),elapsed_seconds=time.perf_counter()-start,optimizer_calls=0,partial_external_reports_preserved=True)
        with (output/'failure.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
        print(json.dumps(report),flush=True);return 1
    return 0


if __name__=='__main__':raise SystemExit(main())
