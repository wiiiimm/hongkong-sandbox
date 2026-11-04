import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import MagicMock, patch

spec=importlib.util.spec_from_file_location('native_source_cache',Path(__file__).with_name('source_cache.py'))
cache=importlib.util.module_from_spec(spec);spec.loader.exec_module(cache)


class SourceCacheTests(unittest.TestCase):
    def bundle(self, extra=(), omit=(), bad_record=False):
        payload=b'fixture source ZIP bytes'
        record={'sheet':'11-SW-1A','bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),'sourceETag':'frozen'}
        if bad_record:record['sha256']='0'*64
        members=[('original/11-SW-1A.zip',payload,None),('original/download.json',json.dumps(record).encode(),None),('converted/never-extract.bin',b'ignored',None)]+list(extra)
        stream=io.BytesIO()
        with tarfile.open(fileobj=stream,mode='w:gz') as tar:
            for name,data,kind in members:
                if name in omit:continue
                info=tarfile.TarInfo(name);info.size=len(data)
                if kind:info.type=kind;info.linkname='/tmp/escape'
                tar.addfile(info,io.BytesIO(data))
        raw=stream.getvalue();sha=hashlib.sha256(raw).hexdigest()
        return raw,{'key':cache.key_for(sha),'sha256':sha,'bytes':len(raw),'kind':cache.KIND}

    def restore(self,raw,artifact,out):
        remote=MagicMock();remote.get.side_effect=lambda key,dest:Path(dest).write_bytes(raw)
        return cache.restore_original(remote,artifact,'11-SW-1A',out)

    def test_restores_only_two_verified_original_files(self):
        raw,artifact=self.bundle()
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'out';path,record=self.restore(raw,artifact,out)
            self.assertEqual(path,out/'download.json');self.assertEqual(record['sourceETag'],'frozen')
            self.assertEqual({p.name for p in out.iterdir()},{'download.json','11-SW-1A.zip'})

    def test_corruption_and_bad_size_do_not_modify_existing_output(self):
        raw,artifact=self.bundle()
        for data,ref in [(raw+b'bad',artifact),(raw,{**artifact,'bytes':len(raw)+1})]:
            with tempfile.TemporaryDirectory() as temp:
                out=Path(temp)/'out';out.mkdir();(out/'keep').write_text('untouched')
                with self.assertRaises(ValueError):self.restore(data,ref,out)
                self.assertEqual([p.name for p in out.iterdir()],['keep'])

    def test_bad_reference_and_sheet_are_rejected_before_download(self):
        raw,artifact=self.bundle();remote=MagicMock()
        for change in ({'key':'astra-modelling/../escape'},{'key':'https://example.test/file'},{'sha256':'z'*64},{'kind':'other'},{'bytes':True}):
            with self.assertRaises(ValueError):cache.restore_original(remote,{**artifact,**change},'11-SW-1A','unused')
        for sheet in ('../escape','/absolute','folder\\name'):
            with self.assertRaises(ValueError):cache.restore_original(remote,artifact,sheet,'unused')
        remote.get.assert_not_called()

    def test_path_duplicate_links_missing_and_record_mismatch_are_rejected(self):
        fixtures=[self.bundle(extra=[('../escape',b'x',None)]),self.bundle(extra=[('/absolute',b'x',None)]),self.bundle(extra=[('original/11-SW-1A.zip',b'x',None)]),self.bundle(extra=[('original/11-SW-1A.zip',b'',tarfile.SYMTYPE)]),self.bundle(omit=['original/download.json']),self.bundle(bad_record=True)]
        for raw,artifact in fixtures:
            with tempfile.TemporaryDirectory() as temp:
                out=Path(temp)/'out'
                with self.assertRaises(ValueError):self.restore(raw,artifact,out)
                self.assertFalse(out.exists())

    def test_bulk_lookup_uses_read_only_transaction_and_validates_refs(self):
        raw,artifact=self.bundle();con=MagicMock();con.execute.return_value.fetchall.return_value=[('1'*64,artifact)]
        with patch.object(cache,'connect') as connect:
            connect.return_value.__enter__.return_value=con
            self.assertEqual(cache.previous_source_artifacts(),{'1'*64:artifact})
        self.assertEqual(con.execute.call_args_list[0].args[0],'SET TRANSACTION READ ONLY')
        self.assertIn('DISTINCT ON(i.source_sha)',con.execute.call_args_list[1].args[0])
        self.assertEqual(con.execute.call_count,2)

if __name__=='__main__':unittest.main()
