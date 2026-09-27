"""One bounded isolated install and empty SCIP capability probe; no optimization."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
from urllib.parse import urlparse
import zipfile
from email.parser import BytesParser

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/research_next/scip_capability/setup01'
PRIVATE=ROOT/'.work/scip_capability/setup01'
ENV=ROOT/'.work/scip_capability_env01'
PROBE=ROOT/'src/researchnext_scip_probe.py'
PROTOCOL=ROOT/'results/research_next/scip_capability/SETUP_PROTOCOL.md'
SPECS=(('pyscipopt','6.2.1','pyscipopt-6.2.1-cp312-cp312-win_amd64.whl'),
       ('numpy','2.3.5','numpy-2.3.5-cp312-cp312-win_amd64.whl'))
SECONDS=1800.0

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
    with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def binding(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def main():
    start=time.perf_counter();stage='fresh_path_check';calls=[];downloads=[]
    assert sys.version_info[:3]==(3,12,14)
    assert not OUT.exists() and not PRIVATE.exists() and not ENV.exists()
    OUT.mkdir(parents=True);PRIVATE.mkdir(parents=True)
    save(OUT/'started.json',dict(utc=datetime.now(timezone.utc).isoformat(),source=binding(Path(__file__)),
        probe=binding(PROBE),protocol=binding(PROTOCOL),allocation_seconds=SECONDS,network='normal TLS; official PyPI only',
        retries=0,optimizer_calls=0,scientific_model_reads=0))
    def remaining():
        left=SECONDS-(time.perf_counter()-start)
        if left<=0:raise TimeoutError('Setup phase allocation exhausted')
        return left
    def fetch(url,dest,maximum):
        assert urlparse(url).scheme=='https' and urlparse(url).hostname in ('pypi.org','files.pythonhosted.org')
        began=time.perf_counter();total=0
        with urllib.request.urlopen(url,timeout=min(60.0,remaining())) as response, dest.open('xb') as f:
            assert urlparse(response.url).scheme=='https' and urlparse(response.url).hostname in ('pypi.org','files.pythonhosted.org')
            while True:
                remaining();block=response.read(1024*1024)
                if not block:break
                total+=len(block);assert total<=maximum;f.write(block)
        downloads.append(dict(url=url,output=binding(dest),seconds=time.perf_counter()-began,attempts=1))
    def child(name,command,limit):
        duration=min(float(limit),remaining());rec=dict(name=name,command=command,timeout_seconds=duration,attempted=1)
        calls.append(rec);save(OUT/(name+'_started.json'),rec);began=time.perf_counter()
        env=dict(os.environ);env['PYTHONNOUSERSITE']='1';env['PYTHONDONTWRITEBYTECODE']='1'
        with (PRIVATE/(name+'.log')).open('xb') as log:
            try:
                process=subprocess.run(command,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,
                    cwd=ROOT,env=env,timeout=duration,check=False)
                rec['returncode']=process.returncode
            finally:rec['seconds']=time.perf_counter()-began
        save(OUT/(name+'_returned.json'),rec)
        assert process.returncode==0,name+' failed; no retry'
    try:
        wheel_records=[]
        for package,version,filename in SPECS:
            stage='official_metadata_'+package
            meta=OUT/(package+'_pypi.json');fetch(f'https://pypi.org/pypi/{package}/{version}/json',meta,10*1024*1024)
            data=json.loads(meta.read_bytes());assert data['info']['version']==version
            matches=[x for x in data['urls'] if x['filename']==filename]
            assert len(matches)==1;record=matches[0]
            assert not record['yanked'] and record['packagetype']=='bdist_wheel'
            wheel_records.append(dict(package=package,version=version,filename=filename,url=record['url'],
                bytes=record['size'],sha256=record['digests']['sha256'],metadata=binding(meta)))
        save(OUT/'official_wheel_selection.json',dict(wheels=wheel_records))
        for record in wheel_records:
            stage='download_'+record['package'];wheel=PRIVATE/record['filename']
            fetch(record['url'],wheel,100*1024*1024)
            assert wheel.stat().st_size==record['bytes'] and sha(wheel)==record['sha256']
            with zipfile.ZipFile(wheel) as z:
                names=[n for n in z.namelist() if n.endswith('.dist-info/METADATA')];assert len(names)==1
                metadata=z.read(names[0]);parsed=BytesParser().parsebytes(metadata)
                assert parsed['Version']==record['version']
                (OUT/(record['package']+'_wheel_METADATA.txt')).write_bytes(metadata)
                record['requires_dist']=parsed.get_all('Requires-Dist',[])
        save(OUT/'downloaded_wheels.json',dict(wheels=wheel_records,downloads=downloads))
        stage='create_isolated_venv'
        child('venv',[sys.executable,'-I','-m','venv',str(ENV)],300)
        python=ENV/'Scripts/python.exe';assert python.is_file()
        requirements=PRIVATE/'requirements.txt'
        requirements.write_text(''.join(f'{(PRIVATE/r["filename"]).as_uri()} --hash=sha256:{r["sha256"]}\n' for r in wheel_records),encoding='utf-8')
        stage='single_offline_package_install'
        child('pip_install',[str(python),'-I','-m','pip','--isolated','--disable-pip-version-check',
             '--retries','0','--timeout','60','install','--no-index','--no-deps','--only-binary=:all:',
             '--require-hashes','-r',str(requirements)],600)
        stage='empty_model_capability_probe'
        child('empty_probe',[str(python),'-I',str(PROBE),'--output',str(OUT/'capability.json')],120)
        capability=json.loads((OUT/'capability.json').read_bytes())
        assert capability['packages']=={'pyscipopt':'6.2.1','numpy':'2.3.5'}
        assert capability['optimizer_calls']==capability['scientific_model_reads']==0
        payloads=[]
        site=ENV/'Lib/site-packages'
        for path in site.rglob('*'):
            if path.is_file() and (path.suffix.lower() in ('.dll','.pyd') or path.name in ('METADATA','WHEEL','INSTALLER','direct_url.json','RECORD')):
                payloads.append(binding(path))
        save(OUT/'installed_payload_hashes.json',dict(files=payloads))
        elapsed=time.perf_counter()-start
        save(OUT/'completion.json',dict(status='CLOSED_EMPTY_MODEL_CAPABILITY_ONLY',utc=datetime.now(timezone.utc).isoformat(),
            calls=calls,downloads=downloads,phase_seconds=elapsed,soft_overrun_seconds=max(0,elapsed-SECONDS),
            source=binding(Path(__file__)),probe=binding(PROBE),protocol=binding(PROTOCOL),
            exact_parameter_enabled=capability['exact_mode']['enabled'],certificate_validated=False,
            package_manager_attempts=1,package_manager_retries=0,optimizer_calls=0,scientific_model_reads=0,
            synthetic_solves=0,global_environment_changes=False,license_modifications=False,
            completion_write_and_private_receipt_outside_elapsed_sample=True))
        print(json.dumps(dict(status='CAPABILITY_SETUP_CLOSED',exact_parameter_enabled=capability['exact_mode']['enabled'])))
    except BaseException as exc:
        save(OUT/'failure.json',dict(stage=stage,error_type=type(exc).__name__,calls=calls,downloads=downloads,
            seconds=time.perf_counter()-start,automatic_retry=False,optimizer_calls=0,scientific_model_reads=0))
        raise RuntimeError('Isolated SCIP setup stopped; failure preserved; no retry') from None
    finally:
        save(OUT/'private_log_receipt.json',dict(raw_logs_public=False,privacy_review='NOT_PERFORMED',
            files=[binding(p) for p in sorted(PRIVATE.glob('*.log'))]))

if __name__=='__main__':main()
