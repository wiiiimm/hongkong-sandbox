"""HKS-222: adversarial per-model isolation, exact UID mapping and restart checks."""
import gzip
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('citywide_convert_test', HERE/'convert.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)


def fixture(folder, variants=('good','bad','unmatched')):
    positions=np.array([[0,10,0],[10,11,0],[0,10,10]],dtype='<f4')
    normals=np.array([[0,1,0]]*3,dtype='<f4')
    raw=positions.tobytes()+normals.tobytes()+np.ones((3,3),dtype='<f4').tobytes()
    data={'asset':{'version':'2.0'},'scene':0,'scenes':[{'nodes':[0]}], 'nodes':[{'matrix':[1,0,0,0,0,1,0,0,0,0,1,0,834500,0,-816500,1],'mesh':0}], 'meshes':[{'primitives':[{'attributes':{'POSITION':0,'NORMAL':1,'COLOR_0':2}}]}], 'buffers':[{'uri':'source.bin','byteLength':len(raw)}], 'bufferViews':[{'buffer':0,'byteOffset':0,'byteLength':36},{'buffer':0,'byteOffset':36,'byteLength':36},{'buffer':0,'byteOffset':72,'byteLength':36}], 'accessors':[{'bufferView':0,'componentType':5126,'type':'VEC3','count':3},{'bufferView':1,'componentType':5126,'type':'VEC3','count':3},{'bufferView':2,'componentType':5126,'type':'VEC3','count':3}]}
    archive=folder/'source.zip'
    with zipfile.ZipFile(archive,'w') as z:
        z.writestr('BUILDING/source.bin',raw)
        for v in variants:
            name='BUILDING/B'+('9999999999' if v=='unmatched' else '1234567890')+v+'.gltf'
            d=json.loads(json.dumps(data))
            if v=='bad':d['nodes'][0]['children']=[0]
            if v=='trs':d['nodes'][0]['translation']=[0,0,0]
            if v=='escape':d['buffers'][0]['uri']='../../outside.bin'
            if v=='range':d['accessors'][0]['count']=999
            if v=='nan':d['nodes'][0]['matrix'][0]=float('nan')
            z.writestr(name,json.dumps(d))
    official={'datasetVersion':'test','features':[{'attributes':{'OBJECTID':7,'GeoRefNo':'1234567890','BuildingCSUID':'source-7','BaseHeight':10,'TopHeight':11},'geometry':{'rings':[[[834500,816500],[834510,816500],[834500,816490],[834500,816500]]]},'viewerUids':[{'uid':'landsd/7:2','rings':[[[0,0],[10,0],[0,10],[0,0]]],'base':10,'height':1}]}]}
    path=folder/'official.json.gz';path.write_bytes(gzip.compress(json.dumps(official).encode()))
    download={'sheet':'TEST','revisionDate':'2026-09-09','source':'synthetic-test','sha256':c.digest(archive)}
    return archive,download,path


class ConvertTests(unittest.TestCase):
    def run_fixture(self,variants):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);folder=Path(t.name)
        archive,download,official=fixture(folder,variants)
        with patch.object(c.shutil,'which',return_value=None):
            result=c.convert_sheet(archive,download,official,folder/'out')
        rows=[json.loads(line)for line in (folder/'out/outcomes.jsonl').read_text().splitlines()]
        return folder,result,rows,(archive,download,official)

    def test_isolates_and_retains_unmatched_packed_sources(self):
        folder,result,rows,args=self.run_fixture(['good','bad','unmatched','trs','range','escape','nan'])
        self.assertEqual(result['sourceModels'],7)
        self.assertEqual(sum(result['outcomes'].values()),7)
        self.assertEqual(result['candidateModels'],1)
        self.assertEqual(result['packedAssets'],2)
        good=next(r for r in rows if r['sourceEntry'].endswith('good.gltf'))
        self.assertEqual(good['candidate']['uid'],'landsd/7:2') # Never invent :0.
        self.assertEqual(good['worldBounds'],[[0.0,10.0,0.0],[10.0,11.0,10.0]])
        self.assertFalse(good['candidate']['placementReviewed'])
        self.assertEqual(next(r for r in rows if r['sourceEntry'].endswith('unmatched.gltf'))['state'],'source-match-held')
        # A restart must not enter the expensive packer for unchanged assets.
        with patch.object(c._packer,'pack',side_effect=AssertionError('Unexpected repack')),patch.object(c.shutil,'which',return_value=None):
            resumed=c.convert_sheet(*args,folder/'out')
        self.assertEqual(resumed['reusedModels'],7)
        asset=folder/'out'/good['asset']['asset'];asset.write_bytes(b'corrupt')
        with patch.object(c.shutil,'which',return_value=None):
            repaired=c.convert_sheet(*args,folder/'out')
        self.assertLess(repaired['reusedModels'],7)
        self.assertEqual(c.digest(asset),good['asset']['sha256'])

    def test_same_uid_multiple_models_held(self):
        folder,result,rows,_=self.run_fixture(['good','other'])
        self.assertEqual(result['candidateModels'],0)
        self.assertEqual(result['outcomes'],{'source-match-held':2})
        self.assertTrue(all(r.get('asset')for r in rows))

    def test_no_uid_invention_when_footprint_has_no_viewer_part(self):
        folder,_,_,args=self.run_fixture(['good'])
        path=args[2];d=json.loads(gzip.decompress(path.read_bytes()));d['features'][0]['viewerUids']=[];path.write_bytes(gzip.compress(json.dumps(d).encode()))
        with patch.object(c.shutil,'which',return_value=None):
            r=c.convert_sheet(*args,folder/'out')
        self.assertEqual(r['candidateModels'],0);self.assertEqual(r['packedAssets'],1)

    def test_terrain_geometry_without_photo_and_failure_isolation(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);folder=Path(t.name)
        archive,download,official=fixture(folder,['good'])
        with zipfile.ZipFile(archive,'a') as z:
            data=json.loads(z.read('BUILDING/B1234567890good.gltf'))
            data['images']=[{'uri':'photo.jpg'}];data['textures']=[{'source':0}]
            data['materials']=[{'pbrMetallicRoughness':{'baseColorTexture':{'index':0}}}]
            z.writestr('TERRAIN/terrain.gltf',json.dumps(data));z.writestr('TERRAIN/source.bin',z.read('BUILDING/source.bin'))
            z.writestr('TERRAIN/malformed.gltf','invalid-json')
        download['sha256']=c.digest(archive)
        with patch.object(c.shutil,'which',return_value=None):
            summary=c.convert_sheet(archive,download,official,folder/'out')
        self.assertEqual(summary['sourceModels'],1)
        self.assertEqual(summary['sourceTerrainModels'],2)
        self.assertEqual(summary['terrainOutcomes'],{'failed':1,'prepared-geometry-only':1})
        terrain=json.loads((folder/'out/terrain-outcomes.json').read_text())
        prepared=next(r for r in terrain['rows'] if r['state']=='prepared-geometry-only')
        self.assertEqual(prepared['omittedPhotoEntries'],['TERRAIN/photo.jpg'])
        manifests=list((folder/'out/native-terrain').glob('*/manifest.json'))
        derived=json.loads((manifests[0].parent/'TERRAIN/terrain-geometry.gltf').read_text())
        self.assertNotIn('images',derived);self.assertNotIn('baseColorTexture',derived['materials'][0]['pbrMetallicRoughness'])

    def test_source_hash_mismatch_rejected(self):
        folder,_,_,args=self.run_fixture(['good'])
        with self.assertRaisesRegex(ValueError,'SHA'):
            c.convert_sheet(args[0],{**args[1],'sha256':'wrong'},args[2],folder/'other')

if __name__=='__main__':unittest.main()
