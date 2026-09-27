"""Replay selected certificates from a verified ZIP in a fresh relocated directory.

This checks package portability on the same host, not native-data assembly or a
second machine. Only selected members are extracted; external manifests are not
replayed. Every extracted byte is first checked against the package manifest.
"""
from pathlib import Path, PurePosixPath
import argparse, csv, hashlib, io, json, subprocess, sys, time, zipfile

EXPECTED_ZIP_SHA256 = "4e1315dffaa6d02e55db5af225b4b0e9d3a8106ee6ba070c43d0fbad000868c6"
VERIFIER = "src/research8h_standalone_verify.py"
RAYS = ["results/research8h/hour_of_day/seed_26093200/lp", "results/research8h/hour_of_day/seed_26093201/lp"]
POINTS = ["results/research8h/hour_of_day/january_identity", "results/research8h/day_blocks/days_312"]
sha = lambda value: hashlib.sha256(value).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip",type=Path,required=True)
    parser.add_argument("--scratch",type=Path,required=True)
    parser.add_argument("--report-dir",type=Path,required=True)
    args=parser.parse_args()
    assert sha(args.zip.read_bytes()) == EXPECTED_ZIP_SHA256
    assert not args.scratch.exists() and not args.report_dir.exists()
    scratch=args.scratch.resolve(); scratch.mkdir(parents=True)
    args.report_dir.mkdir(parents=True)
    members={VERIFIER}
    for d in RAYS:
        members.update(d+"/"+n for n in ["matrix.npz","bounds.npz","row_metadata.csv.gz","raw_solver_ray.npz","dual_certificate.json"])
    for d in POINTS:
        members.update(d+"/"+n for n in ["matrix.npz","bounds.npz","integrality.npz","constructive_vector.npz"])
    extracted=[]
    with zipfile.ZipFile(args.zip) as archive:
        assert len(archive.namelist()) == len(set(archive.namelist()))
        manifest={r["path"]:r for r in csv.DictReader(io.StringIO(archive.read("FILE_MANIFEST.csv").decode("utf-8")))}
        for name in sorted(members):
            parts=PurePosixPath(name)
            assert not parts.is_absolute() and ".." not in parts.parts
            path=scratch.joinpath(*parts.parts).resolve()
            assert path.is_relative_to(scratch)
            data=archive.read(name); record=manifest[name]
            assert len(data)==int(record["bytes"]) and sha(data)==record["sha256"]
            path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
            extracted.append({"path":name,"bytes":len(data),"sha256":sha(data)})
    commands=[("self_test",["self-test"],"SELF_TESTS_PASS")]
    for i,d in enumerate(RAYS):
        commands.append(("HOD_ray_"+str(i),["ray","--model-dir",d,"--certificate",d+"/dual_certificate.json"],"CERTIFIED_EXPANDED_INFEASIBLE"))
    for i,d in enumerate(POINTS):
        commands.append(("point_"+str(i),["point","--model-dir",d,"--vector",d+"/constructive_vector.npz","--integrality",d+"/integrality.npz"],"CERTIFIED_EXPANDED_ONLY_POINT"))
    results=[]
    for name,tail,expected in commands:
        command=[sys.executable,"-I","-S",VERIFIER,*tail]
        started=time.perf_counter()
        call=subprocess.run(command,cwd=scratch,capture_output=True,text=True,timeout=180)
        report=json.loads(call.stdout)
        (args.report_dir/(name+".json")).write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        (args.report_dir/(name+".stderr.txt")).write_text(call.stderr,encoding="utf-8")
        assert call.returncode==0 and report["status"]==expected,(name,report)
        assert report["optimization_calls"]==0
        if "archived_gap_claim_comparison" in report:
            assert all(report["archived_gap_claim_comparison"].values())
        results.append({"case":name,"status":report["status"],"elapsed_s":time.perf_counter()-started,"command":command})
        print(json.dumps({"case":name,"status":report["status"]}),flush=True)
    output={"status":"SELECTED_RELOCATION_REPLAY_PASS","zip_sha256":EXPECTED_ZIP_SHA256,
        "source_sha256":sha(Path(__file__).read_bytes()),"scratch":str(scratch),"extracted_members":extracted,
        "results":results,"new_optimization_calls":0,"same_host":True,"new_experimental_cases":0,
        "scope":"Selected mathematical certificates replayed solely from ZIP member inputs using isolated stdlib Python. Full original-host manifests and native input assembly are not replayed here. Package manifest hashes checked for all extracted bytes. Not a second-machine test or general parser proof."}
    (args.report_dir/"summary.json").write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
