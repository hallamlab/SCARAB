#!/usr/bin/env python3
"""Keep Mamba and Conda dependencies aligned with the Python package."""
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def render():
    runtime=json.loads((ROOT/'packaging/runtime.json').read_text())
    version=re.search(r'^version = "([^"]+)"', (ROOT/'src/scarab/__init__.py').read_text(),re.M)[1]
    requirements=[s.strip() for s in (ROOT/'requirements.txt').read_text().splitlines() if s.strip() and not s.startswith('#')]
    deps=['python='+runtime['python'], 'pip', 'wheel']+[s.replace('==','=') for s in requirements]+runtime['tools']
    env='name: scarab_cenv\nchannels:\n  - conda-forge\n  - bioconda\ndependencies:\n'+''.join('  - '+s+'\n' for s in deps)
    files={'environment.yml':env,'scarab_env.yml':env}
    for folder,source in [('conda-recipe-local','  path: ..'),('conda-recipe',f'  git_url: https://github.com/hallamlab/SCARAB.git\n  git_rev: v{version}')]:
        run=['python >=3.10,<3.11']+[s.replace('==',' ') for s in requirements]+[s.replace('=',' ') for s in runtime['tools']]
        files[folder+'/meta.yaml']=f'''package:
  name: scarab
  version: {version}
source:
{source}
build:
  noarch: python
  number: 0
  script: "{{{{ PYTHON }}}} -m pip install . --no-deps --no-build-isolation -vv"
requirements:
  host:
    - python 3.10
    - pip
    - setuptools >=68,<81
    - wheel
  run:
'''+''.join('    - '+s+'\n' for s in run)+'''test:
  imports:
    - scarab.commands
    - scarab.utilities
    - scarab.clusterer
  commands:
    - scarab info
    - scarab recruit --help
    - minimap2 --version
    - samtools --version
    - command -v jgi_summarize_bam_contig_depths
    - command -v dedupe.sh
about:
  home: https://github.com/hallamlab/SCARAB
  license: GPL-3.0-only
  license_file: LICENSE
  summary: Genome-guided recruitment of metagenomic contigs and extended partial genomes.
extra:
  recipe-maintainers:
    - RyloByte
'''
    return files
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    for name,text in render().items():
        path=ROOT/name
        if args.check:
            if not path.exists() or path.read_text()!=text: raise SystemExit('Stale packaging file: '+name)
        else:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
