# Troubleshooting

| Symptom | Check |
|---|---|
| Missing minimap2, samtools, depth-summary tool, or dedupe.sh | Activate the complete Mamba environment or use the container. Pip alone does not install these executables. |
| Python import/ABI error | Use the supported environment specification; do not mix incompatible NumPy, pandas, SciPy, HDBSCAN, or Python builds. |
| Reads not found | Inspect each manifest row from the launch directory or container; paired paths require a literal tab. |
| Different samples overwrite mapping files | Use distinct read basenames; duplicates are rejected before analysis. |
| Trusted references are not discovered | Check accepted filename extensions and that the files are nonempty. |
| No anchored bins | Inspect reference matches and retained sequence lengths; no supported anchors need not mean a successful genome recovery. |
| Changed settings seem ignored | Check logged effective parameters. Use a new output or `--force` for changed settings; incomplete runs cannot silently reuse partial files. |
| Memory exhaustion | Reduce workload/window count or request more memory; `-t` does not cap RAM. |

Report a reproducible problem at [GitHub](https://github.com/hallamlab/SCARAB/issues). Include `scarab info`, installation route, software revision or image tag, the exact command, relevant log lines, and a minimal non-sensitive input example. Do not post credentials or private study data.
