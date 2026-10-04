#!/usr/bin/env python3
"""Validate candidate metadata and require a matching tag for publication."""
import os
from pathlib import Path
import re


def validate(version, publish=False, ref_type='', ref_name='', repository='', event='workflow_dispatch'):
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('Expected a three-part release version')
    if publish:
        if event != 'workflow_dispatch':
            raise ValueError('Publication requires a manual workflow dispatch')
        if repository.lower() != 'hallamlab/scarab':
            raise ValueError('Publication is restricted to hallamlab/SCARAB')
        if ref_type != 'tag' or ref_name != 'v' + version:
            raise ValueError(f'Publication requires selecting existing tag v{version}; branches build only')
    return version


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    match = re.search(r'^version = "([^"]+)"', (root/'src/scarab/__init__.py').read_text(), re.M)
    if not match:
        raise SystemExit('Cannot read SCARAB version')
    requested = os.environ.get('PUBLISH_REQUESTED', 'false').lower()
    if requested not in ('true', 'false'):
        raise SystemExit('PUBLISH_REQUESTED must be true or false')
    version = validate(match[1], requested == 'true', os.environ.get('GITHUB_REF_TYPE', ''),
                       os.environ.get('GITHUB_REF_NAME', ''), os.environ.get('GITHUB_REPOSITORY', ''), os.environ.get('GITHUB_EVENT_NAME', ''))
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as handle:
            handle.write(f'version={version}\n')
    print(f'SCARAB {version}: ' + ('publication requested for matching tag' if requested == 'true' else 'build and test only'))
