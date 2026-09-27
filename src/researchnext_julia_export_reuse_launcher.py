"""Prepare one offline native export; launch only after explicit external review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, sys, threading, time, tomllib

REPO = Path(__file__).resolve().parents[1]
BASE = REPO / '.work/researchnext_julia_export'
SETUP = BASE / 'setup_reuse01'
SECONDARY = BASE / 'setup_efficient01/depot'
ENVOUT = REPO / 'results/research_next/orlib_julia_export/setup_reuse01'
PREP = ENVOUT.parent / 'official_export_reuse01_prepared'
OUT = ENVOUT.parent / 'official_export_reuse01_launcher'
EXPORT_OUT = ENVOUT.parent / 'official_export_reuse01'
PRIVATE = BASE / 'official_export_reuse01_launcher'
EXPORTER = REPO / 'src/researchnext_julia_export_reuse.jl'
PROTOCOL = REPO / 'docs/research_next/ORLIB_JULIA_REUSE_EXPORT_PROTOCOL.md'
JULIA = BASE / 'attempt01/runtime/julia-1.6.7/bin/julia.exe'
CASE = REPO / 'results/research_next/orlib_preflight/solver_prepared01/inputs/selected_case.json.gz'
PYMODEL = CASE.with_name('identity__native_penalized.json')
RECEIPT_SHA = 'fd3f2db6f0a62ecb0733ef903ff5ac0760b6375f7c723f14e536983ad1839872'
MANIFEST_SHA = '2434d5a9878bd443e95e339dd0b71e1632bc61988fd1272af54461f6bad9d831'
PROJECT_SHA = '02e2d39820e8f8b03404d75ff1970764c68309e6afee996571d229c4cf84690a'
INVENTORY_SHA = '76f9343b5519f590e25d5d97c6f34e080f146a650dd32478240cdee973f8ea5d'
SELECTED_SHA = 'c90c9c9b43f47a5d2c0235a5792eedefa9eb0ab199f709385e6fa21d48fa293b'
PREPARED_SETUP_SHA = '6113f906703d29da0177e666f1fc66eda0854efb4432ff2017197997186cc4d2'
UC = '4f04f0dd6641b071fd7556346c3d7190c2ffdfe5'
UC_TREE = '619a6b12e1005425e6ac08c4c45e445bb0a6f134'
VERSIONS = {'UnitCommitment':'0.4.0','JuMP':'1.15.1','MathOptInterface':'1.20.1','PackageCompiler':'1.7.7'}

def utc(): return datetime.now(timezone.utc).isoformat()
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, d):
    with p.open('x', encoding='utf-8') as f:
        json.dump(d, f, indent=2, allow_nan=False); f.write('\n')
def plain(p):
    for q in (p, *p.parents):
        if q.exists():
            st=q.lstat()
            assert not q.is_symlink() and not getattr(st,'st_file_attributes',0)&0x400, 'Link/reparse path rejected'
def bind(p, expected, bindings):
    plain(p); assert p.is_file() and digest(p)==expected, 'Input binding mismatch: '+str(p)
    if str(p) in bindings: assert bindings[str(p)]==expected
    bindings[str(p)]=expected

def admitted_bindings():
    b={}
    fixed=[(ENVOUT/'ENVIRONMENT_ACQUISITION.json', RECEIPT_SHA),
           (SETUP/'project/Manifest.toml', MANIFEST_SHA),(ENVOUT/'Manifest.toml',MANIFEST_SHA),
           (SETUP/'project/Project.toml',PROJECT_SHA),(ENVOUT/'Project.toml',PROJECT_SHA),
           (SETUP/'package_inventory.toml',INVENTORY_SHA),(ENVOUT/'package_inventory.toml',INVENTORY_SHA),
           (ENVOUT/'selected_registry_and_installed_metadata.json',SELECTED_SHA),
           (ENVOUT.parent/'reuse_prepared01/prepared.json',PREPARED_SETUP_SHA),
           (CASE,'6ef95ef5a1966914306da848f2ffa4bd835c49d520e30b1dcbcfa948eee85cbe'),
           (PYMODEL,'5abc7c12289d6428081f49646553863abaa041abfd4bac6215d7d49130b2f725'),
           (JULIA,'29ebe4b29362a2e380848dd4803e67343fe1779207b4970390418a1d495da67f'),
           (REPO/'src/researchnext_julia_export.jl','e7429f67a3d984976c84081acb3845dbd1238f198afb21b49266d87fae3d9088'),
           (REPO/'docs/research_next/ORLIB_JULIA_EXPORT_PROTOCOL.md','c1d21f79ed26f53c23e771b627b8291656c8fd9c7c3e8db4a2009b1686dad17b')]
    for p, h in fixed: bind(p,h,b)
    for p in (Path(__file__).resolve(),EXPORTER,PROTOCOL): bind(p,digest(p),b)
    d=json.loads((ENVOUT/'ENVIRONMENT_ACQUISITION.json').read_text())
    assert d['status']=='READY_ENVIRONMENT_ONLY_NO_MODEL_BUILD' and d['julia_exit_code']==0
    assert d['Julia_invocations']==d['Pkg_add_calls']==1 and not d['stream_errors']
    assert d['scientific_model_builds']==d['optimizer_calls']==0
    assert not d['owned_parent_alive_after_postlaunch_guard']
    assert d['prepared_sha256']==PREPARED_SETUP_SHA
    assert d['source_sha256']=='2e1add47952cbeb1f2a26800619277623c4b8975118fe19e933b7680eea61a3a'
    assert d['protocol_sha256']=='eb1f8a857ca8228bcf33b7bb85fdddf4c157d49295883c3fc52fa0b0b7b51a2b'
    assert all(d[k] for k in ('source_unchanged_at_closure','protocol_unchanged_at_closure','admitted_archive_unchanged_at_closure'))
    assert d['installed_direct_versions']==VERSIONS and d['selected_package']['git_revision']==UC and d['selected_package']['tree_hash']==UC_TREE
    assert not d['whole_disk_registry_readback_completed']
    assert d['Windows_installed_archive_full_tree_verification']=='NOT_ESTABLISHED_BY_PKG_INSTALL_ARCHIVE'
    a={x['path']:x['sha256'] for x in d['artifacts']}
    for name,h in (('Manifest.toml',MANIFEST_SHA),('Project.toml',PROJECT_SHA),('package_inventory.toml',INVENTORY_SHA),('selected_registry_and_installed_metadata.json',SELECTED_SHA)):
        assert a[name]==h
    setup_prep=json.loads((ENVOUT.parent/'reuse_prepared01/prepared.json').read_text())
    for row in setup_prep['bindings']: bind(Path(row['path']),row['sha256'],b)
    meta=json.loads((ENVOUT/'selected_registry_and_installed_metadata.json').read_text())
    for row in meta['selected_registry_metadata']:
        p=Path(row['path']); assert p.resolve().is_relative_to((SECONDARY/'registries/General').resolve())
        bind(p,row['sha256'],b)
    for row in meta['installed_project_metadata']:
        p=Path(row['path']); assert p.resolve().is_relative_to((SETUP/'depot/packages').resolve())
        bind(p,row['sha256'],b)
    assert {p.name for p in SECONDARY.iterdir()}=={'registries'}
    assert {p.name for p in (SECONDARY/'registries').iterdir()}=={'General'}
    assert not (SECONDARY/'registries/General/.git').exists() and not (SECONDARY/'registries/General/.tree_info.toml').exists()
    if (SETUP/'depot/registries').exists(): assert not list((SETUP/'depot/registries').iterdir())
    native=Path(d['selected_package']['source']); assert native.resolve().is_relative_to((SETUP/'depot/packages').resolve())
    assert len(d['pinned_native_files_verified'])==18 and len({x['path'] for x in d['pinned_native_files_verified']})==18
    for row in d['pinned_native_files_verified']:
        p=native/row['path']; assert p.resolve().is_relative_to(native.resolve()); bind(p,row['sha256'],b)
    inventory=tomllib.loads((SETUP/'package_inventory.toml').read_text())
    assert inventory['julia_version']=='1.6.7'
    assert inventory['depot_path']==[str(SETUP/'depot'),str(SECONDARY)]
    packages=inventory['packages']; assert len(packages)==110 and len({x['uuid'] for x in packages})==110
    for row in packages:
        p=Path(row['source']); plain(p)
        root=(JULIA.parent.parent/'share/julia/stdlib') if row['is_stdlib'] else SETUP/'depot/packages'
        assert p.resolve().is_relative_to(root.resolve())
    for name,version in VERSIONS.items():
        rows=[x for x in packages if x['name']==name]; assert len(rows)==1 and rows[0]['version']==version
        p=Path(rows[0]['source'])/'src'/f'{name}.jl'; bind(p,digest(p),b)
    return b

def command_and_environment():
    env={'JULIA_DEPOT_PATH':str(SETUP/'depot')+';'+str(SECONDARY),'JULIA_LOAD_PATH':'@;@stdlib',
         'JULIA_PROJECT':str(SETUP/'project'),'JULIA_PKG_SERVER':'','JULIA_PKG_OFFLINE':'true',
         'JULIA_PKG_PRECOMPILE_AUTO':'0','JULIA_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1',
         'TEMP':str(PRIVATE/'temporary'),'TMP':str(PRIVATE/'temporary')}
    cmd=[str(JULIA),'--startup-file=no','--history-file=no','--project='+str(SETUP/'project'),
         str(EXPORTER),str(CASE),str(ENVOUT/'ENVIRONMENT_ACQUISITION.json'),RECEIPT_SHA,
         str(EXPORT_OUT),str(SETUP/'project/Manifest.toml'),MANIFEST_SHA]
    return cmd,env

def prepare():
    assert not any(p.exists() for p in (PREP,OUT,EXPORT_OUT,PRIVATE)), 'Fresh preparation only'
    plain(PREP.parent); PREP.mkdir()
    try:
        b=admitted_bindings(); cmd,env=command_and_environment()
        for p,h in b.items(): assert digest(Path(p))==h
        d={'status':'PREPARED_OFFLINE_EXPORT_NO_JULIA','created_utc':utc(),
           'bindings':[{'path':p,'sha256':h} for p,h in sorted(b.items())],
           'command':cmd,'environment':env,'overall_seconds':600,'read_build_export_seconds':120,
           'Julia_invocations':0,'native_read_attempts':0,'native_build_attempts':0,'optimizer_calls':0,
           'scientific_import_order':'External admission before launch; exporter main guards follow package imports',
           'scope':'One fixed identity native penalized case; raw export only, no comparison or retry',
           'whole_registry_readback':False,'whole_installed_package_tree_rehash':False}
        save(PREP/'prepared.json',d)
        print(json.dumps({'status':d['status'],'bindings':len(b),'prepared_sha256':digest(PREP/'prepared.json')}),flush=True)
    except BaseException as e:
        save(PREP/'failure.json',{'status':'PREPARATION_FAILED_NO_RETRY','utc':utc(),'exception_type':type(e).__name__,'message':str(e)})
        raise

def run(expected):
    prepared_path=PREP/'prepared.json'; assert digest(prepared_path)==expected
    prep=json.loads(prepared_path.read_text()); assert prep['status']=='PREPARED_OFFLINE_EXPORT_NO_JULIA'
    assert prep['command']==command_and_environment()[0] and prep['environment']==command_and_environment()[1]
    for row in prep['bindings']: bind(Path(row['path']),row['sha256'],{})
    assert admitted_bindings()=={r['path']:r['sha256'] for r in prep['bindings']}
    assert not any(p.exists() for p in (OUT,EXPORT_OUT,PRIVATE))
    plain(OUT.parent); plain(PRIVATE.parent); OUT.mkdir(); PRIVATE.mkdir(); (PRIVATE/'temporary').mkdir()
    assert not os.environ.get('JULIA_SSL_NO_VERIFY_HOSTS') and not os.environ.get('JULIA_NO_VERIFY_HOSTS')
    began=time.perf_counter(); deadline=began+600
    d={'status':'STARTED','started_utc':utc(),'prepared_sha256':expected,'Julia_invocations':0,
       'native_read_attempts':0,'native_build_attempts':0,'optimizer_calls':0,'network_calls_requested':0,
       'Pkg_resolution_calls':0,'automatic_retry':False,'overall_seconds':600,'read_build_export_seconds':120,
       'command':prep['command'],'environment':prep['environment'],'source_sha256':digest(Path(__file__).resolve()),
       'exporter_sha256':digest(EXPORTER),'protocol_sha256':digest(PROTOCOL)}
    save(OUT/'execution_started.json',d.copy())
    child=None; threads=[]; stream_errors=[]; subdeadline=None; detected=None; observed_end=None
    def pump(stream,path):
        try:
            with path.open('xb',buffering=0) as f:
                while True:
                    data=os.read(stream.fileno(),4096)
                    if not data: break
                    f.write(data)
        except BaseException as e: stream_errors.append(repr(e))
    try:
        try:
            assert time.perf_counter()<deadline
            child=subprocess.Popen(prep['command'],cwd=PRIVATE,env=dict(os.environ,**prep['environment']),
                stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
            d.update(Julia_invocations=1,julia_pid=child.pid,julia_started_utc=utc())
            save(OUT/'julia_launch.json',{'pid':child.pid,'utc':d['julia_started_utc'],'command':prep['command'],'environment':prep['environment']})
            for stream,path in ((child.stdout,PRIVATE/'stdout.log'),(child.stderr,PRIVATE/'stderr.log')):
                t=threading.Thread(target=pump,args=(stream,path),daemon=True); t.start(); threads.append(t)
            while child.poll() is None:
                if stream_errors: raise RuntimeError('Durable log capture failed')
                now=time.perf_counter()
                if now>=deadline: raise TimeoutError('Overall 600-second allocation expired')
                marker=EXPORT_OUT/'native_read_attempt.json'
                if subdeadline is None and marker.exists():
                    # Marker is written before native read. A partial write is reread next poll.
                    try: mark=json.loads(marker.read_text())
                    except json.JSONDecodeError: mark=None
                    if mark is not None:
                        wall_start=float(mark['native_read_started_unix_seconds'])
                        wall_age=time.time()-wall_start
                        assert wall_age>=-1, 'Unexpected backwards wall-clock discrepancy'
                        subdeadline=now+120-max(0,wall_age); detected=now
                        d.update(native_read_started_utc=mark['native_read_started_utc'],
                            native_subphase_detected_utc=utc(),native_marker_detection_age_seconds=wall_age,
                            import_and_pre_read_seconds=now-began-max(0,wall_age))
                        save(OUT/'native_subphase_admission.json',d.copy())
                if subdeadline is not None and now>=subdeadline: raise TimeoutError('Native read/build/export 120-second subphase expired')
                try: child.wait(timeout=0.5)
                except subprocess.TimeoutExpired: pass
        finally:
            if child is not None and child.poll() is None:
                termination={'pid':child.pid,'requested_utc':utc()}
                try:
                    killed=subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
                    termination['taskkill_exit_code']=killed.returncode
                    try: (PRIVATE/'termination.log').write_bytes(killed.stdout)
                    except BaseException as e: termination['log_error']=repr(e)
                except BaseException as e: termination['taskkill_error']=repr(e)
                if child.poll() is None:
                    try: child.kill(); termination['owned_parent_kill_fallback']=True
                    except BaseException as e: termination['parent_kill_error']=repr(e)
                try: child.wait(timeout=30)
                except BaseException as e: termination['wait_error']=repr(e)
                d['termination']=termination
            for t in threads:
                t.join(timeout=10)
                if t.is_alive(): stream_errors.append('Stream drain did not finish')
            if child is not None:
                observed_end=time.perf_counter()
                d.update(julia_exit_code=child.returncode,owned_parent_alive=child.poll() is None,julia_ended_utc=utc())
        assert child is not None and child.returncode==0 and not stream_errors, 'Julia export/log capture did not close normally'
        completed=json.loads((EXPORT_OUT/'completion.json').read_text())
        assert completed['status']=='OFFICIAL_RAW_EXPORT_COMPLETE_PENDING_COMPARISON'
        assert completed['native_read_attempts']==completed['native_build_attempts']==1 and completed['optimizer_calls']==0
        mark=json.loads((EXPORT_OUT/'native_read_attempt.json').read_text())
        end=datetime.fromisoformat(completed['ended_utc'].replace('Z','+00:00')).timestamp()
        native_elapsed=end-float(mark['native_read_started_unix_seconds'])
        d['native_subphase_elapsed_seconds']=native_elapsed
        d['import_and_pre_read_wall_seconds']=float(mark['native_read_started_unix_seconds'])-datetime.fromisoformat(d['julia_started_utc']).timestamp()
        assert 0<=native_elapsed<=120, 'Completed native subphase violated fixed allowance/clock ordering'
        assert time.perf_counter()<=deadline, 'Closure exceeded overall allocation'
        for row in prep['bindings']: assert digest(Path(row['path']))==row['sha256']
        assert digest(EXPORT_OUT/'official_raw_model.json')==completed['raw_model_sha256']
        assert digest(EXPORT_OUT/'official_parsed_instance.json')==completed['parsed_instance_sha256']
        d.update(status='OFFICIAL_RAW_EXPORT_COMPLETE_PENDING_COMPARISON',native_read_attempts=1,
                 native_build_attempts=1,inputs_unchanged=True,counts=completed['counts'])
    except BaseException as e:
        d.update(status='EXPORT_FAILED_PRESERVED_NO_RETRY',exception_type=type(e).__name__,message=str(e))
    for name,key in (('native_read_attempt.json','native_read_attempts'),('native_build_attempt.json','native_build_attempts')):
        d[key]=int((EXPORT_OUT/name).exists())
    d.update(stream_errors=stream_errors,
             native_subphase_monitor_overrun_seconds=(max(0,observed_end-subdeadline) if subdeadline is not None and observed_end is not None else None),
             import_subphase_observed=detected is not None)
    try:
        d['artifacts']=[{'path':str(p),'bytes':p.stat().st_size,'sha256':digest(p)} for folder in (OUT,EXPORT_OUT)
                        if folder.exists() for p in sorted(folder.iterdir()) if p.is_file()]
        d['private_logs']=[{'path':str(p),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(PRIVATE.iterdir()) if p.is_file()]
    except BaseException as e:
        d.update(status='EXPORT_FAILED_PRESERVED_NO_RETRY',closure_exception_type=type(e).__name__,closure_message=str(e))
    # Final admission follows all potentially expensive input/output/log hashing.
    closed=time.perf_counter()
    if d['status']=='OFFICIAL_RAW_EXPORT_COMPLETE_PENDING_COMPARISON' and closed>deadline:
        d.update(status='EXPORT_FAILED_PRESERVED_NO_RETRY',exception_type='TimeoutError',message='Closure hashes exceeded overall 600-second allocation')
    d.update(ended_utc=utc(),elapsed_seconds=closed-began,overall_overrun_seconds=max(0,closed-deadline),
             completion_receipt_write_excluded_from_elapsed=True)
    d['private_logs_publication_status']='NOT_SELECTED_PENDING_REVIEW'
    save(OUT/'completion.json',d)
    print(json.dumps({k:d[k] for k in ('status','elapsed_seconds','Julia_invocations','native_read_attempts','native_build_attempts','optimizer_calls')}),flush=True)
    return 0 if d['status']=='OFFICIAL_RAW_EXPORT_COMPLETE_PENDING_COMPARISON' else 1

if __name__=='__main__':
    if sys.argv[1:]==['--prepare-once']: prepare()
    elif len(sys.argv)==3 and sys.argv[1]=='--run-prepared' and len(sys.argv[2])==64: sys.exit(run(sys.argv[2]))
    else: raise ValueError('Use --prepare-once or --run-prepared EXPECTED_PREPARED_SHA256')
