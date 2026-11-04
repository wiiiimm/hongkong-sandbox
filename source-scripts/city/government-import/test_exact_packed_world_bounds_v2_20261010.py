import unittest,gzip,json,struct,numpy as np
from pathlib import Path
from exact_packed_world_bounds_v2_20261010 import packed_world_bounds
from exact_packed_world_bounds_20261009 import packed_world_bounds as indexed_bounds

def fixture(points,index,node=None):
 p=np.asarray(points,dtype='<f4');i=np.asarray(index,dtype='<u4');data=p.tobytes()+i.tobytes();doc={'asset':{'version':'2.0'},'buffers':[{'byteLength':len(data)}],'bufferViews':[{'buffer':0,'byteOffset':0,'byteLength':p.nbytes},{'buffer':0,'byteOffset':p.nbytes,'byteLength':i.nbytes}],'accessors':[{'bufferView':0,'componentType':5126,'count':len(p),'type':'VEC3'},{'bufferView':1,'componentType':5125,'count':len(i),'type':'SCALAR'}],'meshes':[{'primitives':[{'attributes':{'POSITION':0},'indices':1}]}],'nodes':[{'mesh':0,**(node or{})}],'scenes':[{'nodes':[0]}],'scene':0};j=json.dumps(doc).encode();j+=b' '*(-len(j)%4);data+=b'\0'*(-len(data)%4);raw=struct.pack('<III',0x46546c67,2,28+len(j)+len(data))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(data),0x004e4942)+data;return gzip.compress(raw)
class Cases(unittest.TestCase):
 def test_unused_extreme(self):
  raw=fixture([[834500,0,-816500],[834501,0,-816500],[834500,1,-816501],[834600,7,-816300]],[0,1,2]);r=packed_world_bounds(raw);self.assertEqual(r['originalWholeSourceBounds'],[[0,0,-1],[100,7,200]]);self.assertEqual(r['originalIndexedFaceBounds'],[[0,0,-1],[1,1,0]]);self.assertEqual(r['originalUnreferencedPositionVertices'],1);self.assertEqual(r['worldTrianglesSHA256'],indexed_bounds(raw)['worldTrianglesSHA256'])
 def test_degenerate_position_retained(self):
  r=packed_world_bounds(fixture([[834500,0,-816500],[834600,0,-816500],[834700,0,-816500]],[0,1,2]));self.assertEqual(r['completeOriginalTriangles'],1);self.assertEqual(r['completeOriginalPositionVertices'],3);self.assertEqual(r['originalWholeSourceBounds'][1][0],200)
 def test_unused_nonfinite_reject(self):self.assertRaises(AssertionError,packed_world_bounds,fixture([[834500,0,-816500],[834501,0,-816500],[834500,0,-816501],[float('nan'),0,0]],[0,1,2]))
 def test_bad_index(self):self.assertRaises(AssertionError,packed_world_bounds,fixture([[1,0,0]],[0,1,2]))
 def test_unreviewed_trs(self):self.assertRaises(AssertionError,packed_world_bounds,fixture([[1,0,0]],[0,0,0],{'translation':[1,0,0]}))
 def test_actual_native(self):
  import sys;sys.path.insert(0,str(Path(__file__).parent));from run import ROOT,read
  m=read(ROOT/'3d-viewer/city/data/manifest.json');found=[]
  for url in m['officialModelCatalogues']:
   p=ROOT/'3d-viewer'/url
   for e in read(p)['models']:
    if e['uid']=='landsd/22089:0':found.append((p,e))
  self.assertEqual(len(found),1);p,e=found[0];raw=(p.parent/e['asset']).read_bytes();old=indexed_bounds(raw);r=packed_world_bounds(raw);self.assertEqual(r['sourceSHA256'],e['sha256']);self.assertEqual(r['completeOriginalTriangles'],3965);self.assertEqual(r['worldTrianglesSHA256'],old['worldTrianglesSHA256']);self.assertTrue(r['allOriginalPositionVerticesAccounted']);self.assertGreaterEqual(r['completeOriginalPositionVertices'],e['indexedVertices'])
if __name__=='__main__':unittest.main()
