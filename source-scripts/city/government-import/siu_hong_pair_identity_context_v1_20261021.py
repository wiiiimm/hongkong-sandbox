"""Source-bound two-form context, retaining individual identity failures."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-siu-hong-pair-identity-context-v1-20261021';DOC=BASE/BATCH
IDENT=BASE/'government-xl-siu-hong-current-identity-v1-20261021';PRIMARY=BASE/'government-xl-siu-hong-primary-records-v1-20261021';CONTACT=BASE/'government-xl-siu-hong-assembly-contacts-v1-20261021';PATHS=BASE/'government-xl-siu-hong-remaining-paths-v1-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 for folder in [IDENT,PRIMARY,CONTACT,PATHS]:
  _,bound=authenticate(folder);refs.append(folder/'result.json')
  for p,h in bound.items():
   assert p not in pins or pins[p]==h
   pins[p]=h
 def take(p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[k];used[k]=pins[k];refs.append(p);return read(p)
 rows=take(IDENT/'selection.json.gz')['rows'];assert {r['uid']for r in rows}=={'landsd/190963:0','landsd/233417:0'};official=take(PRIMARY/'footprints.json')['features'];pair=[];triangles={};records=[]
 for r in rows:
  uid=r['uid'];b=r['source']['building'];tile=ROOT/'3d-viewer'/r['source']['tile'];assert next(x for x in read(tile)['buildings']if x['uid']==uid)==b;refs.append(tile);used[str(tile.relative_to(ROOT))]=digest(tile.read_bytes());pair.append(b)
  f=[x for x in official if x['attributes']['BuildingCSUID']==b['buildingCSUID']];assert len(f)==1;f=f[0];a=f['attributes'];assert a['Status']=='Active' and a['GeoRefNo']==r['modelId'][1:11] and a['BuildingID']==b['buildingId']
  rings=[[[x-834500,816500-y]for x,y in ring]for ring in f['geometry']['rings']];assert len(rings)==1;shape=Polygon(b['rings'][0],b['rings'][1:]);primary=Polygon(rings[0]);records.append(dict(uid=uid,attributes=a,hausdorffDistanceM=shape.hausdorff_distance(primary),currentCoveredByOfficialFraction=shape.intersection(primary).area/shape.area))
  path=ROOT/r['candidate']['path'];assert digest(path.read_bytes())==r['sourceSHA256'];refs.append(path);used[str(path.relative_to(ROOT))]=r['sourceSHA256'];triangles[uid]=decode_original_world_triangles(path.read_bytes());proof=take(IDENT/uid.split('/')[1]/'identity.json');assert proof['originalOwnership']['sourceGraphVerified'];assert proof['freshCurrentIdentity']['exactObjectAndCSUID']
 assert len({b['parent']for b in pair})==1 and set(pair[0].get('osmRefs',[]))&set(pair[1].get('osmRefs',[]))
 tri=np.concatenate(list(triangles.values()));lo,hi=tri.min((0,1)),tri.max((0,1));final=module('siu_pair_context',HERE/'xl-final-script-pass.py');near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);uids={r['uid']for r in rows};others=shapely.union_all([p for b,p,t in near if b['uid']not in uids]);shape=shapely.union_all([Polygon(b['rings'][0],b['rings'][1:])for b in pair]);measures=[]
 for name,t in [*triangles.items(),('completeTwoOriginalAssembly',tri)]:
  polygons=shapely.polygons(t[:,:,[0,2]]);projection=shapely.union_all(polygons[shapely.area(polygons)>0]);measures.append(dict(source=name,targetCoveredBySourceProjection=projection.intersection(shape).area/shape.area,sourceExcessMaximumDistanceFromTargetM=float(shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),shape).max()),sourceExcessCoveredByUnrelatedFormsM2=projection.difference(shape).intersection(others).area))
 for b,p,t in near:refs.append(ROOT/'3d-viewer'/t);used['3d-viewer/'+t]=digest((ROOT/'3d-viewer'/t).read_bytes())
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 result=dict(uids=sorted(uids),officialRecords=records,measures=measures,neighbourForms=len(near),pairForms=pair,installationApproved=False,sourceIdentityAccepted=False,qualification='Complete original pair context only; preserve raw per-source identity failures. No shared-parent-wide scope or geometry changes.')
 save(DOC/'context.json',result);refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'china_ferry_current_foundations_v1_20261020.py']);module('siu_pair_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-two-form-original-source-context',list(dict.fromkeys(refs)),result);print(dict(records=records,measures=measures,neighbourForms=len(near)),flush=True)
if __name__=='__main__':main()
