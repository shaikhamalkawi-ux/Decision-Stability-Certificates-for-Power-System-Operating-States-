"""Invoke the frozen approved runner once; observe its allocation clock only."""
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import runpy
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
RUNNER = ROOT/"src/research8h_hour_of_day.py"
SOURCE = Path(r"C:/Users/gmalkawi/.codex/worktrees/dsc-v8r1-evidence/3/.work/v8r1_rts_inputs")
EXPECTED = "b617d41ab09d18d57c003147b52ae80f369225bc6029121109cee3d53e71d60e"
MANIFEST = "078082667f83322d3540ad3ac215ebcc996d0d31b04fd52bfa75c1d2fd814fcc"


def save(path, value):
    with path.open("x",encoding="utf-8") as f:
        json.dump(value,f,indent=2)
        f.write("\n")


assert hashlib.sha256(RUNNER.read_bytes()).hexdigest() == EXPECTED
assert hashlib.sha256((BASE/"input_manifest.csv").read_bytes()).hexdigest() == MANIFEST
review = json.loads((BASE/"independent_prepared_review.json").read_text(encoding="utf-8"))
assert review["status"] == "INDEPENDENT_PREPARED_REVIEW_PASS" and review["manifest_sha256"] == MANIFEST
assert not (BASE/"execution_started.json").exists()
assert sys.gettrace() is None
started_utc = datetime.now(timezone.utc)
started_clock = time.perf_counter()
save(BASE/"timed_execution_started.json",{"observed_process_invocation_utc":started_utc.isoformat(),
    "root_GO_received":True,"frozen_source_sha256":EXPECTED,"frozen_manifest_sha256":MANIFEST,
    "timing_wrapper_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "instrumentation":"read phase_started from original running frame; no model or runner mutation",
    "additional_optimization_calls":0})
allocation = {}


def trace(frame,event,arg):
    if Path(frame.f_code.co_filename).resolve() != RUNNER.resolve():
        return None
    if frame.f_code.co_name == "run_prepared" and event == "line" and "phase_started" in frame.f_locals:
        clock = time.perf_counter()
        utc = datetime.now(timezone.utc)
        phase = float(frame.f_locals["phase_started"])
        allocation.update({"allocation_start_perf_counter":phase,"observation_perf_counter":clock,
            "observation_utc":utc.isoformat(),"observation_lag_seconds":clock-phase,
            "allocation_start_utc_approximate":(utc-timedelta(seconds=clock-phase)).isoformat(),
            "timestamp_scope":"UTC inferred from paired live clocks, not a file timestamp; perf_counter start read directly",
            "validation_and_native_loading_seconds_approximate":phase-started_clock})
        sys.settrace(None)
        save(BASE/"allocation_clock_observation.json",allocation)
        return None
    return trace


error = None
try:
    sys.path.insert(0,str(ROOT/"src"))
    sys.argv = [str(RUNNER),"--source-v3",str(SOURCE),"--run-prepared"]
    sys.settrace(trace)
    runpy.run_path(str(RUNNER),run_name="__main__")
except BaseException as exc:
    error = {"type":type(exc).__name__,"message":str(exc)}
    raise
finally:
    sys.settrace(None)
    ended_clock = time.perf_counter()
    ended_utc = datetime.now(timezone.utc)
    completion_path = BASE/"completion.json"
    completion = json.loads(completion_path.read_text(encoding="utf-8")) if completion_path.exists() else None
    phase_elapsed = completion["phase_elapsed_s"] if completion is not None else None
    save(BASE/"postrun_allocation_audit.json",{"process_invocation_utc":started_utc.isoformat(),
        "process_end_observed_utc":ended_utc.isoformat(),"invocation_elapsed_s":ended_clock-started_clock,
        "allocation_clock_observation":allocation,"configured_soft_allocation_s":1200,
        "reported_phase_elapsed_s":phase_elapsed,
        "reported_phase_overrun_s":max(0.,phase_elapsed-1200) if phase_elapsed is not None else None,
        "hard_wall_time_cap_claim":False,"error":error,"frozen_completion":completion,
        "frozen_source_sha256_after":hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
        "frozen_manifest_sha256_after":hashlib.sha256((BASE/"input_manifest.csv").read_bytes()).hexdigest(),
        "additional_optimization_calls":0})
