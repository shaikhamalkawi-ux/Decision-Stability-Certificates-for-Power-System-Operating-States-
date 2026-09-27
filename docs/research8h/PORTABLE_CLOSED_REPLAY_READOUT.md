# Closed-evidence portable replay: first relocated execution

The reviewed wrapper completed its first full execution successfully in a newly extracted directory on the same Windows host. The isolated Python 3.12.14 command used `-I -S`, the standard library and the hash-pinned existing exact-verification kernel. It made no optimizer or network calls. Elapsed wrapper time was 59.566826099995524 seconds; process session 57877 exited 0. There were no replay retries or source changes after review.

## Package and provenance

The candidate was built from the corrected, unchanged Checkpoint04 ZIP (73,771,852 bytes; SHA256 `27f0ecd3645331d926da10694e995547f132a0e61f7f75420a3012d41384bf03`). All 3,154 base payloads were preserved. Only `reproducibility/replay_closed_research.py` and its protocol were added, and the candidate outer manifest was regenerated. The 3,156-payload candidate manifest has SHA256 `1d71503802a3cd34f5eadbcfe6c697045e26a3a9be5f1c387311257d611b0653`.

Before mathematical checks, the wrapper verified every candidate payload, all 24 native-addendum payloads, the 17 original native byte bindings (3,734,672 bytes), and seven unchanged historical manifests through explicit research/native prefix maps. These manifests contain 735 bindings to 564 unique files, without missing files or conflicting versions. The wrapper rechecked complete package/addendum hashes after the arithmetic replay. A separate final inventory found exactly the declared 3,157 files including the manifest, no unmanifested files and no new bytecode files. The original ZIP remained unchanged.

Preparation, original/candidate manifests, 28 replay reports, and execution closure are retained under `results/research8h/portable_closed_replay/`. The new report directory was outside the extracted package. Neither this test nor its successful result is a claim that the already published Checkpoint04 ZIP contains the subsequently added wrapper, that a remote download was tested, or that a second computer was used.

## Fixed mathematical results

| Check | Result |
|---|---|
| Five capped HOD/fresh negative rays | Every exact expanded separation and archived rational claim matched. |
| Ten original-full-mask binary points | All passed exact expanded membership; all failed strict nominal membership. |
| Fresh seed 26093211 | Continuous point passed with integrality disabled; 359 original state coordinates were not exactly binary. The MIP has no incumbent, and its binary verdict remains UNKNOWN in the four-case denominator. |
| Six fixed coefficient-transfer candidates | All remained valid nonseparating rays; no feasibility conclusion follows. |
| Shared identity and two HOD uncapped models | Cap-row-only deletion, unchanged boxes/original masks, the 23-unit fossil objective and all exact lower bounds/residuals matched. |
| Three uncapped upper witnesses and two energy intervals | Original-mask membership, exact energy sums and all difference/relative interval endpoints matched. |
| Eleven focused new-logic checks | Passed; the existing kernel's 35-fixture suite was not redundantly rerun. |

The 359 count uses exact comparison with zero and one; it differs from the earlier 304-coordinate diagnostic that counted only deviations larger than the numerical tolerance. Neither count upgrades the continuous point to a binary witness.

All exact positive and negative statements concern the archived binary64-coefficient models with each finite bound expanded outward by exactly `Fraction.from_float(1e-5)`, retaining the original 12,096 U/Y/Z binary coordinates for positive witnesses. No solver optimality claim is needed. The two target upper witnesses were also checked in the ten-point set; the repeated energy checks do not create additional experimental cases.

The objective checks recompute the finite-box stationarity-residual correction and outward expansion, rather than treating a numerical solver dual objective as exact. The native roster excludes nuclear. The wrapper does not reconstruct the complete physical model from raw CSVs, recheck native engineering equations independently, repeat all historical experiments, test solver performance, or include active fresh-energy/comparator outcomes. Its scope is the fixed closed evidence specified in the protocol through scientific commit `520fe5974a4d92892906c42ce51a9d12ef304d3a`.

## Review and recorded correction

Root and an independent agent approved source SHA256 `c6cf226ac82ecb5551dee2241e89b2fd1c990fdde3e27878758331b3f998fb85` and protocol SHA256 `88864255bcd8bb479df79c100e6d67628647c03f97ef6dfade07d4add7544f12` before execution. The shared kernel SHA256 was `708c3843425eea494a0561e83a275f7059f22bcd546a036705323d056bcf906f`. No source or protocol changed afterward.

After the successful replay, an additional reviewer closure assertion initially required that no `__pycache__` directory exist anywhere. It failed because the original Checkpoint04 already contained one manifest-bound `nominal_balance_audit` reviewer bytecode file. This was not a wrapper write or a failed mathematical replay. `closure_attempt01.json` retains that diagnostic; `execution_closure.json` verifies the inherited file against the base manifest, exact final file-set equality, and absence of newly created bytecode. No second replay was performed.

## Reuse

From a package containing the reviewed wrapper, protocol, native addendum, required closed results and their outer manifest, run:

```text
python -I -S reproducibility/replay_closed_research.py --package-root EXTRACTED_ROOT --report-dir NEW_EXTERNAL_DIRECTORY
```

The report directory must not exist and must be outside the package. `summary.json` with status `CLOSED_RESEARCH_PORTABLE_REPLAY_PASS` is written only after every fixed check and final hash replay succeeds. A mismatch creates `failure.json`, preserves partial reports, and exits nonzero.
