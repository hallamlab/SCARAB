# SCARAB

**1.0.0 release candidate:** the source installation and reviewer demo have been tested. Anaconda and Quay publication is pending; registry commands apply once the release is available.

SCARAB recruits metagenomic reads using single-cell amplified genomes as references.

Its recruitment workflow combines assembly composition, read-coverage profiles, and optional trusted-genome anchors to recover metagenomic contigs and extended partial genomes (xPGs).

[User guide](docs/index.md) · [Installation](docs/installation.md) · [CLI reference](docs/cli-reference.md) · [Issues and feature requests](https://github.com/hallamlab/SCARAB/issues)

## Quick start

Install a released package with Mamba:

```bash
mamba create -n scarab -c conda-forge -c bioconda -c hallamlab scarab
mamba activate scarab
scarab recruit --help
```

See [installation](docs/installation.md) for Docker, Apptainer, and installation from GitHub, including how to test a source build before release. Package and container versions should match the code you intend to run.

With the [demo dataset](docs/reviewer-test.md) downloaded and extracted:

```bash
cd demo
scarab recruit -m k12.gold_assembly.fasta -l read_list.txt   -s SAG -o SCARAB_out -t 4
```

For your own data, provide an assembly FASTA, a text list of FASTQ paths, and optionally trusted-reference FASTAs. Follow the [first-run walkthrough](docs/quickstart.md) and [input format guide](docs/inputs.md).

## Workflow

[![SCARAB workflow](docs/assets/workflow-main.svg)](docs/assets/workflow-main.svg)

[Detailed workflow and data flow](docs/workflow.md) · [SVG](docs/assets/workflow-main.svg) · [PDF](docs/assets/workflow-main.pdf)

## Full documentation

The [user guide](docs/index.md) covers [installation](docs/installation.md), the [reviewer test](docs/reviewer-test.md), [parameters](docs/parameters.md), [outputs](docs/outputs.md), and [HPC execution and reruns](docs/resources.md).

Documentation source lives in `docs/`. [Report issues or request features](https://github.com/hallamlab/SCARAB/issues).
