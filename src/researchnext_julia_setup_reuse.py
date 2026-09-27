"""Prospective narrower-provenance reuse setup. One Pkg.add, no scientific model.

Do not execute until explicit review/GO. Attempt01 is never changed.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess, sys, threading, time, tomllib

REPO=Path(__file__).resolve().parents[1]
BASE=REPO/'.work/researchnext_julia_export'
OLD=BASE/'attempt01'
ATTEMPT=BASE/'setup_reuse01'
OUT=REPO/'results/research_next/orlib_julia_export/setup_reuse01'
PRIVATE_LOGS=ATTEMPT/'private_logs'
PROTOCOL=REPO/'docs/research_next/JULIA_REUSE_SETUP_PROTOCOL.md'
PREP=REPO/'results/research_next/orlib_julia_export/reuse_prepared01'
SECONDARY=BASE/'setup_efficient01/depot'
GENERAL_PATH=SECONDARY/'registries/General'
EXTRACTION_RECEIPT=REPO/'results/research_next/orlib_julia_export/setup_efficient01/ENVIRONMENT_ACQUISITION.json'
EXTRACTION_RECEIPT_SHA='bdfae531e4721bf617444d1014e6d3917b93468d10e1472056511e42017c5989'
PROPOSAL=REPO/'docs/research_next/JULIA_REGISTRY_REUSE_PROPOSAL.md'
PROPOSAL_SHA='fc27147c2ca0fa0d0cbff34d2a7b810b3a09a199f21a702ee947ed4da883d5a6'
UC_TREE='619a6b12e1005425e6ac08c4c45e445bb0a6f134'
EXPECTED_VERSIONS={'UnitCommitment':'0.4.0','JuMP':'1.15.1','MathOptInterface':'1.20.1','PackageCompiler':'1.7.7'}
REGISTRY=BASE/'registry_acquire03/General.tar.gz'
REGISTRY_SHA='53e48326acc56f53ac4527a41e7362a29622d3bf9d406234c5ddc05566869211'
REGISTRY_RECEIPT=REPO/'results/research_next/registry_acquire03/run01/receipt.json'
REGISTRY_RECEIPT_SHA='86eeaf107b46baaabd4abc88b54507b934822956d18d0d917e4ccda2682788d5'
REGISTRY_INVENTORY=REGISTRY_RECEIPT.with_name('registry_file_inventory.json')
REGISTRY_INVENTORY_SHA='cc8d9ce6757ffc70a1347ab3bf9e74a2bbaba87f4131bb3737746a52c19f0f42'
PARENT_SOURCE=REPO/'src/researchnext_julia_setup_efficient.py'
PARENT_SOURCE_SHA='b3ed859e6d7a8416ea8fc76b8184e8362c121e81952c854b748b0972e323fd00'
PKG_SOURCE_SHA={'Pkg.jl':'c5fb5ff466afecdeafd9aec8c1579a907625a2a10c014992243884936018ab6b',
 'Types.jl':'8c3933c01dfdd1cc8af575594064eeb6433e5b777b586edc59cf2e9ed36dcada',
 'API.jl':'ed80ac79c48fc6a33b28ab9a6ad639a517ff605cecebcf9601228f7392e2c172',
 'Operations.jl':'ef3b6b4d3d349929fb812aac6c81c2bd9ee053f32c859176e7dca812f7a15fa6'}
RESERVED={'con','prn','aux','nul'}|{'com'+str(n) for n in range(1,10)}|{'lpt'+str(n) for n in range(1,10)}
UC='4f04f0dd6641b071fd7556346c3d7190c2ffdfe5'
GENERAL='416a13c3e4888af4b245812d8f4ab040a042c38f'
GENERAL_TREE='f39bab42a09b8a82574435c6e402e598b3200dc3'
ARCHIVE_SHA='63e14aa2e056f76f4a8f79eb8b4ed6698e3817eb3584e12b030f26f36e70cce6'
EXE_SHA='29ebe4b29362a2e380848dd4803e67343fe1779207b4970390418a1d495da67f'
SOURCE_BINDING_SHA='6038d94eca340f7f0bf759330aa57f30d3930834fb4e1eccd8ff824c61fbd927'

def utc(): return datetime.now(timezone.utc).isoformat()
def sha(b): return hashlib.sha256(b).hexdigest()
def save(path,obj):
    with path.open('x',encoding='utf-8') as f:
        json.dump(obj,f,indent=2,allow_nan=False); f.write('\n')
def file_sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def require_plain(path):
    for parent in (path,*path.parents):
        if parent.exists():
            info=parent.lstat()
            if parent.is_symlink() or getattr(info,'st_file_attributes',0)&0x400:
                raise ValueError('Reparse/link path rejected: '+str(parent))

def safe_parts(name):
    if not name or name.startswith('/') or '\\' in name or '\0' in name:
        raise ValueError('Unsafe registry path')
    parts=tuple(name.rstrip('/').split('/'))
    for part in parts:
        if not part or part in ('.','..') or ':' in part or part.endswith(('.', ' ')):
            raise ValueError('Unsafe registry component')
        if part.split('.')[0].casefold() in RESERVED: raise ValueError('Reserved registry path')
    return parts

def selected_registry_context():
    require_plain(SECONDARY); require_plain(GENERAL_PATH)
    assert {p.name for p in SECONDARY.iterdir()}=={'registries'}
    assert {p.name for p in (SECONDARY/'registries').iterdir()}=={'General'}
    assert not (GENERAL_PATH/'.git').exists() and not (GENERAL_PATH/'.tree_info.toml').exists()
    inv=json.loads(REGISTRY_INVENTORY.read_text())
    assert inv['commit']==GENERAL and inv['git_tree']==GENERAL_TREE
    files={row['path']:row for row in inv['files']}; assert len(files)==61167
    records=[]
    def checked(rel, required=True):
        parts=safe_parts(rel); path=GENERAL_PATH.joinpath(*parts)
        if rel not in files:
            assert not path.exists(), 'Unexpected selected metadata outside admitted inventory'
            if required: raise ValueError('Required selected registry metadata absent')
            return None
        require_plain(path); data=path.read_bytes(); row=files[rel]
        assert len(data)==row['bytes'] and sha(data)==row['sha256'], 'Selected registry metadata mismatch'
        records.append({'path':str(path),'registry_relative_path':rel,'bytes':len(data),'sha256':sha(data)})
        return tomllib.loads(data.decode('utf-8'))
    registry=checked('Registry.toml')
    assert registry['name']=='General' and registry['uuid']=='23338594-aafe-5451-b93e-139f81909106'
    return registry,checked,records

def package_registry_metadata(registry,checked,uuid,name,version=None,tree=None):
    item=registry['packages'][uuid]
    assert item['name']==name
    prefix=item['path']; safe_parts(prefix)
    package=checked(prefix+'/Package.toml')
    assert package['name']==name and package['uuid']==uuid
    versions=checked(prefix+'/Versions.toml')
    for leaf in ('Deps.toml','Compat.toml','WeakDeps.toml','WeakCompat.toml'):
        checked(prefix+'/'+leaf,required=False)
    if version is not None:
        assert version in versions, 'Resolved version missing from pinned registry'
        if tree is not None: assert versions[version]['git-tree-sha1']==tree, 'Reported dependency tree differs from pinned selected registry version'

def fixed_bindings():
    pkgsrc=OLD/'runtime/julia-1.6.7/share/julia/stdlib/v1.6/Pkg/src'
    pairs=[(REGISTRY,REGISTRY_SHA),(REGISTRY_RECEIPT,REGISTRY_RECEIPT_SHA),
           (REGISTRY_INVENTORY,REGISTRY_INVENTORY_SHA),(EXTRACTION_RECEIPT,EXTRACTION_RECEIPT_SHA),
           (PARENT_SOURCE,PARENT_SOURCE_SHA),(PROPOSAL,PROPOSAL_SHA),
           (OLD/'julia-1.6.7-win64.zip',ARCHIVE_SHA),(OLD/'runtime/julia-1.6.7/bin/julia.exe',EXE_SHA),
           (REPO/'results/research_next/orlib_julia_export/SETUP_CLOSURE_AND_LOCAL_SOURCE_BINDINGS.json',SOURCE_BINDING_SHA)]
    pairs.extend((pkgsrc/name,value) for name,value in PKG_SOURCE_SHA.items())
    return pairs

def verify_extraction_receipt():
    record=json.loads(EXTRACTION_RECEIPT.read_text())
    assert record['status']=='SETUP_FAILED_PRESERVED_NO_RETRY'
    assert record['stage']=='full_registry_content_tree_readback_before_Julia'
    assert record['registry_extraction']['files_written']==61167
    assert record['registry_extraction']['directories_created_including_root']==14474
    assert record['registry_archive_sha256']==REGISTRY_SHA
    assert record['registry_inventory_sha256']==REGISTRY_INVENTORY_SHA
    assert record['source_sha256']==PARENT_SOURCE_SHA
    assert all(record[k]==0 for k in ('Julia_invocations','Pkg_add_calls','scientific_model_builds','optimizer_calls'))
    assert record['source_unchanged_at_closure'] and record['admitted_archive_unchanged_at_closure']
    assert 'registry_before_setup' not in record

def prepare():
    assert not PREP.exists() and not ATTEMPT.exists() and not OUT.exists(), 'Fresh preparation only'
    require_plain(PREP.parent); PREP.mkdir()
    snapshot={str(p):file_sha(p) for p in (Path(__file__),PROTOCOL)}
    try:
        for path,expected in fixed_bindings():
            assert file_sha(path)==expected, 'Fixed preparation binding mismatch'
            snapshot[str(path)]=expected
        verify_extraction_receipt()
        registry,checked,records=selected_registry_context()
        for name in EXPECTED_VERSIONS:
            uuid=next(uuid for uuid,item in registry['packages'].items() if item['name']==name)
            # UC is repository tracked: no claim its chosen revision equals the registered release tree.
            package_registry_metadata(registry,checked,uuid,name)
        for row in records: snapshot[row['path']]=row['sha256']
        for path,expected in snapshot.items(): assert file_sha(Path(path))==expected
        report={'status':'PREPARED_SOURCE_AND_SELECTED_METADATA_ONLY','created_utc':utc(),
                'source_sha256':snapshot[str(Path(__file__))],'protocol_sha256':snapshot[str(PROTOCOL)],
                'bindings':[{'path':path,'sha256':value} for path,value in sorted(snapshot.items())],
                'selected_registry_metadata':records,'secondary_depot':str(SECONDARY),
                'prospective_private_attempt':str(ATTEMPT),'prospective_output':str(OUT),
                'phase_limit_seconds':1800,'expected_versions':EXPECTED_VERSIONS,
                'whole_disk_registry_readback_completed':False,'registry_reextractions':0,
                'Julia_invocations':0,'Pkg_add_calls':0,'scientific_model_builds':0,'optimizer_calls':0,
                'Windows_installed_archive_full_tree_verification':'NOT_ESTABLISHED_BY_PKG_INSTALL_ARCHIVE',
                'trust_contract':'Inherited verified archive and controlled extraction; selected physical metadata checked; assumes no external concurrent mutation or storage fault in unselected materialized registry bytes'}
        save(PREP/'prepared.json',report)
        print(json.dumps({'status':report['status'],'bindings':len(report['bindings']),
                          'prepared_sha256':file_sha(PREP/'prepared.json')}),flush=True)
    except BaseException as exc:
        save(PREP/'failure.json',{'status':'PREPARATION_FAILED_PRESERVED_NO_RETRY','utc':utc(),
                                 'exception_type':type(exc).__name__,'message':str(exc)})
        raise

def verify_prepared(expected_sha):
    path=PREP/'prepared.json'; assert file_sha(path)==expected_sha
    report=json.loads(path.read_text()); assert report['status']=='PREPARED_SOURCE_AND_SELECTED_METADATA_ONLY'
    assert report['source_sha256']==file_sha(Path(__file__)) and report['protocol_sha256']==file_sha(PROTOCOL)
    for item in report['bindings']: assert file_sha(Path(item['path']))==item['sha256']
    verify_extraction_receipt(); selected_registry_context()
    return report

def cleanup_owned_process(child, receipt, errors):
    """Termination does not depend on successfully opening a diagnostic file."""
    if child is None:
        return
    if child.poll() is None:
        termination={'pid':child.pid,'started_utc':utc(),'reason':'post-launch failure or timeout'}
        try:
            stopped=subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],
                stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW)
            termination['taskkill_exit_code']=stopped.returncode
            try:
                with (PRIVATE_LOGS/'termination.log').open('xb') as f: f.write(stopped.stdout)
            except BaseException as exc:
                termination['log_write_error']=repr(exc)
        except BaseException as exc:
            termination['taskkill_error']=repr(exc)
        # Even a logging/taskkill failure must not leave the owned Julia parent
        # running. The tree-kill attempt above remains separately accounted for.
        if child.poll() is None:
            try:
                child.kill()
                termination['owned_parent_kill_fallback']=True
            except BaseException as exc:
                termination['owned_parent_kill_error']=repr(exc)
        try: child.wait(timeout=30)
        except BaseException as exc: termination['wait_error']=repr(exc)
        termination['owned_parent_alive']=child.poll() is None
        receipt['owned_process_cleanup']=termination
        if termination['owned_parent_alive']:
            errors.append('OWNED_JULIA_PARENT_STILL_ALIVE_AFTER_CLEANUP')
    receipt['owned_parent_alive_after_postlaunch_guard']=child.poll() is None

def run_prepared(expected_sha):
    prepared=verify_prepared(expected_sha)
    assert not ATTEMPT.exists() and not OUT.exists(), 'Preserve every prior attempt'
    require_plain(ATTEMPT.parent); require_plain(OUT.parent)
    ATTEMPT.mkdir(); OUT.mkdir(); PRIVATE_LOGS.mkdir()
    began=time.perf_counter(); deadline=began+1800
    receipt={'status':'STARTED','started_utc':utc(),'limit_seconds':1800,'source_sha256':sha(Path(__file__).read_bytes()),
             'protocol_sha256':file_sha(PROTOCOL),'parent_source_sha256':PARENT_SOURCE_SHA,
             'prepared_sha256':expected_sha,'whole_disk_registry_readback_completed':False,
             'registry_reextractions':0,'registry_full_content_scans':0,
             'Windows_installed_archive_full_tree_verification':'NOT_ESTABLISHED_BY_PKG_INSTALL_ARCHIVE',
             'Julia_invocations':0,'Pkg_add_calls':0,'scientific_model_builds':0,'optimizer_calls':0,
             'package_cache_copied':False,'runtime_reused_read_only':True,'automatic_retry':False,
             'TLS_bypass':False,'certificate_injection':False,'global_settings_changed':False,
             'concurrent_path_replacement_assumption':'No external writer or storage fault changes unselected inherited registry bytes; selected pathname checks are not adversarial race-proof'}
    save(OUT/'started.json',receipt)
    def remaining():
        value=deadline-time.perf_counter()
        if value<=0: raise TimeoutError('Reuse setup 1800-second package-phase allocation expired')
        return value
    def stage(name):
        remaining(); receipt['stage']=name
        event={'stage':name,'utc':utc(),'elapsed_seconds':time.perf_counter()-began}
        with (OUT/'stages.jsonl').open('a',encoding='utf-8') as f:
            f.write(json.dumps(event)+'\n'); f.flush()
        print(json.dumps(event),flush=True)
    try:
        stage('verify_runtime_reuse_and_prior_bindings')
        archive=OLD/'julia-1.6.7-win64.zip'
        julia=OLD/'runtime/julia-1.6.7/bin/julia.exe'
        assert sha(archive.read_bytes())==ARCHIVE_SHA and sha(julia.read_bytes())==EXE_SHA
        prior=REPO/'results/research_next/orlib_julia_export/SETUP_CLOSURE_AND_LOCAL_SOURCE_BINDINGS.json'
        assert sha(prior.read_bytes())==SOURCE_BINDING_SHA
        prior_binding=json.loads(prior.read_text())['native_source_bindings']
        receipt.update(runtime_executable=str(julia),runtime_executable_sha256=EXE_SHA,
                       runtime_archive_sha256=ARCHIVE_SHA,prior_source_bindings_sha256=SOURCE_BINDING_SHA)
        project=ATTEMPT/'project'; depot=ATTEMPT/'depot'; temp=ATTEMPT/'temporary'
        for p in (project,depot,temp): p.mkdir()
        stage('reuse_inherited_registry_selected_metadata_only')
        registry,checked,initial_records=selected_registry_context()
        receipt.update(registry_archive_sha256=REGISTRY_SHA,registry_inventory_sha256=REGISTRY_INVENTORY_SHA,
                       inherited_extraction_receipt_sha256=EXTRACTION_RECEIPT_SHA,
                       secondary_depot=str(SECONDARY),registry_network_requests=0,
                       registry_trust='Inherited archive and controlled complete extraction; no whole on-disk tree readback claim')
        script=ATTEMPT/'instantiate_once.jl'
        script.write_text('''function durable_stage(s)
    msg=string(s," unix_seconds=",time())
    open(joinpath(dirname(ARGS[2]),"julia_stages.log"),"a") do io
        println(io,msg); flush(io)
    end
    println(stderr,msg); flush(stderr)
end
durable_stage("BEFORE_PKG_IMPORT")
using Pkg, TOML, Dates, Logging
durable_stage("AFTER_PKG_IMPORT")
@assert VERSION == v"1.6.7"
@assert length(DEPOT_PATH) == 2
@assert abspath(DEPOT_PATH[2]) == abspath(ARGS[3])
@assert abspath(DEPOT_PATH[1]) == abspath(ARGS[1])
@assert get(ENV,"JULIA_PKG_SERVER","unset") == ""
function stage(s)
    durable_stage(s)
end
global_logger(ConsoleLogger(stderr))
stage("PKG_TOML_IMPORT_COMPLETE")
@assert isfile(joinpath(DEPOT_PATH[2],"registries","General","Registry.toml"))
@assert isempty(Pkg.Types.collect_registries(DEPOT_PATH[1]))
@assert length(Pkg.Types.collect_registries()) == 1
specs=[PackageSpec(url="https://github.com/ANL-CEEESA/UnitCommitment.jl",rev="4f04f0dd6641b071fd7556346c3d7190c2ffdfe5"),
       PackageSpec(name="JuMP",version=v"1.15.1"),
       PackageSpec(name="MathOptInterface",version=v"1.20.1"),
       PackageSpec(name="PackageCompiler",version=v"1.7.7")]
open(joinpath(dirname(ARGS[2]),"pkg_add_started.txt"),"w") do io
    println(io,"One Pkg.add attempt; ",Dates.now(Dates.UTC)); flush(io)
end
stage("PKG_ADD_ATTEMPT")
Pkg.add(specs)
stage("PKG_ADD_RETURNED")
deps=Pkg.dependencies()
expected=Dict("UnitCommitment"=>v"0.4.0","JuMP"=>v"1.15.1","MathOptInterface"=>v"1.20.1","PackageCompiler"=>v"1.7.7")
rows=Any[]
for (uuid,p) in deps
    if haskey(expected,p.name)
        @assert p.version==expected[p.name]; delete!(expected,p.name)
    end
    row=Dict{String,Any}("uuid"=>string(uuid),"name"=>p.name,
        "version"=>(p.version===nothing ? "" : string(p.version)),
        "tree_hash"=>(p.tree_hash===nothing ? "" : string(p.tree_hash)),
        "source"=>(p.source===nothing ? "" : string(p.source)),"direct"=>p.is_direct_dep,
        "is_stdlib"=>Pkg.Types.is_stdlib(uuid))
    for key in (:git_revision,:git_source,:is_tracking_repo,:is_tracking_path)
        if hasproperty(p,key)
            v=getproperty(p,key); row[string(key)]=v===nothing ? "" : string(v)
        end
    end
    push!(rows,row)
end
@assert isempty(expected)
sort!(rows,by=x->x["name"])
open(ARGS[2],"w") do io
    TOML.print(io,Dict("julia_version"=>string(VERSION),"machine"=>Sys.MACHINE,
      "active_project"=>Base.active_project(),"depot_path"=>DEPOT_PATH,"packages"=>rows))
end
stage("DEPENDENCY_INVENTORY_CLOSED_NO_SCIENTIFIC_IMPORT")
''',encoding='utf-8')
        assert not os.environ.get('JULIA_SSL_NO_VERIFY_HOSTS'), 'Inherited TLS bypass not permitted'
        assert not os.environ.get('JULIA_NO_VERIFY_HOSTS'), 'Inherited TLS bypass not permitted'
        env=dict(os.environ,JULIA_DEPOT_PATH=str(depot)+';'+str(SECONDARY),JULIA_LOAD_PATH='@;@stdlib',
                 JULIA_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',JULIA_PKG_PRECOMPILE_AUTO='0',
                 JULIA_PKG_SERVER='',JULIA_PROJECT=str(project),TEMP=str(temp),TMP=str(temp))
        cmd=[str(julia),'--startup-file=no','--history-file=no','--project='+str(project),
             str(script),str(depot),str(ATTEMPT/'package_inventory.toml'),str(SECONDARY)]
        receipt.update(command=cmd,isolated_environment={k:env[k] for k in ('JULIA_DEPOT_PATH','JULIA_LOAD_PATH',
            'JULIA_PROJECT','JULIA_NUM_THREADS','OPENBLAS_NUM_THREADS','JULIA_PKG_PRECOMPILE_AUTO','JULIA_PKG_SERVER','TEMP','TMP')})
        stage('one_pkg_resolution_direct_official_routes')
        child=None
        threads=[]
        errors=[]
        def pump(stream,path):
            try:
                with path.open('xb',buffering=0) as f:
                    while True:
                        data=os.read(stream.fileno(),4096)
                        if not data: break
                        f.write(data)
            except Exception as exc: errors.append(repr(exc))
        # This guard includes Popen, launch receipt, thread construction/start,
        # monitoring and all post-launch receipt operations, not only the loop.
        try:
            remaining()
            child=subprocess.Popen(cmd,cwd=ATTEMPT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
            receipt.update(Julia_invocations=1,julia_pid=child.pid,julia_started_utc=utc())
            save(OUT/'julia_launch.json',{'pid':child.pid,'utc':receipt['julia_started_utc'],
                                        'command':cmd,'environment':receipt['isolated_environment']})
            for stream,path in ((child.stdout,PRIVATE_LOGS/'julia_stdout.log'),
                                (child.stderr,PRIVATE_LOGS/'julia_stderr.log')):
                t=threading.Thread(target=pump,args=(stream,path),daemon=True)
                t.start()
                threads.append(t)
            while child.poll() is None:
                if errors:
                    raise RuntimeError('Durable Julia stream capture failed; preserve attempt')
                remaining()
                # Restrict observation to this known parent and its direct children.
                ps=(f'$p=Get-Process -Id {child.pid} -ErrorAction SilentlyContinue; '
                    f'$c=Get-CimInstance Win32_Process -Filter "ParentProcessId = {child.pid}"; '
                    '@{parent=@($p|Select-Object Id,CPU,WorkingSet64);children=@($c|Select-Object ProcessId,ParentProcessId,Name,CreationDate)}|ConvertTo-Json -Compress -Depth 4')
                try:
                    observed=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',ps],
                        stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=min(10,remaining()),
                        creationflags=subprocess.CREATE_NO_WINDOW)
                    observation={'returncode':observed.returncode,
                        'observation':observed.stdout.decode('utf-8-sig',errors='replace').strip()}
                except subprocess.TimeoutExpired:
                    observation={'status':'OWNED_PROCESS_OBSERVATION_TIMEOUT','Julia_termination_requested':False}
                with (PRIVATE_LOGS/'owned_process_observations.jsonl').open('a',encoding='utf-8') as f:
                    f.write(json.dumps(dict(utc=utc(),**observation))+'\n')
                try: child.wait(timeout=min(30,remaining()))
                except subprocess.TimeoutExpired: pass
        finally:
            cleanup_owned_process(child,receipt,errors)
            for t in threads:
                t.join(timeout=10)
                if t.is_alive(): errors.append('STREAM_DRAIN_THREAD_DID_NOT_FINISH')
            receipt['stream_errors']=list(errors)
        receipt.update(julia_exit_code=child.returncode,julia_ended_utc=utc(),stream_errors=errors)
        assert child.returncode==0 and not errors, 'Package setup or durable log capture failed'
        stage('verify_and_archive_resolved_metadata')
        import tomllib
        meta=tomllib.loads((ATTEMPT/'package_inventory.toml').read_text())
        packages=meta['packages']; uc=next(p for p in packages if p['name']=='UnitCommitment')
        assert uc['git_revision']==UC and uc['tree_hash']==UC_TREE
        assert meta['depot_path']==[str(depot),str(SECONDARY)]
        registry,checked,selected_records=selected_registry_context()
        installed_projects=[]
        for package in packages:
            source=Path(package['source'])
            if package['is_stdlib']:
                assert source.resolve().is_relative_to((OLD/'runtime/julia-1.6.7/share/julia/stdlib').resolve())
                continue
            assert source.resolve().is_relative_to((depot/'packages').resolve()), 'Nonstdlib package outside fresh writable depot'
            if package['name']!='UnitCommitment':
                package_registry_metadata(registry,checked,package['uuid'],package['name'],package['version'],package['tree_hash'])
            project_file=source/'Project.toml'
            if project_file.exists():
                require_plain(project_file); data=project_file.read_bytes(); project_meta=tomllib.loads(data.decode('utf-8'))
                assert project_meta['name']==package['name'] and project_meta['uuid']==package['uuid']
                installed_projects.append({'package':package['name'],'path':str(project_file),'sha256':sha(data),'version':project_meta.get('version')})
                if package['name'] in EXPECTED_VERSIONS:
                    assert project_meta['version']==EXPECTED_VERSIONS[package['name']]
            else:
                assert package['name'] not in EXPECTED_VERSIONS, 'Required direct package Project.toml absent'
        save(OUT/'selected_registry_and_installed_metadata.json',{'selected_registry_metadata':selected_records,'installed_project_metadata':installed_projects,'full_registry_readback':False,'whole_installed_package_tree_rehash':False})
        verified=[]
        for binding in prior_binding:
            rel=binding['path']; data=(Path(uc['source'])/rel).read_bytes()
            assert sha(data.replace(b'\r\n',b'\n'))==binding['commit_blob_sha256'], 'Non-newline native source mismatch'
            verified.append({'path':rel,'sha256':sha(data),'bytes':len(data),
                             'git_blob_sha256':binding['commit_blob_sha256'],
                             'raw_blob_equal':sha(data)==binding['commit_blob_sha256'],
                             'CRLF_to_LF_exact_blob_equal':True})
        for source in (project/'Project.toml',project/'Manifest.toml',ATTEMPT/'package_inventory.toml',script):
            with (OUT/source.name).open('xb') as f: f.write(source.read_bytes())
        stage('final_selected_bindings_and_provenance_checks')
        for item in prepared['bindings']: assert file_sha(Path(item['path']))==item['sha256']
        selected_registry_context()
        if (depot/'registries').exists():
            require_plain(depot/'registries')
            assert not list((depot/'registries').iterdir()), 'Unexpected registry installed in writable depot'
        assert sha(julia.read_bytes())==EXE_SHA and sha(archive.read_bytes())==ARCHIVE_SHA
        receipt.update(status='READY_ENVIRONMENT_ONLY_NO_MODEL_BUILD',selected_package=uc,
            pinned_native_files_verified=verified,installed_direct_versions={p['name']:p['version'] for p in packages if p['direct']},
            native_source_binding='Raw hashes preserved; read-only CRLF-to-LF equality to fixed Git blobs; no source normalization written')
    except BaseException as exc:
        receipt.update(status='SETUP_FAILED_PRESERVED_NO_RETRY',exception_type=type(exc).__name__,message=str(exc))
    # Preserve partial metadata even when the single resolution fails.
    for partial in (ATTEMPT/'project/Project.toml',ATTEMPT/'project/Manifest.toml',
                    ATTEMPT/'package_inventory.toml',ATTEMPT/'instantiate_once.jl',ATTEMPT/'julia_stages.log'):
        if partial.is_file() and not (OUT/partial.name).exists():
            with (OUT/partial.name).open('xb') as f: f.write(partial.read_bytes())
    marker=ATTEMPT/'pkg_add_started.txt'
    receipt['Pkg_add_calls']=int(marker.exists())
    receipt['Pkg_add_attempt_count_evidence']='Durable pre-call marker; one source call site; a marker records attempted entry, not successful completion'
    if marker.exists(): receipt['Pkg_add_marker_sha256']=sha(marker.read_bytes())
    receipt.update(ended_utc=utc(),elapsed_seconds=time.perf_counter()-began,
                   allocation_overrun_seconds=max(0,time.perf_counter()-deadline))
    receipt['source_unchanged_at_closure']=file_sha(Path(__file__))==receipt['source_sha256']
    receipt['protocol_unchanged_at_closure']=file_sha(PROTOCOL)==receipt['protocol_sha256']
    receipt['admitted_archive_unchanged_at_closure']=file_sha(REGISTRY)==REGISTRY_SHA
    receipt['artifacts']=[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
                          for p in sorted(OUT.iterdir()) if p.is_file()]
    receipt['private_log_artifacts']=[{'path':p.relative_to(ATTEMPT).as_posix(),
        'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
        for p in sorted(PRIVATE_LOGS.iterdir()) if p.is_file()]
    receipt['private_logs_publication_status']='NOT_SELECTED_PENDING_ENTERPRISE_TLS_REVIEW'
    save(OUT/'ENVIRONMENT_ACQUISITION.json',receipt)
    print(json.dumps({k:receipt[k] for k in ('status','stage','elapsed_seconds','Julia_invocations','Pkg_add_calls')}),flush=True)
    return 0 if receipt['status']=='READY_ENVIRONMENT_ONLY_NO_MODEL_BUILD' else 1

if __name__=='__main__':
    if sys.argv[1:]==['--prepare-once']:
        prepare()
    elif len(sys.argv)==3 and sys.argv[1]=='--run-prepared' and len(sys.argv[2])==64:
        sys.exit(run_prepared(sys.argv[2]))
    else:
        raise ValueError('Use --prepare-once or --run-prepared EXPECTED_PREPARED_SHA256')
