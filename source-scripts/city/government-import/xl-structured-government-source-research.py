"""Bounded, read-only 3DSD tile metadata investigation; no import/acceptance."""
import json, hashlib, struct, urllib.request, urllib.parse
from pathlib import Path
import numpy as np
from pyproj import Transformer
ROOT=Path(__file__).resolve().parents[3]
DOC=ROOT/'docs/astra-city/government-import/government-xl-structured-source-research-20261008'
BASE='https://data.map.gov.hk/api/3d-data/3dsd/WGS84/building/'
KEY='3967f8f365694e0798af3e7678509421' # published official API example, not a local credential
CACHE=ROOT/'source-scripts/city/government-import/local/government-xl-structured-source-research-20261008'
TARGETS={'apex':(833329.6,814993.7,460),'hsbc-centre':(834598.9,820020.1,45)}
T=Transformer.from_crs(2326,4978,always_xy=True)
POINTS={k:np.array(T.transform(*v)) for k,v in TARGETS.items()}
records=[]; leaves=[]; total=0

def fetch(uri):
 global total
 path=urllib.parse.urlparse(uri).path
 assert path.startswith('/api/3d-data/3dsd/WGS84/building/'),path
 name=hashlib.sha256(path.encode()).hexdigest(); p=CACHE/name
 if p.exists():b=p.read_bytes()
 else:
  assert len(records)<60 and total<50_000_000
  with urllib.request.urlopen(uri+'?key='+KEY,timeout=45) as r:
   b=r.read(20_000_001)
  assert len(b)<=20_000_000
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 total+=len(b)
 records.append({'path':path,'cache':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
 return b

def near(node,transform):
 box=node.get('boundingVolume',{}).get('box')
 assert box is not None,'Unsupported volume: fail closed'
 center=(transform@np.array(box[:3]+[1]))[:3]
 axes=transform[:3,:3]@np.array(box[3:]).reshape(3,3).T
 # Approximate vertical routing only; never an accepted datum conversion.
 lengths=np.linalg.norm(axes,axis=0)
 out=[]
 for k,p in POINTS.items():
  q=np.linalg.solve(axes,p-center)
  radial=p/np.linalg.norm(p)
  allowance=10+190*np.abs((axes/np.maximum(lengths,1e-9)).T@radial)
  if np.all(np.abs(q)<=1+allowance/np.maximum(lengths,1e-9)):out.append(k)
 return out

def visit(node,parent,url,depth):
 assert depth<=18
 tr=parent@np.array(node.get('transform',np.eye(4).flatten(order='F'))).reshape(4,4,order='F')
 selected=near(node,tr)
 if not selected:return
 content=node.get('content',{})
 u=content.get('uri',content.get('url'))
 if u and (u.endswith('.json') or not node.get('children')):
  child=urllib.parse.urljoin(url,u);b=fetch(child)
  if b.lstrip().startswith(b'{'):
   j=json.loads(b);visit(j['root'],tr,child,depth+1)
  elif b[:4]==b'b3dm':
   magic,version,size,fj,fb,bj,bb=struct.unpack_from('<4s6I',b)
   assert version==1 and size==len(b)
   feature=json.loads(b[28:28+fj].rstrip(b'\x00 \n')) if fj else {}
   offset=28+fj+fb;batch=json.loads(b[offset:offset+bj].rstrip(b'\x00 \n')) if bj else {}
   glb=offset+bj+bb;gltf={}
   if b[glb:glb+4]==b'glTF':
    n,kind=struct.unpack_from('<II',b,glb+12)
    assert kind==0x4e4f534a
    gltf=json.loads(b[glb+20:glb+20+n])
   leaves.append({'path':urllib.parse.urlparse(child).path,'targets':selected,'featureTable':feature,'batchTable':batch,'gltfAsset':gltf.get('asset'),'gltfExtensionsUsed':gltf.get('extensionsUsed'),'gltfMeshCount':len(gltf.get('meshes',[])),'gltfNodeCount':len(gltf.get('nodes',[])),'gltfMeshNames':[x.get('name') for x in gltf.get('meshes',[])],'gltfNodeNames':[x.get('name') for x in gltf.get('nodes',[])],'transform':tr.flatten(order='F').tolist()})
  else:raise ValueError('Unsupported tile '+str(b[:4]))
 for c in node.get('children',[]):visit(c,tr,url,depth+1)

def main():
 output=DOC/'metadata.json';assert not output.exists()
 root=json.loads((DOC/'building-tileset.json').read_text())
 visit(root['root'],np.eye(4),BASE+'tileset.json',0)
 result={'documentation':'https://p1hosting.csdi.gov.hk/csdi-webpage/apidoc/3d-spatial-data-api','targetsHK1980Approximate':TARGETS,'targetECEFRoutingOnly':{k:v.tolist() for k,v in POINTS.items()},'routeAllowanceMetres':{'horizontal':10,'radialVertical':200},'files':records,'totalBytes':total,'leaves':leaves,'modelGeometryChanges':0,'installationApproved':False,'qualification':'Metadata research only. Route coordinates use EPSG2326 to ECEF with supplied approximate height; no vertical datum/pose equivalence or identity is established. Only terminal B3DM content is inspected; initial coarse-content probe stopped at 60 requests before creating a report.'}
 output.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'files':len(records),'bytes':total,'leaves':len(leaves),'batchKeys':[list(x['batchTable']) for x in leaves],'nodeNames':[x['gltfNodeNames'][:5] for x in leaves]},indent=2),flush=True)
if __name__=='__main__':main()
