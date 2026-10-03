# Resources, HPC execution, and reruns

## Local execution

`scarab recruit` is a Python controller executing recruitment stages in sequence. `--num_threads` is passed to supported tools and parallel operations. It is not a total-memory limit, and some numerical libraries may use their own thread pools. Memory use grows with the number of sequence windows, abundance samples, and embedding/clustering matrices. Measure a representative assembly before sizing a large run.

BBTools deduplication uses a 4 GB Java heap by default. Set `--dedupe_memory 8g` (or a value in `m`) for larger xPGs. This bounds that subprocess heap only; Python matrices, other tools, and Java overhead need additional memory.

SCARAB gives Numba a temporary cache inside the output directory and removes it after the run. This supports read-only installations and containers running as your user. An explicitly configured `NUMBA_CACHE_DIR` is respected.

## Slurm

SCARAB has no native Nextflow/Slurm submission interface. Submit the whole command as one cluster job and request resources for that command. For example, adapt this submission script to your cluster:

```bash
#!/usr/bin/env bash
#SBATCH --job-name=scarab
#SBATCH --account=YOUR_ACCOUNT
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=12:00:00
#SBATCH --output=scarab-%j.log
set -euo pipefail

mamba run -n scarab scarab recruit   -m /shared/assembly.fasta -l /shared/read_list.txt   -s /shared/trusted_genomes -o /shared/scarab_results   -t "$SLURM_CPUS_PER_TASK"
```

Submit with `sbatch scarab-job.sh`. Memory and time are illustrative requests, not measured guarantees. Ensure Mamba is available in the batch shell (load your site's module if required), and that reads, references, outputs and the environment are accessible to the compute node. Containers offer an alternative execution environment; they do not add a scheduler to SCARAB.

## Reusing outputs and forcing a fresh run

SCARAB records input file paths, sizes, modification times, version, and analysis settings in `scarab_run.json`, with execution state in `scarab_status.json`. A directory lock prevents simultaneous commands from using the same output. A completed run with matching recorded inputs/settings may reuse existing stage products; this is not a content-hashed, per-stage receipt system.

Changed or unrecorded inputs/settings and interrupted/failed runs require a fresh output or `--force`. Forced execution moves the old directory to a sibling `OUTPUT.previous-UNIQUE_ID` and starts from scratch, preserving previous results for inspection. It does not selectively invalidate individual stage files. This deliberately avoids trusting partial files from a failed command. Keep inputs outside the output tree; unsafe source/output arrangements are rejected before moving anything.

```bash
scarab recruit -m assembly.fasta -l read_list.txt -s SAG -o results -t 4 --force
```

Independent assemblies need separate output directories. Minimap2 temporary prefixes are scoped to the output directory. CPU thread count and log verbosity are excluded from the analysis-settings comparison, but changing them can affect timing and should be recorded in performance benchmarks.
