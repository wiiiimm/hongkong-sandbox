"""Capture canonical failure face locations without changing foundation classification."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-source-285509-failure-locations-v1-20261022';DOC=BASE/BATCH;UID='landsd/285509:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)]
 def take(batch,path):
  _,pins=authenticate(BASE/batch);assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.extend([BASE/batch/'result.json',path]);return read(path)
 cap='government-xl-next-three-terrain-runtime-v1-20261021';row=next(r for r in take(cap,BASE/cap/'selection.json.gz')['rows']if r['uid']==UID);g=next(r for r in take(cap,HERE/'local'/cap/'runtime-geometry.json.gz')['rows']if r['uid']==UID);tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert g['sourceSHA256']==row['sourceSHA256']
 ground='government-xl-source-285509-adjacent-ground-v1-20261022';terrain=np.asarray(take(ground,HERE/'local'/ground/'combined-original-terrain.json.gz')['triangles']);expected=take(ground,BASE/ground/'summary.json')['combinedOriginalTerrainFoundation'];final=module('source285509_failure_locations',HERE/'xl-final-script-pass.py');original=final.connected_components;groups=[]
 def capture(t,mask):
  result=original(t,mask);groups.extend([np.asarray(c,dtype=int)for c in result]);return result
 final.connected_components=capture
 b=row['source']['building']
 try:actual=final.foundation_context(tri,terrain,Polygon(b['rings'][0],b['rings'][1:]))
 finally:final.connected_components=original
 assert actual==expected
 records=[]
 for ordinal,ids in enumerate(groups):
  faces=tri[ids];records.append(dict(group=ordinal,canonicalRuntimeFaceIds=ids.tolist(),triangles=faces.tolist(),bounds=[faces.min((0,1)).tolist(),faces.max((0,1)).tolist()],centroid=faces.mean((0,1)).tolist()))
 assert sum(len(r['canonicalRuntimeFaceIds'])for r in records)==expected['fullyBuriedTriangles']
 save(DOC/'failure-locations.json.gz',dict(uid=UID,sourceSHA256=row['sourceSHA256'],groups=records,faceIdentity='Exact current-runtime packed index order, not original glTF primitive identity',canonicalFoundationUnchanged=True))
 summary=dict(uids=[UID],failureGroups=len(records),failedFaces=sum(len(r['canonicalRuntimeFaceIds'])for r in records),sourceGeometryChanges=0,installationApproved=False,nextAction='Inspect mapped runtime faces against original source and terrain context; no intentional-basement or corruption inference from numeric failure alone.')
 refs.append(HERE/'xl-final-script-pass.py');module('source285509_locations_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'canonical-foundation-failure-location-diagnostic',refs,summary);print(summary,flush=True)
if __name__=='__main__':main()
