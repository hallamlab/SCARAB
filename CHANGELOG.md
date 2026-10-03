## [1.0.0] - Unreleased

- Align Python, Mamba, Conda, Docker, and Apptainer installation paths.
- Add a public Read the Docs guide and workflow diagrams.
- Validate recruitment inputs and apply manual clustering overrides.
- Make forced reruns preserve previous output and start fresh.
- Propagate mapping and deduplication failures instead of silently continuing.
- Preserve distinct paired reads and sample basenames; isolate mapping temporary files.
- Handle custom k-mer sizes, missing anchors, and noise-only clusters.
- Use a private temporary Numba cache for read-only installations and arbitrary container users.
- Bound the BBTools heap with `--dedupe_memory` (default 4g).
- Add a checksum-verified public reviewer demo and table/sequence consistency checks.
- Replace obsolete CI and automatic tag publication with explicit candidate builds.

## [0.0.1] - 2021

### Added

### Fixed

### Changed
