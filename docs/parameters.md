# Parameters and interpretation

Use `scarab recruit --help` for the complete [CLI reference](cli-reference.md). Start with defaults, then change one scientifically justified setting at a time in a new output directory.

## Sequence and similarity settings

| Option | Default | Meaning |
|---|---:|---|
| `--max_contig_len` | 10000 | Maximum tile length. |
| `--overlap_len` | 2000 | Overlap between adjacent tiles. |
| `--min_len` | 2000 | Minimum included sequence length. |
| `--kmer_size` | 201 | k-mer size used in MinHash recruitment. |
| `--jaccard` | 1.0 | Similarity threshold supplied to the recruitment/clustering logic. |
| `-t`, `--num_threads` | 1 | Threads for tools and parallel stages that use the setting. |
| `--pacbio` | off | Use the HiFi mapping preset for single-file read rows. |

## Parameter selection

`--autoopt` accepts the implemented methods `algo_defaults`, `majority_rule`, `best_cluster`, and `best_match`. The code calculates abundance-entropy features and consults its bundled reference/parameter tables. Those runtime tables are part of the installed package and are distinct from unpublished manuscript tables.

The relaxed/strict flags select calibrated recall/precision-oriented parameter sets. Specify only one of `--very_relaxed`, `--relaxed`, `--strict`, and `--very_strict`. Their descriptions express the calibration objective, not a guaranteed biological strain boundary for your dataset.

With no preset and `algo_defaults`, the selected setting is `Default`: de novo and anchored minimum cluster size 5, minimum samples unset, OC-SVM nu 0.5, and gamma `scale`. A nondefault AutoOpt method without a strictness flag selects `very_strict`. A strictness flag with `algo_defaults` selects `majority_rule`. The log records the effective selection.

## Manual overrides and fresh runs

Explicit `--denovo_min_clust`, `--denovo_min_samp`, `--anchor_min_clust`, `--anchor_min_samp`, `--nu`, and `--gamma` values override the selected AutoOpt values. Minimum cluster sizes must be at least 2, minimum samples at least 1, nu in `(0,1]`, and gamma either `scale`, `auto`, or a positive finite number. Effective values are logged.

`--jaccard` is a minimum threshold, so qualifying hits at or above the value are retained. The MinHash search collects both Jaccard and containment hits in the legacy `jacc_sim` column; a score of 1 can therefore indicate complete containment rather than whole-genome identity. Custom k-mer sizes use their corresponding MinHash results. Specify only one strictness preset; incompatible flags and invalid numeric ranges fail before analysis.

`--force` preserves an existing output directory as a sibling named `OUTPUT.previous-UNIQUE_ID` and starts a fresh output. Source inputs must be outside the output tree. See [rerun behavior](resources.md).

`--dedupe_memory` sets the BBTools Java heap limit (default `4g`), avoiding automatic allocation based on the entire host. It is not a whole-workflow memory limit.
