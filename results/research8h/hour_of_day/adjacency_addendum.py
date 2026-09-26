"""Read-only arithmetic over frozen source-hour maps; no optimizer/imported model."""
from pathlib import Path
import csv
import hashlib
import json

BASE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (BASE/"execution_started.json").exists()
    freeze = json.loads((BASE/"prepared_freeze.json").read_text(encoding="utf-8"))
    assert digest(BASE/"input_manifest.csv") == freeze["manifest_sha256"]
    checks = []
    for row in csv.DictReader((BASE/"input_manifest.csv").open(newline="",encoding="utf-8")):
        path = Path(row["path"])
        assert path.stat().st_size == int(row["bytes"]) and digest(path) == row["sha256"]
        checks.append(row)
    cases = []
    for case in ["january_identity", "seed_26093200", "seed_26093201", "seed_26100200"]:
        path = BASE/case/"permutation.csv"
        records = list(csv.DictReader(path.open(newline="",encoding="utf-8")))
        order = [int(x["source_hour_0based"]) for x in records]
        broken = [t for t in range(167) if order[t+1] != order[t]+1]
        positionwise = [t for t in range(167) if (order[t],order[t+1]) != (t,t+1)]
        assert sorted(order) == list(range(168)) and all(order[t]%24 == t%24 for t in range(168))
        prior = json.loads((BASE/case/"preservation.json").read_text(encoding="utf-8"))
        assert prior["changed_adjacent_pair_count"] == len(broken)
        assert prior["changed_adjacent_pairs_after_hours"] == broken
        cases.append({"case":case,"source_permutation_sha256":digest(path),
            "broken_source_continuity_count":len(broken),"broken_source_continuity_after_destination_hours":broken,
            "literal_positionwise_changed_pair_count":len(positionwise),
            "literal_positionwise_changed_pairs":[{"after_destination_hour":t,"left_source_hour":order[t],
                "right_source_hour":order[t+1]} for t in positionwise]})
    result = {"optimization_calls":0,"source_and_protocol_unchanged":True,"frozen_files_checked":len(checks),
        "frozen_manifest_sha256":freeze["manifest_sha256"],"source_sha256":freeze["source_sha256"],
        "protocol_sha256":freeze["protocol_sha256"],"addendum_source_sha256":digest(Path(__file__)),
        "interpretation_sha256":digest(BASE/"PREPARED_INTERPRETATION.md"),"cases":cases}
    with (BASE/"adjacency_addendum.json").open("x",encoding="utf-8") as output:
        json.dump(result,output,indent=2)
        output.write("\n")
    print(json.dumps({"frozen_files_checked":len(checks),"cases":[{k:r[k] for k in ["case",
        "broken_source_continuity_count","literal_positionwise_changed_pair_count"]} for r in cases]}))


if __name__ == "__main__":
    main()
