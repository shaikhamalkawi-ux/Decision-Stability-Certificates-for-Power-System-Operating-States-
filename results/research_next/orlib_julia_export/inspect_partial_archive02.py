"""Bounded read-only gzip/tar diagnostic; no extraction, Julia or network."""
from pathlib import Path
from datetime import datetime, timezone
import gzip, hashlib, json, tarfile, time

repo=Path(__file__).resolve().parents[3]
folder=Path(__file__).resolve().parent
archive=repo/'.work/researchnext_julia_export/attempt02/General.tar.gz'
output=folder/'ATTEMPT02_PARTIAL_ARCHIVE_DIAGNOSTIC.json'
assert not output.exists()
start=time.perf_counter(); deadline=start+30
def guard():
    if time.perf_counter()>=deadline: raise TimeoutError('30-second diagnostic limit')
record={'status':'READ_ONLY_DIAGNOSTIC_STARTED','started_utc':datetime.now(timezone.utc).isoformat(),
        'limit_seconds':30,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'archive_bytes':archive.stat().st_size,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
        'extractions':0,'Julia_invocations':0,'optimizer_calls':0,'network_requests':0,
        'recorded_HTTP_metadata':{'final_url':'https://codeload.github.com/JuliaRegistries/General/tar.gz/416a13c3e4888af4b245812d8f4ab040a042c38f',
            'Content_Length':'NOT_RECORDED','Transfer_Encoding':'NOT_RECORDED','expected_total_bytes':'UNKNOWN'}}
decoded=0
try:
    with gzip.open(archive,'rb') as f:
        while True:
            guard(); data=f.read(64*1024)
            if not data: break
            decoded+=len(data)
            if decoded>2_000_000_000: raise ValueError('Diagnostic uncompressed-size limit')
    record['gzip']={'status':'COMPLETE_STREAM_CRC_AND_SIZE_ACCEPTED','decoded_bytes':decoded}
except Exception as exc:
    record['gzip']={'status':'NOT_ACCEPTED_COMPLETE_GZIP','decoded_bytes_before_failure':decoded,
                    'exception_type':type(exc).__name__,'error':str(exc)}
members=0; declared=0; last=None
try:
    guard()
    with tarfile.open(archive,'r|gz') as tar:
        for item in tar:
            guard(); members+=1; declared+=item.size; last=item.name
            if members>250000 or declared>2_000_000_000: raise ValueError('Diagnostic tar-size limit')
    record['tar']={'status':'TAR_READER_REACHED_END','members_yielded':members,
                   'declared_payload_bytes':declared,'last_member':last,
                   'limit':'Tar end recognition alone does not certify the enclosing gzip CRC/trailer.'}
except Exception as exc:
    record['tar']={'status':'TAR_READER_DID_NOT_COMPLETE','members_yielded':members,
                   'declared_payload_bytes':declared,'last_member':last,
                   'exception_type':type(exc).__name__,'error':str(exc)}
record.update(status='CLOSED_PARTIAL_ARCHIVE_DIAGNOSTIC',ended_utc=datetime.now(timezone.utc).isoformat(),
              elapsed_seconds=time.perf_counter()-start)
record['archive_unchanged']=hashlib.sha256(archive.read_bytes()).hexdigest()==record['archive_sha256']
record['admission']='NOT_ADMITTED_UNLESS_COMPLETE_GZIP_AND_PINNED_GIT_TREE_VERIFIED; no tree verification performed here'
with output.open('x',encoding='utf-8') as f: json.dump(record,f,indent=2); f.write('\n')
print(json.dumps(record))
