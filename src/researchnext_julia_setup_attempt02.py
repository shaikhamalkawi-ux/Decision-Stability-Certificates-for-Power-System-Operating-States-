"""Prospective isolated setup attempt02. One Pkg.add, no scientific model.

Do not execute until explicit review/GO. Attempt01 is never changed.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import ast, hashlib, json, os, re, subprocess, sys, tarfile, threading, time, urllib.request

REPO=Path(__file__).resolve().parents[1]
BASE=REPO/'.work/researchnext_julia_export'
OLD=BASE/'attempt01'
ATTEMPT=BASE/'attempt02'
OUT=REPO/'results/research_next/orlib_julia_export/attempt02'
PRIVATE_LOGS=ATTEMPT/'private_logs'
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
def git_hash(kind,data):
    return hashlib.sha1(kind+b' '+str(len(data)).encode()+b'\0'+data).digest()
def git_tree(entries):
    tree={}
    for parts,mode,blob in entries:
        branch=tree
        for part in parts[:-1]: branch=branch.setdefault(part,{})
        assert parts[-1] not in branch
        branch[parts[-1]]=(mode,blob)
    def visit(node):
        ordered=sorted(node.items(),key=lambda x:(x[0]+('/' if isinstance(x[1],dict) else '')).encode())
        data=b''
        for name,value in ordered:
            mode,digest=(b'40000',visit(value)) if isinstance(value,dict) else value
            data+=mode+b' '+name.encode()+b'\0'+digest
        return git_hash(b'tree',data)
    return visit(tree).hex()

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

def main():
    assert sys.argv[1:]==['--run-attempt02'], 'Explicit launch flag required'
    assert not ATTEMPT.exists() and not OUT.exists(), 'Preserve every prior attempt'
    ATTEMPT.mkdir(); OUT.mkdir(); PRIVATE_LOGS.mkdir()
    began=time.perf_counter(); deadline=began+3600
    receipt={'status':'STARTED','started_utc':utc(),'limit_seconds':3600,'source_sha256':sha(Path(__file__).read_bytes()),
             'Julia_invocations':0,'Pkg_add_calls':0,'scientific_model_builds':0,'optimizer_calls':0,
             'package_cache_copied':False,'runtime_reused_read_only':True,'automatic_retry':False,
             'TLS_bypass':False,'certificate_injection':False,'global_settings_changed':False}
    save(OUT/'started.json',receipt)
    def remaining():
        value=deadline-time.perf_counter()
        if value<=0: raise TimeoutError('Attempt02 allocation expired')
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
        general=depot/'registries/General'; general.mkdir(parents=True)
        stage('download_pinned_official_registry_archive')
        registry_zip=ATTEMPT/'General.tar.gz'
        url='https://codeload.github.com/JuliaRegistries/General/tar.gz/'+GENERAL
        with urllib.request.urlopen(url,timeout=min(40,remaining())) as response, registry_zip.open('xb') as f:
            receipt['registry_final_url']=response.url; downloaded=0
            while True:
                remaining(); chunk=response.read(1024*1024)
                if not chunk: break
                downloaded+=len(chunk)
                if downloaded>100_000_000: raise ValueError('Registry compressed size cap')
                f.write(chunk)
        receipt.update(registry_archive_bytes=downloaded,registry_archive_sha256=sha(registry_zip.read_bytes()),
                       registry_commit=GENERAL,registry_expected_git_tree=GENERAL_TREE)
        stage('extract_and_verify_official_registry_git_tree')
        seen=set(); entries=[]; inventory=[]; total=0
        with tarfile.open(registry_zip,'r:gz') as tar:
            for member in tar:
                remaining()
                path=PurePosixPath(member.name)
                assert path.parts and path.parts[0]=='General-'+GENERAL
                parts=path.parts[1:]
                if not parts: assert member.isdir(); continue
                assert all(p not in ('.','..') and ':' not in p and '\\' not in p for p in parts)
                assert not member.issym() and not member.islnk()
                target=general.joinpath(*parts)
                assert target.resolve().is_relative_to(general.resolve())
                if member.isdir(): target.mkdir(parents=True,exist_ok=True); continue
                assert member.isfile()
                key='/'.join(parts).casefold(); assert key not in seen; seen.add(key)
                assert len(seen)<=250000
                total+=member.size; assert total<=2_000_000_000
                data=tar.extractfile(member).read(); assert len(data)==member.size
                target.parent.mkdir(parents=True,exist_ok=True)
                with target.open('xb') as f: f.write(data)
                assert sha(target.read_bytes())==sha(data)
                entries.append((parts,b'100755' if member.mode & 0o111 else b'100644',git_hash(b'blob',data)))
                inventory.append({'path':'/'.join(parts),'bytes':len(data),'sha256':sha(data)})
        actual_tree=git_tree(entries)
        assert actual_tree==GENERAL_TREE, 'Official archive differs from pinned full Git tree'
        save(OUT/'registry_inventory.json',{'commit':GENERAL,'git_tree':actual_tree,'files':inventory})
        receipt.update(registry_files=len(inventory),registry_bytes=total,registry_git_tree_verified=actual_tree)
        script=ATTEMPT/'instantiate_once.jl'
        script.write_text('''using Pkg, TOML, Dates, Logging
@assert VERSION == v"1.6.7"
@assert length(DEPOT_PATH) == 1
@assert abspath(DEPOT_PATH[1]) == abspath(ARGS[1])
@assert get(ENV,"JULIA_PKG_SERVER","unset") == ""
function stage(s)
    println(stderr, "STAGE ", s, " ", Dates.now(Dates.UTC)); flush(stderr)
end
global_logger(ConsoleLogger(stderr))
stage("PKG_TOML_IMPORT_COMPLETE")
@assert isfile(joinpath(DEPOT_PATH[1],"registries","General","Registry.toml"))
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
        "source"=>(p.source===nothing ? "" : string(p.source)),"direct"=>p.is_direct_dep)
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
        env=dict(os.environ,JULIA_DEPOT_PATH=str(depot),JULIA_LOAD_PATH='@;@stdlib',
                 JULIA_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',JULIA_PKG_PRECOMPILE_AUTO='0',
                 JULIA_PKG_SERVER='',TEMP=str(temp),TMP=str(temp))
        cmd=[str(julia),'--startup-file=no','--history-file=no','--project='+str(project),
             str(script),str(depot),str(ATTEMPT/'package_inventory.toml')]
        receipt.update(command=cmd,isolated_environment={k:env[k] for k in ('JULIA_DEPOT_PATH','JULIA_LOAD_PATH',
            'JULIA_NUM_THREADS','OPENBLAS_NUM_THREADS','JULIA_PKG_PRECOMPILE_AUTO','JULIA_PKG_SERVER','TEMP','TMP')})
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
        assert uc['git_revision']==UC
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
        assert sha(julia.read_bytes())==EXE_SHA and sha(archive.read_bytes())==ARCHIVE_SHA
        receipt.update(status='READY_ENVIRONMENT_ONLY_NO_MODEL_BUILD',selected_package=uc,
            pinned_native_files_verified=verified,installed_direct_versions={p['name']:p['version'] for p in packages if p['direct']},
            native_source_binding='Raw hashes preserved; read-only CRLF-to-LF equality to fixed Git blobs; no source normalization written')
    except BaseException as exc:
        receipt.update(status='SETUP_FAILED_PRESERVED_NO_RETRY',exception_type=type(exc).__name__,message=str(exc))
    marker=ATTEMPT/'pkg_add_started.txt'
    receipt['Pkg_add_calls']=int(marker.exists())
    if marker.exists(): receipt['Pkg_add_marker_sha256']=sha(marker.read_bytes())
    receipt.update(ended_utc=utc(),elapsed_seconds=time.perf_counter()-began,
                   allocation_overrun_seconds=max(0,time.perf_counter()-deadline))
    receipt['artifacts']=[{'path':p.name,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
                          for p in sorted(OUT.iterdir()) if p.is_file()]
    receipt['private_log_artifacts']=[{'path':p.relative_to(ATTEMPT).as_posix(),
        'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
        for p in sorted(PRIVATE_LOGS.iterdir()) if p.is_file()]
    receipt['private_logs_publication_status']='NOT_SELECTED_PENDING_ENTERPRISE_TLS_REVIEW'
    save(OUT/'ENVIRONMENT_ACQUISITION.json',receipt)
    print(json.dumps({k:receipt[k] for k in ('status','stage','elapsed_seconds','Julia_invocations','Pkg_add_calls')}),flush=True)
    return 0 if receipt['status']=='READY_ENVIRONMENT_ONLY_NO_MODEL_BUILD' else 1

if __name__=='__main__': sys.exit(main())
