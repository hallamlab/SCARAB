# Reviewer/demo test

Use the historical public E. coli K12 demo: one assembly, **three paired-read libraries**, and **two trusted genomes**. The 56 MiB archive is downloaded separately; the repository includes preparation, checksum, and result-validation tools. This is an installation and workflow test, not an independent biological accuracy benchmark.

## Prepare the data

Use your existing SCARAB checkout for the helper scripts. If you installed only the package or container, obtain the scripts first:

```bash
git clone https://github.com/hallamlab/SCARAB.git SCARAB-reviewer
cd SCARAB-reviewer
```

From that checkout:

```bash
python scripts/prepare_reviewer.py --output ~/scarab-reviewer
cd ~/scarab-reviewer/demo
```

The helper downloads [demo.zip](https://drive.google.com/file/d/1yUoPpoNRl6-CZHkRoUYDbikBJk4yC-3V/view?usp=sharing), verifies its SHA-256, and extracts it. It refuses to overwrite an existing demo directory. If you already downloaded the archive, add `--archive /path/to/demo.zip` to the preparation command.

The included `read_list.txt` uses relative paths to `fastq/`; run from the `demo` directory. No path editing is needed. Archive and per-file checksums are recorded in `tests/reviewer/demo.json`.

## Mamba package or GitHub installation

With the SCARAB environment activated:

```bash
scarab info
scarab recruit \
  -m k12.gold_assembly.fasta -l read_list.txt \
  -s SAG -o SCARAB_out -t 4
```

The default command runs MinHash recruitment, maps all three paired libraries, builds abundance/composition features, clusters contigs, and builds anchored xPGs. Allow 8 GB RAM and 2 GB free disk as an initial provision for this demo; these are recommendations, not limits for arbitrary datasets. BBTools uses a bounded 4 GB Java heap by default.

## Docker

After building or installing the image, run from the same demo directory. For a local build, replace the image with `scarab:local`:

```bash
docker run --rm -u "$(id -u):$(id -g)" \
  -v "$PWD:$PWD" -w "$PWD" quay.io/hallamlab/scarab:1.0.0 \
  scarab recruit -m k12.gold_assembly.fasta -l read_list.txt \
  -s SAG -o SCARAB_out_docker -t 4
```

The registry image becomes available after release publication. See [installation](installation.md) for the local build route.

## Apptainer

```bash
apptainer exec --bind "$PWD:$PWD" --pwd "$PWD" scarab.sif \
  scarab recruit -m k12.gold_assembly.fasta -l read_list.txt \
  -s SAG -o SCARAB_out_apptainer -t 4
```

All routes use the same CLI and inputs. Additional input locations require additional mounts. Use separate output directories when comparing installations.

## Validate the results

From your SCARAB checkout, point the validator at the dataset and the output directory you used:

```bash
python scripts/validate_reviewer.py \
  --dataset ~/scarab-reviewer/demo \
  --output ~/scarab-reviewer/demo/SCARAB_out
```

Success prints **`All reviewer checks passed`**. Validation checks the original input hashes, successful run status, coverage for all three libraries, matching subcontig/coverage identifiers, and anchored products for both trusted genomes. It verifies that assignment tables agree with FASTA membership, recruited sequences match the assembly, and xPG sequences come from the trusted genome or recruits. Noise labels must not become exported bins.

The validator does not impose an exact number of clusters: numerical behavior can vary across platforms. Read `SCARAB_log.txt` and the [output guide](outputs.md) to interpret the results. Passing these checks establishes data consistency and successful execution, not a claim that every inferred bin is biologically correct.

To exercise the optional unanchored route, run the same command without `-s SAG` and use a new output directory. That route produces de novo products; the anchored-demo validator deliberately requires trusted-genome outputs.
