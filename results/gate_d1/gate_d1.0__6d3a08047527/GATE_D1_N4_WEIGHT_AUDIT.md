# Gate D1 corrected audit: response-blind N=4 $\nu_\pi$ raw-weight screen

## Corrected decision

Gate D1 is a valid, prospectively frozen candidate screen and **passes the literal frozen rule, authorizing a separately frozen N=6 confirmation**. All eight exact N=4 results pass both manifest SHA-256 and result self-hash verification. The response-blind candidate selector, protocol, and runner were publicly committed before the new calculations.

The earlier v1 audit incorrectly imposed a factor-10 threshold on the all-point condition. In the frozen protocol, the factor-10 threshold applies to the two fixed-$\nu_0$ median ratios; the all-point condition only requires the smallest sampled $\nu_\pi=1$ weight to exceed the largest sampled $\nu_\pi=0$ weight. The protocol itself is unchanged. This correction makes the audit conform to it.

## Frozen protocol

All points use the exact N=4 OBC full model, contact $m=0$, common $|\uparrow_z\rangle^{\otimes4}\otimes|0_d\rangle$ preparation, fixed $gT=\gamma_1T=0.207345$, 80 periods, a 20-period discard, four samples per half step, and the same eleven-point detuning-ratio grid. Candidate selection used only closed-chain BDI labels and bulk safety margins.

| sampled class | median $W_r$ | frozen fixed-$\nu_0$ contrast |
|---|---:|---:|
| $(0,0)$ | $1.4005\times10^{-4}$ | $\mathrm{median}(W_{01})/\mathrm{median}(W_{00})=239.10$ |
| $(0,1)$ | $3.3486\times10^{-2}$ | |
| $(1,0)$ | $6.4092\times10^{-7}$ | $\mathrm{median}(W_{11})/\mathrm{median}(W_{10})=4276.67$ |
| $(1,1)$ | $2.7410\times10^{-3}$ | |

Both predeclared fixed-$\nu_0$ median-ratio conditions exceed the factor-10 screen threshold. The weakest sampled $\nu_\pi=1$ point divided by the strongest sampled $\nu_\pi=0$ point is **7.004**, which also satisfies the separately stated directional all-point requirement $\min W_{\nu_\pi=1}>\max W_{\nu_\pi=0}$.

> The N=4 data provide a substantial but nonuniform $\nu_\pi$-associated raw-weight hierarchy under this stratified screen. Passing authorizes an N=6 transfer test on the same response-blind-selected points; it does not itself establish a general $\nu_\pi$-weight law.

## Consequence for the manuscript route

Gate A v3 remains the strongest exact N=6 evidence for finite-system boundary selectivity. Gate D1 now permits a prospectively frozen N=6 transfer test using exactly the same eight response-blind-selected drives. Until that confirmation is complete, the manuscript should describe the N=4 result as a passed candidate screen, not as established $\nu_\pi$-specific spectroscopy.

## Correction record

The raw result JSON files, frozen protocol, selected drives, and manifest are unchanged. Only the audit implementation and interpretation were corrected. Git history retains the superseded v1 decision for transparency.

## References

[1]: ../../../protocols/gate_d1/gate_d1_n4_nupi_weight_protocol.json "Gate D1 frozen protocol."

[2]: GATE_D1_N4_WEIGHT_AUDIT.json "Machine-readable corrected Gate D1 audit."

[3]: ../../gate_a_v3/gate_a_v3.0__1b3dd5130c77/GATE_A_V3_AUDIT.md "Gate A v3 finite-system audit."
