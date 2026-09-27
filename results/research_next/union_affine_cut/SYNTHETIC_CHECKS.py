"""Invented endpoint arithmetic only; no scientific arrays or optimizer."""
from pathlib import Path
import hashlib,importlib.util,json,sys
from fractions import Fraction as F
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'src/researchnext_union_affine_cut.py'
spec=importlib.util.spec_from_file_location('affine_cut_synthetic_only',SOURCE);a=importlib.util.module_from_spec(spec);sys.modules[spec.name]=a;spec.loader.exec_module(a)
tau=F(1,100);checks=[]
def passed(name,condition):
    assert condition,name
    checks.append(dict(name=name,pass_=True))
def rejects(name,fn):
    try:fn()
    except ValueError:checks.append(dict(name=name,pass_=True));return
    raise AssertionError(name+' was accepted')
q,r=a.upper_endpoint({0:F(2),1:F(3)},F(10),'upper',tau)
nq,nr,w=a.normalize_generation(q,r,0,False)
passed('positive coefficient upper',nq=={0:F(1),1:F(3,2)} and nr==F(5)+tau/2 and w==F(1,2))
q,r=a.upper_endpoint({0:F(2),1:F(3)},F(10),'lower',tau)
nq,nr,w=a.normalize_generation(q,r,0,True)
passed('positive coefficient lower',nq=={0:F(-1),1:F(-3,2)} and nr==F(-5)+tau/2 and w==F(1,2))
q,r=a.upper_endpoint({0:F(-2),1:F(3)},F(4),'upper',tau)
nq,nr,w=a.normalize_generation(q,r,0,True)
passed('negative coefficient upper becomes lower',nq=={0:F(-1),1:F(3,2)} and nr==F(2)+tau/2)
q,r=a.upper_endpoint({0:F(-2),1:F(3)},F(4),'lower',tau)
nq,nr,w=a.normalize_generation(q,r,0,False)
passed('negative coefficient lower becomes upper',nq=={0:F(1),1:F(-3,2)} and nr==F(-2)+tau/2)
endpoints={('row',0,'upper'):a.upper_endpoint({0:F(-1),1:F(2)},F(0),'upper',tau),('row',1,'upper'):a.upper_endpoint({0:F(1)},F(7),'upper',tau)}
weights={k:F(1) for k in endpoints}
vec,rhs=a.combine_endpoints(endpoints.__getitem__,weights,2,lambda:None)
passed('full generation cancellation and summed tolerance',vec==[F(0),F(2)] and rhs==F(7)+2*tau)
rejects('wrong inequality direction',lambda:a.normalize_generation({0:F(-2)},F(1),0,False))
rejects('zero generation coefficient',lambda:a.normalize_generation({1:F(2)},F(1),0,True))
rejects('negative endpoint multiplier',lambda:a.combine_endpoints(endpoints.__getitem__,{('row',0,'upper'):F(-1)},2,lambda:None))
rejects('out of range original column',lambda:a.combine_endpoints(endpoints.__getitem__,weights,1,lambda:None))
wrong=dict(endpoints);wrong[('row',0,'upper')]=a.upper_endpoint({0:F(-1),1:F(2)},F(0),'upper',2*tau)
wv,wr=a.combine_endpoints(wrong.__getitem__,weights,2,lambda:None)
rejects('wrong tau changes exact certificate endpoint',lambda:a.need(wr==rhs,'Wrong exact endpoint sum'))
rejects('invalid endpoint side',lambda:a.upper_endpoint({0:F(1)},F(0),'invalid',tau))
receipt=dict(status='PASS_INVENTED_ARITHMETIC_ONLY',checks=checks,count=len(checks),scientific_model_reads=0,optimizer_calls=0,
    source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),fixture_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
with (Path(__file__).parent/'SYNTHETIC_CHECKS.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt))
