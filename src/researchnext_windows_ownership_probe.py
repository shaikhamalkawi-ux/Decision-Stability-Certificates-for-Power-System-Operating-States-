"""Prospective harmless Windows ownership capability probe; never imports a backend."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import types
import uuid

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
ARM=ROOT/'results/research_next/windows_ownership_probe';RUN=ARM/'probe01'
PROTOCOL=ROOT/'docs/research_next/WINDOWS_OWNERSHIP_PROBE_PROTOCOL.md'
FROZEN=ROOT/'src/researchnext_common_refinement_batch.py'
FROZEN_SHA='f7f79ecca154169832c8739d9c17889c5c5993aa460f6d528d6f115c60018371'
WORKER_PY=ROOT/'.work/scip_capability_env01/Scripts/python.exe'
ARMS=('shared_job_launcher_then_actual','separate_job_per_process')
PHASE=120.;HANDSHAKE=20.;WORKER_LIFETIME=45.

def need(ok,message):
    if not ok:raise ValueError(message)
def utc():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def save(path,value):
    with Path(path).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def publish(path,value):
    path=Path(path);tmp=path.with_name(path.name+'.writing');need(not path.exists(),'Fresh marker');save(tmp,value);tmp.rename(path)
def no_backend():
    forbidden=('pyscipopt','highspy','numpy','scipy','gurobipy')
    return not any(n==p or n.startswith(p+'.') for n in sys.modules for p in forbidden)

def harmless_worker(folder,token,source_sha):
    path=Path(folder).resolve();need(path.parent==RUN.resolve() and path.name in ARMS,'Only fresh probe child path')
    need(sha(__file__)==source_sha and Path(sys.executable).resolve()==WORKER_PY.resolve(),'Pinned harmless worker')
    need(no_backend(),'No scientific backend imports');started=time.perf_counter()
    publish(path/'ready.json',dict(utc=utc(),token=token,pid=os.getpid(),parent_pid=os.getppid(),source_sha256=source_sha,
        executable=sys.executable,python=sys.version,backend_imports=0,scientific_reads=0))
    while time.perf_counter()-started<WORKER_LIFETIME:
        if (path/'continue.json').exists():
            need(read(path/'continue.json')['token']==token,'Authenticated harmless continuation')
            publish(path/'running.json',dict(utc=utc(),pid=os.getpid(),only_action='bounded sleep',backend_imports=0,scientific_reads=0))
            while time.perf_counter()-started<WORKER_LIFETIME:time.sleep(.05)
            break
        time.sleep(.05)
    need(no_backend(),'No scientific imports at child close')
    save(path/'self_exit.json',dict(utc=utc(),pid=os.getpid(),elapsed=time.perf_counter()-started,backend_imports=0,optimizer_calls=0))

def load_frozen_class():
    captured=FROZEN.read_bytes();need(hashlib.sha256(captured).hexdigest()==FROZEN_SHA,'Captured frozen ownership source unchanged')
    name='ownership_frozen_source_only';obj=types.ModuleType(name);obj.__file__=str(FROZEN)
    sys.modules[name]=obj;exec(compile(captured,str(FROZEN),'exec'),obj.__dict__)
    need(no_backend(),'Importing definitions must not import a backend')
    return obj.OwnedWindowsJob

def probe_arm(name,Job,deadline):
    folder=RUN/name;folder.mkdir();token=uuid.uuid4().hex;started=time.perf_counter();jobs=[];handles=[];child=None
    report=dict(arm=name,assignment_attempts=[],processes=[],scientific_reads=0,backend_imports=0,optimizer_calls=0,status='UNRESOLVED')
    # The same pinned class constructs job flags, ctypes layouts and API prototypes.
    rootjob=Job();jobs.append(rootjob);ct=rootjob.ct;wt=rootjob.wt;k=rootjob.k
    k.IsProcessInJob.argtypes=[wt.HANDLE,wt.HANDLE,ct.POINTER(wt.BOOL)];k.IsProcessInJob.restype=wt.BOOL
    k.TerminateProcess.argtypes=[wt.HANDLE,wt.UINT];k.TerminateProcess.restype=wt.BOOL
    k.GetExitCodeProcess.argtypes=[wt.HANDLE,ct.POINTER(wt.DWORD)];k.GetExitCodeProcess.restype=wt.BOOL
    def membership(handle,job):
        answer=wt.BOOL();ct.set_last_error(0);ok=k.IsProcessInJob(handle,job,ct.byref(answer));error=ct.get_last_error()
        return dict(api_succeeded=bool(ok),win32_last_error=error,in_job=bool(answer.value) if ok else None)
    def capture(pid,role):
        ct.set_last_error(0);h=k.OpenProcess(0x0001|0x0100|0x0400|0x00100000,False,pid);error=ct.get_last_error()
        need(bool(h),'Open exact owned harmless process; Win32='+str(error));handles.append(h)
        item=dict(role=role,pid=pid,creation_filetime=None,any_job_before=None);report['processes'].append(item)
        a,b,c,d=(wt.FILETIME() for _ in range(4));ct.set_last_error(0)
        ok=k.GetProcessTimes(h,ct.byref(a),ct.byref(b),ct.byref(c),ct.byref(d));error=ct.get_last_error();need(bool(ok),'Exact process creation capture; Win32='+str(error))
        item.update(creation_filetime=(a.dwHighDateTime<<32)|a.dwLowDateTime,any_job_before=membership(h,None));return h,item
    def assign(job,h,item,number):
        before_any=membership(h,None);before_own=membership(h,job.handle)
        ct.set_last_error(0);ok=k.AssignProcessToJobObject(job.handle,h);error=ct.get_last_error()
        attempt=dict(order=number,role=item['role'],pid=item['pid'],creation_filetime=item['creation_filetime'],
            job_index=jobs.index(job),before_any=before_any,before_selected=before_own,assignment_succeeded=bool(ok),win32_last_error=error,
            after_any=membership(h,None),after_selected=membership(h,job.handle))
        report['assignment_attempts'].append(attempt);save(folder/f'assignment_{number}.json',attempt)
        return bool(ok)
    try:
        need(deadline-time.perf_counter()>=HANDSHAKE+10.,'Prospective arm start guard')
        command=[str(WORKER_PY),'-I',str(Path(__file__).resolve()),'--harmless-worker','--folder',str(folder.resolve()),'--token',token,'--expected-source-sha256',sha(__file__)]
        save(folder/'launch.json',dict(utc=utc(),command=command,worker_launches=1,optimizer_calls=0))
        with (folder/'worker_stdout.log').open('x',encoding='utf-8') as output:
            child=subprocess.Popen(command,stdout=output,stderr=output);limit=min(deadline,time.perf_counter()+HANDSHAKE)
            while not (folder/'ready.json').exists():
                need(child.poll() is None,'Harmless child ended before ready');need(time.perf_counter()<limit,'Harmless handshake timeout');time.sleep(.05)
            ready=read(folder/'ready.json');need(ready['token']==token and ready['source_sha256']==sha(__file__),'Ready binding')
            need(ready['pid']==child.pid or ready['parent_pid']==child.pid,'Exact direct parent chain')
            launcher,li=capture(child.pid,'launcher');actual,ai=(launcher,li) if ready['pid']==child.pid else capture(ready['pid'],'actual_python')
            save(folder/'owned_process_chain.json',dict(launcher_pid=child.pid,actual_pid=ready['pid'],actual_parent_pid=ready['parent_pid'],processes=report['processes']))
            first=assign(rootjob,launcher,li,1);second=None
            if first and actual!=launcher:
                target=rootjob
                if name=='separate_job_per_process':target=Job();jobs.append(target)
                second=assign(target,actual,ai,2)
            assignments_pass=first and (actual==launcher or second is True)
            report['assignments_passed']=assignments_pass
            if assignments_pass:
                publish(folder/'continue.json',dict(token=token,harmless_action_only=True));limit=min(deadline,time.perf_counter()+5.)
                while not (folder/'running.json').exists():need(time.perf_counter()<limit,'Harmless running marker timeout');time.sleep(.05)
                report['status']='ASSIGNMENT_PASSED_HARMLESS_CLEANUP_PENDING'
            else:report['status']='ASSIGNMENT_FAILED_RECORDED'
    except BaseException as exc:
        report['error']=dict(type=type(exc).__name__,message=str(exc));report['status']='PROBE_ERROR'
    finally:
        cleanup=[]
        # Exact retained handles identify only this arm's authenticated harmless processes.
        for index,job in reversed(list(enumerate(jobs))):
            ct.set_last_error(0);ok=k.TerminateJobObject(job.handle,73);error=ct.get_last_error()
            cleanup.append(dict(action='TerminateJobObject',job_index=index,succeeded=bool(ok),win32_last_error=error))
        for h,item in reversed(list(zip(handles,report['processes']))):
            wait=int(k.WaitForSingleObject(h,1000))
            if wait!=0:
                ct.set_last_error(0);ok=k.TerminateProcess(h,74);error=ct.get_last_error()
                cleanup.append(dict(action='TerminateProcess_owned_retained_handle',pid=item['pid'],creation_filetime=item['creation_filetime'],succeeded=bool(ok),win32_last_error=error))
                wait=int(k.WaitForSingleObject(h,5000))
            exitcode=wt.DWORD();ok=k.GetExitCodeProcess(h,ct.byref(exitcode))
            cleanup.append(dict(action='reap',pid=item['pid'],wait_result=wait,reaped=wait==0,exit_code=int(exitcode.value) if ok else None))
        if child is not None:
            if child.poll() is None and not handles:
                # Popen supplies ownership of this exact launcher before a handshake; no guessed descendant PID.
                child.kill();report['unhandshaken_launcher_terminated']=True
            try:child.wait(timeout=5.);report['launcher_exit_code']=child.returncode
            except subprocess.TimeoutExpired:report['launcher_reap_failed']=True
        report['cleanup']=cleanup
        report['captured_process_count']=len(handles)
        report['all_captured_handles_reaped']=bool(handles) and all(x['reaped'] for x in cleanup if x['action']=='reap')
        report['child_closure_unverified_without_handles']=not handles
        report['unobserved_child_selfexit_required']=bool(child is not None and not handles)
        report['elapsed_seconds']=time.perf_counter()-started
        report['no_outer_job_reconfiguration']=True;report['no_breakaway_flags']=True
        if report['status']=='ASSIGNMENT_PASSED_HARMLESS_CLEANUP_PENDING' and report['all_captured_handles_reaped']:report['status']='PASS_HARMLESS_ASSIGNMENT_AND_CLEANUP'
        save(folder/'result.json',report)
        for h in handles:k.CloseHandle(h)
        for job in jobs:job.close()
    return report

def run(expected_source,expected_protocol):
    pins=[(Path(__file__).resolve(),expected_source),(PROTOCOL,expected_protocol),(FROZEN,FROZEN_SHA)]
    need(os.name=='nt' and all(hashlib.sha256(p.read_bytes()).hexdigest()==digest for p,digest in pins),'Externally approved probe bytes')
    need(not RUN.exists() and no_backend(),'One fresh harmless probe');RUN.mkdir(parents=True);started=time.perf_counter();deadline=started+PHASE
    save(RUN/'started.json',dict(utc=utc(),pid=os.getpid(),parent_pid=os.getppid(),source_sha256=expected_source,protocol_sha256=expected_protocol,
        frozen_class_sha256=FROZEN_SHA,arms=list(ARMS),phase_seconds=PHASE,scientific_reads=0,optimizer_calls=0))
    results=[]
    try:
        Job=load_frozen_class()
        for name in ARMS:
            if deadline-time.perf_counter()<HANDSHAKE+10.:
                results.append(dict(arm=name,status='NOT_RUN_PHASE_GUARD'));continue
            try:result=probe_arm(name,Job,deadline)
            except BaseException as exc:
                save(RUN/name/'outer_failure.json',dict(utc=utc(),error_type=type(exc).__name__,message=str(exc),no_retry=True))
                results.append(dict(arm=name,status='PROBE_ERROR_OUTER',failure_sha256=sha(RUN/name/'outer_failure.json')));break
            results.append(dict(arm=name,status=result['status'],result_sha256=sha(RUN/name/'result.json')))
            need(result['all_captured_handles_reaped'] and not result.get('launcher_reap_failed'),'Stop if owned cleanup is unresolved')
    finally:
        need(no_backend(),'No backend imported during capability test')
        final_bindings=[]
        for path,expected in pins:
            actual=sha(path) if path.is_file() else None
            final_bindings.append(dict(path=str(path),expected_sha256=expected,actual_sha256=actual,unchanged=actual==expected))
        unchanged=all(x['unchanged'] for x in final_bindings)
        save(RUN/'completion.json',dict(utc=utc(),arms=results,elapsed_seconds=time.perf_counter()-started,scientific_reads=0,backend_imports=0,optimizer_calls=0,
            no_scientific_resume_authorized=True,no_frozen_source_changed=unchanged,final_source_bindings=final_bindings,original_failure_which_assignment_remains_unrecorded=True))
        need(unchanged,'Closing probe/source/protocol/helper pin changed')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--run-probe',action='store_true');g.add_argument('--harmless-worker',action='store_true')
    p.add_argument('--expected-source-sha256',required=True);p.add_argument('--expected-protocol-sha256');p.add_argument('--folder');p.add_argument('--token');a=p.parse_args()
    if a.harmless_worker:need(a.folder and a.token,'Harmless worker arguments');harmless_worker(a.folder,a.token,a.expected_source_sha256)
    else:need(a.expected_protocol_sha256,'External protocol hash');run(a.expected_source_sha256,a.expected_protocol_sha256)
