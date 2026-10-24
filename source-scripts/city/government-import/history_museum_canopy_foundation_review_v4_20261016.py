"""Qualify existing illustrative foundations separately from immutable source meshes."""
from pathlib import Path
import numpy as np,shapely
import subprocess
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-history-museum-canopy-foundation-review-v4-20261016';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-history-museum-canopy-posts-v2-20261016'
CAP=BASE/'government-xl-history-museum-repaired-ground-capture-v1-20261016'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'history_museum_canopy_foundation_review_v3_20261016.py',BASE/'government-xl-history-museum-canopy-foundation-review-v3-20261016/failed-worker.log',HERE/'history_museum_canopy_foundation_review_v2_20261016.py',BASE/'government-xl-history-museum-canopy-foundation-review-v2-20261016/failed-worker.log',HERE/'history_museum_canopy_foundation_review_v1_20261016.py',BASE/'government-xl-history-museum-canopy-foundation-review-v1-20261016/failed-worker.log'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PRIOR,CAP]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for q in r['evidenceRefs']:
    assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 b=read(PRIOR/'input.json')['building'];proposal=read(PRIOR/'proposal.json');proof=read(PRIOR/'render-proof.json');parts=read(PRIOR/'description.json')['parts'];assert b['uid']=='landsd/4760:0'and b['baseSource']=='terrain-estimated'and b['heightSource']=='estimated'and not b.get('modelGeometry');assert proof['roofPartsExactlyUnchanged']and proof['allXZExactlyUnchanged']and proof['onlyIllustrativePostBottomVerticesChanged'];assert all(p['kind']=='roof'or p['kind']=='post'and p['illustrative']for p in parts)
 geometry=CAP/'after-ground.json.gz';ground=np.asarray(read(geometry)['completeRelevantDrawnTriplets']).reshape(-1,3,3);polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;coverage=shapely.union_all(polys[valid]);rows=[]
 for part in parts:
  poly=Polygon(part['rings'][0],part['rings'][1:]);missing=poly.difference(coverage).area;heights=[];faceids=[]
  for i in np.flatnonzero(valid&shapely.intersects(polys,poly)):
   intersection=polys[i].intersection(poly)
   if intersection.area<=1e-10:continue
   coords=shapely.get_coordinates(intersection);a,c,d=ground[i];n=np.cross(c-a,d-a);ys=a[1]-(n[0]*(coords[:,0]-a[0])+n[2]*(coords[:,1]-a[2]))/n[1];heights.extend(ys.tolist());faceids.append(int(i))
  assert heights
  row=dict(kind=part['kind'],groundRange=[min(heights),max(heights)],completeClippedFaceIds=faceids,uncoveredAreaM2=missing,top=part['top'],bottom=proposal['foundationBase']if part['kind']=='post'else part['bottom'])
  if part['kind']=='post':row['foundationAtOrBelowAllGround']=proposal['foundationBase']<=min(heights)+.002;row['postTopAboveAllGround']=part['top']>max(heights)+.02
  else:row['wholeRoofAboveAllGround']=part['bottom']>max(heights)+.02
  rows.append(row)
 summary=dict(uid=b['uid'],exactExistingIllustrativeFoundationMechanismVerified=True,fullPostFootprintsMeetGround=all(x['uncoveredAreaM2']<1e-8 and x['foundationAtOrBelowAllGround'] and x['postTopAboveAllGround'] for x in rows if x['kind']=='post'),wholeRoofClear=all(x['uncoveredAreaM2']<1e-8 and x['wholeRoofAboveAllGround'] for x in rows if x['kind']=='roof'),roofCoverageGapM2=sum(x['uncoveredAreaM2'] for x in rows if x['kind']=='roof'),roofAndRecordedElevationsUnchanged=True,completePostCount=sum(x['kind']=='post'for x in rows),rawHalfMetreBottomDiagnosticRetained=read(PRIOR/'summary.json')['minimumPostGap'],interpretation='The existing foundationBase contract extends illustrative posts below terrain; buried footings are intentional. This qualification applies only to these exact non-native illustrative posts, never government-source facets or arbitrary building burial.',physicalStagingRequired=True,collisionAndVisualAcceptancePending=True,fullAcceptance=False,publication=False)
 DOC.mkdir();save(DOC/'continuous-part-ground-proof.json',dict(rows=rows));save(DOC/'summary.json',summary);test=subprocess.run(['node','--test','--test-reporter=tap','3d-viewer/city/tests/building-geometry.test.js'],cwd=ROOT,capture_output=True,check=True);(DOC/'building-geometry-tests.log').write_bytes(test.stdout+test.stderr);assert '# fail 0' in test.stdout.decode()
 refs += [geometry,PRIOR/'description.json',PRIOR/'proposal.json',PRIOR/'render-proof.json',ROOT/'3d-viewer/city/building-geometry.js',ROOT/'3d-viewer/city/tests/building-geometry.test.js',ROOT/'source-scripts/city/mui-wo-buildings/integrate.py'];out=module('museum_foundation_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'museum-existing-canopy-foundation-continuous-ground-qualification-v1',list(dict.fromkeys(refs)),dict(uids=[b['uid']],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],postCount=summary['completePostCount'],wholeRoofClear=summary['wholeRoofClear'],roofCoverageGapM2=summary['roofCoverageGapM2'],fullAcceptance=False),flush=True)
if __name__=='__main__':main()
