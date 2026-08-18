# Reproducibility notes

The notebooks are provided without executed cell outputs, but they retain the model definitions and numerical workflow. The `data/checkpoints` directory contains compact saved outputs from the production scans.

The primary numerical conventions are: a two-step Floquet Ising drive, a locally exchange-coupled TLS, Lindblad amplitude damping of the TLS, and a transverse TLS subharmonic phasor used as the response observable.

Finite-size and finite-observation-window limitations are part of the result. The N=4 channel calculation is an exact validation layer; the N=6 targeted Arnoldi calculation is the production-scale channel analysis.
