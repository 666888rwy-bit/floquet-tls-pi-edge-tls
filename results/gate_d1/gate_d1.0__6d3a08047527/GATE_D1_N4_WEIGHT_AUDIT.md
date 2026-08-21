# Gate D1 audit: response-blind N=4 \(\nu_\pi\) raw-weight screen

## Decision

Gate D1 is a valid, prospectively frozen **candidate screen**, not a passed basis for N=6 confirmation. All eight exact N=4 results pass both manifest SHA-256 and result self-hash verification. The response-blind candidate selector, the frozen protocol, and runner were publicly committed before the new calculations.

The screen produces strong median weight separations within each fixed \(\nu_0\) stratum, but fails the stricter predeclared all-point separation condition. Under the frozen stop rule, **no N=6 confirmation is authorized** and no response-informed candidate revision is allowed.

## Frozen protocol

The eight controls comprise two BDI-safe, geometrically separated points in each of \((\nu_0,\nu_\pi)=(0,0),(1,0),(0,1),(1,1)\). Selection used only the closed-chain BDI classifier, a bulk-gap margin threshold, and geometrical separation in \((\alpha/\pi,\beta/\pi)\). It did not use TLS response, Floquet-pair ranking, local matrix elements, or phase conventions.

All points use the exact N=4 OBC full model, contact \(m=0\), common \(|\uparrow_z\rangle^{\otimes4}\otimes|0_d\rangle\) preparation, fixed \(gT=\gamma_1T=0.207345\), 80 drive periods, 20 discarded periods, four samples per half step, and the fixed eleven-point detuning-ratio grid. Periods differ among BDI candidates, so this is a stratified screen rather than a common-period four-class causal comparison.

## Results

| BDI class | Median \(W_r\) | Fixed-\(\nu_0\) comparison |
|---|---:|---:|
| \((0,0)\) | \(1.4005\times10^{-4}\) | \(\mathrm{median}(W_{01})/\mathrm{median}(W_{00})=239.10\) |
| \((0,1)\) | \(3.3486\times10^{-2}\) |  |
| \((1,0)\) | \(6.4092\times10^{-7}\) | \(\mathrm{median}(W_{11})/\mathrm{median}(W_{10})=4276.67\) |
| \((1,1)\) | \(2.7410\times10^{-3}\) |  |

Both predeclared fixed-\(\nu_0\) median-ratio conditions exceed the factor-10 screen threshold. However, the weakest sampled \(\nu_\pi=1\) point divided by the strongest sampled \(\nu_\pi=0\) point is only **7.004**, below the predeclared factor-10 condition. The strict all-point separation requirement therefore fails.

> The N=4 data are consistent with a substantial but nonuniform \(\nu_\pi\)-associated raw-weight hierarchy under this stratified protocol. They do not provide a response-uniform separation across the selected deep BDI points, and they do not license a general \(\nu_\pi\)-weight law or an N=6 confirmation campaign.

## Consequence for the manuscript route

Gate A v3 remains the strongest exact N=6 evidence for finite-system boundary selectivity. Gate D1 prevents an overinterpretation of its exploratory four-point amplitude hierarchy: the broader response-blind N=4 screen supports fixed-\(\nu_0\) median contrasts but fails the stricter pointwise condition. The manuscript may describe this as a transparent negative/heterogeneity result if useful, but should not recast it as positive \(\nu_\pi\)-specific spectroscopy.

## References

[1]: ../../../protocols/gate_d1/gate_d1_n4_nupi_weight_protocol.json "Gate D1 frozen protocol."

[2]: GATE_D1_N4_WEIGHT_AUDIT.json "Machine-readable Gate D1 audit."

[3]: ../../gate_a_v3/gate_a_v3.0__1b3dd5130c77/GATE_A_V3_AUDIT.md "Gate A v3 finite-system audit."
