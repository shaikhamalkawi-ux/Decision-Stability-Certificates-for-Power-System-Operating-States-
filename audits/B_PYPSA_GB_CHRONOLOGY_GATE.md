# Workstream B - PyPSA-GB chronology gate

## Gate decision

**HOLD.** The frozen January and July PyPSA-GB cases support the already
reported LP dispatch replication, but they do not contain a native unit-
commitment chronology that can be admitted without inventing parameters.

| Frozen case | Generator rows | Committable | Positive min-up | Positive min-down | Finite up-ramp | Finite down-ramp |
|---|---:|---:|---:|---:|---:|---:|
| January 2020 | 2,692 | 0 | 0 | 0 | 0 | 0 |
| July 2020 | 2,713 | 0 | 0 | 0 | 0 | 0 |

All generators are marked non-committable; minimum up/down times are zero; and
ramp-limit fields are null. Consequently, a GB MILP chronology experiment
would require a new fleet mapping and externally sourced or imputed UC
parameters. Doing so inside this evidence gate would change the model rather
than restore information already present in the frozen provenance.

The V7 GB static/conditional result remains admitted unchanged. It is an
independent system replication of the distributional information hierarchy,
not a replication of the RTS minimum-up/down rejection. Machine-readable audit
outputs are in `results/pypsa_gb_chronology_audit`.
