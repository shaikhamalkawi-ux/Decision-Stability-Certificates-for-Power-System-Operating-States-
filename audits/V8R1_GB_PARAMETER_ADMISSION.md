# V8R1 GB parameter admission audit

Audit date: 2026-09-26. PyPSA-GB source commit: `8e084afe4fb2d4be86f270d3f12ad3315eee2a3a`. Frozen environment: PyPSA `1.0.7`, as recorded in `reproducibility/provenance/pypsa_gb_generation_environment.json`.

**Decision: KEEP the recovered upstream wholesale UC parameterization as an explicitly declared optional model sensitivity. HOLD a matched GB network chronology/mean-feasibility result until the complete model, eligibility flags and time-dependent inputs are available.** No solver was run. No manuscript, historical V8 results, release assets or external repository was changed.

## What the sources establish

The pinned repository has two separate UC routes. The old frozen-LP audit cannot establish absence of UC parameters in PyPSA-GB. Its stronger inference that any GB chronology test must use invented parameters is unsupported and is superseded by this audit.

1. **Thermal integration route:** `add_thermal_generators` reads the raw fuel CSV when its local solve-mode reader returns MILP. This route has unresolved time units and carrier mapping; its raw numerical parameters are HOLD for physical/native historical claims.
2. **Wholesale overlay:** `apply_wholesale_unit_commitment` assigns an explicit carrier-based set immediately before the wholesale solve, independently of global LP mode. Its equations and values are reproducible source-defined model assumptions. They are KEEP for a labelled optional sensitivity, but are not measured 2020 plant parameters or proof of an already-activated historical UC model.

Primary links are pinned to the inspected commit. SHA-256 hashes, source paths and raw downloads are indexed by `provenance/v8r1/gb/source_manifest.csv`.

## Optional overlay: exact values and use conditions

| Carrier | Minimum output / p_nom | Min up / down (snapshots) | Normal up / down ramp (p_nom/snapshot) | Startup cost / MW |
|---|---:|---:|---:|---:|
| CCGT | 0.35 | 4 / 3 | 0.50 / 0.50 | 45 |
| OCGT | 0.20 | 1 / 1 | 1.00 / 1.00 | 20 |
| coal | 0.40 | 8 / 6 | 0.35 / 0.35 | 80 |
| oil | 0.25 | 2 / 2 | 0.80 / 0.80 | 30 |

All startup/shutdown ramp defaults are 1.0 p.u.; all shutdown costs per MW are zero. Startup cost is multiplied by `p_nom` by the helper to produce PyPSA's absolute currency cost. Costs do not affect a pure feasibility result unless the experiment adds an objective-budget constraint. Source: [defaults L330–385](https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/config/defaults.yaml#L330-L385), [assignment L376–420](https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/scripts/market/solve_wholesale.py#L376-L420).

Eligibility is the conjunction of exact carrier spelling, `p_nom >= 50 MW`, `active=True`, and `p_nom_extendable=False`; excluded carriers and disabled carrier blocks are skipped. All generators' committable flags are reset to false before the selected rows are enabled. Nuclear, biomass, renewables, imports and small thermal units are not silently assigned the four-carrier set. [Code L313–374](https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/scripts/market/solve_wholesale.py#L313-L374).

The frozen January/July metadata gives **52 carrier/nameplate candidates per month**, totaling **36,830 MW**: CCGT 36/29,673 MW; OCGT 7/1,175 MW; coal 3/5,341 MW; oil 6/641 MW. It does not export `active` or `p_nom_extendable`; hence these are candidate counts, not a fully verified eligible set. No missing flag is imputed as true or false. Exact names/buses and input hashes are supplied in the candidate CSVs.

Default `initial_status: off` sets `up_time_before=0` and `down_time_before=max(min_down_time,1)`. Thus minimum prior downtime is already satisfied; there is no observed historical state implied. The source's `on` alternative sets `down_time_before=0` and `up_time_before=max(min_up_time,1)`. `preserve` requires actual prior state and cannot be inferred from the frozen extracts. [Initialization L253–276](https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/scripts/market/solve_wholesale.py#L253-L276).

PyPSA 1.0.7 defines minimum up/down times and initial dwell as **snapshot counts**, independent of snapshot weights. Ramps are changes as a fraction of nominal power **per snapshot**, also independent of weights. Default 60-minute resolution makes the numerical dwell values hours; no automatic conversion in the overlay justifies using the same values for half-hourly data. `p_min_pu` is a fraction of nameplate conditional on commitment; for a noncommittable unit it is a must-run floor. PyPSA defaults are `up_time_before=1`, `down_time_before=0`, and start/stop ramps 1. [Exact component schema](https://github.com/PyPSA/PyPSA/blob/v1.0.7/pypsa/data/component_attrs/generators.csv#L12-L38).

At the modeled horizon's end, minimum-time obligations are enforced only over remaining snapshots. Ramp constraints do not generally constrain an unprovided pre-horizon dispatch; the initial dwell is a separate condition. Preserve these finite-horizon conventions explicitly; do not describe them as cyclic chronology or post-horizon feasibility. [PyPSA UC documentation](https://github.com/PyPSA/PyPSA/blob/v1.0.7/docs/user-guide/optimization/unit-commitment.md#L43-L75), [ramp equations](https://github.com/PyPSA/PyPSA/blob/v1.0.7/docs/user-guide/optimization/unit-commitment.md#L133-L189).

## Thermal CSV route: why admission is held

The raw CSV has no units in its headers. For example CCGT gives min-up `247.5`, min-down `150`, ramp-up/down `5.78`, minimum output `40`, and initial uptime `0`. The thermal function directly casts minimum times with `int`, producing **247 and 150 snapshots**, without dividing by minutes or snapshot duration. Its ramp comment says percent/hour and the code divides by 100, producing **0.0578**; no independently verified source mapping establishes that the raw CSV actually uses that physical unit. We therefore record the code effect but do not reinterpret the raw values as minutes, hours or percent/minute. [Raw fuel table](https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/data/generators/generator_data_by_fuel.csv), [thermal assignments L1594–1655](https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/scripts/generators/integrate_thermal_generators.py#L1594-L1655).

Further source mismatches prevent treating that CSV as an automatically admitted UC model:

- Carrier normalization produces `coal`, `oil`, `nuclear`, `biomass`, but CSV keys include `Coal`, `Oil`, `Nuclear`, `Biomass (dedicated)` and `Biomass (co-firing)`. The subsequent lookup is exact and case sensitive. CCGT/OCGT match; the named lowercase carriers do not. Their fallback is noncommittable, minimum times zero and MILP default normal ramps 1.0. [Normalization L1474–1534](https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/scripts/generators/integrate_thermal_generators.py#L1474-L1534), [lookup L1613–1629](https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/scripts/generators/integrate_thermal_generators.py#L1613-L1629).
- The thermal function does not copy this CSV's `p_min_pu`, `p_max_pu`, `up_time_before` or `start_up_cost`. In particular, raw `up_time_before=0` is not evidence that the built thermal unit starts off; PyPSA's default initial uptime is 1 snapshot. Other pipeline stages may later change limits; that requires inspecting a complete generated network.
- `get_solve_mode()` reads **`config/config.yaml` → `optimization.solve_mode`** with LP fallback, whereas pinned `defaults.yaml` has a top-level `solve_mode`. The thermal caller omits an explicit solve-mode argument. The effective run configuration must therefore be checked rather than assuming that changing a top-level default changes this builder. [Mode reader L750–770](https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/scripts/generators/integrate_thermal_generators.py#L750-L770), [caller L2069–2074](https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/scripts/generators/integrate_thermal_generators.py#L2069-L2074).
- Optional thermal availability factors can set additional biomass/waste must-run floors, but they are disabled by default. These are a separate feature and cannot be treated as the unused raw fuel floor. [defaults L894–914](https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/config/defaults.yaml#L894-L914).

Documentation credits DUKES for historical location, fuel/type and capacity, and names Schröder et al. and Angerer et al. broadly for technical characteristics. The inspected documents do not supply a complete reference/table mapping for every CSV or overlay number. These are provenance leads, not verified empirical calibrations. [Data sources L417–419](https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/docs/source/data_reference/data_sources.md#L417-L419).

## Historical2020 Reduced compatibility and scope limits

KEEP documented configuration compatibility: `Historical_2020_reduced` explicitly selects 2020 for model, renewable and demand years, Reduced network, and January 1–7. Reduced is described as a 32-bus model; that label is not an assertion that every derived full network has exactly 32 total buses. [Scenario L22–31](https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/config/scenarios.yaml#L22-L31), [configuration example](https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/config/README.md#L23-L29). The paper's frozen January and July seven-day scenario settings remain traceable in `reproducibility/provenance/pypsa_gb_scenario_freeze.yaml`.

The full wholesale entrypoint relaxes transmission to a copperplate before applying UC. Running it unchanged would change the network feasibility problem. Reusing its parameter helper with a Reduced network must be described as an extracted source-defined overlay, and requires a complete validated network. Also, `optimization.remove_must_run=True` resets all minimum outputs after the overlay. [Entrypoint L699–730](https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/scripts/market/solve_wholesale.py#L699-L730).

The rolling-day-ahead path creates copies with restricted snapshots and explicitly carries storage SoC. No corresponding generator status/minimum-dwell carry was found in the inspected loop. HOLD any claim of continuous multi-window UC from that path without an additional state audit; a single declared 168-hour horizon avoids making that particular unsupported claim. [Rolling implementation L503–579](https://github.com/andrewlyden/PyPSA-GB/blob/8e084afe4fb2d4be86f270d3f12ad3315eee2a3a/scripts/market/solve_wholesale.py#L503-L579).

A matched network experiment remains HOLD because no complete solved GB `.nc` or equivalent time-dependent native network has been recovered for this audit. The frozen metadata does not provide branches and capacities, topology, loads, renewable availability, historical nuclear maximum-output series, storage states, links/import schedules, eligibility flags or initial commitment states. The root task separately confirmed that its seven-file GB return package and V7 archive do not supply the full networks/time-dependent inputs; a fresh upstream workflow requires the pinned weather cutout and remaining source inputs. Dispatch matrices alone are insufficient to reconstruct the feasible set. Parameter recovery does not close this model-recovery gap.

## Concrete admitted next use

The recovered overlay CSV can support a clearly labelled **parameter-only necessary-condition diagnostic** or an explicitly hypothetical schedule test, with missing flags and boundary assumptions stated. It cannot establish that a GB target mean is feasible or infeasible under its original network. Admit a matched-network chronology experiment only after recovering or reproducibly rebuilding the full base model, validating all input hashes and activated constraints, retaining its loads/availability/storage/network semantics, and comparing static/commitment/ramp/minimum-time cases against identical target definitions.

The audit contains 43 overlay/control decisions, 261 raw fuel-field decisions, and 104 exact carrier/nameplate candidate mappings. Generation checks verified expected carrier keys, raw values and candidate counts; raw-source hashes are recorded. No numerical feasibility conclusion has been manufactured from missing network data.
