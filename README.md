# SCARAB: SCaffold-Anchored Recruitment And Binning

SCARAB recruits and bins metagenomic contigs using sequence composition, read abundance, and optional trusted genomes such as SAGs. It produces extended population-genomes (xPGs) and supports optional guided reassembly in the same environment.

**[Full user guide](https://hallamlab-scarab.readthedocs.io/en/latest/index.html)** · [Test](https://hallamlab-scarab.readthedocs.io/en/latest/test.html) · [Issues and feature requests](https://github.com/hallamlab/SCARAB/issues)

## Quick start

Install a released package with Mamba:

```bash
mamba create -n scarab --strict-channel-priority -c conda-forge -c bioconda -c hallamlab scarab=1.0.0
mamba activate scarab
scarab recruit --help
```

SCARAB 1.0.0 is available from [Anaconda](https://anaconda.org/hallamlab/scarab) and [Quay](https://quay.io/repository/hallamlab/scarab?tab=tags). The user guide covers Docker, Apptainer, source installation and the test dataset.

The tiny recruitment-and-reassembly demo is bundled in `examples/test/demo/` (about 1.7 MiB). No separate data download is needed. To obtain the example matching the release:

```bash
git clone https://github.com/hallamlab/SCARAB.git
cd SCARAB/examples/test/demo
scarab recruit -m k12.gold_assembly.fasta -l read_list.txt -s SAG -o SCARAB_out -t 4
scarab reassemble \
  -i SCARAB_out/algo_defaults/Default/xpgs/ecoli-COLI-K12.3578.intersect.xPG.fasta \
  -l read_list.txt -o reassembly -t 4 --memory 4
python ../../../scripts/validate_test.py --dataset . --output SCARAB_out --reassembly reassembly
```

## Workflow

[![SCARAB workflow](docs/assets/workflow-brief.svg?v=local-tiling-20261010)](https://hallamlab-scarab.readthedocs.io/)

For input preparation, parameters, outputs, guided reassembly, and resource settings, see the **[user guide](https://hallamlab-scarab.readthedocs.io/)**.

[Report issues or request features](https://github.com/hallamlab/SCARAB/issues). Documentation source is maintained in `docs/`.
