"""Qualify existing illustrative foundations separately from immutable source meshes."""
from pathlib import Path
import numpy as np,shapely
import subprocess
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-science-history-retained-canopy-review-v1-20261016';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-science-museum-canopy-posts-v1-20261016'
CAP=BASE/'government-xl-science-history-repaired-ground-capture-v1-20261016'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for q in r['evidenceRefs']:
    assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 b=next(r['building'] for r in read(CAP/'basic-actors.json.gz')['rows'] if r['uid']=='landsd/4760:0');assert b['baseSource']=='terrain-estimated' and b['heightSource']=='estimated' and b['foundationPolicy']=='terrain-derived-illustrative-posts'
 DOC.mkdir();save(DOC/'form.json',b);tool=HERE/'science_history_retained_canopy_describe_v1_20261016.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);parts=read(DOC/'description.json')['parts'];proposal=dict(foundationBase=b['foundationBase']);assert all(p['kind']=='roof' or p['kind']=='post' and p['illustrative'] for p in parts)
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
  else:
   # A roof spans air; only posts require terrain coverage. Include vertical/zero-area
   # drawn faces conservatively through their closed XZ bounding boxes.
   degenerate=[]
   for i in np.flatnonzero(~valid):
    lo=ground[i].min(axis=0);hi=ground[i].max(axis=0)
    if poly.intersects(shapely.box(lo[0],lo[2],hi[0],hi[2]).buffer(1e-9)):
     degenerate.append(int(i));heights.extend(ground[i,:,1].tolist())
   row['verticalOrDegenerateConservativeFaceIds']=degenerate
   row['groundRangeIncludingVerticals']=[min(heights),max(heights)]
   row['wholeRoofAboveAllGround']=part['bottom']>max(heights)+.02
  rows.append(row)
 summary=dict(uid=b['uid'],exactExistingIllustrativeFoundationMechanismVerified=True,roofCoverageRequired=False,roofCoverageRationale='An open-sided roof is elevated and may span air. Every post still requires complete terrain coverage; all intersecting drawn terrain including conservative vertical-face bounds must remain below the unchanged roof.',fullPostFootprintsMeetGround=all(x['uncoveredAreaM2']<1e-8 and x['foundationAtOrBelowAllGround'] and x['postTopAboveAllGround'] for x in rows if x['kind']=='post'),wholeRoofClear=all(x['wholeRoofAboveAllGround'] for x in rows if x['kind']=='roof'),roofCoverageGapM2=sum(x['uncoveredAreaM2'] for x in rows if x['kind']=='roof'),roofAndRecordedElevationsUnchanged=True,completePostCount=sum(x['kind']=='post'for x in rows),currentInstalledFoundationBase=b['foundationBase'],interpretation='The existing foundationBase contract extends illustrative posts below terrain; buried footings are intentional. This qualification applies only to these exact non-native illustrative posts, never government-source facets or arbitrary building burial.',physicalStagingRequired=True,collisionAndVisualAcceptancePending=True,fullAcceptance=False,publication=False)
 save(DOC/'continuous-part-ground-proof.json',dict(rows=rows));save(DOC/'summary.json',summary)
 refs += [geometry,CAP/'basic-actors.json.gz',tool,ROOT/'3d-viewer/city/building-geometry.js'];description=read(DOC/'description.json')
 for path,h in description['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
 out=module('museum_foundation_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'museum-existing-canopy-foundation-continuous-ground-qualification-v1',list(dict.fromkeys(refs)),dict(uids=[b['uid']],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],postCount=summary['completePostCount'],wholeRoofClear=summary['wholeRoofClear'],roofCoverageGapM2=summary['roofCoverageGapM2'],fullAcceptance=False),flush=True)
if __name__=='__main__':main()
