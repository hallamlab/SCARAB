# Installation

**Release preparation:** Anaconda and Quay publication and namespace configuration are pending. The source route is available for testing; registry commands apply once the release is published. Container testing is provided by the release-candidate workflow.

SCARAB supports Linux. All installation routes provide the same `scarab` CLI and use the dependency versions recorded in this repository. The supported runtime is Python 3.10; the scientific dependency versions are kept consistent across Python, Mamba, Conda recipes, and the container.

## 1. Released Mamba/Conda package

For a published release in the Hallam Lab channel:

```bash
mamba create -n scarab --strict-channel-priority \
  -c conda-forge -c bioconda -c hallamlab scarab=1.0.0
mamba activate scarab
scarab info
scarab recruit --help
```

The Conda package declares the Python libraries and external executables, including minimap2, SAMtools, MetaBAT's depth summarizer, and BBTools. No Git-based pip helper installation is required. Package availability follows release publication; a version prepared in a checkout is not automatically available on Anaconda. To test before publication, use the source route below and review the [release checklist](development.md).

Then follow the [same demo test](reviewer-test.md) used by all installation routes.

## 2. Docker

For a published image tag:

```bash
docker pull quay.io/hallamlab/scarab:1.0.0
docker run --rm quay.io/hallamlab/scarab:1.0.0 scarab info
```

Run the [Docker demo command](reviewer-test.md#docker) with your input directory mounted. Use a version tag or digest when recording a reproducible analysis. The Docker image installs the actual Python package; it does not depend on a source-directory `PYTHONPATH` wrapper.

To build this checkout locally:

```bash
docker build -t scarab:local .
docker run --rm scarab:local scarab recruit --help
```

`BASE_IMAGE` can be set to a pinned micromamba image digest for a release build. The build context allows only package source and installation files, excluding developer research directories and manuscript material.

## 3. Apptainer

A published Docker image can be converted once and moved to the cluster:

```bash
apptainer pull scarab.sif docker://quay.io/hallamlab/scarab:1.0.0
apptainer exec scarab.sif scarab info
```

Run the [Apptainer demo command](reviewer-test.md#apptainer). The SIF already contains SCARAB and its dependencies; an additional runtime Mamba environment is unnecessary. Build/pull on a machine with internet, then copy the SIF to an offline HPC filesystem.

For an unpublished locally built image:

```bash
docker save scarab:local -o scarab-image.tar
apptainer build scarab.sif docker-archive://scarab-image.tar
```

This uses the local image archive and does not require uploading it to Quay.

## 4. GitHub source installation

```bash
git clone https://github.com/hallamlab/SCARAB.git
cd SCARAB
mamba env create -f environment.yml
mamba activate scarab_cenv
python -m pip install --no-deps --no-build-isolation .
scarab info
scarab recruit --help
```

`environment.yml` supplies the pinned scientific Python packages and native tools. Pip installs SCARAB into that active environment. Installing with pip alone does not install external mapping and deduplication programs. `scarab_env.yml` is a generated compatibility copy of the same environment specification, not a different installation route.

Run the [demo test](reviewer-test.md), then proceed to [your own inputs](quickstart.md). Before updating a working checkout/environment, stop any runs that use it. Keep separate output directories for different scientific configurations.
