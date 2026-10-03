# Packaging, validation, and releases

## One dependency definition

`requirements.txt` defines Python runtime requirements. `packaging/runtime.json` defines the supported Python version and external bioinformatics tools. `scripts/render_packaging.py` generates `environment.yml`, its compatibility alias `scarab_env.yml`, and both Conda recipes from those sources.

```bash
python scripts/render_packaging.py
python scripts/render_packaging.py --check
```

The setuptools upper bound preserves `pkg_resources`, used by the supported UMAP version. Do not remove it without updating and validating that dependency. Scientific versions are preserved rather than silently upgrading algorithms during a packaging refresh.

## Validate this checkout

In the source installation environment:

```bash
python -m unittest discover -s tests -p 'test_*.py'
python scripts/render_packaging.py --check
scarab info
```

The regression tests exercise input validation, effective parameter overrides, safe reruns, read-name collisions, similarity thresholds, external-tool failure propagation, and unanchored/noise behavior. They are not a replacement for a representative biological reviewer run.

## Build a local Conda package

```bash
mamba create -n scarab-build -c conda-forge python=3.11 conda-build conda-index python-build
mamba run -n scarab-build conda build conda-recipe-local \
  --override-channels -c conda-forge -c bioconda --no-anaconda-upload --output-folder "$PWD/dist/conda"
mamba run -n scarab-build conda index "$PWD/dist/conda"
mamba create -n scarab-package-test --strict-channel-priority \
  -c "file://$PWD/dist/conda" -c conda-forge -c bioconda scarab=1.0.0
mamba run -n scarab-package-test scarab info
mamba run -n scarab-package-test scarab recruit --help
```

The local recipe builds the working tree. The release recipe uses the matching version tag from GitHub. No package upload happens during these commands.

## Python artifacts

```bash
mamba run -n scarab-build python -m build
python scripts/check_artifacts.py dist
```

The artifact check requires the runtime parameter tables, rejects manuscript/developer directories, and verifies the wheel's version and CLI entry point. The package version comes from `src/scarab/__init__.py`. Preserve the configuration tables under `src/scarab/configs`: those are required runtime reference assets, not manuscript supplements.

## Configure publishing once

Create or confirm the **hallamlab** upload destination on [Anaconda.org](https://anaconda.org/) and the public **hallamlab/scarab** repository on [Quay](https://quay.io/). Package hosting on Anaconda.org is separate from Anaconda's paid package-access products. Anaconda upload credentials need permission to publish in the chosen organization.

For Quay, create a [robot account](https://docs.quay.io/glossary/robot-accounts.html), such as `hallamlab+scarab`, and grant it **Write** permission on `hallamlab/scarab`. Use the robot's token for automation.

In **hallamlab/SCARAB → Settings → Environments**, create an environment named **release**. Add these environment secrets there (repository Actions secrets also work):

| Secret | Value |
|---|---|
| `ANACONDA_API_TOKEN` | Anaconda.org upload token authorized for the destination organization. |
| `QUAY_USERNAME` | Quay robot username, for example `hallamlab+scarab`. |
| `QUAY_PASSWORD` | That robot's token. |

Configure a required reviewer on the `release` environment if you want a human approval before publication. Never put tokens in configuration files, issues, or source control.

The workflow defaults to Anaconda owner `hallamlab` and image repository `quay.io/hallamlab/scarab`. Optional GitHub Actions variables `ANACONDA_OWNER` and `QUAY_REPOSITORY` override those destinations; update the public installation instructions if you change them. No Quay source-build trigger is required: GitHub Actions builds, tests, and pushes the image.

## Build candidates without publishing

The **Build and validate release candidates** workflow runs automatically for container/build-configuration changes on `docs/user-guide`. It can also be run manually after its workflow file is present on the repository's default branch. Leave **publish** unchecked.

It builds/tests the Conda package, runs regression tests and the public demo in Docker, converts that same image to an Apptainer SIF, and runs the demo again in Apptainer. Both container runs use the same result validator as the source route. Packages, the Docker archive, the SIF, checksums, and reviewer logs are retained as workflow artifacts for seven days. Build-only runs need no registry credentials.

The ordinary test workflow separately exercises the source install, unit tests, public reviewer demo, and documentation. The Python artifact workflow verifies source/wheel contents.

## Publish an approved release

1. Review the tests and merge the approved changes into the production branch.
2. Create the matching version tag (for version 1.0.0, `v1.0.0`).
3. In **Actions → Build and validate release candidates → Run workflow**, select that tag and check **publish**.
4. The workflow rebuilds and validates the artifacts. The publication job runs only after both Conda and container checks succeed and any configured `release` environment approval is granted.
5. It verifies checksums and the Docker source/version labels, then uploads the Conda package and pushes the tested versioned image to Quay.
6. Verify clean installations from both registries before announcing availability. Enable the corresponding Read the Docs version; create a GitHub release and use Zenodo integration separately when ready.

The release guard rejects publication from a branch, a mismatched tag, or a different repository. Ordinary pushes and build-only runs do not publish, create tags, merge code, or create GitHub releases. No `latest` image tag is changed. If one registry upload fails after the other succeeds, inspect the existing artifact before retrying; the workflow does not force-overwrite Conda packages.

The local Conda recipe uses the checkout. The release recipe uses the matching version tag and cannot be used until that tag exists.
