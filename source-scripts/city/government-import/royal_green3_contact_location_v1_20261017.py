"""Locate exact residual contact on current private candidate and original TIN; no tolerance changes."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-royal-green3-retained-terrain-v1-20261017';BATCH='government-xl-royal-green3-contact-location-v1-20261017';DOC=BASE/BATCH
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256']
 rtpath=HERE/'local'/PRIOR.name/'runtime-geometry.json.gz';rt=read(rtpath);assert len(rt['rows'])==1;g=rt['rows'][0];assert g['uid']=='landsd/11093:0';t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
 second=module('royal_green_second',HERE/'xl-second-pass.py');second.LOCAL=HERE/'local'/BATCH;points,bottom=second.resolution.sample_points(g)
 def samples(mesh,points):
  polys=shapely.polygons(mesh[:,:,[0,2]]);valid=shapely.area(polys)>1e-10
  return second.context.shared.samples(points[:,[0,2]],mesh[valid],shapely.STRtree(polys[valid]))
 heights=samples(ground,points);gaps=points[:,1]-heights;assert np.isfinite(gaps).all();metrics=read(PRIOR/'metrics.json')['rows'][0];assert abs(float(gaps.min())-metrics['minSurfaceGap'])<1e-7,(float(gaps.min()),metrics['minSurfaceGap'])
 bad=np.flatnonzero(gaps<-.5);assert len(bad)>0
 recovery=read(PRIOR/'source-recovery.json');sources=[];refs=[Path(__file__),PRIOR/'result.json',PRIOR/'metrics.json',PRIOR/'source-recovery.json',rtpath,HERE/'xl-second-pass.py',HERE/'resolve-pass.py']
 for sheet in recovery['sheets']:
  folder=ROOT/sheet['cache'];proof=read(folder/'original/download.json');assert proof['directorySHA256']==sheet['directorySHA256'];refs.append(folder/'original/download.json')
  for e in sheet['terrainFiles']:
   p=folder/'terrain'/e['name'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
   if p.suffix=='.gltf':sources.append(second.terrain_triangles(p))
 original=np.concatenate(sources);original_heights=samples(original,points[bad]);assert np.isfinite(original_heights).all()
 rows=[]
 for k,i in enumerate(bad):
  p=points[i];incident=[]
  for j,face in enumerate(t):
   a,b,c=face;u=b-a;v=c-a;n=np.cross(u,v);n2=np.dot(n,n)
   if n2 and abs(np.dot(p-a,n))/np.sqrt(n2)<1e-7:
    w=p-a;aa=np.dot(u,u);bb=np.dot(v,v);ab=np.dot(u,v);det=aa*bb-ab*ab
    if det>0:
     s=(np.dot(w,u)*bb-np.dot(w,v)*ab)/det;q=(np.dot(w,v)*aa-np.dot(w,u)*ab)/det
     if s>=-1e-8 and q>=-1e-8 and s+q<=1+1e-8:incident.append(j)
  rows.append(dict(sampleIndex=int(i),position=p.tolist(),candidateGapM=float(gaps[i]),originalTerrainGapM=float(p[1]-original_heights[k]),candidateMinusOriginalTerrainM=float(heights[i]-original_heights[k]),incidentOriginalFaces=incident))
 save(DOC/'contacts.json.gz',dict(uid=g['uid'],sourceSHA256=g['sourceSHA256'],rows=rows,checks=len(points),rawMinimumGapM=float(gaps.min()),installationApproved=False));summary=dict(failingSamples=len(rows),minimumCandidateGapM=float(gaps.min()),minimumOriginalGapAtFailuresM=min(x['originalTerrainGapM']for x in rows),maximumCandidateOriginalDifferenceM=max(abs(x['candidateMinusOriginalTerrainM'])for x in rows),fullAcceptance=False)
 out=module('royal_contact_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'royal-green3-exact-residual-contact-location-v1',refs,dict(uids=[g['uid']],summary=summary,nextStep='Use exact original versus candidate terrain attribution to resolve the residual contact without shifting source or relaxing fixed thresholds.'))
 print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
