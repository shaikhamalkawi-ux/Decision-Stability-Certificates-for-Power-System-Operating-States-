"""Independent binding-only admission for the native reverse certificate."""
from pathlib import Path
import hashlib,json,time
ROOT=Path("C:/Users/gmalkawi/.codex/worktrees/dsc-temporal-information/3")
ARM=ROOT/"results/research_next/native_expanded_reverse"
PRE=ARM/"prepared"
FSHA="6863fc3027f570a87161c059f08789d967f891f3c87f5dc96add17fc97966eaa"
MSHA="f9b3c147cc517e5e028200c519b32238f4ec144c65b56ca7773a467e6c1635fa"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def validate(items):
 for x in items:
  b=Path(x["path"]).read_bytes()
  assert len(b)==x["bytes"] and hashlib.sha256(b).hexdigest()==x["sha256"],x["path"]
start=time.perf_counter()
assert not (ARM/"run01").exists()
assert sha(PRE/"prepared_freeze.json")==FSHA and sha(PRE/"manifest.json")==MSHA
m=read(PRE/"manifest.json");f=read(PRE/"prepared_freeze.json")
assert f["manifest_sha256"]==MSHA and f["scientific_arithmetic_runs"]==f["optimizer_calls"]==0
assert m["source_sha256"]=="494517bef073fca4126b37194c61b9cafbbab347798a7cf950bd548ca18bde6f"
assert m["protocol_sha256"]=="3c11f1c47301db1e6d3a4bdd11476010734fc688cb645536f7489b63dd187a6a"
assert len(m["inputs"])==499 and len(m["copies"])==34
validate(m["inputs"]);validate(m["copies"].values())
originals={x["path"]:x for x in m["inputs"]}
original_sha={(x["sha256"],x["bytes"]) for x in m["inputs"]}
for x in m["copies"].values():assert (x["sha256"],x["bytes"]) in original_sha
cp=lambda k:Path(m["copies"][k]["path"])
cm=read(cp("comparison_manifest"))
assert sha(cp("comparison_manifest"))=="b594e558f7587a1667407d48d39d0bc9f4c7a6804620121e438908d804eb4fc4"
assert all(originals[x["path"]]==x for x in cm["inputs"]+list(cm["copies"].values()))
for k in ("raw","parsed","normal","model"):
 x=cm["copies"][k];assert cp(k).read_bytes()==Path(x["path"]).read_bytes()
review=read(cp("comparison_review"))
assert sha(cp("comparison_review"))=="bb44ef305c468a9e334a0a8e5ee63fc84ac8e87aec057c8e05e21ad07a2f8cc6"
assert review["case"]=="reverse_4_19__native_penalized"
assert review["status"]=="PASS_INDEPENDENT_EXACT_NOMINAL_PROJECTION_EQUIVALENCE"
assert review["manifest_sha256"]=="b594e558f7587a1667407d48d39d0bc9f4c7a6804620121e438908d804eb4fc4"
for name,digest in review["producer_snapshot"].items():assert sha(ROOT/"results/research_next/native_reverse_compare/run01"/name)==digest
ir=read(cp("identity_review"))
assert sha(cp("identity_review"))=="8f13f3a1751e03f2e4487127159420d14717bfff2b2c810a5c829f13bfa1b2e1"
assert ir["status"]=="PASS_INDEPENDENT_NATIVE_EXPANDED_POINT_AND_LOWER_REPLAY"
for k,n in [("identity_result","result.json"),("identity_lower","native_lower_certificate.json"),("identity_point","native_point_check.json"),("identity_completion","completion.json")]:
 assert sha(cp(k))==ir["producer_outputs_unchanged"][n]
lookup={x["path"]:x for x in read(cp("old_output_manifest"))["files"]}
for role,suffix in [("candidate","mip/candidate_vector.json"),("raw_lp","lp/raw_solution.npz"),("signed_bound","lp/signed_dual_bound.json"),("mip_result","mip/result.json"),("mip_checks","mip/exact_candidate_checks.json"),("lp_result","lp/result.json")]:
 x=lookup["outputs/reverse_4_19__native_penalized/"+suffix]
 assert sha(cp(role))==x["sha256"] and cp(role).stat().st_size==x["bytes"]
validate(m["inputs"]);validate(m["copies"].values())
assert sha(PRE/"prepared_freeze.json")==FSHA and sha(PRE/"manifest.json")==MSHA
assert not (ARM/"run01").exists()
result=dict(status="PASS_INDEPENDENT_BINDING_ONLY_PREPARED_GATE",elapsed_seconds=time.perf_counter()-start,
 freeze_sha256=FSHA,manifest_sha256=MSHA,original_bindings=499,copies=34,all_unchanged=True,
 actual_target_comparison_inherited=True,closed_identity_bounds_inherited=True,
 scientific_models_or_points_decoded=False,scientific_arithmetic_runs=0,optimizer_calls=0,
 producer_imports=0,review_source_sha256=sha(__file__))
with (ARM/"ROOT_PREPARED_REVIEW.json").open("x",encoding="utf-8") as out:json.dump(result,out,indent=2);out.write("\n")
print(json.dumps(result))
