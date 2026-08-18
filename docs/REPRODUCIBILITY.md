# Reproducibility protocol

## 1. Purpose and evidence hierarchy

This document is written for a referee, collaborator, or reader who wants to determine exactly what is directly reproducible from the public repository. The project studies a **finite** Floquet–Lindblad spin chain with a locally exchange-coupled, amplitude-damped TLS. Its evidence hierarchy has three layers: closed-chain Floquet benchmarks, compact checkpoints from production open-system scans, and independent channel/time-domain cross-checks.

> **Scope statement.** The calculations establish finite-size, finite-observation-window results. They do not establish a thermodynamic-limit time-crystal phase, a sharp open-system phase boundary, or a universal multi-position effective-coupling collapse.

| Claim under examination | Public verification route | Numerical form of the conclusion |
|---|---|---|
| The TLS response is enhanced near the boundary and has a response-specific localization length. | Run `scripts/10_double_boundary_localization.py`. | The fitted \(\xi_{\rm response}\) is larger than the independently quoted closed-chain \(\xi_B\) and \(\xi_\pi\); it must not be identified with either bare closed-chain length. |
| A resolved boundary-response splitting tracks the selected local edge matrix element over the available edge scan. | Run `scripts/20_effective_coupling_scaling.py`. | The reported relation is an empirical resolved-regime line in \(|gB_{0\pi}(0)|\), with a nonzero intercept retained. |
| A selected Floquet channel pair explains the late-time subharmonic signal quantitatively but not perfectly. | Run `scripts/30_channel_time_validation.py`. | Channel and time-domain fits agree at the approximately 8% lifetime and 13% phase-offset levels for the stated N=4 protocol. |

## 2. Software environment

The repository was tested using Python 3.11 with the packages declared in `requirements.txt`.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

No commercial software, hidden API key, or remote numerical service is required. The public scripts use only NumPy, SciPy, Matplotlib, and the Python standard library. The notebooks require JupyterLab only for interactive execution.

## 3. Fast verification path

From the repository root, execute the following commands. Each script resolves its own repository-relative data paths and writes only to `results/reproduced/`.

```bash
python scripts/10_double_boundary_localization.py
python scripts/20_effective_coupling_scaling.py
python scripts/30_channel_time_validation.py
```

| Command | Input checkpoint or calculation | Expected primary output | Reviewer check |
|---|---|---|---|
| `10_double_boundary_localization.py` | `floquet_tls_N6_position_frequency_checkpoint.npz` | `A_double_boundary_localization_fit.png` | Confirm two-boundary fits across the three discard windows and compare the common \(\xi\) with the listed closed-chain lengths. |
| `20_effective_coupling_scaling.py` | `floquet_tls_N6_g_frequency_checkpoint.npz` | `B_response_splitting_vs_geff.png` | Confirm that only accepted/resolved peak pairs are fit, and retain the negative intercept rather than forcing a line through the origin. |
| `30_channel_time_validation.py` | Exact N=4 channel construction | `C_N4_channel_time_validation.png` | Confirm that the time-trace fit does not initialize from the channel eigenvalue, and compare both decay and phase offset. |

The scripts also create Markdown and JSON summaries. These are versioned under `results/reproduced/` so that a reviewer can compare a newly generated artifact with the committed baseline using ordinary file diff tools.

## 4. Direct N=6 implementation check

The long-form direct propagation check is separate from the fast checkpoint analyses:

```bash
python scripts/00_reproduce_n6_reference.py
```

This script reconstructs an N=6 open-system trajectory at the stated reference working point and compares its observables against the corresponding saved production checkpoint. It is intentionally provided as an implementation check rather than as a claim of full scan reproduction on a laptop. Runtime depends strongly on CPU, sparse-exponential implementation, and available memory.

## 5. Reproducing the main analyses

### 5.1 Double-boundary response localization

The primary spatial proxy is the root integrated TLS transverse response,

\[
A_{\rm response}(m)=\left[\int \left|A_{\rm TLS}^{\perp}(\omega;m)\right|^2\,d\omega\right]^{1/2},
\]

fit with

\[
A(m)=A_L e^{-m/\xi}+A_R e^{-(N-1-m)/\xi}.
\]

The script performs window-resolved and joint fits for three spatial proxies. The root-integrated quantity is primary; peak height and exact-resonance amplitude are sensitivity tests. The committed analysis reports a joint primary estimate \(\xi_{\rm response}=0.856\pm0.017\), where the displayed uncertainty is the across-window systematic variation, not a thermodynamic or statistical confidence interval. The closed-chain comparison values are \(\xi_B=0.3336\) and \(\xi_\pi=0.3671\).

### 5.2 Effective-coupling scaling

The boundary coupling scan is replotted against

\[
|g_m|=g\,|B_{0\pi}(m)|,
\]

using the selected N=6 edge matrix element \(|B_{0\pi}(0)|=0.2726796705\). The four accepted resolved points yield the committed empirical fit

\[
\Delta\omega_{\rm response}=12.662|g_m|-0.07333, \qquad R^2=0.99825.
\]

The nonzero intercept is physically and methodologically important: this is a **resolved-regime empirical scaling**, not a perturbative theorem or an extrapolation to vanishing coupling. The companion `90_` analysis documents why moving the TLS into the bulk cannot, at the available parameters, be treated as a clean one-parameter collapse experiment.

### 5.3 Channel-to-time-domain validation

For the N=4 exact one-period channel, the selected \(\pi\)-sector eigenvalue gives

\[
\tau_{\rm channel}=-\frac{T}{\ln|\lambda_\pi|},
\qquad
\delta\omega_{\rm channel}=\frac{|\arg(\lambda_\pi)-\pi|}{T}.
\]

The time trace is fit independently to a decaying subharmonic form with a baseline,

\[
m(n)=m_\infty+A\exp[-n/(\tau/T)]\cos[(\pi+\delta)n+\phi].
\]

The comparison is deliberately not called exact. Early-time multimode contributions produce window sensitivity, while the late-time fit is consistent with the selected slow \(\pi\)-sector pair at the reported 8% lifetime and 13% frequency-offset comparison levels.

## 6. Checkpoints, figures, and notebooks

The scripts consume compact `.npz` files under `data/checkpoints/`. A file-by-file dictionary of axes, observables, metadata, and completion masks is available in [DATA_DICTIONARY.md](DATA_DICTIONARY.md). Two result directories are retained intentionally:

| Directory | Meaning |
|---|---|
| `results/manuscript_figures/` | Frozen reference images representing the reviewed analysis state. |
| `results/reproduced/` | Baseline generated figures and machine-readable summaries; these are recreated by the public scripts. |

The four notebooks in `notebooks/` preserve the original numerical workflow without embedded output cells. They are exploratory and production-workflow records; the numbered scripts are the recommended audit path because they are shorter, deterministic at the checkpoint-analysis layer, and directly linked to the public claims.

## 7. Numerical conventions and limitations

The model uses a two-step Floquet Ising drive, an exchange-coupled TLS contact, and Markovian TLS amplitude damping. The main open-system response observable is a transverse TLS subharmonic phasor extracted after a stated discarded transient window. Completion masks and the discard windows are carried inside the checkpoints so that no incomplete grid point is silently interpreted as data.

Finite chain length, finite frequency resolution, finite discard windows, Markovian damping, and the selected initial state are all part of the protocol. In particular, the effective-matrix-element rescaling is useful for the boundary scan but becomes unreliable at interior sites when matching \(|g_m|\) requires a bare coupling that is no longer weak relative to the microscopic drive scales.

## 8. Troubleshooting and integrity checks

If a script produces a result in a different directory, confirm that you are using the current numbered version from `scripts/`; all four analysis scripts are intended to target `results/reproduced/`. If figures differ substantially, first compare package versions and confirm that the checkpoint files have not changed. A quick content audit can be performed with:

```bash
git status --short
sha256sum data/checkpoints/*.npz
```

For a clean clone at the tagged or cited version, `git status --short` should produce no output before running scripts. Generated figures can be regenerated safely; they do not modify the checkpoints.

## 9. Citation

The earlier manuscript version is archived at [Zenodo, DOI: 10.5281/zenodo.20685212](https://doi.org/10.5281/zenodo.20685212). Please cite the final article when available; until then, cite the Zenodo record together with the repository URL and the commit or release tag used for analysis.
