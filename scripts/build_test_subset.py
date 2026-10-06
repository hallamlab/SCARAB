#!/usr/bin/env python3
"""Build the tiny SCARAB workflow fixture from the original public demo."""
import argparse
from contextlib import ExitStack
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def fasta_records(text):
    name, sequence = None, []
    for line in text.splitlines():
        if line.startswith('>'):
            if name is not None: yield name, ''.join(sequence)
            name, sequence = line[1:].split()[0], []
        else: sequence.append(line.strip())
    if name is not None: yield name, ''.join(sequence)


def write_fasta(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(f'>{name}\n'+ '\n'.join(seq[i:i+80] for i in range(0,len(seq),80))+'\n' for name,seq in records))


def build(archive, output):
    original = json.loads((ROOT/'tests/test/demo.json').read_text())
    if hashlib.sha256(archive.read_bytes()).hexdigest() != original['archive_sha256']:
        raise ValueError('Original demo archive checksum mismatch')
    if output.exists(): raise ValueError('Choose a new output directory')
    output.mkdir(parents=True)
    counts = {}
    with zipfile.ZipFile(archive) as source, tempfile.TemporaryDirectory(prefix='scarab-demo-build-') as temporary:
        tmp = Path(temporary)
        assembly = [(name,seq) for name,seq in fasta_records(source.read('demo/k12.gold_assembly.fasta').decode()) if len(seq)>=2000][:64]
        write_fasta(output/'k12.gold_assembly.fasta',assembly)
        trusted_name, trusted_seq = next(fasta_records(source.read('demo/SAG/ecoli-COLI-K12.3578.fasta').decode()))
        write_fasta(output/'SAG/ecoli-COLI-K12.3578.fasta',[(trusted_name+'|demo_first_150000',trusted_seq[:150000])])
        for library in 'ABC':
            names = [f'fastq/k12_{library}_R{mate}.fastq.gz' for mate in (1,2)]
            paths=[]
            for name in names:
                target=tmp/Path(name).name;target.write_bytes(source.read('demo/'+name));paths.append(target)
            sam=tmp/'mapped.sam'
            with sam.open('w') as handle:
                subprocess.run(['minimap2','-ax','sr','-t','2',str(output/'k12.gold_assembly.fasta'),*map(str,paths)],stdout=handle,check=True)
            mapped=set()
            with sam.open() as handle:
                for line in handle:
                    if line.startswith('@'):continue
                    fields=line.split('\t');flag=int(fields[1])
                    if flag & 1 and not flag & 2316: mapped.add(fields[0])
            with ExitStack() as stack:
                readers=[stack.enter_context(gzip.open(path,'rb')) for path in paths]
                writers=[]
                for name in names:
                    target=output/name;target.parent.mkdir(exist_ok=True)
                    raw=stack.enter_context(target.open('wb'))
                    writers.append(stack.enter_context(gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0)))
                total=eligible=kept=0
                while True:
                    pair=[[f.readline() for _ in range(4)] for f in readers]
                    if not pair[0][0] and not pair[1][0]:break
                    for read in pair:
                        if not all(read) or not read[0].startswith(b'@') or not read[2].startswith(b'+') or len(read[1].strip())!=len(read[3].strip()):raise ValueError('Malformed paired FASTQ')
                    ids=[r[0].split()[0].removeprefix(b'@').removesuffix(b'/1').removesuffix(b'/2').decode() for r in pair]
                    if ids[0]!=ids[1]:raise ValueError('Mismatched FASTQ mates')
                    if ids[0] in mapped:
                        if eligible % 4 == 0:
                            for f,read in zip(writers,pair):f.writelines(read)
                            kept+=1
                        eligible+=1
                    total+=1
                counts[library]=dict(source_pairs=total,mapped_pairs=eligible,retained_pairs=kept)
    (output/'read_list.txt').write_text(''.join(f'fastq/k12_{x}_R1.fastq.gz\tfastq/k12_{x}_R2.fastq.gz\n' for x in 'ABC'))
    manifest=dict(source=original['source'],archive_sha256=original['archive_sha256'],
                  description='Technical demonstration only: first 64 assembly contigs >=2 kb; first 150 kb of the first .3578 trusted scaffold; every fourth primary pair mapping both mates to the subset, in source order. Reads and qualities unchanged. Not an accuracy benchmark.',
                  minimap2_version=subprocess.check_output(['minimap2','--version'],text=True).strip(),
                  assembly_contigs=len(assembly),assembly_bases=sum(len(s) for _,s in assembly),trusted_bases=150000,libraries=counts,
                  files={str(p.relative_to(output)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.rglob('*')) if p.is_file()})
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();build(args.archive,args.output)
