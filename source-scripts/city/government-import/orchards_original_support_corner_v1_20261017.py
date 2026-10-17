"""All original podium layers at the sole strict support failure; no waiver."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-orchards-original-podium-support-v1-20261017';POD=BASE/'government-xl-orchards-podium-original-recovery-v1-20261017';BATCH='government-xl-orchards-original-support-corner-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256']
 failures=read(PRIOR/'support-checks.json.gz')['rows'][0]['unresolved'];assert len(failures)==1;p=np.array(failures[0]['position']);row=read(POD/'selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());hits=[]
 for i,face in enumerate(tri):
  a,b,c=face;matrix=np.array([(b-a)[[0,2]],(c-a)[[0,2]]]).T;det=np.linalg.det(matrix)
  if abs(det)<1e-12:continue
  q=np.linalg.solve(matrix,(p-a)[[0,2]])
  if q.min()>=-1e-10 and q.sum()<=1+1e-10:
   n=np.cross(b-a,c-a);n/=np.linalg.norm(n);hits.append(dict(face=i,height=float(a[1]+q[0]*(b[1]-a[1])+q[1]*(c[1]-a[1])),normal=n.tolist(),vertices=face.tolist()))
 save(DOC/'corner.json',dict(failure=failures[0],podiumSourceSHA256=row['sourceSHA256'],allPodiumFacesExamined=len(tri),intersectingLayers=hits,diagnosticFloatingBarycentrics=True,fullAcceptance=False))
 result=module('orchards_corner_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'orchards-original-podium-single-corner-all-layers-v1',[Path(__file__),PRIOR/'result.json',PRIOR/'support-checks.json.gz',POD/'selection.json.gz',asset,HERE/'exact_packed_world_geometry_20261009.py'],dict(uids=['landsd/254629:0','landsd/233002:0'],fullAcceptance=False,summary=dict(intersectingLayers=len(hits),supportPointY=float(p[1]),highestSurfaceY=max(h['height']for h in hits)),nextStep='Interpret exact upper strip628 against original pillar faces1032/1035; neither available layer passes strict point contact. Retain raw failure and unchanged0.5m allowance. No corruption or permanent disposition follows.'))
 print(result['jobId'])
if __name__=='__main__':main()
