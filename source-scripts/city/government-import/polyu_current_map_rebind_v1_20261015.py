"""Bind completed PolyU finite evidence to current, spatially disjoint installations."""
from pathlib import Path
import gzip,json,struct
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-current-map-rebind-v1-20261015';DOC=BASE/BATCH
NAMES=['government-xl-polyu-complete-saved-actor-finite-v2-20261014','government-xl-polyu-whole-actor-current-ground-delta3-v1-20261014','government-xl-polyu-refined-candidate-overlap-max-v1-20261014','government-xl-polyu-refined-candidate-metadata-validator-v1-20261014']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def packed_positions(raw):
 data=gzip.decompress(raw);magic,version,total=struct.unpack_from('<III',data);assert magic==0x46546c67 and version==2 and total==len(data)
 size,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a;doc=json.loads(data[20:20+size]);n,k=struct.unpack_from('<II',data,20+size);assert k==0x004e4942;binary=data[28+size:];assert len(binary)==n
 parts=[]
 def visit(i,parent,ancestors):
  assert i not in ancestors;n=doc['nodes'][i];assert not any(k in n for k in ['translation','rotation','scale'])
  matrix=parent@np.asarray(n.get('matrix',np.eye(4).reshape(-1,order='F')),float).reshape(4,4,order='F')
  if 'mesh'in n:
   for p in doc['meshes'][n['mesh']]['primitives']:
    a=doc['accessors'][p['attributes']['POSITION']];v=doc['bufferViews'][a['bufferView']];assert a['componentType']==5126 and a['type']=='VEC3' and not a.get('sparse') and not a.get('normalized') and v['buffer']==0
    xyz=np.ndarray((a['count'],3),dtype='<f4',buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',12),4)).astype(float)
    world=(np.c_[xyz,np.ones(len(xyz))]@matrix.T)[:,:3]+[-834500,0,816500];parts.extend([world,world.astype(np.float32).astype(float)])
  for child in n.get('children',[]):visit(child,matrix,ancestors|{i})
 for i in doc['scenes'][doc.get('scene',0)]['nodes']:visit(i,np.eye(4),set())
 v=np.concatenate(parts);assert np.isfinite(v).all();return [float(v[:,0].min()),float(v[:,2].min()),float(v[:,0].max()),float(v[:,2].max())]
def main():
 assert not DOC.exists()
 folders=[BASE/n for n in NAMES];installs=[BASE/n for n in ['government-xl-heritage165054-original-installed-v2-20261015','government-xl-esplanade-original-installed-v2-20261015','government-xl-primrose-original-installed-v1-20261015']]
 receipts=[read(d/'result.json')for d in folders+installs]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for r in receipts:assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 refs={(q['path'],q['sha256']):q for r in receipts[:len(folders)]for q in r['evidenceRefs']};backups={}
 for d in installs:
  for q in read(d/'historical-input-context.json')['mutableCurrentByteSnapshots']:backups[(q['originalPath'],q['originalSHA256'])]=q['savedHistoricalBytes']
 paths=[];changed=[]
 for key,q in refs.items():
  if ref(ROOT/q['path'])==q:paths.append(ROOT/q['path']);continue
  backup=backups[key];assert ref(ROOT/backup['path'])==backup and backup['sha256']==q['sha256'];paths.extend([ROOT/backup['path'],ROOT/q['path']]);changed.append(dict(previous=q,exactHistoricalBytes=backup,current=ref(ROOT/q['path'])))
 allowed={'3d-viewer/city/data/manifest.json','3d-viewer/city/data/tiles/1_-6.json','docs/astra-city/model-integration-20260909/current-source-review.json'}
 assert {q['previous']['path']for q in changed}<=allowed
 manifest=ROOT/'3d-viewer/city/data/manifest.json';oldref=next(q for q in changed if q['previous']['path']==str(manifest.relative_to(ROOT)));old=read(ROOT/oldref['exactHistoricalBytes']['path']);new=read(manifest)
 assert {k for k in old.keys()|new.keys()if old.get(k)!=new.get(k)}=={'officialModelCatalogues','terrainPatches','tiles'}
 assert new['officialModelCatalogues'][:-3]==old['officialModelCatalogues']and new['terrainPatches'][:-3]==old['terrainPatches']
 roi=read(folders[0]/'complete-full-actor-current-candidate-finite.json.gz')['completeWholeActorROI']
 def outside(b):return b[2]<roi[0]or b[0]>roi[2]or b[3]<roi[1]or b[1]>roi[3]
 assert len(old['tiles'])==len(new['tiles']);tc=[(a,b)for a,b in zip(old['tiles'],new['tiles'])if a!=b];assert len(tc)==1
 a,b=tc[0];assert a['url']==b['url']=='city/data/tiles/1_-6.json'and outside(a['bounds']);assert {k:v for k,v in a.items()if k!='bytes'}=={k:v for k,v in b.items()if k!='bytes'}
 added=[]
 for url in new['officialModelCatalogues'][-3:]:
  p=ROOT/'3d-viewer'/url;paths.append(p)
  for m in read(p)['models']:
   asset=p.parent/m['asset'];assert ref(asset)['sha256']==m['sha256'];bounds=packed_positions(asset.read_bytes());assert outside(bounds);paths.append(asset);added.append(dict(uid=m['uid'],completePackedPositionBounds=bounds,sourceSHA256=m['sha256']))
 assert len(added)==7
 patches=[]
 for e in new['terrainPatches'][-3:]:
  p=ROOT/'3d-viewer'/e['url'];assert ref(p)['sha256']==e['sha256'];v=np.asarray(read(p)['nativeMesh']['position']).reshape(-1,3);bounds=[float(v[:,0].min()),float(v[:,2].min()),float(v[:,0].max()),float(v[:,2].max())];assert outside(bounds);patches.append(dict(file=ref(p),bounds=bounds));paths.append(p)
 paths += [d/'result.json'for d in folders+installs]+[d/'historical-input-context.json'for d in installs]+[Path(__file__)]
 DOC.mkdir();save(DOC/'reconciliation.json',dict(currentManifest=ref(manifest),changedReferences=changed,completeWholeActorROI=roi,addedModels=added,addedTerrain=patches,changedTileOutsideROI=True,allOtherEvidenceBytesUnchanged=True,currentLocalFiniteEvidenceReusable=True,fullAcceptance=False,publication=False))
 module('polyu_rebind_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-polyu-local-evidence-binding-v1',paths,dict(uids=['landsd/305582:0'],fullAcceptance=False,currentMapReconciled=True))
 print('Completed current PolyU evidence binding',flush=True)
if __name__=='__main__':main()
