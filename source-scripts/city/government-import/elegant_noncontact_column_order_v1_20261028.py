"""Resolve complete projected-column ordering for two noncontact original pairs."""
import argparse,sys,uuid
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_closed_projection_intersection_20261010 import intersection
from exact_original_projection_coverage_20261009 import signed_area
from exact_original_triangle_pair_column_gap_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-elegant-garden-'
PAIRS=[['landsd/236170:0','landsd/236367:0'],['landsd/173764:0','landsd/224121:0']]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert a.batch.startswith(PREFIX)and '/'not in a.batch
 out,local=BASE/a.batch,HERE/'local'/a.batch;assert not out.exists()
 rp=BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json');resources=set(read(rp)['resources']);lp=local/'reservation.json'
 if not a.owned:
  assert not local.exists();claim=reservations.claim('noncontact-original-column-order-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(PREFIX+'sixteen-original-updated-runtime-v1-20261028','selection.json.gz');sources={r['uid']:r for r in selection['rows']};attrs={r['uid']:r for r in take(PREFIX+'sixteen-original-final-attributes-v1-20261028','attributes.json.gz')['rows']}
 contacts=take(PREFIX+'active-boundary-contacts-v1-20261028','summary.json');worlds={}
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 for uid in sorted({u for pair in PAIRS for u in pair}):
  row=sources[uid];attr=attrs[uid];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
  index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);worlds[uid]={'original':decode_original_world_triangles(asset.read_bytes())}
  for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[uid][mode]=np.asarray(attr[field]).reshape(-1,3)[index]
 rows=[]
 for left,right in PAIRS:
  for mode in ['original','literal','leftF32','balancedF32']:
   ta,tb=worlds[left][mode],worlds[right][mode];prior=next(r for r in contacts['rows']if r['sourceUid']==left and r['otherUid']==right and r['mode']==mode);assert prior['contacts']==0
   assert digest(ta.astype('<f8').tobytes())==prior['sourceWorldSHA256']and digest(tb.astype('<f8').tobytes())==prior['otherWorldSHA256']
   blo,bhi=tb[:,:,[0,2]].min(1),tb[:,:,[0,2]].max(1);pairs=[];candidates=0;directions=Counter();positive_directions=Counter();lp_count=0
   for i,fa in enumerate(ta):
    xy=fa[:,[0,2]];ids=np.flatnonzero(np.all(bhi>=xy.min(0),axis=1)&np.all(blo<=xy.max(0),axis=1))
    for j in ids:
     j=int(j);fb=tb[j];candidates+=1;poly=intersection(xy.tolist(),fb[:,[0,2]].tolist())
     if not poly:continue
     area=abs(signed_area(poly));low=F(float(fa[:,1].min()))-F(float(fb[:,1].max()));high=F(float(fa[:,1].max()))-F(float(fb[:,1].min()));proof=None
     if low>0:direction='source-above-other';contract='strict-whole-facet-vertical-bound'
     elif high<0:direction='source-below-other';contract='strict-whole-facet-vertical-bound'
     else:
      proof=verify(fa,fb);reverse=verify(fb,fa);assert proof['exactClosedHorizontalProjectionsMeet']and reverse['exactClosedHorizontalProjectionsMeet'];low=F(proof['exactMinimumFiniteColumnGapM']);high=-F(reverse['exactMinimumFiniteColumnGapM']);lp_count+=1
      assert low>0 or high<0,'Column-zero contact contradicts the complete exact primitive contact result'
      direction='source-above-other'if low>0 else 'source-below-other';contract='exact-finite-barycentric-column-order'
      proof=dict(forward=proof,reverse=reverse)
     directions[direction]+=1
     if area:positive_directions[direction]+=1
     pairs.append(dict(sourceFace=i,otherFace=j,exactProjectedIntersection=[[str(v)for v in p]for p in poly],exactProjectedIntersectionAreaM2=str(area),direction=direction,contract=contract,exactGapLowerBoundM=str(low),exactGapUpperBoundM=str(high),finiteColumnProof=proof))
   file=left.split('/')[1]+'--'+right.split('/')[1]+'--'+mode+'.json.gz';save(out/file,dict(sourceUid=left,otherUid=right,mode=mode,completeSourceFaces=len(ta),completeOtherFaces=len(tb),inclusiveXZCandidatePairs=candidates,exactClosedProjectionPairs=len(pairs),exactPositiveAreaProjectionPairs=sum(F(r['exactProjectedIntersectionAreaM2'])>0 for r in pairs),directions=dict(directions),positiveAreaDirections=dict(positive_directions),finiteColumnLPs=lp_count,allSourceAndOtherPrimitivesConsidered=True,rows=pairs,sourceGeometryChanges=0))
   row=dict(sourceUid=left,otherUid=right,mode=mode,proof=file,completeSourceFaces=len(ta),completeOtherFaces=len(tb),sourceWorldSHA256=prior['sourceWorldSHA256'],otherWorldSHA256=prior['otherWorldSHA256'],inclusiveXZCandidatePairs=candidates,exactClosedProjectionPairs=len(pairs),exactPositiveAreaProjectionPairs=sum(F(r['exactProjectedIntersectionAreaM2'])>0 for r in pairs),directions=dict(directions),positiveAreaDirections=dict(positive_directions),finiteColumnLPs=lp_count,physicalAccepted=False)
   rows.append(row);print(row,flush=True)
 result=dict(uids=sorted(worlds),rows=rows,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,publication=False,qualification='All inclusive XZ candidates are tested by exact closed projected primitive intersection, retaining collapsed faces and boundary points. Every common finite column is strictly ordered by a whole-facet interval or exact rational barycentric LP; zero would contradict the separately complete primitive contact result. Mixed directions remain explicit and require source-role interpretation. No source facet, vertical component, closed boundary, source pose or clearance threshold is omitted or changed. This is finite surface ordering, not a reverse closed-solid containment or whole-assembly approval.')
 save(out/'summary.json',result);assert reservations.owns(lease)
 refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_closed_projection_intersection_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_triangle_pair_column_gap_20261010.py'])
 module('noncontact_column_order_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-noncontact-original-pair-finite-column-order',list(dict.fromkeys(refs)),read(out/'summary.json'))

if __name__=='__main__':main()
