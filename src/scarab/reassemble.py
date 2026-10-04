"""Guided short-read reassembly of trusted/recruited genome FASTAs."""
import argparse
import csv
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import shlex
import hashlib

from scarab.validation import run_guard


def positive(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError('must be a positive integer')
    return number


def parse_inputs(args):
    source = Path(args.input).expanduser().resolve()
    refs = sorted(p for p in source.iterdir() if p.suffix.lower() in ('.fa', '.fna', '.fasta')) if source.is_dir() else [source]
    if not refs:
        raise ValueError('No FASTA inputs found; pass an xpgs directory or one FASTA')
    names = set()
    for ref in refs:
        if not ref.is_file() or ref.stat().st_size == 0:
            raise ValueError(f'Missing or empty FASTA: {ref}')
        if ref.stem in names:
            raise ValueError(f'Duplicate FASTA basename: {ref.stem}')
        names.add(ref.stem)
        with ref.open() as handle:
            if not handle.readline().startswith('>'):
                raise ValueError(f'Expected an uncompressed FASTA: {ref}')
    manifest = Path(args.reads).expanduser().resolve()
    rows = []
    for number, line in enumerate(manifest.read_text().splitlines(), 1):
        fields = line.split('\t')
        if len(fields) not in (1, 2) or any(not x.strip() for x in fields):
            raise ValueError(f'Read-list row {number}: expected interleaved FASTQ or tab-separated R1 and R2')
        reads = [Path(x).expanduser().resolve() for x in fields]
        if len(reads) == 2 and reads[0] == reads[1]:
            raise ValueError('R1 and R2 must be different files')
        for read in reads:
            if not read.is_file() or read.stat().st_size == 0:
                raise ValueError(f'Missing or empty FASTQ: {read}')
        rows.append(reads)
    if not rows:
        raise ValueError('Read list is empty')
    paths = refs + [manifest] + [r for reads in rows for r in reads]
    output = Path(args.save_path).expanduser().absolute()
    if output.is_symlink():
        raise ValueError('Output must not be a symlink')
    output = output.resolve()
    if output == Path.home() or output == Path.cwd() or output in Path.cwd().parents:
        raise ValueError('Choose a dedicated output directory')
    if any(p == output or output in p.parents for p in paths):
        raise ValueError('Keep input FASTAs and reads outside the output directory')
    args.input, args.reads, args.save_path = str(source), str(manifest), str(output)
    return refs, rows, paths


def tools_and_adapters(args):
    tools = {}
    for name in ('minimap2', 'samtools', 'reformat.sh', 'repair.sh', 'bbduk.sh', 'spades.py'):
        tools[name] = shutil.which(name)
        if not tools[name]:
            raise ValueError(f'Missing executable {name}; install the SCARAB environment including SPAdes')
    adapters = Path(args.adapters).expanduser().resolve() if args.adapters else Path(tools['bbduk.sh']).resolve().parent / 'resources/adapters.fa'
    if not adapters.is_file() or not adapters.stat().st_size:
        raise ValueError('Cannot locate BBTools adapters.fa; supply --adapters PATH')
    args.adapters = str(adapters)
    return tools, adapters


def run(command, log, stdout=None):
    command = list(map(str, command))
    print('Command: ' + shlex.join(command), flush=True)
    with log.open('ab') as handle:
        handle.write(('\nCommand: ' + shlex.join(command) + '\n').encode())
        handle.flush()
        if stdout:
            with stdout.open('wb') as out:
                subprocess.run(command, stdout=out, stderr=handle, check=True)
        else:
            subprocess.run(command, stdout=handle, stderr=subprocess.STDOUT, check=True)


def fastq_records(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt') as handle:
        while True:
            header = handle.readline()
            if not header:
                return
            seq, plus, quality = handle.readline(), handle.readline(), handle.readline()
            if not header.startswith('@') or not plus.startswith('+') or len(seq.rstrip()) != len(quality.rstrip()) or not seq.strip():
                raise ValueError(f'Invalid or incomplete FASTQ record in {path}')
            name = header[1:].split()[0]
            yield name.removesuffix('/1').removesuffix('/2')


def paired_count(first, second):
    from itertools import zip_longest
    count = 0
    for a, b in zip_longest(fastq_records(first), fastq_records(second)):
        if a is None or b is None or a != b:
            raise ValueError('Extracted FASTQs have unmatched or out-of-order pairs')
        count += 1
    return count


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def reassemble_one(ref, rows, output, args, tools):
    dest = output / ref.stem
    receipt = dest / 'reassembly.json'
    if receipt.exists():
        record = json.loads(receipt.read_text())
        products = [dest / x for x in record.get('products', [])]
        if record.get('state', '').startswith('skipped_') or (record.get('state') == 'complete' and products and all(p.is_file() and p.stat().st_size and digest(p) == record.get('sha256', {}).get(p.name) for p in products)):
            print(f'{ref.stem}: reusing completed result', flush=True)
            return record
        raise ValueError(f'Incomplete result in {dest}; choose a fresh output or --force')
    print(f'{ref.stem}: reassembly logs and products: {dest}', flush=True)
    dest.mkdir(parents=True, exist_ok=True)
    work = dest / 'work'
    work.mkdir()
    log = dest / 'commands.log'
    threads = args.nthreads
    # samtools -@ requests additional workers; the main thread counts too.
    extra = max(0, threads - 1)
    heap = f'-Xmx{min(4, args.memory)}g'
    counts = []
    cleaned = []
    for index, reads in enumerate(rows, 1):
        lib = work / f'library-{index:04d}'
        lib.mkdir()
        if len(reads) == 1:
            r1, r2 = lib/'input.R1.fastq.gz', lib/'input.R2.fastq.gz'
            run([tools['reformat.sh'],heap,'-Xms128m',f'in={reads[0]}','interleaved=t',f'out1={r1}',f'out2={r2}',f'threads={threads}'],log)
            reads = [r1, r2]
        sam, bam = lib/'mapped.sam', lib/'mapped.bam'
        run([tools['minimap2'],'-ax','sr','-t',threads,ref,*reads],log,stdout=sam)
        # Keep primary paired alignments with BOTH mates mapped, matching the
        # original guided-reassembly selection. Drop secondary/supplementary hits.
        run([tools['samtools'],'view','-@',extra,'-b','-f','1','-F','2316','-o',bam,sam],log)
        sam.unlink()
        sorted_bam = lib/'names.bam'
        run([tools['samtools'],'sort','-n','-@',extra,'-m','256M','-o',sorted_bam,bam],log)
        bam.unlink()
        r1, r2 = lib/'mapped.R1.fastq', lib/'mapped.R2.fastq'
        run([tools['samtools'],'fastq','-@',extra,'-n','-1',r1,'-2',r2,'-0',os.devnull,'-s',lib/'singletons.fastq',sorted_bam],log)
        sorted_bam.unlink()
        mapped = paired_count(r1,r2)
        if not mapped:
            counts.append(dict(library=index,mapped_pairs=0,clean_pairs=0))
            continue
        p1,p2 = lib/'paired.R1.fastq.gz',lib/'paired.R2.fastq.gz'
        run([tools['repair.sh'],heap,'-Xms128m',f'in={r1}',f'in2={r2}',f'out={p1}',f'out2={p2}','repair=t','qin=33',f'threads={threads}'],log)
        q1,q2 = lib/'clean.R1.fastq.gz',lib/'clean.R2.fastq.gz'
        run([tools['bbduk.sh'],heap,'-Xms128m',f'in1={p1}',f'in2={p2}',f'out1={q1}',f'out2={q2}',f'ref={args.adapters}',
             'ktrim=r','k=23','mink=11','hdist=1','tpe=t','tbo=t','qtrim=rl','trimq=10','minlen=75',f'threads={threads}'],log)
        clean = paired_count(q1,q2)
        counts.append(dict(library=index,mapped_pairs=mapped,clean_pairs=clean))
        if clean:
            cleaned.append((q1,q2))
    record = dict(reference=str(ref),libraries=counts,products=[])
    if not cleaned:
        record['state'] = 'skipped_no_usable_pairs'
    else:
        # Concatenated gzip members retain paired ordering. Libraries were
        # collated independently so repeated read names cannot cross libraries.
        combined = [work/'reads.R1.fastq.gz',work/'reads.R2.fastq.gz']
        for mate,target in enumerate(combined):
            with target.open('wb') as handle:
                for pair in cleaned:
                    with pair[mate].open('rb') as source:
                        shutil.copyfileobj(source,handle)
        assembly = work/'spades'
        run([tools['spades.py'],'--isolate','--trusted-contigs',ref,'-1',combined[0],'-2',combined[1],'-t',threads,'-m',args.memory,'-o',assembly],log)
        for name in ('contigs.fasta','scaffolds.fasta'):
            product = assembly/name
            if not product.is_file() or product.stat().st_size == 0:
                raise ValueError(f'SPAdes did not produce nonempty {product}; see {log}')
            shutil.copy2(product,dest/name)
            record['products'].append(name)
        if (assembly/'spades.log').is_file():
            shutil.copy2(assembly/'spades.log',dest/'spades.log')
        record['sha256'] = {name: digest(dest/name) for name in record['products']}
        record['state'] = 'complete'
    temp=receipt.with_suffix('.tmp')
    temp.write_text(json.dumps(record,indent=2)+'\n')
    temp.replace(receipt)
    if not args.keep_intermediates:
        shutil.rmtree(work)
    print(f'{ref.stem}: {record["state"]}',flush=True)
    return record


def reassemble(argv):
    parser = argparse.ArgumentParser(prog='scarab reassemble', description=__doc__)
    parser.add_argument('-i','--input',required=True,help='One uncompressed FASTA or directory of xPG/genome FASTAs')
    parser.add_argument('-l','--reads','--metaraw',required=True,help='Same short-read manifest format as recruit; R1 TAB R2 or interleaved FASTQ')
    parser.add_argument('-o','--output-dir',dest='save_path',required=True)
    parser.add_argument('-t','--threads','--num_threads',dest='nthreads',type=positive,default=1)
    parser.add_argument('--memory',type=positive,default=16,help='SPAdes memory limit in GB (default: 16); BBTools heap capped at 4 GB')
    parser.add_argument('--adapters',help='Adapter FASTA; defaults to resources/adapters.fa beside BBTools')
    parser.add_argument('--keep-intermediates',action='store_true')
    parser.add_argument('--force',action='store_true',help='Preserve previous output as a sibling backup and start fresh')
    args = parser.parse_args(argv)
    try:
        refs, rows, paths = parse_inputs(args)
        tools, adapters = tools_and_adapters(args)
        if Path(args.save_path) in adapters.parents:
            raise ValueError('Keep the adapter FASTA outside the output directory')
        # Include command identity and resolved tool paths in checkpoint settings.
        args.command='reassemble'
        args.tools=tools
        with run_guard(args,paths+[adapters]):
            output=Path(args.save_path)
            records=[reassemble_one(ref,rows,output,args,tools) for ref in refs]
            with (output/'reassembly_summary.tsv').open('w') as handle:
                writer=csv.writer(handle,delimiter='\t')
                writer.writerow(['genome','status','mapped_pairs','clean_pairs','contigs','scaffolds'])
                for ref,record in zip(refs,records):
                    writer.writerow([ref.stem,record['state'],sum(x['mapped_pairs'] for x in record['libraries']),sum(x['clean_pairs'] for x in record['libraries']),
                                     str(output/ref.stem/'contigs.fasta') if record['products'] else '',str(output/ref.stem/'scaffolds.fasta') if record['products'] else ''])
    except (OSError,ValueError,RuntimeError,subprocess.CalledProcessError) as exc:
        parser.exit(1,f'SCARAB reassembly: {exc}\n')
