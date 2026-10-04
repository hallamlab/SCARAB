# SCARAB

SCARAB recruits and bins metagenomic contigs using sequence composition, read abundance, and optional trusted genomes such as SAGs. It produces extended partial genomes (xPGs) and supports optional guided reassembly in the same environment.

**[Full user guide](https://hallamlab-scarab.readthedocs.io/en/latest/index.html)** · [Reviewer test](https://hallamlab-scarab.readthedocs.io/en/latest/reviewer-test.html) · [Issues and feature requests](https://github.com/hallamlab/SCARAB/issues)

## Quick start

Install a released package with Mamba:

```bash
mamba create -n scarab -c conda-forge -c bioconda -c hallamlab scarab
mamba activate scarab
scarab recruit --help
```

Version 1.0.0 is being validated; Anaconda and Quay publication is pending. The user guide covers source installation, Docker, Apptainer, and the reviewer dataset.

The tiny recruitment-and-reassembly demo is bundled in `examples/reviewer/demo/` (about 1.7 MiB). No separate data download is needed. From this checkout:

```bash
cd examples/reviewer/demo
scarab recruit -m k12.gold_assembly.fasta -l read_list.txt -s SAG -o SCARAB_out -t 4
scarab reassemble \
  -i SCARAB_out/algo_defaults/Default/xpgs/ecoli-COLI-K12.3578.intersect.xPG.fasta \
  -l read_list.txt -o reassembly -t 4 --memory 4
python ../../../scripts/validate_reviewer.py --dataset . --output SCARAB_out --reassembly reassembly
```

## Workflow

[![SCARAB workflow](docs/assets/workflow-brief.svg)](https://hallamlab-scarab.readthedocs.io/)

For input preparation, parameters, outputs, guided reassembly, and HPC execution, see the **[user guide](https://hallamlab-scarab.readthedocs.io/)**.

[Report issues or request features](https://github.com/hallamlab/SCARAB/issues). Documentation source is maintained in `docs/`.
