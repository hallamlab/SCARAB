# Tiny installation and workflow demo

SCARAB includes **one bundled demo** that exercises recruitment through guided reassembly. Its inputs total about **1.7 MiB**: a 403 kb assembly, one 150 kb trusted-reference fragment, and three paired-read libraries of roughly 3,000 pairs each. It is deliberately a technical demonstration, not a biological accuracy benchmark.

## Get the bundled inputs

Use your SCARAB checkout. If you installed only the Mamba package or container, obtain the example from GitHub:

```bash
git clone https://github.com/hallamlab/SCARAB.git
cd SCARAB
```

Then:

```bash
cd examples/reviewer/demo
```

No separate archive download or path editing is required. `read_list.txt` contains relative paths, so run the commands from this directory.

## Mamba package or source installation

Activate your SCARAB environment, then run:

```bash
scarab recruit \
  -m k12.gold_assembly.fasta -l read_list.txt \
  -s SAG -o SCARAB_out -t 4

scarab reassemble \
  -i SCARAB_out/algo_defaults/Default/xpgs/ecoli-COLI-K12.3578.intersect.xPG.fasta \
  -l read_list.txt -o reassembly -t 4 --memory 4

python ../../../scripts/validate_reviewer.py \
  --dataset . --output SCARAB_out --reassembly reassembly
```

The xPG path is the default combined recruitment product for the bundled reference. Recruitment and guided reassembly use the same environment. Allow 8 GB RAM for the demo; `--memory 4` controls SPAdes' memory limit, while BBTools has its own bounded heap. See [installation](installation.md) for environment setup and [guided reassembly](reassembly.md) for the individual stages.

## Docker

Run from the same demo directory. Use the released image below, or `scarab:local` for a local build:

```bash
docker run --rm -u "$(id -u):$(id -g)" \
  -v "$PWD:$PWD" -w "$PWD" quay.io/hallamlab/scarab:1.0.0 \
  scarab recruit -m k12.gold_assembly.fasta -l read_list.txt -s SAG -o SCARAB_out -t 4

docker run --rm -u "$(id -u):$(id -g)" \
  -v "$PWD:$PWD" -w "$PWD" quay.io/hallamlab/scarab:1.0.0 \
  scarab reassemble \
  -i SCARAB_out/algo_defaults/Default/xpgs/ecoli-COLI-K12.3578.intersect.xPG.fasta \
  -l read_list.txt -o reassembly -t 4 --memory 4

python3 ../../../scripts/validate_reviewer.py --dataset . --output SCARAB_out --reassembly reassembly
```

The registry image becomes available after release publication. The [installation guide](installation.md) includes local builds.

## Apptainer

Place `scarab.sif` in this working directory or replace its path:

```bash
apptainer exec --bind "$PWD:$PWD" --pwd "$PWD" scarab.sif \
  scarab recruit -m k12.gold_assembly.fasta -l read_list.txt -s SAG -o SCARAB_out -t 4

apptainer exec --bind "$PWD:$PWD" --pwd "$PWD" scarab.sif \
  scarab reassemble \
  -i SCARAB_out/algo_defaults/Default/xpgs/ecoli-COLI-K12.3578.intersect.xPG.fasta \
  -l read_list.txt -o reassembly -t 4 --memory 4

python3 ../../../scripts/validate_reviewer.py --dataset . --output SCARAB_out --reassembly reassembly
```

These are three installation routes for the same demo. Use a fresh copy of the inputs when comparing installations; completed matching runs otherwise reuse their outputs. `scripts/prepare_reviewer.py --output /new/workspace` copies only the verified bundled inputs to `/new/workspace/demo` without downloading anything or copying previous results.

## What success means

The validator prints **`All reviewer checks passed`** only after checking:

- Bundled input checksums and successful run status.
- Coverage from all three libraries and agreement between coverage and subcontig IDs.
- De novo, HDBSCAN, OC-SVM and combined assignment tables against their FASTA membership; noise must not be exported as a bin.
- Recruited sequences against the assembly and xPG sequences against their trusted/recruited sources.
- A completed guided assembly, usable read pairs from every library, nonempty contigs/scaffolds, and normal intermediate cleanup. A target skipped for lack of reads does not pass.

Inspect `SCARAB_out/SCARAB_log.txt`, the recruited FASTAs, and `reassembly/reassembly_summary.tsv`. Each assembly target also retains commands, an assembly log and its result receipt. See [outputs](outputs.md) and [reassembly](reassembly.md).

The fixture checks technical execution and data consistency. Its selected reads and shortened reference are unsuitable for measuring recruitment accuracy or biological genome quality.

## Provenance

The fixture derives from the [original public E. coli K12 SCARAB demo](https://drive.google.com/file/d/1yUoPpoNRl6-CZHkRoUYDbikBJk4yC-3V/view). `tests/reviewer/demo.json` preserves the original archive provenance; `tests/reviewer/bundled.json` records the selection procedure, tool version, retained read counts and input hashes. `examples/reviewer/README.md` and `scripts/build_reviewer_subset.py` document reproduction. The original 55.7 MiB archive is a source artifact, not a second reviewer test.
