"""Invented NPZ-schema controls only; no historical point or cut arithmetic."""
from pathlib import Path
import ast,hashlib,importlib.util,json,struct,sys,zipfile
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
SOURCE=ROOT/'src/researchnext_union_affine_cut_schema2.py';KERNEL=ROOT/'src/research8h_standalone_verify.py'
assert hashlib.sha256(KERNEL.read_bytes()).hexdigest()=='708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f'
ast.parse(SOURCE.read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('invented_npz_schema_decoder',KERNEL);v=importlib.util.module_from_spec(spec);sys.modules[spec.name]=v;spec.loader.exec_module(v)
def npy(values):
    header=repr(dict(descr='<f8',fortran_order=False,shape=(len(values),))).encode('ascii')+b'\n'
    return b'\x93NUMPY\x01\x00'+struct.pack('<H',len(header))+header+struct.pack('<'+'d'*len(values),*values)
values={'vector':(1.0,-0.0),'row_value':(3.0,),'row_dual':(0.5,),'col_dual':(0.0,0.0)}
def archive(name,items):
    p=OUT/name
    with zipfile.ZipFile(p,'x',compression=zipfile.ZIP_STORED) as z:
        for key,data in items.items():z.writestr(key+'.npy',npy(data))
    return p
p=archive('invented_four_members.npz',values);schema=tuple(values);loaded=v.read_npz(p,schema)
selected=v.vector(loaded['vector'],('<f8',),2,'invented point')
assert struct.pack('<2d',*selected)==struct.pack('<2d',*values['vector'])
checks=['complete four-member schema and unchanged signed-zero vector']
def reject(name,fn):
    try:fn()
    except v.InvalidInput:checks.append(name);return
    raise AssertionError(name)
reject('old single-member expectation rejects four-member archive',lambda:v.read_npz(p,('vector',)))
missing=archive('invented_missing_member.npz',{k:x for k,x in values.items() if k!='row_dual'})
reject('missing member rejected',lambda:v.read_npz(missing,schema))
extra=archive('invented_extra_member.npz',{**values,'unrequested':(1.0,)})
reject('unexpected member rejected',lambda:v.read_npz(extra,schema))
receipt=dict(status='PASS_INVENTED_SCHEMA_ONLY',checks=checks,source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    fixture_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),historical_arrays_read=0,cut_arithmetic=0,optimizer_calls=0)
with (OUT/'SCHEMA_FIXTURES.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt))
