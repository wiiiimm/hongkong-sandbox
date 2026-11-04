"""Qualify existing illustrative foundations separately from immutable source meshes."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-history-museum-canopy-foundation-review-v1-20261016';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-history-museum-canopy-posts-v2-20261016'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p)
 b=read(PRIOR/'input.json')['building'];proposal=read(PRIOR/'proposal.json');proof=read(PRIOR/'render-proof.json');parts=read(PRIOR/'description.json')['parts'];assert b['uid']=='landsd/4760:0'and b['baseSource']=='terrain-estimated'and b['heightSource']=='estimated'and not b.get('modelGeometry');assert proof['roofPartsExactlyUnchanged']and proof['allXZExactlyUnchanged']and proof['onlyIllustrativePostBottomVerticesChanged'];assert all(p['kind']=='roof'or p['kind']=='post'and p['illustrative']for p in parts)
 geometry=HERE/'local/government-xl-history-museum-preserved-neighbours-v1-20261016/runtime-geometry.json.gz';ground=np.asarray(read(geometry)['rows'][0]['drawnGroundGeometry']).reshape(-1,3,3);polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;coverage=shapely.union_all(polys[valid]);rows=[]
 for part in parts:
  poly=Polygon(part['rings'][0],part['rings'][1:]);missing=poly.difference(coverage).area;assert missing<1e-8;heights=[];faceids=[]
  for i in np.flatnonzero(valid&shapely.intersects(polys,poly)):
   intersection=polys[i].intersection(poly)
   if intersection.area<=1e-10:continue
   coords=shapely.get_coordinates(intersection);a,c,d=ground[i];n=np.cross(c-a,d-a);ys=a[1]-(n[0]*(coords[:,0]-a[0])+n[2]*(coords[:,1]-a[2]))/n[1];heights.extend(ys.tolist());faceids.append(int(i))
  assert heights
  row=dict(kind=part['kind'],groundRange=[min(heights),max(heights)],completeClippedFaceIds=faceids,uncoveredAreaM2=missing,top=part['top'],bottom=proposal['foundationBase']if part['kind']=='post'else part['bottom'])
  if part['kind']=='post':row['foundationAtOrBelowAllGround']=proposal['foundationBase']<=min(heights)+.002;row['postTopAboveAllGround']=part['top']>max(heights)+.02;assert row['foundationAtOrBelowAllGround']and row['postTopAboveAllGround']
  else:row['wholeRoofAboveAllGround']=part['bottom']>max(heights)+.02;assert row['wholeRoofAboveAllGround']
  rows.append(row)
 summary=dict(uid=b['uid'],exactExistingIllustrativeFoundationMechanismVerified=True,fullPostFootprintsMeetGround=True,wholeRoofClear=True,roofAndRecordedElevationsUnchanged=True,completePostCount=sum(x['kind']=='post'for x in rows),rawHalfMetreBottomDiagnosticRetained=read(PRIOR/'summary.json')['minimumPostGap'],interpretation='The existing foundationBase contract extends illustrative posts below terrain; buried footings are intentional. This qualification applies only to these exact non-native illustrative posts, never government-source facets or arbitrary building burial.',physicalStagingRequired=True,collisionAndVisualAcceptancePending=True,fullAcceptance=False,publication=False)
 DOC.mkdir();save(DOC/'continuous-part-ground-proof.json',dict(rows=rows));save(DOC/'summary.json',summary);(DOC/'building-geometry-tests.log').write_bytes(Path('/tmp/museum-building-geometry-tests.log').read_bytes());assert '# fail 0' in (DOC/'building-geometry-tests.log').read_text()
 refs += [geometry,PRIOR/'description.json',PRIOR/'proposal.json',PRIOR/'render-proof.json',ROOT/'3d-viewer/city/building-geometry.js',ROOT/'3d-viewer/city/tests/building-geometry.test.js',ROOT/'source-scripts/city/mui-wo-buildings/integrate.py'];out=module('museum_foundation_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'museum-existing-canopy-foundation-continuous-ground-qualification-v1',list(dict.fromkeys(refs)),dict(uids=[b['uid']],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],postCount=summary['completePostCount'],wholeRoofClear=True,fullAcceptance=False),flush=True)
if __name__=='__main__':main()
