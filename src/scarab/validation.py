"""Validate public recruitment inputs before creating output or importing tools."""
import json
import os
from pathlib import Path
import uuid


def read_id(filename):
    name = Path(filename).name
    if name.endswith('.gz'):
        name = name[:-3]
    return os.path.splitext(name)[0]


def validate_inputs(args):
    paths = [Path(args.mg_file).expanduser().resolve(), Path(args.mg_raw_file_list).expanduser().resolve()]
    for path in paths:
        if not path.is_file() or not path.stat().st_size:
            raise ValueError(f'Missing or empty input: {path}')
    seen = set()
    lines = paths[1].read_text().splitlines()
    if not lines:
        raise ValueError('Read list is empty')
    for number, line in enumerate(lines, 1):
        fields = line.split('\t')
        if len(fields) not in (1, 2) or any(not field.strip() for field in fields):
            raise ValueError(f'Read-list row {number}: expected one FASTQ or two tab-separated FASTQs, without a header')
        if args.pacbio and len(fields) != 1:
            raise ValueError('--pacbio requires one HiFi FASTQ per row')
        reads = [Path(field).expanduser().resolve() for field in fields]
        for read in reads:
            if not read.is_file() or not read.stat().st_size:
                raise ValueError(f'Read-list row {number}: missing or empty FASTQ {read}')
        if len(reads) == 2 and reads[0] == reads[1]:
            raise ValueError(f'Read-list row {number}: R1 and R2 must be different files')
        identifier = read_id(reads[0])
        if identifier in seen:
            raise ValueError(f'Duplicate mapping sample name: {identifier}; give read files unique basenames')
        seen.add(identifier)
        paths.extend(reads)
    if args.trust_path:
        trusted = Path(args.trust_path).expanduser().resolve()
        refs = sorted(p for p in trusted.iterdir() if p.is_file() and p.suffix in ('.fa','.fna','.fasta')) if trusted.is_dir() else [trusted]
        if not refs:
            raise ValueError(f'No trusted FASTA files in {trusted}')
        names = {Path(args.mg_file).stem}
        for ref in refs:
            if not ref.is_file() or not ref.stat().st_size or ref.suffix not in ('.fa','.fna','.fasta'):
                raise ValueError(f'Expected nonempty trusted FASTA (.fa/.fna/.fasta): {ref}')
            if ref.stem in names:
                raise ValueError(f'Assembly and trusted genomes need unique basenames: {ref.stem}')
            names.add(ref.stem)
        paths.extend(refs)
    output = Path(args.save_path).expanduser().absolute()
    if output.exists() and not output.is_dir():
        raise ValueError('Output path must be a directory')
    if output.is_symlink():
        raise ValueError('Output directory must not be a symlink')
    output = output.resolve()
    if output == Path.home() or output == Path.cwd() or output in Path.cwd().parents:
        raise ValueError('Choose a dedicated output directory, not your home or working directory')
    if any(p == output or output in p.parents for p in paths):
        raise ValueError('Keep source inputs outside the output directory')
    args.mg_file, args.mg_raw_file_list, args.save_path = str(paths[0]), str(paths[1]), str(output)
    if args.trust_path:
        args.trust_path = str(trusted)
    return paths


def prepare_output(args, paths):
    from scarab import version
    output = Path(args.save_path)
    settings = {k:v for k,v in vars(args).items() if k not in ('force','verbose','nthreads')}
    evidence = [(str(p), p.stat().st_size, p.stat().st_mtime_ns) for p in sorted(set(paths))]
    record = json.loads(json.dumps(dict(version=version, settings=settings, inputs=evidence)))
    marker = output/'scarab_run.json'
    status = output/'scarab_status.json'
    if output.exists() and any(output.iterdir()):
        if args.force:
            backup = output.with_name(output.name+'.previous-'+uuid.uuid4().hex[:12])
            output.rename(backup)
            print(f'Previous output preserved: {backup}', flush=True)
        elif (not marker.is_file() or json.loads(marker.read_text()) != record or
              (status.exists() and json.loads(status.read_text()).get('state') != 'complete')):
            raise ValueError('Existing output is incomplete or has different/unrecorded inputs/settings; choose a new -o or use --force to preserve it and start fresh')
    output.mkdir(parents=True, exist_ok=True)
    temporary = marker.with_suffix('.tmp')
    temporary.write_text(json.dumps(record, indent=2)+'\n')
    temporary.replace(marker)


from contextlib import contextmanager
import fcntl
import tempfile


@contextmanager
def numerical_cache(output):
    """Let Numba run under arbitrary container UIDs and read-only installs."""
    if os.environ.get('NUMBA_CACHE_DIR'):
        yield
        return
    previous = os.environ.get('NUMBA_CACHE_DIR')
    with tempfile.TemporaryDirectory(prefix='.scarab-numba-', dir=output) as cache:
        os.environ['NUMBA_CACHE_DIR'] = cache
        try:
            yield
        finally:
            if previous is None:
                os.environ.pop('NUMBA_CACHE_DIR', None)
            else:
                os.environ['NUMBA_CACHE_DIR'] = previous


@contextmanager
def run_guard(args, paths):
    output = Path(args.save_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Keep the lock outside the directory so --force cannot bypass an active run.
    with (output.parent/('.'+output.name+'.scarab.lock')).open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError(f'Another SCARAB run is using {output}')
        prepare_output(args, paths)
        status = output/'scarab_status.json'
        def save(state, error=None):
            temp = status.with_suffix('.tmp')
            temp.write_text(json.dumps(dict(state=state, error=error))+'\n')
            temp.replace(status)
        save('running')
        try:
            yield
        except BaseException as exc:
            save('failed', str(exc))
            raise
        else:
            save('complete')
