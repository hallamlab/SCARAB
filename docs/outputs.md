# Output files

SCARAB writes logs, feature matrices, clustering assignments, and FASTA products under `-o`. It does not provide the report/explorer interface of MetaPathways or ASPIRE.

```text
OUTPUT/
├── SCARAB_log.txt
├── scarab_run.json
├── scarab_status.json
├── *.subcontigs.fasta
├── *.mbacov.tsv
├── *.coverage.scaled.tsv
├── feature/signature/parameter intermediates
└── <autoopt-method>/<selected-setting>/
    ├── *.tsv
    ├── denovo/
    ├── hdbscan/
    ├── ocsvm/
    ├── intersect/
    └── xpgs/
```

The method and setting names are resolved by AutoOpt and printed in the log. Some intermediate names and optional products depend on which paths ran; this is a guide to the layout, not a promise that every directory will contain sequences.

| Product | Interpretation |
|---|---|
| `*.mbacov.tsv` | Raw MetaBAT depth-summary table used for abundance features. |
| `*.coverage.scaled.tsv` | Scaled abundance matrix used by clustering. |
| `*.denovo_clusters.tsv` and `*.denovo_noise.tsv` | De novo assignments and unassigned/noise records. |
| `*.hdbscan_clusters.tsv` | Trusted-anchor HDBSCAN assignments. |
| `*.ocsvm_clusters.tsv` | One-class SVM recruitment assignments. |
| `*.inter_clusters.tsv` | Pairwise-agreement recruitment plus qualifying anchors; see the workflow set formula. |
| `*.denovo.fasta` | Original contigs assigned to de novo bins. |
| `*.hdbscan.fasta`, `*.ocsvm.fasta`, `*.intersect.fasta` | Recruited contig sets from the anchored approaches. |
| `*.xPG.fasta` | Trusted reference plus recruits after BBTools deduplication. |

Recruited FASTAs and xPG FASTAs answer different questions: the first contains recruited metagenomic sequence; the latter also contains the trusted reference. The deduplication command uses a 97% minimum identity setting. Independently validate genome quality and interpret overlap between recruitment approaches.

The abundance stage removes SAM/BAM and selected tool-output intermediates after coverage generation. Retain final FASTAs, assignment tables, logs, input manifests, and the software revision for downstream review. Avoid manually pruning a partially completed output if you intend to reuse it.

For guided assemblies derived from these products, see [reassembly](reassembly.md).
