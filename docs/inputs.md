# Input files

| Input | Argument | Format and meaning |
|---|---|---|
| Metagenome assembly | `-m`, `--metag` | Nucleotide FASTA; assembled contigs with unique identifiers. |
| Read manifest | `-l`, `--metaraw` | Plain text, no header; one interleaved FASTQ path or two tab-separated paired FASTQ paths per row. |
| Trusted genomes | `-s`, `--trusted-contigs` | Optional FASTA file or a directory of trusted FASTAs. |
| Output directory | `-o`, `--output-dir` | Dedicated directory for one assembly and one analysis configuration. |

## Read lists

Each paired row must have R1 first and R2 second, separated by a literal tab. Do not add sample IDs as another column or use comma-separated input. Avoid blank rows and comments. Use unique read-file basenames: mapping IDs preserve periods and remove the FASTQ/compression extensions. Duplicate resulting basenames are rejected before mapping, even if the reads are in different directories.

PacBio HiFi input uses `--pacbio` with a single FASTQ path per row. The implementation selects minimap2 `map-hifi` for that single-file mode; paired-file rows use the short-read mapping path. Do not describe `--pacbio` as a generic mode for every long-read platform.

## Trusted references

For directory input the current discovery code accepts lowercase `.fasta`, `.fna`, and `.fa`. Use plain FASTA files with distinct basenames. Directory discovery does not include `.fasta.gz`. Reference quality affects anchor quality; remove contamination and record the origin of each reference.

## Contig tiling

By default, contigs shorter than 2,000 bp are excluded before contig tiling. Longer sequences are divided into contig tiles up to 10,000 bp with 2,000 bp overlap. Clustering uses contig tiles and final sequence products return to original contig identifiers. Keep identifiers unique and stable across your analysis.

For containers, every manifest path must exist **inside the container**. Bind the data directory at the same absolute path when using absolute read lists, or launch from a mounted working directory when using relative lists.
