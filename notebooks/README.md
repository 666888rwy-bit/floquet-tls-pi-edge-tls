# Research notebooks

The notebooks retain the broader numerical workflow from which the compact checkpoints and short audit scripts were derived. They are intentionally distributed **without executed outputs** so that the repository remains lightweight and does not confuse a saved notebook display with a current numerical result.

| Notebook | Role in the workflow | Preferred reviewer use |
|---|---|---|
| `01_numerical_validation.ipynb` | Model-level numerical validation and reference diagnostics. | Consult after the direct `00_` script if the Liouvillian implementation needs inspection. |
| `02_parameter_scans.ipynb` | Frequency, coupling, damping, and finite-size scan workflow. | Use to inspect how the compact production checkpoints were generated. |
| `03_channel_and_position_validation.ipynb` | Position-resolved response and Floquet-channel workflow. | Use to inspect the N=6 channel and spatial-validation context behind scripts `10`, `20`, and `30`. |
| `04_closed_chain_edge_mode.ipynb` | Closed-chain \(0\)–\(\pi\) mode and matrix-element benchmark. | Use to inspect the origin of the closed-chain comparison lengths and local matrix element. |

The recommended reproducibility order remains the shorter scripts in `../scripts/`, because they have stable inputs, declared outputs, and a direct claim-to-file mapping. The notebooks are the complete methodological record, not the fastest route to reproduce the headline figures.
