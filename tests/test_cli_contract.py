import contextlib
import io
import json
import os
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from scarab.commands import _parse_recruit_args
from scarab.validation import validate_inputs, prepare_output, run_guard, read_id, numerical_cache


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        for name in ('assembly.fa','one.R1.fastq','one.R2.fastq'):
            (self.root/name).write_text('fixture')
        self.manifest=self.root/'reads.txt'
        self.manifest.write_text(str(self.root/'one.R1.fastq')+'\t'+str(self.root/'one.R2.fastq')+'\n')
        self.base=['-m',str(self.root/'assembly.fa'),'-l',str(self.manifest),'-o',str(self.root/'out')]
    def test_typed_manual_overrides(self):
        args=_parse_recruit_args(self.base+['--nu','0.2','--gamma','0.4','--denovo_min_clust','9'])
        self.assertEqual((args.nu,args.gamma,args.denovo_min_clust),(0.2,0.4,9))
    def test_invalid_options_stop_before_work(self):
        for flags in (['-t','0'],['--jaccard','nan'],['--overlap_len','10000'],['--nu','2'],['--gamma','inf'],['--strict','--relaxed'],['--autoopt','oops'],['--dedupe_memory','0g'],['--dedupe_memory','4g;rm']):
            with self.subTest(flags=flags),contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                _parse_recruit_args(self.base+flags)
    def test_missing_r2_is_rejected(self):
        (self.root/'one.R2.fastq').unlink()
        with self.assertRaisesRegex(ValueError,'FASTQ'):
            validate_inputs(_parse_recruit_args(self.base))
    def test_same_reads_are_rejected(self):
        self.manifest.write_text((str(self.root/'one.R1.fastq')+'\t')+str(self.root/'one.R1.fastq'))
        with self.assertRaisesRegex(ValueError,'different'):
            validate_inputs(_parse_recruit_args(self.base))
    def test_force_preserves_old_output_and_changed_inputs_fail(self):
        args=_parse_recruit_args(self.base);paths=validate_inputs(args)
        with run_guard(args,paths): (Path(args.save_path)/'sentinel').write_text('keep')
        prepare_output(args,paths)
        (self.root/'one.R1.fastq').write_text('changed input')
        with self.assertRaisesRegex(ValueError,'different'): prepare_output(args,paths)
        args.force=True
        with run_guard(args,paths): self.assertFalse((Path(args.save_path)/'sentinel').exists())
        self.assertEqual(next(self.root.glob('out.previous-*/sentinel')).read_text(),'keep')
    def test_failure_requires_fresh_work_and_active_run_blocks_force(self):
        args=_parse_recruit_args(self.base);paths=validate_inputs(args)
        with self.assertRaisesRegex(RuntimeError,'tool failed'):
            with run_guard(args,paths):
                args.force=True
                with self.assertRaisesRegex(RuntimeError,'Another'):
                    with run_guard(args,paths): pass
                args.force=False
                raise RuntimeError('tool failed')
        with self.assertRaisesRegex(ValueError,'incomplete'): prepare_output(args,paths)
    def test_basenames_preserve_periods(self):
        self.assertEqual(read_id('sample.one.fastq.gz'),'sample.one')
        self.assertNotEqual(read_id('sample.one.fastq.gz'),read_id('sample.two.fastq.gz'))
    def test_input_in_output_is_protected(self):
        args=_parse_recruit_args(self.base);args.save_path=str(self.root)
        with self.assertRaisesRegex(ValueError,'outside'): validate_inputs(args)
    def test_output_file_is_rejected_without_altering_it(self):
        (self.root/'out').write_text('keep')
        with self.assertRaisesRegex(ValueError,'directory'):
            validate_inputs(_parse_recruit_args(self.base+['--force']))
        self.assertEqual((self.root/'out').read_text(),'keep')
    def test_private_numba_cache_is_cleaned_after_failure(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                with numerical_cache(self.root):
                    cache=Path(os.environ['NUMBA_CACHE_DIR'])
                    (cache/'compiled').write_text('cache')
                    self.assertEqual(cache.parent,self.root)
                    raise RuntimeError('stop')
            self.assertFalse(cache.exists())
            self.assertNotIn('NUMBA_CACHE_DIR',os.environ)
    def test_explicit_numba_cache_is_preserved(self):
        with patch.dict(os.environ, {'NUMBA_CACHE_DIR':str(self.root)}):
            with numerical_cache(self.root):
                self.assertEqual(os.environ['NUMBA_CACHE_DIR'],str(self.root))
            self.assertEqual(os.environ['NUMBA_CACHE_DIR'],str(self.root))

if __name__=='__main__': unittest.main()
