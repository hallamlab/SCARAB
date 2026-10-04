# Guided reassembly

Use `scarab reassemble` after recruitment when you want a new assembly guided
by an xPG or another trusted genome FASTA. Both commands use the same installed
SCARAB environment, including SPAdes; no separate environment or Snakemake
configuration is required.

## Start with one target

```bash
scarab reassemble \
  -i SCARAB_out/algo_defaults/Default/xpgs/target.xPG.fasta \
  -l read_list.txt \
  -o reassembly \
  --threads 8 --memory 32
```

Replace the example FASTA with an actual xPG from your recruitment output.
AutoOpt method and setting directories depend on your run; consult the log
and [output guide](outputs.md). To process several targets, pass their FASTA
directory to `-i`. Discovery is nonrecursive and accepts `.fa`, `.fna`, and
`.fasta`; use uncompressed input FASTAs and unique basenames. References,
read files and adapters must remain outside the output directory.

The read list is headerless: one interleaved short-read FASTQ or two
 tab-separated R1/R2 paths per row. Relative paths resolve from the working
directory, as in `recruit`. Paired FASTQs may be gzip-compressed. This command
is for paired short reads; the recruitment command's HiFi mode is not a
reassembly mode. Use a separate output for reassembly, preserving recruitment
results.

## What runs

For each target and library, minimap2 uses its short-read preset. Primary
alignments are retained only when both mates are mapped. Secondary and
supplementary alignments are excluded. SAMtools groups names and extracts
paired reads; libraries are processed separately so repeated read names do
not become cross-library pairs. Unpaired alignments are not assembly input.

BBTools repairs pairing and BBDuk removes adapters and trims low-quality
sequence. Settings follow the existing guided-reassembly recipe: right-end
k-mer trimming (`k=23`, `mink=11`, `hdist=1`, paired overlap handling), quality
trimming at 10, and minimum read length 75. Paired identifiers and counts are
checked before assembly. SPAdes runs with `--isolate` and the target FASTA as
`--trusted-contigs`. Trusted sequence can bias reconstruction; inspect read
support and genome quality rather than treating the result as a validated
complete genome.

## Resources and outputs

| Option | Meaning |
|---|---|
| `--threads`, `-t` | Threads for the active target; default 1. Targets run sequentially. |
| `--memory` | SPAdes memory limit in GB; default 16. BBTools heap is capped at the smaller of this value and 4 GB. This is not an operating-system memory limit for the whole command. |
| `--adapters` | Optional adapter FASTA. Normally discovered beside the installed BBTools executable. |
| `--keep-intermediates` | Preserve successful mapping, QC and SPAdes work directories. |
| `--force` | Preserve previous output in a sibling backup and start a fresh run. |

The output contains `reassembly_summary.tsv`, run provenance/status JSON and
one directory per target. Successful targets have `contigs.fasta`,
`scaffolds.fasta`, `reassembly.json`, `commands.log` and `spades.log`. The
summary reports mapped and clean pair counts and final sequence paths.
Targets with no usable pairs are explicitly recorded as
`skipped_no_usable_pairs`; they do not produce invented assembly files.

Intermediate work is removed after a successful or explicitly skipped target
unless requested otherwise. Failure preserves diagnostic files and exits
nonzero. A matching completed run can be invoked again to reuse its results.
An interrupted or changed run requires a fresh output or `--force`; this first
implementation does not resume individual failed SPAdes stages.

Under Slurm, request resources for one whole command and use the same
`--threads` and `--memory` values. Container users must bind all input paths
and a writable output directory. See [installation](installation.md) and
[resources](resources.md).
