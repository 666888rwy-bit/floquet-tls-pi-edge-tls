# Public numerical data

The `checkpoints/` directory contains compact, versioned `.npz` files that support the public figure-regeneration scripts. These files are **derived numerical outputs** from the stated finite Floquet–Lindblad protocol, not experimental measurements and not every raw transient trajectory from the original production runs.

A reviewer should begin with [../docs/DATA_DICTIONARY.md](../docs/DATA_DICTIONARY.md), which specifies each file's sweep axes, observable names, completion masks, and intended inferential use. The checksums can be generated locally with:

```bash
sha256sum checkpoints/*.npz
```

The repository intentionally excludes browser-renamed duplicates, transient solver files, manuscript drafts, and large intermediate trajectory dumps. The included checkpoints are sufficient to regenerate the public A/B analyses, inspect the damping and finite-size scans, and document the multi-position effective-model boundary test.
