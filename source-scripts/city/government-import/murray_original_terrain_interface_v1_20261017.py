"""Exact source/terrain context for all Murray buried faces; no acceptance or geometry edits."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-murray-original-terrain-foundation-v3-20261017'
PHYSICAL=BASE/'government-xl-murray-current-pair-physical-v1-20261017'
BATCH='government-xl-murray-original-terrain-interface-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in {(e['path'],e['sha256'])for e in r['evidenceRefs']}:assert digest((ROOT/p).read_bytes())==h,p
 comparison=read(PRIOR/'flagged-face-comparison.json');files=[f for part in comparison['source'].values()for f in part['sourceFiles']]
 second=module('murray_context_decoder',HERE/'xl-second-pass.py');second.LOCAL=HERE/'local'/BATCH
 terrain=np.concatenate([second.terrain_triangles(ROOT/e['path'])for e in files if e['path'].endswith('.gltf')]);assert len(terrain)==611436
 rtpath=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';g=next(x for x in read(rtpath)['rows']if x['uid']=='landsd/248655:0')
 t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 lo,hi=t.min(axis=(0,1))-2,t.max(axis=(0,1))+2;ground=terrain[(terrain[:,:,0].max(axis=1)>=lo[0])&(terrain[:,:,0].min(axis=1)<=hi[0])&(terrain[:,:,2].max(axis=1)>=lo[2])&(terrain[:,:,2].min(axis=1)<=hi[2])]
 final=module('murray_context_foundation',HERE/'xl-final-script-pass.py');points=np.concatenate([t,t.mean(axis=1)[:,None,:]],axis=1)
 polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10
 heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),ground[valid],shapely.STRtree(polygons[valid])).reshape(-1,4)
 assert np.isfinite(heights).all();gaps=points[:,:,1]-heights;buried=(gaps<-.5).all(axis=1);assert int(buried.sum())==10
 cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(cross,axis=1)/2;normals=np.divide(cross,2*area[:,None],out=np.zeros_like(cross),where=area[:,None]>0)
 assert abs(float(area[buried].sum())-read(PRIOR/'foundation.json')['fullyBuriedAreaM2'])<1e-9
 from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify
 from fu_tor_loy_nearest_interfaces_v1_20261017 import nearest
 rows=[]
 for i in np.flatnonzero(buried):
  proof=verify(t[i],terrain);witnesses=[]
  for point in points[i]:
   j,q,d=nearest(point,terrain);n=np.cross(terrain[j,1]-terrain[j,0],terrain[j,2]-terrain[j,0]);length=np.linalg.norm(n)
   witnesses.append(dict(point=point.tolist(),hostFace=j,hostPoint=q.tolist(),distanceM=d,hostNormal=(n/length).tolist()if length else None))
  rows.append(dict(faceIndex=int(i),wholeFacetProof=proof,witnesses=witnesses));print(dict(faceIndex=int(i),wholeFacetWithinBand=proof['wholeFacetAssociated'],maximumWitnessDistance=max(w['distanceM']for w in witnesses)),flush=True)
 save(DOC/'interfaces.json.gz',dict(rows=rows,sourceSHA256=g['sourceSHA256'],originalTerrainTriangles=len(terrain),strictAcceptanceUnchanged=True,installationApproved=False))
 refs=[Path(__file__),PRIOR/'result.json',PRIOR/'flagged-face-comparison.json',PRIOR/'foundation.json',rtpath,HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',HERE/'exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py',HERE/'fu_tor_loy_nearest_interfaces_v1_20261017.py']+[ROOT/e['path']for e in files]
 refs.extend(p for p in (HERE/'local'/BATCH).rglob('*')if p.is_file())
 summary=dict(faces=len(rows),completeFacetAssociations=sum(x['wholeFacetProof']['wholeFacetAssociated']for x in rows),fullAcceptance=False)
 save(DOC/'summary.json',summary)
 out=module('murray_interface_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'murray-original-terrain-fixed-facet-interface-v1',refs,dict(uids=[g['uid']],sourceSHA256=g['sourceSHA256'],summary=summary,nextStep='Use exact finite-facet positive and negative evidence for source function review; no tolerance changes or contact acceptance from proximity alone.'))
 print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
