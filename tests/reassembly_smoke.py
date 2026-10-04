"""Small synthetic, non-manuscript test using the installed reassembly CLI."""
from pathlib import Path
import json
import random
import subprocess
import tempfile


def main():
    with tempfile.TemporaryDirectory(prefix='scarab-reassembly-') as temporary:
        root = Path(temporary)
        rng = random.Random(218)
        sequence = ''.join(rng.choices('ACGT', k=30000))
        reference = root/'target.fasta'
        reference.write_text('>synthetic\n'+sequence+'\n')
        first, second, interleaved = root/'R1.fastq', root/'R2.fastq', root/'interleaved.fastq'
        complement = str.maketrans('ACGT','TGCA')
        with first.open('w') as a, second.open('w') as b, interleaved.open('w') as together:
            for number,start in enumerate(range(0,len(sequence)-350,10)):
                reads = [sequence[start:start+150], sequence[start+200:start+350].translate(complement)[::-1]]
                records = [f'@pair{number}/{mate}\n{seq}\n+\n'+('I'*150)+'\n' for mate,seq in enumerate(reads,1)]
                a.write(records[0]);b.write(records[1]);together.write(''.join(records))
        for mode,line in [('paired',f'{first}\t{second}\n'),('interleaved',str(interleaved)+'\n')]:
            manifest = root/f'{mode}.tsv';manifest.write_text(line)
            output = root/mode
            command = ['scarab','reassemble','-i',str(reference),'-l',str(manifest),'-o',str(output),'-t','2','--memory','4']
            subprocess.run(command,check=True)
            receipt = json.loads((output/'target/reassembly.json').read_text())
            assert receipt['state']=='complete' and receipt['libraries'][0]['clean_pairs']==2965
            assembled=''.join(l for l in (output/'target/contigs.fasta').read_text().splitlines() if not l.startswith('>'))
            assert assembled in (sequence,sequence.translate(complement)[::-1]), 'Synthetic reference not recovered exactly'
            assert not (output/'target/work').exists()
            before=(output/'target/commands.log').stat().st_mtime_ns
            subprocess.run(command,check=True)
            assert (output/'target/commands.log').stat().st_mtime_ns==before, 'Completed run unexpectedly executed tools'
        print('Guided reassembly: paired/interleaved reads, exact synthetic recovery, cleanup and reuse passed.')


if __name__=='__main__':
    main()
