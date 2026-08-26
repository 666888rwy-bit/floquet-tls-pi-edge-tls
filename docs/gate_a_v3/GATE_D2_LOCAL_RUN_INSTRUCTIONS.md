# Gate D2 local N=6 run instructions

## 1. Freeze before calculating

Commit and push the complete Gate D2 source-freeze set before calculating the first N=6 response. Keep this commit separate from unrelated manuscript or infrastructure work. Then confirm:

```bash
git status --short
git rev-parse HEAD
git ls-remote origin | grep "$(git rev-parse HEAD)"
```

The first command must print nothing and the third must find the exact commit. The runner repeats both protections and refuses propagation if either fails.

## 2. Inspect the frozen plan

The dry run performs no propagation and no writes:

```bash
python scripts/gate_a_v3/33_run_gate_d2_n6_weight_transfer.py --dry-run
```

It must report both D1 hash anchors as valid, `selected_drives_exact_match: true`, and exactly these eight IDs:

```text
nu00_a  nu00_b  nu10_a  nu10_b
nu01_a  nu01_b  nu11_a  nu11_b
```

## 3. Run and resume locally

The complete N=6 campaign exceeds five minutes and should be run locally:

```bash
python scripts/gate_a_v3/33_run_gate_d2_n6_weight_transfer.py
```

If interrupted, do not delete the `.npz`/JSON checkpoint equivalent or restart without resume. Use:

```bash
python scripts/gate_a_v3/33_run_gate_d2_n6_weight_transfer.py --resume
```

The runner validates every completed JSON before skipping it. It writes `CHECKPOINT_MANIFEST.json` after each complete drive and writes `MANIFEST.json` only after all eight drives validate. A single frozen drive may be scheduled without changing the protocol:

```bash
python scripts/gate_a_v3/33_run_gate_d2_n6_weight_transfer.py --drive nu00_a --resume
```

Do not replace, add, or retune a drive after inspecting its response. If a partial record is invalid, preserve it for diagnosis; do not overwrite it silently.

## 4. Audit after completion

First run the no-write audit:

```bash
python scripts/gate_a_v3/34_audit_gate_d2_n6_weight_transfer.py --check-only
```

Then generate derived files outside the versioned evidence directory:

```bash
python scripts/gate_a_v3/34_audit_gate_d2_n6_weight_transfer.py \
  --output-dir build/gate_d2_audit
```

Gate D2 passes only if both fixed-$\nu_0$ median ratios exceed 10 and every sampled $\nu_\pi=1$ weight exceeds every sampled $\nu_\pi=0$ weight. Regardless of the outcome, do not add replacement points, N=8/N=10 extensions, or a response-informed sweep under Gate D2.

## 5. Manuscript language

If Gate D2 passes, the safe wording is: “the $\nu_\pi$-associated raw-weight hierarchy persists from N=4 to N=6 for the same response-blind, cross-period, eight-drive stratified protocol.” A pass does not establish a common-period causal law, thermodynamic topology, universal $\pi$-edge spectroscopy, or a universal lineshape.
