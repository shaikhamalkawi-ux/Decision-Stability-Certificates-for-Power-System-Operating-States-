# Fixed closed-evidence portable replay protocol

Prospective verification-only protocol. This entrypoint covers only evidence closed by research commit `520fe5974a4d92892906c42ce51a9d12ef304d3a`, plus the separately prepared native-byte provenance addendum and this replay implementation. It admits no active fresh-energy or comparator outcomes. Source and protocol require root and independent review before the first full relocated execution. Drafting, syntax inspection, and static review are not a successful replay.

## Inputs and boundaries

Entrypoint: `python -I -S reproducibility/replay_closed_research.py --package-root EXTRACTED_ROOT --report-dir NEW_EXTERNAL_DIRECTORY`.

Use only the Python standard library and the already reviewed exact NPZ/model/ray/point kernel `src/research8h_standalone_verify.py`, pinned by SHA256. The wrapper imports no producer solver or native reconstruction module and makes no network request. It must write only beneath a nonexistent report directory outside the extracted package. Existing report directories, archive path escapes, source/hash mismatches, unexpected masks or cases, and altered exact claims cause failure. There are no optimizers, retries, certificate searches, point repairs, or new experimental cases.

Before any real mathematical replay, verify every outer package-manifest payload, the complete 24-payload native addendum manifest, its exact 17 original native byte bindings, and explicit research/native prefix remaps. Replay the seven required unchanged historical manifests: HOD, fresh references, fresh targets, HOD uncapped, HOD fixed-ray transfer, inherited identity energy refinement, and original seasonal fixed-rule transfer. Their digests are fixed in source. Relative package/addendum manifests and unchanged original absolute-path experiment manifests are verified by separate explicit routines. This is the dependency scope of this entrypoint, not a claim to replay all historical experimental manifests or reconstruct physical models from raw CSVs.

## Finite fixed verification set

1. Five exact expanded negative rays: original HOD seeds 26093200/01 and fresh seeds 26093210/20/21. Check model/raw-ray/row-label hash bindings, exact selected-sign row sums, boxes, and expanded gaps against their archived exact fractions.
2. Ten original-full-mask positive points: original HOD identity and class control; two fresh uncapped references; two fresh capped identities and two fresh class controls; two HOD uncapped recovered witnesses. All original masks must equal the declared 12,096-coordinate U/Y/Z mask, not the 4,032-coordinate optimizer projection. Record strict and expanded membership separately.
3. Fresh seed 26093211's continuous-only point, explicitly using a zero integrality mask and checking that at least one original binary coordinate is nonbinary. Its final binary verdict must remain UNKNOWN, its MIP must report no accepted incumbent, and no raw/recovered MIP vector may be present. Retain the four-case final denominator.
4. All six fixed HOD coefficient-transfer candidates, in their frozen order, must remain valid but nonseparating. No candidate is repaired or reoptimized. A nonseparating ray does not establish feasibility.
5. For both HOD uncapped models and the shared uncapped identity, replay actual cap-row-only deletion against the parent model, unchanged boxes and original mask, fossil objective support, and exact lower bounds from archived projected duals. Recompute stationarity residuals and finite-box corrections with Fraction arithmetic and the same outward expansion. Compare exact scalar claims and sparse residuals. The objective has exactly 3,864 ones over the 23 native Coal/Oil/NG units, excluding nuclear.
6. Recheck the identity's uncapped original-binary point, exact objective sums for all three upper witnesses, inherited identity bounds, and all two-case difference/relative intervals against their archived rational records. No solver optimality claim is used.

The continuous UNKNOWN diagnostic and uncapped identity check are additional membership evaluations, not new experimental cases or new positive targets. Full raw/native physical reconstruction is outside the wrapper. It verifies the included native byte provenance, archived model mathematics, declared model relations, and exact displayed scientific ledger; it does not repeat solver performance or claim a second-machine test.

## New logic checks and output

Run a small fixed set of focused checks for the new objective-bound and interval arithmetic, inadmissible endpoint handling, negative lower-bound retention, original-mask enforcement, denominator enforcement and package-path confinement. Do not duplicate the old kernel's 35 fixtures merely to inflate test counts.

Store new JSON reports for provenance, focused checks, points/rays/nulls, continuous-versus-UNKNOWN distinction, objective lower/upper calculations and exact intervals, followed by a single summary. Preserve all partial reports on failure; create no success summary after a mismatch. Verify the complete package and addendum hashes again after replay to detect mutation. The final success status may be stated only after the reviewed entrypoint finishes in a new extracted directory under isolated `-I -S` execution. Packaging/extraction SHA verification and same-host-versus-second-machine provenance remain explicitly reported by the execution owner.
