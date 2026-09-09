"""Reproducible HKS-225 lightweight trial; no AI calls or source downloads."""
import gzip,hashlib,json,sqlite3,struct
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'3d-viewer/city/data/whampoa-light-trial';HERE=Path(__file__).parent
read=lambda p:json.loads(p.read_bytes())
def write(p,data):p.write_text(json.dumps(data,separators=(',',':'))+'\n')
def simplify(path,out,cell=1.0):
 raw=gzip.decompress(path.read_bytes());n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);binary=raw[28+n:];primitive=doc['meshes'][0]['primitives'][0]
 def attr(i):
  a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];dtype={5126:'<f4',5123:'<u2',5125:'<u4',5121:'u1'}[a['componentType']];width={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']]
  return np.ndarray((a['count'],width),dtype=dtype,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',np.dtype(dtype).itemsize*width),np.dtype(dtype).itemsize)).copy()
 positions=attr(primitive['attributes']['POSITION']);faces=attr(primitive['indices']).reshape(-1,3)
 # Weld coincident vertices, then cluster lower surfaces on a fixed metre grid.
 # Preserve the upper 20% of elevation individually to retain the ship's mast.
 keys=np.floor(positions/cell).astype('int64');keep=positions[:,2]>positions[:,2].min()+np.ptp(positions[:,2])*.8
 mapping={};groups=[];indices=[]
 for i,k in enumerate(keys):
  key=('tip',*positions[i].tolist()) if keep[i] else tuple(k.tolist())
  if key not in mapping:mapping[key]=len(groups);groups.append([])
  groups[mapping[key]].append(i);indices.append(mapping[key])
 vertices=np.array([positions[g].mean(axis=0) for g in groups],dtype='<f4');remap=np.array(indices);tri=remap[faces];tri=tri[(tri[:,0]!=tri[:,1])&(tri[:,0]!=tri[:,2])&(tri[:,1]!=tri[:,2])]
 # Preserve winding; remove only identical faces.
 tri=np.unique(tri,axis=0);area=np.linalg.norm(np.cross(vertices[tri[:,1]]-vertices[tri[:,0]],vertices[tri[:,2]]-vertices[tri[:,0]]),axis=1);tri=tri[area>1e-7]
 used,inv=np.unique(tri,return_inverse=True);vertices=vertices[used];tri=inv.reshape(-1,3).astype('<u4')
 normals=np.zeros_like(vertices);fn=np.cross(vertices[tri[:,1]]-vertices[tri[:,0]],vertices[tri[:,2]]-vertices[tri[:,0]])
 for j in range(3):np.add.at(normals,tri[:,j],fn)
 length=np.linalg.norm(normals,axis=1);normals/=np.maximum(length[:,None],1e-10)
 chunks=[vertices.tobytes(),normals.tobytes(),tri.tobytes()];offset=0;views=[]
 for b in chunks:views.append({'buffer':0,'byteOffset':offset,'byteLength':len(b)});offset+=len(b)
 doc['bufferViews']=views;doc['buffers']=[{'byteLength':offset}];doc['accessors']=[{'bufferView':0,'componentType':5126,'count':len(vertices),'type':'VEC3','min':vertices.min(0).tolist(),'max':vertices.max(0).tolist()},{'bufferView':1,'componentType':5126,'count':len(vertices),'type':'VEC3'},{'bufferView':2,'componentType':5125,'count':tri.size,'type':'SCALAR'}]
 primitive['attributes']={'POSITION':0,'NORMAL':1};primitive['indices']=2
 j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*((-len(j))%4);b=b''.join(chunks);b+=b'\0'*((-len(b))%4)
 result=struct.pack('<III',0x46546c67,2,28+len(j)+len(b))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(b),0x004e4942)+b
 packed=gzip.compress(result,mtime=0);out.write_bytes(packed)
 return {'asset':out.name,'bytes':len(packed),'triangles':len(tri),'vertices':len(vertices),'sha256':hashlib.sha256(packed).hexdigest(),'sourceSHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'cellMetres':cell,'maxVertexDisplacement':float(np.linalg.norm(np.array([positions[g].mean(0) for g in groups])[remap]-positions,axis=1).max())}

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 c=sqlite3.connect('file:'+str(ROOT/'source-scripts/city/building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
 culture=read(ROOT/'3d-viewer/city/data/official-models/cultural-landmarks/catalogue.json')
 extra=[m['uid'] for m in culture['models']]
 rows=[dict(r) for r in c.execute("select uid,name,zh,base,height,x,z,rings_json,csuid from buildings where active=1 and (uid in ('landsd/144948:0','landsd/225581:0','landsd/324574:0') or name like 'Whampoa Garden Bamboo Mansions Block %') order by uid")]
 rows += [dict(r) for r in c.execute('select uid,name,zh,base,height,x,z,rings_json,csuid from buildings where active=1 and uid in ('+','.join('?'for _ in extra)+')',extra)]
 for r in rows:r['rings']=json.loads(r.pop('rings_json'))
 groups=[{'id':'ship','name':'The Whampoa','uids':['landsd/144948:0','landsd/225581:0']},{'id':'site8','name':'Site 8 · Whampoa Plaza','uids':['landsd/324574:0']},{'id':'site12','name':'Site 12 · Bamboo Mansions','uids':[r['uid']for r in rows if 'Bamboo Mansions' in r['name']]}]
 groups += [{'id':'cultural','name':'Hong Kong Cultural Centre','uids':[m['uid']for m in culture['models']if 'SPACE MUSEUM' not in m.get('label','')]},{'id':'museum','name':'Hong Kong Space Museum','uids':[m['uid']for m in culture['models']if 'SPACE MUSEUM' in m.get('label','')]}]
 assert len(groups[2]['uids'])==9
 catalogue=read(ROOT/'3d-viewer/city/data/official-models/whampoa-special/catalogue.json');light=[]
 for m in catalogue['models']:
  name=m['uid'].replace('/','-').replace(':','-')+'.glb.gz';result=simplify(ROOT/'3d-viewer/city/data/official-models/whampoa-special'/m['asset'],OUT/name)
  light.append({**result,'uid':m['uid']})
 references={'ship':{'high':catalogue['models'],'light':light,'prefix':'city/data/official-models/whampoa-special/','rootTranslation':catalogue['rootTranslation']}}
 for group in groups[3:]:
  high=[m for m in culture['models']if m['uid']in group['uids']];low=[]
  for m in high:
   name=m['uid'].replace('/','-').replace(':','-')+'.glb.gz';result=simplify(ROOT/'3d-viewer/city/data/official-models/cultural-landmarks'/m['asset'],OUT/name);low.append({**result,'uid':m['uid']})
  references[group['id']]={'high':high,'light':low,'prefix':'city/data/official-models/cultural-landmarks/','rootTranslation':culture['rootTranslation']}
 basic={'groups':groups,'buildings':rows};write(OUT/'basic.json',basic)
 manifest={'generatorSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'shaderSHA256':hashlib.sha256((ROOT/'3d-viewer/city/whampoa-comparison.js').read_bytes()).hexdigest(),'aiCalls':0,'issue':'HKS-225','references':references,'groups':groups,'lightShip':light,'highShip':catalogue,'basicBytes':(OUT/'basic.json').stat().st_size,'basicGzipBytes':len(gzip.compress((OUT/'basic.json').read_bytes(),mtime=0)),'method':'1m vertex clustering with preserved upper silhouette for ship; footprint-preserving procedural facades for sites','newHighPass':'pending user effort switch','sources':['https://www.rvd.gov.hk/doc/en/urban.pdf','https://www.rvd.gov.hk/doc/en/urban_201504.pdf'],'limits':['Native high is existing government geometry, not a new high-effort generation.','Site 8 membership currently includes named Gourmet Place component; ancillary structures require high-pass review.','Site 12 includes nine named towers; shared podium/landscaping membership remains for high-pass review.','Procedural facade spacing/materials are illustrative, not surveyed.','Cultural Centre study includes seven detailed source components; six separately unmatched canopies remain outside this bounded comparison.','Ship simplification may remove small details and is not approved for the city.']}
 write(OUT/'manifest.json',manifest);write(HERE/'targets.json',{'issue':'HKS-225','groups':groups,'sources':manifest['sources'],'status':'light-trial; high-next'})
 print(json.dumps({'shipHighBytes':sum(m['bytes']for m in catalogue['models']),'shipLightBytes':sum(m['bytes']for m in light),'shipHighTriangles':sum(m['triangles']for m in catalogue['models']),'shipLightTriangles':sum(m['triangles']for m in light),'selectedForms':len(rows)}))
if __name__=='__main__':main()
