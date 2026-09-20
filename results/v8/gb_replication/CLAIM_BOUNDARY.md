# GB replication claim boundary

This is an independent PyPSA-GB Reduced-network application of the same empirical mean-versus-shape decomposition.
It is not the official NESO Reduced Model and is not labelled a field trial.
The primary metric uses common non-emergency generator active-power coordinates from two solved 2020 weeks.
Storage-unit and interconnector states are not folded into this state vector; their presence is reported in diagnostics.
Any nonzero load shedding must be treated as a validation warning and blocks a clean physical replication claim.
This LP workflow does not by itself reproduce the RTS minimum-up/down rejection; it tests transfer of the distributional operating-law diagnostic to an independent system model.
