# Independent locality review

A separate read-only reviewer inspected the protocol, implementation and completed outputs without editing files or running optimization. No support-decoding, row-renumbering or constraint-subsetting defect was found.

The reviewer independently derived expected up/down row counts from native dwell parameters. All nine observed counts agree: widths 0/8/16/24/48/72/96/120/168 retain respectively 0/212/564/918/2024/3176/4328/5480/8016 dwell rows. The global row count is 16,289 before dwell rows, and all 18,984 columns remain. Source support decoding correctly maps CSR columns into U/Y/Z hours; containment of the minimum and maximum touched hour is sufficient for a contiguous window. Row subsetting retains all column bounds, slices the matching row bounds, renumbers local rows and preserves original row IDs.

The pre-solve checks establish equality with archived full-model arrays, nested kept sets, full restoration at width 168, nine valid identity controls, and a valid empty-window twin with rebuilt transition flags. Certificate replay reconstructs hexadecimal row multipliers against the hashed restricted matrix and requires both exact separation and the outward-bound robustness check. All observed outcomes and controls match the readout.

The reviewer confirms the qualified interpretation: dwell rows directly supported in hours 60–107 suffice together with unchanged whole-week/static/global-transition constraints; 48 is only the shortest examined centered width. Global transitions can connect an earliest startup to the preceding outside status. The 24-hour continuous admission establishes neither UC feasibility nor an intrinsic temporal-memory threshold.

Untriggered implementation limitation: if a future run produces an exact but numerically fragile ray, the archive replay currently asserts instead of recording that fragility and proceeding to later cases. Every observed rejection was robust, so this does not affect this fixed completed run. No such case was retried, omitted or reclassified.
