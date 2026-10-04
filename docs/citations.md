# Software and method citations

The repository's `CITATION.cff` declares Ryan J. McLaughlin and Steven J. Hallam
as the provisional author list supplied by the maintainer. Confirm the final
manuscript authors before archiving a release. Affiliations and ORCIDs are
intentionally omitted until supplied; do not derive them from GitHub profiles.

Record the SCARAB repository revision or release with your methods, and cite the tools used by the enabled stages. The [workflow page](workflow.md) shows where they enter the analysis. This guide does not assign an unverified manuscript DOI to SCARAB.

| Software | Use | Citation / project |
|---|---|---|
| HDBSCAN | Density-based clustering | McInnes, Healy & Astels (2017), *hdbscan: Hierarchical density based clustering*, JOSS 2(11):205. [DOI](https://doi.org/10.21105/joss.00205); [project](https://github.com/scikit-learn-contrib/hdbscan). |
| UMAP | Low-dimensional embeddings | [Project and citation guidance](https://github.com/lmcinnes/umap). |
| scikit-learn | Statistical learning and preprocessing | [Project and citation guidance](https://scikit-learn.org/stable/about.html). |
| NumPy, SciPy, pandas | Numerical arrays, scientific routines, and tables | [NumPy](https://numpy.org/citing-numpy/), [SciPy](https://scipy.org/citing-scipy/), [pandas](https://pandas.pydata.org/about/citing.html). |

| sourmash | MinHash signatures and similarity searches | Irber et al. (2024), *sourmash v4: A multitool to quickly search, compare, and analyze genomic and metagenomic data sets*, JOSS 9(98):6830. [DOI](https://doi.org/10.21105/joss.06830); [project](https://github.com/sourmash-bio/sourmash). |
| minimap2 | Read mapping | Li (2018), *Minimap2: pairwise alignment for nucleotide sequences*, Bioinformatics 34:3094–3100. [DOI](https://doi.org/10.1093/bioinformatics/bty191); [project](https://github.com/lh3/minimap2). |
| SAMtools | BAM conversion and sorting | [Project and citation guidance](https://www.htslib.org/). |
| MetaBAT2 depth summarizer | Coverage features; SCARAB does not call MetaBAT2 binning here | [Project](https://bitbucket.org/berkeleylab/metabat). |
| BBTools | Deduplication of reference-plus-recruit xPG sequences | [Project](https://sourceforge.net/projects/bbmap/). |
| scikit-bio, Numba, pyfastx, screed | Composition utilities, compiled numerical routines, and sequence I/O | [scikit-bio](https://scikit.bio/), [Numba](https://numba.pydata.org/), [pyfastx](https://github.com/lmdu/pyfastx), [screed](https://github.com/dib-lab/screed). |

Mamba manages software environments; see the [Mamba project](https://github.com/mamba-org/mamba). Record environment specifications and actual versions alongside scientific citations.

Guided reassembly additionally uses [SPAdes](https://github.com/ablab/spades);
follow its [citation guidance](https://ablab.github.io/spades/citation.html).
Read selection and quality trimming also use minimap2, SAMtools and BBTools
as listed above.
