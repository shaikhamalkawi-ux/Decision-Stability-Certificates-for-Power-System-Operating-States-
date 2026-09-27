"""Portable exact verification of one archived necessary state cut, without a solver."""
from pathlib import Path, PurePosixPath
from fractions import Fraction as F
import argparse, gzip, hashlib, importlib.util, json, math, sys, time
sys.dont_write_bytecode=True
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def q(pair):
 need(type(pair) is list and len(pair)==2 and all(type(x)is str and len(x)<2500 for x in pair),'Unsupported rational record')
 a=F(int(pair[0]),int(pair[1]));need(pair==[str(a.numerator),str(a.denominator)],'Noncanonical rational');return a
def pair(a):return [str(a.numerator),str(a.denominator)]
def reconstruct(m,mask,state,d,tau):
 need(len(mask)==m.cols and len(d)==m.rows and len(state)==sum(mask),'Complete matrix/state dimensions')
 need(all(type(x)is int and x in(0,1) for x in mask),'Exact original binary mask')
 need(set(state)=={j for j,b in enumerate(mask) if b},'State coordinates')
 need(all(type(z)is int and z in(0,1) and m.lower[j]<=z<=m.upper[j] for j,z in state.items()),'Exact admissible nominated bits')
 need(all(math.isfinite(a) and math.isfinite(b) and a<=b for a,b in zip(m.lower,m.upper)),'Finite ordered original boxes')
 need(all(a<=b for a,b in zip(m.row_lower,m.row_upper)),'Ordered original rows')
 need(tau>=0,'Nonnegative exact expansion')
 full=[F(0)]*m.cols;beta=F(0)
 for r,w in enumerate(d):
  if w:
   endpoint=m.row_lower[r] if w>0 else m.row_upper[r];need(math.isfinite(endpoint),'Finite signed endpoint')
   beta+=w*F(endpoint)
   for k in range(m.indptr[r],m.indptr[r+1]):full[m.indices[k]]+=w*F(m.data[k])
 support=sum((a*F(m.upper[j] if a>=0 else m.lower[j]) for j,a in enumerate(full) if not mask[j]),F(0))
 rn=sum(map(abs,d),F(0));cn=sum((abs(a) for j,a in enumerate(full) if not mask[j]),F(0))
 rhs=beta-support-tau*(rn+cn);lhs=sum((full[j]*z for j,z in state.items()),F(0))
 return dict(full=full,beta=beta,continuous_support=support,original_row_norm=rn,continuous_q_norm=cn,tau_loss=tau*(rn+cn),cut_rhs=rhs,nominee_state_value=lhs,expanded_margin=rhs-lhs)
def verify(folder,expected):
 started=time.perf_counter();root=Path(folder).resolve();mp=root/'MANIFEST.json';need(sha(mp)==expected,'Externally supplied manifest hash')
 manifest=read(mp);need(manifest['schema']=='portable_state_cut_v1','Bundle schema');paths={}
 for e in manifest['files']:
  rel=PurePosixPath(e['path']);need(not rel.is_absolute() and all(x not in ('..','.') for x in rel.parts) and ':' not in e['path'] and '\\' not in e['path'],'Portable confined relative path')
  path=(root/str(rel)).resolve();need(path.is_relative_to(root) and path.is_file() and e['path'] not in paths,'Unique confined file')
  need(path.stat().st_size==e['bytes'] and sha(path)==e['sha256'],'Bundle file bytes: '+e['path']);paths[e['path']]=path
 needed={'verify.py','decoder.py','model/matrix.npz','model/bounds.npz','model/integrality.npz','model/column_maps.json','model/row_origins.json','certificate.json.gz','fixed_schedule.json','README.md'}
 need(set(paths)==needed,'Exact declared bundle roles');need(sha(__file__)==sha(paths['verify.py']),'Executing bundled verifier bytes')
 need(sha(paths['decoder.py'])=='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f','Reviewed stdlib NPZ decoder')
 spec=importlib.util.spec_from_file_location('portable_state_cut_decoder',paths['decoder.py']);v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
 m=v.load_model(root/'model');mask=tuple(v.vector(v.read_npz(paths['model/integrality.npz'],('integrality',))['integrality'],('|u1',),m.cols,'binary mask'))
 with gzip.open(paths['certificate.json.gz'],'rt',encoding='utf-8') as f:c=json.load(f)
 entries=read(paths['fixed_schedule.json'])['fixed_columns'];state={e['column']:e['value'] for e in entries};need(len(state)==len(entries),'Unique state records')
 need(c['nominee_sha256']==sha(paths['fixed_schedule.json']),'Certificate nominee binding')
 need(c['model_bindings']=={n:sha(paths['model/'+n]) for n in('matrix.npz','bounds.npz','integrality.npz','column_maps.json','row_origins.json')},'Original model role bindings')
 tau=q(manifest['tau']);d=[q(x) for x in c['original_d']];r=reconstruct(m,mask,state,d,tau)
 need([q(x) for x in c['full_A_transpose_d']]==r['full'],'Every original residual coefficient')
 for key,value in r.items():
  if key!='full':need(q(c[key])==value,'Exact archived scalar: '+key)
 need(r['expanded_margin']>0 and c['strictly_positive_expanded_margin'] is True,'Strict exact fixed-state separation')
 need(c['extra_binary_tau']==c['derived_row_extra_tau']==0,'No extra derived/state expansion')
 for rel,path in paths.items():need(sha(path)==next(e['sha256'] for e in manifest['files'] if e['path']==rel),'Files unchanged')
 return dict(status='PASS_EXACT_FIXED_STATE_REJECTION',manifest_sha256=expected,rows=m.rows,columns=m.cols,binary_coordinates=sum(mask),exact_margin=pair(r['expanded_margin']),tau=pair(tau),solver_calls=0,external_paths_read=0,elapsed_seconds=time.perf_counter()-started,scope='One original expanded-matrix necessary cut and fixed-state rejection. No optimizer/backend/provenance replay, physical remapping, fractional full-point replay, unrestricted common exclusion or second-machine claim.')
def selftest():
 class Toy:
  rows=1;cols=2;data=(1.,1.);indices=(0,1);indptr=(0,2);row_lower=(1.5,);row_upper=(3.,);lower=(0.,0.);upper=(1.,1.)
 a=reconstruct(Toy(),(1,0),{0:0},[F(2)],F(1,16));need(a['cut_rhs']==F(3,4) and a['expanded_margin']==F(3,4),'Signed row plus both expansion losses')
 b=reconstruct(Toy(),(1,0),{0:1},[F(2)],F(1,16));need(b['expanded_margin']==F(-5,4),'Another state is preserved')
 c=reconstruct(Toy(),(1,0),{0:0},[F(-2)],F(1,16));need(c['cut_rhs']==F(-25,4),'Negative endpoint and continuous lower support')
 try:reconstruct(Toy(),(1,0),{0:0.5},[F(2)],F(0))
 except ValueError:pass
 else:raise AssertionError('Nonbinary state accepted')
 print(json.dumps(dict(status='PASS_INVENTED_CONTROLS',scientific_inputs=0,solver_calls=0)))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--self-test',action='store_true');p.add_argument('--bundle');p.add_argument('--manifest-sha256');a=p.parse_args()
 if a.self_test:need(not a.bundle and not a.manifest_sha256,'Separate control mode');selftest()
 else:need(a.bundle and a.manifest_sha256,'Bundle and externally published manifest hash required');print(json.dumps(verify(a.bundle,a.manifest_sha256),indent=2))
