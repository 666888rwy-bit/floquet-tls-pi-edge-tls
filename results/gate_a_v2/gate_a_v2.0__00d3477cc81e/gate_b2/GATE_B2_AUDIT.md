# Gate B2 audit: initial-support-compatible Floquet manifolds

**Decision: Gate B2 does not pass its prospectively frozen \(K=16\) success rule at both topological OBC points.** The mixed pair-plus-initial-support manifold restores physical initial-state weight, but the static \(B^{(0)}\)-only reduced spectra remain quantitatively insufficient at the declared benchmark dimension. The next appropriate calculation is the small-\(N\) controlled micromotion/Sambe feasibility study (Gate C), not a larger-\(N\) rerun.

## Frozen provenance

The protocol is [`gate_b2_initial_support_manifold_protocol.json`](../../../protocols/gate_a_v2/gate_b2_initial_support_manifold_protocol.json), SHA-256 `4394de0b1b1a84dea903fc3e058fb3c02e2d7f819a5ea71c0a0773244cdd79d5`. The result JSON is [`GATE_B2_INITIAL_SUPPORT_BENCHMARK.json`](GATE_B2_INITIAL_SUPPORT_BENCHMARK.json), generated under public commit `0c8d51c` and with its own source-result hashes.

> **Scope.** The test starts from the same physical \(|\uparrow_z\rangle^{\otimes6}\otimes|0_d\rangle\) preparation as Gate A v2. Floquet pairs are used only to anchor a local mechanism in the reduced basis; they never define the full-model initial state.

## Why the original local manifold failed

The initial-support diagnostic found that 90% of the physical initial-state Floquet weight requires 12 states at the production point and 11 states at the held-out point; 95% requires 16 and 15 states, respectively. In contrast, the legacy local near-\(\pi\) K=4 manifold retained only \(p_4=0.01116\) at production and \(p_4=1.65\times10^{-29}\) at the held-out point. This directly explains why a pair-based reduction cannot be assumed to represent the common physical preparation.

## Frozen benchmark result

| Point | Hybrid \(p_{16}\) | Hybrid \(\epsilon_{\rm spec}(16)\) | Peak ratio at K=16 | \(\|\hat a_{32}-\hat a_{16}\|_2\) | K=16 rule |
|---|---:|---:|---:|---:|---|
| Production topological OBC | 0.9408 | 0.4292 | 0.6811 | 0.0914 | Fail |
| Held-out topological OBC | 0.9425 | 0.3808 | 0.8654 | 0.0453 | Fail |

The frozen K=16 requirements were \(p_{16}\ge0.90\), \(\epsilon_{\rm spec}(16)\le0.35\), raw-peak ratio in \([0.50,2.00]\), and K=16-to-K=32 shape change \(\le0.05\). Both points satisfy the retained-weight and peak-ratio conditions. The production point additionally fails K=16-to-K=32 stability; both points fail the K=16 shape-error target.

At K=32, the shape errors improve to 0.3401 (production) and 0.3382 (held-out), but this does **not** rescue the frozen K=16 criterion. It merely demonstrates that the missing ingredients are not solely initial-state overlap: even after most of the physical state is retained, the static zero-harmonic model converges slowly with manifold size.

## Interpretation and next task

The experiment distinguishes two facts:

1. **Preparation compatibility is necessary.** Adding initial-support states raises \(p_{16}\) above 94% at both drives.
2. **Preparation compatibility is not sufficient.** The static \(B^{(0)}\)-only reduction still misses the full normalized spectral shape at K=16, and the production point remains visibly K-sensitive through K=32.

Therefore the present data do not justify a general static local Floquet reduction. Gate C should now be a controlled small-system test retaining \(n=0,\pm1\) Floquet/Sambe replicas and a micromotion-consistent observable, with replica-cutoff convergence and raw-observable benchmarks. No new N=8 or N=10 campaign is justified before that feasibility check.

## References

[1]: ../../../protocols/gate_a_v2/gate_b2_initial_support_manifold_protocol.json "Gate B2.0 prospectively frozen initial-support manifold protocol."

[2]: GATE_B2_INITIAL_SUPPORT_BENCHMARK.json "Machine-readable Gate B2 results, source-result hashes and frozen decisions."

[3]: ../GATE_A_V2_FINAL_AUDIT.md "Gate A v2 common-preparation full-model control audit."
