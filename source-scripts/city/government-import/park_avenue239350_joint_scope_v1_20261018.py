"""Read-only original-source joint terrain scope; no placement approval."""
from pathlib import Path
import shapely
from shapely.geometry import box
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-park-avenue239350-joint-scope-v1-20261018'
DOC=BASE/BATCH
def main():
 assert not DOC.exists()
 names=['current-identity-runtime-v3','companion-identity-runtime-v1','terrain-inputs-v1','native-scope-v1','identity-review-v1']
 folders={n:BASE/('government-xl-park-avenue239350-'+n+'-20261018') for n in names}
 pins={};refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py']
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in folders.values():
   receipt=read(folder/'result.json')
   assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
   refs.append(folder/'result.json')
   for e in receipt['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256']
    pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(folders['current-identity-runtime-v3']/'selection.json.gz')['rows']+read(folders['companion-identity-runtime-v1']/'selection.json.gz')['rows']
 assert {r['uid'] for r in rows}=={'landsd/239350:0','landsd/240161:0','landsd/227455:0'}
 parts=[]
 for row in rows:
  p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256']
  t=decode_original_world_triangles(p.read_bytes());assert len(t)==row['triangles']
  xz=t[:,:,[0,2]];parts.extend(shapely.polygons(xz))
  for i in range(3):parts.extend(shapely.linestrings(xz[:,[i,(i+1)%3],:]))
 projection=shapely.union_all(parts).buffer(.1)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest)
 entries={}
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;refs.append(p)
  for entry in read(p)['models']:
   assert entry['uid'] not in entries
   entries[entry['uid']]=entry
 parents=read(folders['terrain-inputs-v1']/'scope.json')['retainedParents'];affected=[];protected=[]
 for parent in parents:
  p=ROOT/'3d-viewer'/parent['url'];assert digest(p.read_bytes())==parent['sha256'];refs.append(p)
  for uid in parent['targetUids']:
   if uid not in entries:continue
   bounds=entries[uid]['worldBounds'];foot=box(bounds[0][0],bounds[0][2],bounds[1][0],bounds[1][2])
   overlap=foot.intersection(projection)
   (affected if not overlap.is_empty else protected).append(dict(uid=uid,intersectionAreaM2=overlap.area,sourceSHA256=entries[uid]['sha256']))
 scope=read(folders['native-scope-v1']/'scope.json')
 assert {e['uid'] for e in affected}<=set(scope['touchingNativeUids'])
 result=dict(uids=[r['uid'] for r in rows],jointReviewRequired=affected,unchangedBoundingBoxes=protected,requiredNativeUids=scope['touchingNativeUids'],publication=False,fullAcceptance=False,newlyInstalled=0,modelGeometryChanges=0)
 save(DOC/'scope.json',result)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins)
 out=module('joint_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'park-avenue-complete-three-source-joint-terrain-scope',list(set(refs)),result)
 print(dict(jobId=out['jobId'],jointReviewRequired=affected,requiredNativeCount=len(scope['touchingNativeUids'])),flush=True)
if __name__=='__main__':main()
