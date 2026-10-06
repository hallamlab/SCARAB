#!/usr/bin/env python3
"""Validate relationships and products from the default public demo run."""
import argparse
import csv
import hashlib
import json
from pathlib import Path


def fasta(path):
    records = {}
    name = None
    for line in path.read_text().splitlines():
        if line.startswith('>'):
            name = line[1:].split()[0]
            assert name not in records, f'Duplicate FASTA identifier: {path}: {name}'
            records[name] = ''
        elif line.strip():
            assert name is not None, f'Invalid FASTA: {path}'
            records[name] += line.strip()
    assert records and all(records.values()), f'Empty FASTA: {path}'
    return records


def table(path):
    with path.open() as handle:
        return list(csv.DictReader(handle, delimiter='\t'))


def validate(dataset, output, reassembly):
    provenance = json.loads((Path(__file__).parent.parent/'tests/test/bundled.json').read_text())
    for name, checksum in provenance['files'].items():
        assert hashlib.sha256((dataset/name).read_bytes()).hexdigest() == checksum, f'Demo input changed: {name}'
    assert json.loads((output/'scarab_status.json').read_text())['state'] == 'complete', 'Run is incomplete'
    run = json.loads((output/'scarab_run.json').read_text())
    assert run['settings']['trust_path'], 'Expected an anchored demo run'
    assembly = fasta(dataset/'k12.gold_assembly.fasta')
    subcontigs = fasta(output/'k12.gold_assembly.subcontigs.fasta')
    coverage = table(output/'k12.gold_assembly.mbacov.tsv')
    assert {r['contigName'] for r in coverage} == set(subcontigs), 'Coverage/subcontig mismatch'
    libraries = [f'k12_{letter}_R1.sorted.bam' for letter in 'ABC']
    assert {k for k in coverage[0] if k.endswith('.bam')} == set(libraries), 'Expected all three read libraries'
    for library in libraries:
        assert any(float(r[library]) > 0 for r in coverage), f'No coverage from {library}'
    roots = list(output.glob('*/*/k12.gold_assembly.denovo_clusters.tsv'))
    assert len(roots) == 1, 'Expected one clustering result set'
    root = roots[0].parent
    expected_trusted = {p.stem for p in (dataset/'SAG').glob('*.fasta')}
    n_products = 0
    for suffix, folder, extension in [('denovo','denovo','denovo'), ('hdbscan','hdbscan','hdbscan'), ('ocsvm','ocsvm','ocsvm'), ('inter','intersect','intersect')]:
        rows = table(root/f'k12.gold_assembly.{suffix}_clusters.tsv')
        assert rows, f'No assignments from {suffix}'
        grouped = {}
        for row in rows:
            assert row['contig_id'] in assembly, f'Unknown contig in {suffix}'
            assert row['best_label'] != '-1', 'Noise was exported as a bin'
            grouped.setdefault(row['best_label'], set()).add(row['contig_id'])
        if suffix != 'denovo':
            assert set(grouped) == expected_trusted, f'Missing trusted genome in {suffix}'
        for label, identifiers in grouped.items():
            records = fasta(root/folder/f'{label}.{extension}.fasta')
            assert set(records) == identifiers, f'Table/FASTA mismatch: {label}/{suffix}'
            assert all(sequence == assembly[name] for name, sequence in records.items()), 'Recruited sequence changed'
            n_products += 1
            if suffix != 'denovo':
                trusted = fasta(dataset/'SAG'/f'{label}.fasta')
                xpg = fasta(root/'xpgs'/f'{label}.{extension}.xPG.fasta')
                allowed = {**trusted, **records}
                assert set(xpg) <= set(allowed), 'Unknown sequence in xPG'
                assert all(sequence == allowed[name] for name, sequence in xpg.items()), 'xPG sequence changed'
                n_products += 1
    assert json.loads((reassembly/'scarab_status.json').read_text())['state'] == 'complete', 'Reassembly incomplete'
    summaries = table(reassembly/'reassembly_summary.tsv')
    assert len(summaries) == 1, 'Expected one guided assembly target'
    receipts = list(reassembly.glob('*/reassembly.json'))
    assert len(receipts) == 1, 'Missing reassembly receipt'
    receipt = json.loads(receipts[0].read_text())
    assert receipt['state'] == 'complete', 'Guided assembly must run, not skip for lack of reads'
    assert len(receipt['libraries']) == 3 and all(x['clean_pairs'] > 0 for x in receipt['libraries']), 'Each library must contribute usable pairs'
    fasta(receipts[0].parent/'contigs.fasta')
    fasta(receipts[0].parent/'scaffolds.fasta')
    assert not (receipts[0].parent/'work').exists(), 'Successful default reassembly should remove intermediates'
    print(f'All test checks passed: 3 paired-read libraries, {len(expected_trusted)} trusted genome, {n_products} recruitment FASTA products, and completed guided assembly.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reassembly', type=Path, required=True)
    args = parser.parse_args()
    validate(args.dataset, args.output, args.reassembly)
