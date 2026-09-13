import tempfile,unittest
from pathlib import Path
from r2_snapshot import LocalStore,digest,key_for
from remote_checkpoint import objects,transfer

class TransferTests(unittest.TestCase):
    def test_parallel_upload_resume_and_fresh_download(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);local=LocalStore(p/'local');remote=LocalStore(p/'remote');fresh=LocalStore(p/'fresh');rows=[]
            for i in range(6):
                source=p/'source';source.write_bytes(str(i).encode());sha=digest(source)
                local.put(key_for(sha),source);rows.append({'kind':'file','sha256':sha,'bytes':1,'path':str(i)})
            manifest={'files':rows+[rows[0]]}
            self.assertEqual(transfer(manifest,local,remote,4)['uploadedObjects'],6)
            self.assertEqual(transfer(manifest,local,remote,4)['uploadedBytes'],0)
            self.assertEqual(transfer(manifest,fresh,remote,4,False)['verifiedObjects'],6)
            for row in rows:self.assertEqual(digest(fresh.root/key_for(row['sha256'])),row['sha256'])

    def test_corrupt_local_prevents_upload(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);local=LocalStore(p/'local');remote=LocalStore(p/'remote')
            with self.assertRaises(ValueError):transfer({'files':[{'kind':'file','sha256':'0'*64,'bytes':1}]},local,remote)
            self.assertFalse(remote.root.exists())

if __name__=='__main__':unittest.main()
