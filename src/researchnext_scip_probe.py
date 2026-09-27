"""Empty-model capability probe only: no variables, files, or optimize call."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode=True

def main(output):
    start=time.perf_counter()
    import pyscipopt
    from pyscipopt import Model
    model=Model('empty_capability_only')
    model.hideOutput()
    assert model.getNVars()==0 and model.getNConss()==0
    params=model.getParams()
    selected={k:v for k,v in params.items() if k.startswith(('exact/','certificate/'))}
    exact=dict(parameter_present='exact/enable' in params,enable_attempted=False,enabled=False)
    if exact['parameter_present']:
        exact['before']=params['exact/enable'];exact['enable_attempted']=True
        try:
            model.setParam('exact/enable',True)
            exact['after']=model.getParam('exact/enable');exact['enabled']=exact['after'] is True
        except Exception as exc:
            exact['error_type']=type(exc).__name__
    assert model.getNVars()==0 and model.getNConss()==0
    result=dict(status='EMPTY_MODEL_CAPABILITY_PROBE_COMPLETE',utc=datetime.now(timezone.utc).isoformat(),
        python=sys.version,executable=sys.executable,
        packages={n:importlib.metadata.version(n) for n in ('pyscipopt','numpy')},
        scip_version=[model.getMajorVersion(),model.getMinorVersion(),model.getTechVersion()],
        initial_stage=model.getStageName(),empty_variables=0,empty_constraints=0,
        selected_parameters_before=selected,exact_mode=exact,
        certificate_filename_parameter_present='certificate/filename' in params,
        scientific_model_reads=0,synthetic_models=0,optimizer_calls=0,problem_file_reads=0,
        capability_is_not_certificate_validation=True,
        probe_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        seconds=time.perf_counter()-start)
    model.freeProb()
    with Path(output).open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);main(parser.parse_args().output)
