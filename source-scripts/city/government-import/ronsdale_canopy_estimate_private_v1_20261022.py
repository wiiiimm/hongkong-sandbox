"""Private terrain-derived base estimates for two unsurveyed BASIC structures."""
from pathlib import Path
import copy,subprocess
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-canopy-estimate-private-v1-20261022';DOC=BASE/BATCH
SRC=BASE/'government-xl-ronsdale-basic-support-v1-20261022';UIDS=['landsd/307560:0']
def main():
 assert not DOC.exists();refs=[Path(__file__),SRC/'result.json'];receipt=read(SRC/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};p=SRC/'input.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);support=read(p);rows={r['uid']:r for r in support['rows']};podium=np.asarray(support['podium']);final=module('plaza_estimated_base_surface',HERE/'xl-final-script-pass.py')
 manifest=ROOT/'3d-viewer/city/data/manifest.json';tile=ROOT/'3d-viewer/city/data/tiles/1_0.json';mh=digest(manifest.read_bytes());th=digest(tile.read_bytes());refs.extend([manifest,tile]);data=read(tile);forms={b['uid']:b for b in data['buildings']};updates=[];staged=copy.deepcopy(data)
 installed=set()
 for url in read(manifest)['officialModelCatalogues']:
  cp=ROOT/'3d-viewer'/url;installed.update(e['uid']for e in read(cp)['models'])
 assert not set(UIDS)&installed
 for uid in UIDS:
  b=forms[uid];assert b['baseSource']=='terrain-estimated'and b['heightSource']=='estimated'and b['baseHeightHKPD']is None and b['topHeightHKPD']is None and not b.get('modelGeometry')
  points=[]
  for ring in b['rings']:
   for a,z in zip(ring,ring[1:]+ring[:1]):
    count=max(1,int(np.ceil(np.linalg.norm(np.asarray(z)-a)/.5)))
    points.extend((np.asarray(a)+(np.asarray(z)-a)*k/count).tolist()for k in range(count))
  points=np.unique(np.asarray(points),axis=0);g=np.concatenate([podium,np.asarray(rows[uid]['drawnGroundGeometry']).reshape(-1,3,3)]);polygons=shapely.polygons(g[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;g,polygons=g[valid],polygons[valid]
  heights=final.s.context.shared.samples(points,g,shapely.STRtree(polygons));assert np.isfinite(heights).all();estimate=float(np.min(heights));new=next(x for x in staged['buildings']if x['uid']==uid);new['base']=estimate;assert {k:v for k,v in new.items()if k!='base'}=={k:v for k,v in b.items()if k!='base'}
  updates.append(dict(uid=uid,previousBase=b['base'],proposedBase=estimate,delta=estimate-b['base'],height=b['height'],surveyBase=None,surveyTop=None,baseSource=b['baseSource'],sampleCount=len(points),minimumSurfaceHeight=estimate,maximumSurfaceHeight=float(np.max(heights)),surfaceSamples=dict(points=points.tolist(),heights=heights.tolist()),qualification='Candidate estimate from the corrected upper support surface at footprint edges sampled every <=0.5m. Not an exact continuous footprint minimum or installation acceptance. Native assets, surveyed records, footprints and estimated heights remain unchanged.'))
 save(DOC/'estimated-bases.json',dict(buildings=updates,installationApproved=False));private=DOC/'private-tile.json';save(private,staged)
 save(DOC/'basic-input.json',dict(manifestSHA256=mh,currentInputHashes={str(tile.relative_to(ROOT)):th,str(private.relative_to(ROOT)):digest(private.read_bytes())},rows=[dict(building=next(x for x in staged['buildings']if x['uid']==uid),tile=str(private.relative_to(ROOT)))for uid in UIDS]))
 capturetool=HERE/'xl-one-peking-current-foreign-basic-tower-geometry-v1-20261010.mjs';subprocess.run(['node',str(capturetool),str((DOC/'basic-input.json').relative_to(ROOT)),str((DOC/'basic-geometry.json').relative_to(ROOT))],cwd=ROOT,check=True);capture=read(DOC/'basic-geometry.json');prepared=[]
 for r in capture['rows']:prepared.append(dict(**r,drawnGroundGeometry=rows[r['uid']]['drawnGroundGeometry']))
 save(DOC/'input.json.gz',dict(podium=podium.tolist(),rows=prepared));tool=HERE/'plaza_ascot_basic_combined_support_v1_20261020.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);proof=read(DOC/'support.json.gz');summary=[]
 for r in prepared:
  tri=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];b=r['currentBuilding'];g=np.concatenate([podium,np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3)]);foundation=final.foundation_context(tri,g,shapely.Polygon(b['rings'][0],b['rings'][1:]));save(DOC/(r['uid'].split('/')[1]+'-foundation.json'),foundation);interface=next(x['proof']for x in proof['rows']if x['uid']==r['uid']);summary.append(dict(uid=r['uid'],supportPassed=interface['passed'],samples=interface['samples'],strictContacts=interface['strictContacts'],wallIntersections=interface['wallIntersections'],unresolved=len(interface['unresolved']),completeFoundationFaces=foundation['completeTerrainTriangles'],faces=len(tri),buried=foundation['fullyBuriedTriangles'],upwardBuried=foundation['fullyBuriedUpwardTriangles']))
 for c in [capture,proof]:
  for p,h in c['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 assert digest(manifest.read_bytes())==mh and digest(tile.read_bytes())==th
 result=dict(uids=UIDS,rows=summary,privateEstimatedBaseChanges=1,productionChanges=0,governmentGeometryChanges=0,installationApproved=False)
 save(DOC/'summary.json',result);refs.extend([tool,capturetool,HERE/'xl-final-script-pass.py']);module('plaza_private_base_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-unsurveyed-basic-private-base-estimates-and-renderer-checks',list(dict.fromkeys(refs)),result);print(summary,flush=True)
if __name__=='__main__':main()
