# Source code

Reproducible computation, verification, and figure-generation code belongs here.

Every script used for a reported result should have an identifiable input/output path and environment provenance.

## Candidate V8R1 commands

Install the computation versions recorded in `requirements-v8r1.txt`, then:

```bash
python src/v8r1_prepare_rts_inputs.py
python src/v8r1_rts_seasonal.py --source-v3 .work/v8r1_rts_inputs
python src/v8r1_rts_residence_certificate.py --source-v3 .work/v8r1_rts_inputs --output results/v8r1/rts_certificate_reproduced
```

For observed-data acquisition and analysis, see the exact commands in
`docs/V8R1_ELEXON_SENSITIVITY_PROTOCOL.md` and
`audits/V8R1_ELEXON_SENSITIVITY.md`. Raw API bytes remain outside Git.
The supplied derived daily matrices, assignments, metrics and provenance allow
inspection of what was computed without inventing missing measurements.
