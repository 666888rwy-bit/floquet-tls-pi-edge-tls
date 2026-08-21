# Gate A v3 audit: matched BDI controls, spatial profile, and numerical-window checks

## Executive decision

Gate A v3 resolves the main **unequal-period trivial-control** defect of Gate A v2. It provides two explicitly matched finite-system BDI comparisons, each preserving \(T\), \(\Omega\), \(gT\), \(\gamma_1T\), total physical propagation time, discard time, detuning-ratio grid, and common product preparation within the declared pair. It also adds an exact full-model six-site spatial profile and a held-out same-drive PBC comparison.

However, the frozen four-class analysis **does not support a universal \(\nu_\pi\)-determined spectral-shape claim**. The two pairwise matched lines cannot be combined into a single four-class common-period test, and the prospectively declared normalized-shape grouping of the \(\nu_\pi=1\) drives fails. This does not imply that \(\nu_\pi\) is physically irrelevant to every response metric: the sampled raw spectral weights show a pronounced exploratory \(\nu_\pi\)-sector separation, documented below. In addition, the deliberately short 8-period discard variant exceeds the protocol's shape-stability acceptance threshold. The resulting limitation is sensitivity of the **detailed early-window lineshape**, not a collapse of late-window weight or timestep convergence.

> The usable evidence is an exact finite-\(N=6\) **edge-selective OBC/PBC response** for specified closed-chain BDI-labelled drives. The data do not establish that a single invariant, especially \(\nu_\pi\), uniquely controls the response.

## Integrity and matching verification

All thirteen newly calculated result files match the SHA-256 values in `MANIFEST.json`. The v2 production and held-out OBC source JSON files are separately hash-recorded in `GATE_A_V3_AUDIT.json`. The v3 protocol SHA-256 is `1b3dd5130c77050af93c03463f6302259b14816870cfee2229d71eb7bedd8a27`.

| Pair | Common period \(T\) | \(gT=\gamma_1T\) | Total physical time | Exact matching statement |
|---|---:|---:|---:|---|
| \((1,1)\) versus \((0,1)\) | 2.591814 | 0.207345 | 207.3451 | All declared dimensionless and time-window controls identical. |
| \((1,0)\) versus \((0,0)\) | 1.295907 | 0.207345 | 207.3451 | All declared dimensionless and time-window controls identical. |

The two-step drive has no safe single constant-period line containing all four BDI classes under the closed-chain classifier and bulk-margin threshold used here. The campaign consequently uses two pairwise matched lines, not an improperly matched all-four comparison.

## Directional matched-control outcomes

All ratios below preserve the numerator/denominator orientation frozen in the protocol; they are not symmetrized.

| Declared comparison | \(W_{\rm numerator}/W_{\rm denominator}\) | Shape distance \(D\) | Raw peak ratio | Interpretation |
|---|---:|---:|---:|---|
| \((1,1)\) OBC / \((0,1)\) OBC | 0.10477 | 0.68647 | 0.28323 | Changing \(\nu_0\) at fixed \(\nu_\pi=1\) produces a large drive-class-dependent change, but not a simple edge-weight enhancement. |
| \((1,0)\) OBC / \((0,0)\) OBC | 0.00453 | 0.46605 | 0.05835 | Changing \(\nu_0\) at fixed \(\nu_\pi=0\) also produces a large drive-class-dependent change. |
| held-out \((1,1)\) OBC / same-drive PBC | 9537.44 | 0.89927 | 55.21 | Strong independent finite-system boundary-condition contrast at the held-out drive. |

The matched data remove the previous factor-of-three period and bare-coupling mismatch. They also show why a stronger invariant claim would be unsafe: the response changes substantially across both matched BDI pairs, and the raw direction is not reducible to a universal “topological enhancement” statement.

## \(\nu_\pi\) specificity check

The prospectively declared descriptive test compares normalized-shape proximity. The two \(\nu_\pi=1\) cases have \(D=0.68647\), whereas the smallest cross-\(\nu_\pi\) distance is 0.15322. The requested qualitative \(\nu_\pi\)-grouping condition is therefore **false**.

This is not evidence against the closed-chain invariant calculation, nor is it evidence that \(\nu_\pi\) is unrelated to every response observable. It establishes only that the available finite dissipative full-model spectra cannot be assigned a **universal \(\nu_\pi\)-determined lineshape** from the four sampled pairwise-matched drives.

## Exploratory raw-weight separation by sampled \(\nu_\pi\)

The raw integrated spectral weights, evaluated on the protocol's fixed ratio grid, display a conspicuous descriptive hierarchy:

| BDI label | \(W_r\) |
|---|---:|
| \((1,1)\) | \(3.3247\times10^{-3}\) |
| \((0,1)\) | \(3.1732\times10^{-2}\) |
| \((1,0)\) | \(1.2677\times10^{-7}\) |
| \((0,0)\) | \(2.8005\times10^{-5}\) |

Thus \(W_{11}/W_{10}=2.62\times10^{4}\), \(W_{01}/W_{00}=1.13\times10^{3}\), and even the smaller sampled \(\nu_\pi=1\) weight exceeds the larger sampled \(\nu_\pi=0\) weight by 118.7. This result is **exploratory and descriptive**, rather than a retroactively passed frozen test: the two \(\nu_\pi\) sectors lie on different equal-period control lines. It motivates a separately frozen multi-point \(\nu_\pi\)-weight test; it does not establish a general invariant law.

## Production spatial profile

The exact product-state full-model spectral weights are symmetric under reflection and strongly edge-selective:

| TLS site \(m\) | \(W_r(m)\) | \(W_r(0)/W_r(m)\) |
|---:|---:|---:|
| 0 | 0.00332466 | 1.00 |
| 1 | 0.00063759 | 5.21 |
| 2 | \(3.39\times10^{-6}\) | 981.45 |
| 3 | \(3.39\times10^{-6}\) | 981.45 |
| 4 | 0.00063759 | 5.21 |
| 5 | 0.00332466 | 1.00 |

This is a useful finite-chain edge-to-interior spatial profile. It must not be rewritten as a thermodynamic localization length or an asymptotic boundary law.

## Sampling and phasor-window check

| Variant relative to 4-samples/20-discard baseline | \(D\) | Frozen \(D\le0.10\) condition |
|---|---:|---|
| 2 samples per half step, 20 discard periods | 0.00106 | Pass |
| 8 samples per half step, 20 discard periods | 0.00031 | Pass |
| 4 samples per half step, 8 discard periods | 0.17688 | **Fail** |
| 4 samples per half step, 40 discard periods | 0.04622 | Pass |

The integration-density test is stable, as are the standard 20-period and longer 40-period discard windows. The 8-period discard does not meet the frozen **shape** criterion, but retains \(W_{8T}/W_{20T}=1.041\); the 40-period window retains \(W_{40T}/W_{20T}=0.932\). The correct conclusion is that inclusion of the early transient changes the detailed lineshape, whereas the late-window response weight and time discretization are stable at the reported level. No post hoc new discard sweep is authorized.

## Manuscript-safe and prohibited claims

The manuscript may report exact finite-\(N=6\) common-preparation OBC/PBC boundary contrasts, a symmetric edge-to-interior spatial response profile, and the matched-period control data with their specified drive labels. It must call the procedure a **prospectively frozen numerical protocol**.

It must not claim: a general quantitative reduced TLS model; a universal topological enhancement; a unique \(\nu_\pi\)-controlled response; a thermodynamic phase boundary; or a window-independent detailed spectral shape. The appropriate wording is that the response is **drive-class-dependent and boundary-selective in a controlled finite system**. The sampled raw weights show an explicitly exploratory \(\nu_\pi\)-sector separation, while their attribution to a single BDI invariant remains unresolved.

## References

[1]: ../../../../protocols/gate_a_v3/gate_a_v3_protocol.json "Gate A v3.0 frozen protocol."

[2]: GATE_A_V3_AUDIT.json "Machine-readable Gate A v3 audit."

[3]: ../gate_a_v2.0__00d3477cc81e/GATE_A_V2_FINAL_AUDIT.md "Gate A v2 exact full-model audit."
