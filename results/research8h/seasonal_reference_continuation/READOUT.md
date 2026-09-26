# Three-reference continuation readout

All three fixed reference cases produced accepted binary DC-network witnesses for the uniformly expanded binary64 model. All three runs reached their time limits; no optimum is claimed. The original 120-second UNKNOWN results remain unchanged.

| Month | Fossil MWh | Numerical solver lower bound | Numerical gap | Actual seconds | Strict exact | Expanded exact |
|---|---:|---:|---:|---:|---|---|
| 04 | 42703.842794399716 | 42178.564764399664 | 1.230049% | 601.265925 | False | True |
| 07 | 182338.932964999811 | 180075.192489999521 | 1.241501% | 634.808209 | False | True |
| 10 | 123932.139824399783 | 123931.337449400060 | 0.000647% | 605.241435 | False | True |

Each raw and recovered matrix check and native no-cap physical check passed. Every recovered U/Y/Z coordinate is exact binary. Dispatch and angles were not altered during recovery. The exact checker interprets stored binary64 values as rational numbers and expands every finite row/column bound outward by Fraction.from_float(1e-5). These are rigorous upper bounds only for that expanded model; strict membership fails at the small residuals below. Solver lower bounds and gaps remain uncertified numerical quantities.

| Month | Exact energy numerator / denominator | Exact maximum row violation | Exact maximum column violation |
|---|---|---:|---:|
| 04 | 6154272335876697791701 / 144115188075855872 | 4.12145872986e-11 | 1.04449782157e-11 |
| 07 | 821181550556307008833 / 4503599627370496 | 2.83534991718e-11 | 1.5916157281e-12 |
| 10 | 558140738732395069817 / 4503599627370496 | 3.2297720054e-11 | 3.2297720054e-11 |

The unchanged uncapped physical model has 34,680 rows, 23,016 columns, 41 generators, 24 thermal units, 24 buses and 38 branches. Its objective is the original 23-unit fossil MWh sum, excluding 121_NUCLEAR_1. No cap or individual mean is present. Exact native model reconstruction and byte-copy checks passed before all three model archives froze. The standard U-only projection changed 12,096 declared binary coordinates to 4,032 U coordinates; full original U/Y/Z integrality was checked after recovery.

Exactly three sequential HiGHS 1.12.0 calls used 600 seconds, one thread, seed zero, presolve on and gap 1e-8 each; no warm starts or retries. Configured solver time was 1,800 seconds. Actual solver time was 1841.315568900 seconds; execution and checks took 1961.799104900 seconds after native model loading. The soft overruns are preserved. Timings are not a benchmark.

All 105 prepared files passed final size/hash revalidation. Manifest SHA256: `cc7ff078ea7e99ac177b3d22be3208cf454ca0726015e4a10c3b65329630758b`. Source SHA256: `8a5cff279e48569056f0217d003f8a43f1d7f026c541f8d9671e8d68e8897d4a`. Protocol SHA256: `b0100c2cae77bb1c38c206a10107ad3c9488a3b466386c02118f371df317d505`.

The independent preflight review is docs/research8h/SEASONAL_REFERENCE_CONTINUATION_REVIEW.md. Its preparation PASS is distinct from an independent post-run witness replay. Canonical raw_vector.npz and recovered_vector.npz are authoritative; CSVs are readable copies. Full solver logs, exact checks, native residuals, bindings and original records are retained.

This arm supplies additional reference schedules for a separately frozen continuation. It does not itself show an order effect, replace the original April/October NO_REFERENCE results, fix the initial failed replication gate, revise January, or demonstrate method novelty or speedup.
