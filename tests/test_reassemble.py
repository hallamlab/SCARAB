import importlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

r = importlib.import_module('scarab.reassemble')


class ReassemblyTests(unittest.TestCase):
    def test_rejects_identical_mates_and_output_containing_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            ref = root/'ref.fa'; ref.write_text('>ref\nACGT\n')
            fq = root/'R1.fq'; fq.write_text('@x\nACGT\n+\nIIII\n')
            manifest = root/'reads.tsv';manifest.write_text(f'{fq}\t{fq}\n')
            args=SimpleNamespace(input=str(ref),reads=str(manifest),save_path=str(root/'out'))
            with self.assertRaisesRegex(ValueError,'different'):
                r.parse_inputs(args)
            manifest.write_text(str(fq)+'\n');args.save_path=str(root)
            with self.assertRaisesRegex(ValueError,'outside'):
                r.parse_inputs(args)

    def test_pair_check_detects_missing_and_mismatched_reads(self):
        with tempfile.TemporaryDirectory() as temp:
            a,b=Path(temp)/'R1.fq',Path(temp)/'R2.fq'
            a.write_text('@x/1\nACGT\n+\nIIII\n');b.write_text('@x/2\nACGT\n+\nIIII\n')
            self.assertEqual(r.paired_count(a,b),1)
            for text in ('','@other/2\nACGT\n+\nIIII\n'):
                b.write_text(text)
                with self.assertRaisesRegex(ValueError,'unmatched'):
                    r.paired_count(a,b)

    def test_empty_mapping_skips_spades_and_passes_distinct_mates(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);ref=root/'ref.fa';ref.write_text('>ref\nACGT\n')
            r1,r2=root/'r1.fq',root/'r2.fq'
            calls=[]
            def fake_run(cmd,log,stdout=None):
                calls.append(list(map(str,cmd)))
                if stdout:stdout.write_text('')
                if '-o' in cmd:Path(cmd[cmd.index('-o')+1]).write_text('')
                if cmd[1]=='fastq':
                    Path(cmd[cmd.index('-1')+1]).write_text('')
                    Path(cmd[cmd.index('-2')+1]).write_text('')
            args=SimpleNamespace(nthreads=4,memory=8,keep_intermediates=False)
            tools={n:n for n in ('minimap2','samtools','spades.py')}
            with patch.object(r,'run',side_effect=fake_run):
                result=r.reassemble_one(ref,[[r1,r2]],root/'output',args,tools)
            self.assertEqual(result['state'],'skipped_no_usable_pairs')
            self.assertEqual(calls[0][-2:],[str(r1),str(r2)])
            self.assertTrue(any('2316' in c and '-f' in c for c in calls))
            self.assertFalse(any(c[0]=='spades.py' for c in calls))
            self.assertFalse((root/'output/ref/work').exists())

    def test_subprocess_errors_are_not_suppressed(self):
        import subprocess,sys
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(subprocess.CalledProcessError):
                r.run([sys.executable,'-c','raise SystemExit(7)'],Path(temp)/'log')
