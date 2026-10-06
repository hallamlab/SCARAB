#!/usr/bin/env python3
"""Copy the checksum-verified bundled SCARAB demo to a fresh working directory."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def prepare(output):
    root = Path(__file__).resolve().parents[1]
    source = root/'examples/test/demo'
    manifest = json.loads((root/'tests/test/bundled.json').read_text())
    output = output.expanduser().resolve()/'demo'
    if output.exists():
        raise ValueError(f'{output} already exists; choose a fresh destination')
    for name, expected in manifest['files'].items():
        if hashlib.sha256((source/name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Bundled input checksum mismatch: {name}')
    for name in manifest['files']:
        target = output/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source/name, target)
    print(f'Verified and copied bundled demo: {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    prepare(args.output)
