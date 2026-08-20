# PRB multichannel controls: fast audit

This file and the associated figures are regenerated from committed JSON summaries; they do not rerun the high-cost full Floquet--Lindblad propagation.

| Control | K=2 | K=4 | K=6 | K=8 |
|---|---:|---:|---:|---:|
| N=6, g=0.08 | 0.3646 | 0.1467 | 0.1442 | 0.1610 |
| N=8, g=0.08 | 0.3466 | 0.1452 | 0.1413 | 0.1384 |
| N=8, g=0.12 | 0.2950 | 0.6287 | 0.6220 | 0.6133 |

## Interpretation boundary

The two $g=0.08$ controls use matched N=6/N=8 protocols and show the dominant error reduction from K=2 to K=4. The N=8, g=0.12 control instead shows that the tested resonance-weighted K=4--8 local manifolds remain nonpredictive. This does not prove that every larger or differently selected reduced space must fail.

## Full-production route

Use `scripts/40_formal_k_convergence.py` with the selected `--n` and `--g` parameters to recompute a control from first principles. N=8 calculations can take a long time and require substantially more memory than this plotting audit.
