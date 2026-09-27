# Isolated SCIP capability: import works, exact parameters absent

The single authorized setup closed successfully in **395.498756 seconds**, within the1,800-second allocation. The fresh environment is `.work/scip_capability_env01`, with CPython3.12.14, PySCIPOpt6.2.1, NumPy2.3.5 and bundled SCIP10.0.2. There were **zero optimization calls, zero synthetic solves and zero scientific-model reads**.

The one empty Model had zero variables and constraints. Its complete parameter dictionary did **not** contain `exact/enable` or `certificate/filename`; therefore enabling exact mode was not attempted. This installed wheel provides no demonstrated exact-solving/proof-logging route through those documented parameters. The observation is specific to this installed build; it is not a claim that SCIP generally lacks exact capability. Even numerical scientific-model solving has not yet been exercised in this environment.

The two official cp312-win_amd64 wheels were downloaded once each over normal TLS and matched PyPI size/SHA metadata before the sole offline hash-required pip installation:

| Wheel | Bytes | SHA256 |
|---|---:|---|
| PySCIPOpt6.2.1 |48,216,285|`784d8fbee8134c7c1cf590a60972008159033938a5044d9ed28cde9abf4f86be`|
| NumPy2.3.5 |12,782,922|`86945f2ee6d10cdfd67bcb4069c1662dd711f7e2a4343db5cecec06b87cf31aa`|

Fresh venv creation took119.551416s; offline pip213.466282s; the empty-probe child25.596404s (its internal import/model/read interval19.111454s). Each ran once and returned0. There was no retry, fallback, global package change, license modification, source compilation or additional capability probe. Installation/probe logs and wheel payloads remain private, with public hashes only; raw log content was not read for this closeout.

This is a separate infrastructure arm after the closed Gurobi size-limit failure. It does not alter that record or resolve the common-commitment question. A future numerical search or synthetic certificate experiment requires its own prospective contract and authorization. As the [official SCIP FAQ](https://www.scipopt.org/doc/html/FAQ.php) explains, original-instance certification must account for presolve, and cut proofs may need `viprcomp` completion; an enabled parameter alone would not have established certificate validity.

Frozen records: `setup01/capability.json` SHA256 `c21670a55e870f5abef24efb74d52b2de17d9e235a82eec0da0bfd7a4e74ebed` and `setup01/completion.json` `bee14a2cbbf2536071c32a738f496baa0cd36a2ebbf6fc0e7347867ecee49c80`. Commands, timings, official metadata/download hashes, installed binary/metadata hashes and private-log receipts are in `setup01`. Source SHA256 `a3b16a16066eff5ccf615c060bbdf1b044321a6734a1d591e53741c01e362e26`, probe `377c91fab45080957d7ecf7f9f0a22ea858e13880fc3de10724100f60a97c88e`, protocol `3087ad4637587dae61d766e8bfddd33f2dd63451ddc41a46311e832aae74341a`. The artifact inventory binds the public record without including the isolated environment, wheels or private logs. Final inventory/readout serialization is outside the measured setup phase.
