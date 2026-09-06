"""Independent source/payload acceptance; no live data or rendering needed."""
import gzip,hashlib,json,pathlib,unittest,zipfile
import numpy as np
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent
PAYLOAD=json.load(gzip.open(HERE/'infrastructure-models.json.gz'))


def read_accessor(g,index,folder):
    a=g['accessors'][index];v=g['bufferViews'][a['bufferView']]
    dtype=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]);size={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']]
    raw=(folder/g['buffers'][v['buffer']]['uri']).read_bytes()
    return np.ndarray((a['count'],size),dtype=dtype,buffer=raw,offset=a.get('byteOffset',0)+v.get('byteOffset',0),strides=(v.get('byteStride',dtype.itemsize*size),dtype.itemsize)).copy()


class InfrastructureAcceptance(unittest.TestCase):
    def test_all_retained_infrastructure_and_hashes(self):
        source_ids=set()
        for sheet in ['9-SW-23A','9-SW-23B']:
            with zipfile.ZipFile(ROOT/'source-scripts/city/tai-o-models/sources'/sheet/(sheet+'.zip')) as z:
                for n in z.namelist():
                    if n.startswith('INFRASTRUCTURE/') and n.endswith('.gltf'):source_ids.add(pathlib.PurePosixPath(n).stem)
        self.assertEqual(source_ids,{m['modelGeometry']['modelId'] for m in PAYLOAD['models']})
        self.assertEqual(len(source_ids),5)
        self.assertEqual(sum(m['modelGeometry']['triangles'] for m in PAYLOAD['models']),2806)
        for m in PAYLOAD['models']:
            for entry,digest in m['modelGeometry']['sourceHashes'].items():
                content=(HERE/'infrastructure-assets'/m['sheet']/entry).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(),digest)
    def test_every_position_matches_native_buffer_without_height_lift(self):
        for m in PAYLOAD['models']:
            model=m['modelGeometry'];p=HERE/'infrastructure-assets'/m['sheet']/model['source'];g=json.loads(p.read_text())
            self.assertEqual(len(g['nodes']),2);self.assertEqual(g['nodes'][1],{'mesh':0})
            matrix=g['nodes'][0]['matrix'];self.assertEqual(matrix[:12],[1,0,0,0,0,0,-1,0,0,1,0,0]);self.assertEqual(matrix[15],1)
            primitive=g['meshes'][0]['primitives'][0];local=read_accessor(g,primitive['attributes']['POSITION'],p.parent).astype(float)
            indices=read_accessor(g,primitive['indices'],p.parent).reshape(-1)
            expected=np.column_stack([local[:,0]+matrix[12]-834500,local[:,2]+matrix[13],-local[:,1]+matrix[14]+816500])[indices]
            actual=np.array(model['position']).reshape(-1,3)
            np.testing.assert_array_equal(actual,expected)
            np.testing.assert_array_equal(model['worldBounds'],[actual.min(axis=0),actual.max(axis=0)])
            colours=read_accessor(g,primitive['attributes']['COLOR_0'],p.parent)[indices].reshape(-1)
            np.testing.assert_array_equal(model['colour'],colours)
        eastern=PAYLOAD['models'][-1]['worldBounds']
        self.assertAlmostEqual(eastern[0][1],-5.509200572967529,places=12)
    def test_only_reviewed_decks_support_public_walking(self):
        public=[m for m in PAYLOAD['models'] if m['walkable']]
        self.assertEqual(len(public),2);self.assertEqual(sum(len(m['walkTriangleIndices']) for m in public),51)
        for m in PAYLOAD['models']:
            tri=np.array(m['modelGeometry']['position']).reshape(-1,3,3)[m['walkTriangleIndices']]
            cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);self.assertTrue(np.all(cross[:,1]/np.linalg.norm(cross,axis=1)>.6))
            self.assertFalse(m['walkSurface']['estimatedElevation'])
            if m['walkable']:
                self.assertTrue(m['publicAccessSource'].startswith('https://www.islands.gov.hk/'))
                union=unary_union([Polygon(t[:,[0,2]]) for t in tri]);self.assertEqual(union.geom_type,'Polygon')
                audit=m['walkSurface']['routeAudit'];self.assertEqual(audit['centreSamplesOnDeck'],audit['samples'])
                self.assertLess(audit['discSamplesOnDeck'],audit['samples'],'Keep the narrow/offset route diagnostic visible')
                # Rail/tower caps are above the walking decks and must not become floors.
                self.assertLess(tri[:,:,1].max(),m['worldBounds'][1][1]-3)
    def test_proxy_suppression_is_unique_local_and_explicit(self):
        ids=[i for m in PAYLOAD['models'] for i in m['suppresses']]
        self.assertEqual(len(ids),5);self.assertEqual(len(ids),len(set(ids)))
        for m in PAYLOAD['models']:
            self.assertEqual(m['suppresses'],[p['id'] for p in m['duplicateSuppression']])
            for p in m['duplicateSuppression']:
                self.assertGreaterEqual(p['pathInsideExactModelFraction'],.85)
                self.assertAlmostEqual(p['pathInsideModelWith1_5mMapToleranceFraction'],1)
                self.assertIn('after valid source mesh has loaded',p['policy'])
    def test_tai_chung_centreline_is_continuous_without_invented_top(self):
        m=PAYLOAD['models'][0];tri=np.array(m['modelGeometry']['position']).reshape(-1,3,3)[m['walkTriangleIndices']]
        bridge=next(b for b in json.loads((ROOT/'3d-viewer/city/data/bridges.json').read_text())['bridges'] if b['id']==m['routeProxyId']);line=LineString(bridge['path']);heights=[]
        for d in np.linspace(0,line.length,int(np.ceil(line.length/.1))+1):
            pt=line.interpolate(float(d));xy=np.array([pt.x,pt.y]);values=[]
            for face in tri:
                xz=face[:,[0,2]];uv=np.linalg.solve(np.column_stack([xz[1]-xz[0],xz[2]-xz[0]]),xy-xz[0])
                if min(uv)>=-1e-8 and sum(uv)<=1+1e-8:values.append(face[0,1]+uv[0]*(face[1,1]-face[0,1])+uv[1]*(face[2,1]-face[0,1]))
            self.assertTrue(values);heights.append(max(values))
        self.assertLess(float(np.abs(np.diff(heights)).max()),.05)
        self.assertAlmostEqual(heights[0],2.6289999485,places=8);self.assertAlmostEqual(heights[-1],4.058000087738037,places=6)

if __name__=='__main__':unittest.main(verbosity=2)
