# CLI reference

Generated from the public parser. Read [parameters](parameters.md) for effective behavior and [resources](resources.md) for rerun semantics.

## recruit

```text
usage: scarab [-v] [-h] -m MG_FILE -l MG_RAW_FILE_LIST -o SAVE_PATH
              [-s TRUST_PATH] [--autoopt AUTO_PARAMS] [--very_relaxed]
              [--relaxed] [--strict] [--very_strict]
              [--denovo_min_clust DENOVO_MIN_CLUST]
              [--anchor_min_clust ANCHOR_MIN_CLUST]
              [--denovo_min_samp DENOVO_MIN_SAMP]
              [--anchor_min_samp ANCHOR_MIN_SAMP] [--nu NU] [--gamma GAMMA]
              [--max_contig_len MAX_CONTIG_LEN] [--overlap_len OVERLAP_LEN]
              [--min_len MIN_LEN] [--kmer_size KMER_SIZE] [--jaccard JACCARD]
              [--pacbio] [-t NTHREADS] [--dedupe_memory DEDUPE_MEMORY]
              [--force]

Recruit environmental reads to reference contigs.

Required parameters:
  -m MG_FILE, --metag MG_FILE
                        Path to a metagenome assembly [FASTA format only].
  -l MG_RAW_FILE_LIST, --metaraw MG_RAW_FILE_LIST
                        Text file containing paths to raw FASTQ files for samples.
                        One file per line, supports interleaved and separate PE reads.
                        For separate PE files, both file paths on one line sep by [tab].
  -o SAVE_PATH, --output-dir SAVE_PATH
                        Path to directory for all outputs.
  -s TRUST_PATH, --trusted-contigs TRUST_PATH
                        Path to reference FASTA file or directory containing only FASTA files.

Optional options:
  --autoopt AUTO_PARAMS
                        select which automatic optimization algorithm parameter set to use,
                        [algorithm default], majority_rule, best_cluster, best_match.
  --very_relaxed        parameter-set that maximizes recall at approximately strain-level
  --relaxed             parameter-set that maximizes recall at substrain-level.
  --strict              parameter-set that maximizes precision at approximately strain-level.
  --very_strict         parameter-set that maximizes precision at substrain-level.
  --denovo_min_clust DENOVO_MIN_CLUST
                        minimum cluster size for De Novo HDBSCAN clustering.
  --anchor_min_clust ANCHOR_MIN_CLUST
                        minimum cluster size for Anchored HDBSCAN clustering.
  --denovo_min_samp DENOVO_MIN_SAMP
                        minimum sample number for De Novo HDBSCAN clustering.
  --anchor_min_samp ANCHOR_MIN_SAMP
                        minimum sample number for De Anchored HDBSCAN clustering.
  --nu NU               nu setting for Anchored OC-SVM clustering.
  --gamma GAMMA         gamma setting for Anchored OC-SVM clustering.
  --max_contig_len MAX_CONTIG_LEN
                        Max subcontig length in basepairs [10000].
  --overlap_len OVERLAP_LEN
                        subcontig overlap in basepairs [2000].
  --min_len MIN_LEN     minimum length of contigs to include in basepairs [2000].
  --kmer_size KMER_SIZE
                        kmer length to use for minhash step [201].
  --jaccard JACCARD     minimum jaccard index to ID contigs as trusted [1.0].
  --pacbio              Set if raw reads are PacBio Hifi [False]

Miscellaneous options:
  -v, --verbose         Prints a more verbose runtime log
  -h, --help            Show this help message and exit
  -t NTHREADS, --num_threads NTHREADS
                        Number of threads [1].
  --dedupe_memory DEDUPE_MEMORY
                        BBTools Java heap limit, e.g. 4g or 512m [4g].
  --force               Preserve existing output in a sibling backup and start a fresh run [False]
```

## info

```text
usage: scarab [-v] [-h]

Return package and executable information.

Miscellaneous options:
  -v, --verbose  Prints a more verbose runtime log
  -h, --help     Show this help message and exit
```

## Guided reassembly

`scarab reassemble --help` lists the integrated reassembly command. See the
[reassembly guide](reassembly.md) for inputs, resources, filtering, outputs and reruns.
