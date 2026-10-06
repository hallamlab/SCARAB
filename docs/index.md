# SCARAB: SCaffold-Anchored Recruitment And Binning

**SCARAB 1.0.0:** install with [Mamba, Docker or Apptainer](installation.md), then run the [bundled recruitment-and-reassembly demo](test.md).

SCARAB uses an ensemble of machine-learning methods to recruit metagenomic contigs around trusted genomic scaffolds, such as single-cell amplified genomes (SAGs). It combines sequence similarity, read-derived abundance and nucleotide composition to recover sequence associated with a target population and construct extended population-genomes (xPGs).

MinHash searches identify candidate contigs and high-similarity anchors. Coverage and tetranucleotide-composition features are transformed, scaled and embedded with Uniform Manifold Approximation and Projection (UMAP). Density-based clustering (HDBSCAN) identifies groups of related sequence windows, while a one-class support vector machine (OC-SVM) learns the feature distribution of anchor-associated windows. Combined recruitment retains contigs supported by at least two of the MinHash, HDBSCAN and OC-SVM evidence sets, together with qualifying anchors. HDBSCAN also provides de novo bins when trusted anchors are unavailable.

AutoOpt can select clustering settings using Rényi entropy profiles of read abundance and bundled reference calibrations; explicit parameter overrides remain available. The optional guided-reassembly step maps paired reads to an xPG and runs SPAdes with trusted contigs. Recruitment and reassembly produce candidates for downstream genome-quality assessment and biological interpretation. See the [detailed workflow](workflow.md), [parameter guide](parameters.md) and [method citations](citations.md) for the algorithms and their assumptions.

Start with [installation](installation.md) and the [tiny end-to-end test test](test.md), then adapt the [input guide](inputs.md) to your own assembly, reads and optional trusted genomes.

```{container} primary-workflow
[![SCARAB workflow](assets/workflow-brief.svg)](assets/workflow-brief.svg)
```

[Explore the detailed workflow](workflow.md) · [Overview SVG](assets/workflow-brief.svg) · [Overview PDF](assets/workflow-brief.pdf)

Arrows between numbered modules trace the conceptual flow of results. Optional branches depend on configuration; the detailed workflow explains task dependencies.

```{toctree}
:maxdepth: 2
:caption: Getting started

installation
quickstart
test
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
