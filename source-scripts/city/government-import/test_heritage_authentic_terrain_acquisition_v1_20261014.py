"""Bounded metadata/member fixtures; no network or model geometry."""
import copy, hashlib, tempfile, unittest, zipfile, zlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import heritage165054_authentic_terrain_acquisition_v1_20261014 as a
class AcquisitionBindings(unittest.TestCase):
    def setup_metadata(self):
        row=dict(a.PIN,status='directory-verified',models=[dict(modelId='retained-building',members=[])])
        infos=[SimpleNamespace(filename=e['name'],CRC=e['crc32'],compress_size=e['compressedBytes'],file_size=e['decodedBytes'],header_offset=e['headerOffset']) for e in a.MEMBERS]
        parsed={k:a.PIN[k] for k in ['completeEntries','centralDirectoryBytes','centralDirectoryOffset','directorySHA256']}
        return row,infos,parsed
    def test_exact_two_terrain_only_and_immutable_original_selection(self):
        row,infos,parsed=self.setup_metadata(); old=copy.deepcopy(row); r=a.terrain_selection(row,infos,parsed)
        self.assertEqual(row,old); self.assertEqual(r['models'],[]); self.assertEqual(sum(e.compress_size for e in infos),2869630)
    def test_revision_etag_directory_mutations_rejected(self):
        for k in ['revision','etag','directorySHA256','sourceURL']:
            row,infos,parsed=self.setup_metadata(); row[k]='different'
            with self.subTest(k=k),self.assertRaises(AssertionError): a.terrain_selection(row,infos,parsed)
    def test_missing_extra_and_changed_header_crc_rejected(self):
        row,infos,parsed=self.setup_metadata()
        for changed in [infos[:1],infos+[SimpleNamespace(filename='TERRAIN/extra.bin',CRC=1,compress_size=1,file_size=1,header_offset=1)]]:
            with self.assertRaises(AssertionError): a.terrain_selection(row,changed,parsed)
        for k in ['CRC','header_offset','compress_size','file_size']:
            changed=copy.deepcopy(infos); setattr(changed[0],k,1)
            with self.subTest(k=k),self.assertRaises(AssertionError): a.terrain_selection(row,changed,parsed)
    def test_complete_directory_guard(self):
        row,infos,parsed=self.setup_metadata(); parsed['completeEntries']-=1
        with self.assertRaises(AssertionError): a.terrain_selection(row,infos,parsed)
    def archive(self,folder):
        data=[b'unchanged original buffer',b'{"buffers":[{"uri":"sample.bin"}]}']
        members=[dict(name='TERRAIN/sample.'+ext,crc32=zlib.crc32(b)&0xffffffff,compressedBytes=100+i,decodedBytes=len(b),headerOffset=20+i) for i,(ext,b) in enumerate(zip(['bin','gltf'],data))]
        p=folder/'fixture.zip'
        with zipfile.ZipFile(p,'w') as z:
            for m,b in zip(members,data): z.writestr(m['name'],b)
        r=dict(sheet=a.PIN['sheet'],source=a.PIN['sourceURL'],sourceETag=a.PIN['etag'],directorySHA256=a.PIN['directorySHA256'],expectedModels=0,terrainGeometryIncluded=True,terrainPhotographsOmitted=True,sourceArchiveBytes=a.PIN['archiveBytes'],dependencyScanVersion=1,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),entries=[dict(name=m['name'],bytes=len(b),sourceCRC32=m['crc32'],sourceCompressedBytes=m['compressedBytes'],sha256=hashlib.sha256(b).hexdigest()) for m,b in zip(members,data)])
        return p,members,r
    def test_actual_zip_member_bytes_checked_without_geometry_decode(self):
        with tempfile.TemporaryDirectory() as d:
            p,m,r=self.archive(Path(d))
            with patch.object(a,'MEMBERS',m): self.assertIs(a.verify_record(r,p),r)
            r['entries'][0]['sha256']='0'*64
            with patch.object(a,'MEMBERS',m),self.assertRaises(AssertionError): a.verify_record(r,p)
    def test_building_or_extra_dependency_cannot_be_credited_as_two_members(self):
        with tempfile.TemporaryDirectory() as d:
            p,m,r=self.archive(Path(d)); r['entries'].append(dict(name='BUILDING/unknown.bin'))
            with patch.object(a,'MEMBERS',m),self.assertRaises(AssertionError): a.verify_record(r,p)
if __name__=='__main__': unittest.main()
