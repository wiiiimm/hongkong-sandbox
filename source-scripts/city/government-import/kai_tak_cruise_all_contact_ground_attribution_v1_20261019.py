"""Compare flagged faces against untouched adjoining government terrain. No acceptance."""
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pathlib import Path
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-kai-tak-cruise-all-contact-ground-attribution-v1-20261019';DOC=BASE/BATCH
CAP=BASE/'government-xl-kai-tak-cruise-expanded-parent-v3-20261019';FACES=BASE/'government-xl-kai-tak-cruise-contact-faces-v1-20261019'
def main():
 assert not DOC.exists(); refs=[Path(__file__)];pins={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,FACES]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:pins.setdefault(e['path'],set()).add(e['sha256'])
 paths=[FACES/'faces.json',HERE/'local/government-xl-next-five-adjoining-ground-v1-20261018/263423:0-ground.json.gz',HERE/'local'/CAP.name/'runtime-geometry.json.gz']
 for p in paths:assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))],p
 refs+=paths
 faces=read(paths[0]);native=np.asarray(read(paths[1])['completeAdjoiningTerrain']);g=read(paths[2])['rows'][0];assert g['sourceSHA256']==faces['sourceSHA256']
 triangles=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 polys=shapely.polygons(native[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;terrain=native[valid];tree=shapely.STRtree(polys[valid])
 final=module('kai_tak_original_ground_samples',HERE/'xl-final-script-pass.py');refs.append(HERE/'xl-final-script-pass.py')
 ids=sorted(set(faces['lowRimFaceIds'])|set(faces['intersectingFaceIds']));t=triangles[ids];points=np.concatenate([t,t.mean(1)[:,None,:]],axis=1);heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),terrain,tree).reshape(-1,4)
 assert np.isfinite(heights).all();gaps=points[:,:,1]-heights;originalById={x['faceId']:x for x in faces['faces']}
 records=[]
 for index,faceId in enumerate(ids):
  old=originalById[faceId];assert np.max(np.abs(t[index]-np.asarray(old['vertices'])))<1e-9
  records.append(dict(faceId=faceId,vertices=t[index].tolist(),normalYRatio=old['normalYRatio'],originalGovernmentTerrainHeights=heights[index].tolist(),originalGovernmentTerrainGaps=gaps[index].tolist(),candidateTerrainGaps=old['gaps'],fullyBuriedInOriginalGovernmentTerrain=bool((gaps[index]<-.5).all()),maximumTerrainDifferenceMetres=float(np.max(np.abs(gaps[index]-old['gaps'])))))
 summary=dict(uid=faces['uid'],sourceSHA256=faces['sourceSHA256'],flaggedFacesCompared=len(records),candidateFullyBuriedIds=faces['fullyBuriedFaceIds'],originalTerrainFullyBuriedIds=[x['faceId']for x in records if x['fullyBuriedInOriginalGovernmentTerrain']],maximumTerrainDifferenceMetres=max(x['maximumTerrainDifferenceMetres']for x in records),installationApproved=False,qualification='Historical captured source faces versus unchanged government adjoining terrain. Current placement, complete source support and publication still require separate verification.')
 vertices=np.unique(triangles.reshape(-1,3),axis=0)
 drawn=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);dp=shapely.polygons(drawn[:,:,[0,2]]);valid=shapely.area(dp)>1e-10
 vh=final.s.context.shared.samples(vertices[:,[0,2]],drawn[valid],shapely.STRtree(dp[valid]));assert np.isfinite(vh).all();vg=vertices[:,1]-vh;contacts=np.flatnonzero(np.abs(vg)<=.1);assert len(contacts)>0
 rim=vertices[:,1]<=faces['globalMinimumY']+.35
 summary.update(uniqueOriginalDrawnVertices=len(vertices),terrainContactCandidateVertices=len(contacts),globalLowRimVertices=int(rim.sum()),globalLowRimGapRange=[float(vg[rim].min()),float(vg[rim].max())],contactCandidatesAreNotSupportApproval=True)
 save(DOC/'contact-candidates.json.gz',dict(uid=faces['uid'],sourceSHA256=faces['sourceSHA256'],points=vertices[contacts].tolist(),gaps=vg[contacts].tolist(),installationApproved=False))
 save(DOC/'attribution.json',dict(summary=summary,faces=records));print(summary,flush=True)
 module('kai_tak_ground_attribution_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-cruise-all-contact-original-government-terrain-attribution',refs,dict(uids=[faces['uid']],summary=summary,installationApproved=False))
if __name__=='__main__':main()
