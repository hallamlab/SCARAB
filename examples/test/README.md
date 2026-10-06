# Tiny SCARAB workflow demo

This fixture showcases installation and execution of recruitment **and guided reassembly**. It is not an accuracy benchmark. Inputs are bundled in `demo/`; no separate download is needed.

With the SCARAB environment activated, start from the repository root:

```bash
cd examples/test/demo
scarab recruit -m k12.gold_assembly.fasta -l read_list.txt -s SAG -o SCARAB_out -t 4
scarab reassemble \
  -i SCARAB_out/algo_defaults/Default/xpgs/ecoli-COLI-K12.3578.intersect.xPG.fasta \
  -l read_list.txt -o reassembly -t 4 --memory 4
python ../../../scripts/validate_test.py --dataset . --output SCARAB_out --reassembly reassembly
```

Recruitment exercises MinHash anchors, read mapping for three paired libraries, coverage/composition features, automatic parameter selection, UMAP, HDBSCAN, OC-SVM, combined recruitment and xPG construction. Reassembly maps the same reads to the combined xPG, selects pairs, repairs/trims them, runs SPAdes with trusted contigs, and writes sequences, logs and a summary. The validator requires a completed assembly, not a skipped no-reads target.

The expected xPG path above uses the default recruitment settings. Use the output guide to locate results when changing parameters on your own data. The two output directories are ignored by Git. Repeating the commands reuses matching completed runs.

## Source and selection

The source is the [historical public E. coli K12 SCARAB demo](https://drive.google.com/file/d/1yUoPpoNRl6-CZHkRoUYDbikBJk4yC-3V/view). The full 55.7 MiB archive is not bundled. Its checksum and original file checksums remain in `tests/test/demo.json` as source provenance.

The tiny fixture contains the first 64 assembly contigs of at least 2 kb (403,315 bases), the first 150 kb of the first trusted scaffold from `ecoli-COLI-K12.3578.fasta`, and a small paired-read subset from each library. Minimap2 selects primary pairs with both mates mapped to the small assembly; every fourth eligible pair in original input order is retained. This leaves 3,021, 3,006 and 3,038 pairs in libraries A, B and C. Sequences and qualities are unchanged, except for the explicitly recorded trusted-scaffold truncation. FASTA line wrapping and gzip metadata are normalized.

This construction intentionally favors a small runnable technical example. Do not infer recruitment accuracy, genome completeness or biological performance from it. Archive provenance, builder version information, counts and bundled checksums are in `tests/test/bundled.json`.

Maintainers can regenerate the fixture with `scripts/build_test_subset.py --archive /path/to/demo.zip --output /new/destination`, using the recorded Minimap2 version in a SCARAB environment. Ordinary users only need the bundled inputs and the commands above.
