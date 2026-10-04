# SCARAB

**SCARAB 1.0.0 release candidate:** the source installation and public reviewer demo have been tested. Anaconda and Quay publication remains pending; use the source route until registry packages are available.

SCARAB recruits and bins metagenomic contigs using sequence composition, read abundance, and optional trusted genomes such as SAGs.

Start with a metagenome assembly and its reads. Add trusted genomes to anchor recruitment, then inspect the contig bins and extended partial genomes produced from composition, abundance, and sequence-similarity evidence.

```{container} primary-workflow
[![SCARAB workflow](assets/workflow-main.svg)](assets/workflow-main.svg)
```

```{toctree}
:maxdepth: 2
:caption: Getting started

installation
quickstart
reviewer-test
inputs
```

```{toctree}
:maxdepth: 2
:caption: Workflow and interpretation

workflow
reassembly
parameters
outputs
resources
cli-reference
troubleshooting
citations
```

```{toctree}
:maxdepth: 2
:caption: Maintaining SCARAB

development
documentation
```
