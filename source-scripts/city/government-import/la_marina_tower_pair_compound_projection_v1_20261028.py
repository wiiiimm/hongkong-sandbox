"""Complete original Tower 2A/2B projection allocation; no identity waiver."""
import argparse,sys,uuid
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-la-marina-tower-pair-compound-projection-v1-20261028';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';CAP='government-xl-la-marina-three-original-assembly-v1-20261028';UIDS={'landsd/311761:0','landsd/311762:0'}
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and{'building:'+u for u in UIDS}<=set(lease['resources'])and not DOC.exists();_,pins=authenticate(BASE/CAP);p=BASE/CAP/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];selected=[r for r in read(p)['rows']if r['uid']in UIDS];assert {r['uid']for r in selected}==UIDS;refs=[Path(__file__),BASE/CAP/'result.json',p,HERE/'exact_packed_world_geometry_20261009.py'];projections={};targets={};sources=[]
 for row in selected:
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==row['triangles'];polys=shapely.polygons(tri[:,:,[0,2]]);projections[row['uid']]=shapely.union_all(polys);b=row['source']['building'];tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256']and next(f for f in read(tile)['buildings']if f['uid']==row['uid'])==b;refs.append(tile);shape=shapely.GeometryCollection()
  for ring in b['rings']:shape=shape.symmetric_difference(shapely.Polygon(ring))
  assert shape.is_valid;targets[row['uid']]=shape;sources.append(dict(uid=row['uid'],name=b.get('name'),parent=b.get('parent'),buildingCSUID=b['buildingCSUID'],sourceSHA256=row['sourceSHA256'],originalWorldSHA256=digest(tri.astype('<f8').tobytes()),completeFaces=len(tri)))
 union=shapely.union_all(list(projections.values()));target=shapely.union_all(list(targets.values()));rows=[]
 for uid in sorted(UIDS):
  own,form=projections[uid],targets[uid];excess=own.difference(form);rows.append(dict(uid=uid,ownTargetCoverage=own.intersection(form).area/form.area,pairTargetCoverage=union.intersection(form).area/form.area,ownMissingM2=form.difference(own).area,pairMissingM2=form.difference(union).area,ownExcessM2=excess.area,ownExcessOutsidePairTargetsM2=own.difference(target).area,ownExcessCoveredByOtherTowerTargetM2=excess.intersection(shapely.union_all([s for u,s in targets.items()if u!=uid])).area))
 result=dict(uids=sorted(UIDS),sources=sources,rows=rows,combinedSourceProjectionM2=union.area,combinedTargetM2=target.area,combinedMissingM2=target.difference(union).area,combinedExcessM2=union.difference(target).area,sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Every original facet retained, including verticals and finite degenerate projections; exact current source records unchanged. The podium projection is excluded so it cannot mask tower footprint holes. Different OSM parents are retained explicitly. Pair allocation is context only, not a family identity/extent exception, physical approval or installation credit.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);module('la_marina_pair_projection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-two-original-tower-projection-allocation-context',refs,result);print(rows,flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('la-marina-pair-projection-'+str(uuid.uuid4()),['building:'+u for u in sorted(UIDS)],batch=BATCH,ttl=1800);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()
