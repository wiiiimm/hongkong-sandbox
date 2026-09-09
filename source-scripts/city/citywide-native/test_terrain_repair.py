import copy,json,unittest
import numpy as np
from terrain_repair import repair_model,accessor


def fixture():
    arrays=[np.array([[0,0,0],[1,0,0],[0,0,1]],dtype='<f4'),np.array([[float('nan'),0,0]]*3,dtype='<f4'),np.array([[float('nan'),0]]*3,dtype='<f4'),np.array([[0],[1],[2]],dtype='<u2')]
    buffers={};data={'asset':{'version':'2.0'},'buffers':[],'bufferViews':[],'accessors':[],'nodes':[{'mesh':0,'translation':[834501,4,-816502]}],'scenes':[{'nodes':[0]}],'scene':0,'meshes':[{'primitives':[{'attributes':{'POSITION':0,'NORMAL':1,'TEXCOORD_0':2},'indices':3}]}],'materials':[{'extensions':{'KHR_materials_ior':{'ior':1.45}},'pbrMetallicRoughness':{'baseColorTexture':{'index':0}}}],'extensionsUsed':['KHR_materials_ior'],'images':[{'uri':'unused.jpg'}],'textures':[{'source':0}]}
    for index,array in enumerate(arrays):
        name=f'{index}.bin';raw=array.tobytes();buffers[name]=raw;data['buffers'].append({'uri':name,'byteLength':len(raw)});data['bufferViews'].append({'buffer':index,'byteLength':len(raw)});data['accessors'].append({'bufferView':index,'componentType':5123 if index==3 else 5126,'count':len(array),'type':'SCALAR'if index==3 else 'VEC3'if index<2 else 'VEC2'})
    return data,buffers


class TerrainRepairTests(unittest.TestCase):
    def test_repairs_shading_preserving_exact_geometry_and_translation(self):
        data,buffers=fixture();raw=json.dumps(data).encode();original=copy.deepcopy(buffers)
        result=repair_model(raw,buffers.__getitem__);self.assertEqual(result['state'],'prepared-geometry-only')
        derived=json.loads(result['files']['geometry.gltf']);p=derived['meshes'][0]['primitives'][0]
        self.assertEqual(p['attributes']['POSITION'],0);self.assertEqual(p['indices'],3)
        for name,value in original.items():self.assertEqual(result['files'][name],value)
        self.assertNotIn('TEXCOORD_0',p['attributes']);self.assertNotIn('images',derived)
        self.assertNotIn('translation',derived['nodes'][0]);self.assertEqual(derived['nodes'][0]['matrix'][12:15],[834501.,4.,-816502.])
        self.assertEqual(result['geometryProof']['worldBounds'],[[1.,4.,-2.],[2.,4.,-1.]])
        self.assertTrue(np.isfinite(accessor(derived,[result['files'][b['uri']]for b in derived['buffers']],p['attributes']['NORMAL'])).all())
        self.assertEqual(repair_model(raw,buffers.__getitem__)['files'],result['files'])

    def test_invalid_positions_and_indices_are_never_discarded(self):
        data,buffers=fixture();buffers['0.bin']=np.array([[float('nan'),0,0]]*3,dtype='<f4').tobytes()
        with self.assertRaisesRegex(ValueError,'Invalid POSITION'):repair_model(json.dumps(data).encode(),buffers.__getitem__)
        data,buffers=fixture();buffers['3.bin']=np.array([0,1,99],dtype='<u2').tobytes()
        with self.assertRaisesRegex(ValueError,'triangle indices'):repair_model(json.dumps(data).encode(),buffers.__getitem__)

    def test_unknown_extensions_and_rotations_remain_held(self):
        for change in ('extension','rotation','scale'):
            data,buffers=fixture()
            if change=='extension':data['extensionsUsed'].append('KHR_draco_mesh_compression')
            else:data['nodes'][0][change]=[0,0,0,1]if change=='rotation'else[1,1,1]
            with self.assertRaises(ValueError):repair_model(json.dumps(data).encode(),buffers.__getitem__)

    def test_zero_mesh_is_explicit_source_empty(self):
        data={'asset':{'version':'2.0'},'meshes':[],'nodes':[{}],'scenes':[{'nodes':[0]}]}
        result=repair_model(json.dumps(data).encode(),{}. __getitem__)
        self.assertEqual(result['state'],'source-empty');self.assertEqual(result['geometryProof']['reachablePrimitives'],0)
        self.assertTrue(result['sourceHashes'])

    def test_degenerate_triangles_are_retained_with_finite_shading(self):
        data,buffers=fixture();buffers['3.bin']=np.array([0,0,0],dtype='<u2').tobytes()
        result=repair_model(json.dumps(data).encode(),buffers.__getitem__)
        self.assertEqual(result['files']['3.bin'],buffers['3.bin']);self.assertEqual(result['geometryProof']['triangles'],1)
        action=next(a for a in result['repairActions']if a['action']=='regenerate-shading-normals')
        self.assertEqual(action['zeroNormalVertices'],3)

    def test_matrix_and_valid_normal_bytes_remain_unchanged(self):
        data,buffers=fixture();data['nodes'][0].pop('translation');data['nodes'][0]['matrix']=np.eye(4).reshape(-1).tolist();buffers['1.bin']=np.array([[0,1,0]]*3,dtype='<f4').tobytes()
        result=repair_model(json.dumps(data).encode(),buffers.__getitem__);derived=json.loads(result['files']['geometry.gltf'])
        self.assertEqual(derived['nodes'][0]['matrix'],data['nodes'][0]['matrix']);self.assertEqual(derived['meshes'][0]['primitives'][0]['attributes']['NORMAL'],1)
        self.assertEqual(result['files']['1.bin'],buffers['1.bin'])

if __name__=='__main__':unittest.main()

class TerrainRepairPipelineTests(unittest.TestCase):
    def test_verified_original_bundle_to_verified_repair_bundle(self):
        import gzip,hashlib,io,tarfile,tempfile,zipfile
        from pathlib import Path
        from unittest.mock import patch
        import repair_terrain_run as runner
        from r2_snapshot import LocalStore,digest,key_for
        data,buffers=fixture();sheet='fixture';entry='TERRAIN/T1/T1.gltf'
        with tempfile.TemporaryDirectory()as temporary:
            temp=Path(temporary);archive=temp/'fixture.zip'
            with zipfile.ZipFile(archive,'w')as z:
                z.writestr(entry,json.dumps(data))
                for name,raw in buffers.items():z.writestr('TERRAIN/T1/'+name,raw)
            record={'sheet':sheet,'source':'https://download.map.gov.hk/fixture.zip','sourceETag':'test','directorySHA256':'1'*64,'bytes':archive.stat().st_size,'sha256':digest(archive)}
            bundle=temp/'original.tar.gz'
            with tarfile.open(bundle,'w:gz')as tar:
                for name,raw in [('original/fixture.zip',archive.read_bytes()),('original/download.json',json.dumps(record).encode())]:
                    info=tarfile.TarInfo(name);info.size=len(raw);tar.addfile(info,io.BytesIO(raw))
            remote=LocalStore(temp/'remote');sha=digest(bundle);key=key_for(sha);remote.put(key,bundle)
            item={'sheet':sheet,'stage':'native-terrain-repair','sourceSha256':runner.store.digest([record['source'],record['sourceETag'],record['directorySHA256']]),'pipelineSha256':'2'*64,'footprintSha256':'3'*64,'terrainSha256':None,'inputs':{'originalCacheKey':'4'*64,'originalArtifact':{'key':key,'sha256':sha,'bytes':bundle.stat().st_size,'kind':'original-and-prepared-sheet'},'sourceEntries':[entry],'code':{}}}
            with patch.object(runner,'HERE',temp):result,folder=runner.process(item,'00000000-0000-4000-8000-000000000001',remote)
            self.assertEqual(result['status'],'prepared');self.assertEqual(result['counts']['sourceTerrainModels'],1)
            self.assertEqual(result['models'],[]);self.assertEqual(result['terrain'][0]['sourceEntry'],entry)
            self.assertTrue(result['terrain'][0]['geometryProof']['sourcePositionsAndIndicesPreserved'])
            self.assertEqual(result['artifacts'][0]['sha256'],digest(folder/'terrain-repair.tar.gz'))
