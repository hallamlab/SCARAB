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

The **Build and validate release candidates** workflow runs automatically for container/build-configuration changes on `docs/user-guide`. It can also be run manually after its workflow file is present on the repository's default branch. Leave **publish_anaconda** and **publish_quay** unchecked.

It builds/tests the Conda package, installs that package into a fresh Mamba environment and runs the complete recruitment-and-reassembly demo. It also runs regression tests and the same demo in Docker, converts that image to an Apptainer SIF, and runs the demo again in Apptainer. Both container runs use the same result validator as the source route. Packages, the Docker archive, the SIF, checksums, and reviewer logs are retained as workflow artifacts for seven days. Build-only runs need no registry credentials.

The ordinary test workflow separately exercises the source install, unit tests, public reviewer demo, and documentation. The Python artifact workflow verifies source/wheel contents.

## Publish an approved release

1. Review the tests and merge the approved changes into the production branch.
2. Create the matching version tag (for version 1.0.0, `v1.0.0`).
3. In **Actions → Build and validate release candidates → Run workflow**, select that tag and check **publish_anaconda**, **publish_quay**, or both.
4. The workflow rebuilds and validates the artifacts. Each publication job runs after its corresponding artifact checks succeed and any configured `release` environment approval is granted.
5. It verifies checksums and the Docker source/version labels, then uploads the Conda package and pushes the tested versioned image to Quay.
6. The `verify_anaconda` and `verify_quay` jobs download the public artifacts without registry credentials and run recruitment plus guided reassembly. Confirm these clean-install checks pass before announcing availability. Enable the corresponding Read the Docs version; create a GitHub release and use Zenodo integration separately when ready.

The release guard rejects publication from a branch, a mismatched tag, or a different repository. Ordinary pushes and build-only runs do not publish, create tags, merge code, or create GitHub releases. No `latest` image tag is changed. Anaconda and Quay use independent publishing jobs. Use **Re-run failed jobs** to retry the failed upload using the original tested artifacts while they remain available (seven days), without rebuilding or repeating the successful registry upload. Do not use **Re-run all jobs** for an upload retry. If an upload completed before its job failed, inspect the registry before retrying; the workflow does not force-overwrite Conda packages.

The local Conda recipe uses the checkout. The release recipe uses the matching version tag and cannot be used until that tag exists.

## Shared controls with MetaPathways

Both repositories use manual `publish_anaconda` and `publish_quay` selections,
defaulting to false. Neither ordinary pushes nor selecting a version tag alone
publishes packages. The credentials have identical names: `ANACONDA_API_TOKEN`,
`QUAY_USERNAME`, and `QUAY_PASSWORD`. Store them in the `release` environment
or repository Actions secrets. No persistent `PUBLISH_*` variables are needed.

Optional `ANACONDA_OWNER` and `QUAY_REPOSITORY` variables only change the
destination. Defaults are `hallamlab` and `quay.io/hallamlab/scarab`.
MetaPathways additionally supports explicit GitHub release publication and
recovery of older tagged artifacts; SCARAB does not create GitHub releases or
Zenodo records through this workflow.

## Manual Zenodo archiving

Keep the SCARAB and MetaPathways switches **off** in
[Zenodo's GitHub settings](https://zenodo.org/account/settings/github/).
This account-side setting prevents automatic deposits on GitHub release
publication; GitHub workflow checkboxes cannot disable an existing integration.
Neither project's release workflow calls the Zenodo API or requires a Zenodo
secret.

For an approved release, manually upload the tested source archive through
Zenodo's dashboard. If the software already has a record, use **New version**
to retain its concept DOI. Review creators, affiliations, version, license,
and the exact GitHub tag link before publishing the draft. Do not infer authors
or affiliations from commit contributors. Correct existing creator metadata
with **Edit**, without making a new software version solely for that correction.

Release validation requires `CITATION.cff` with explicit, nonduplicate author
names and a version matching the package. An overriding `.zenodo.json` is
rejected so there is only one citation metadata source. The current two-author
list is provisional and must be reviewed against the manuscript before archiving.
