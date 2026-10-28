"""Attribute assembly projection excess to exact current forms and original facets."""
import argparse,sys,uuid
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';ASSEMBLY='government-xl-elegant-garden-complete-two-permit-assemblies-v1-20261028';CAP='government-xl-elegant-garden-seventeen-original-current-selection-v1-20261028';SCOPE='government-xl-elegant-garden-sixteen-original-updated-scope-v1-20261028'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert a.batch.startswith('government-xl-')and '/'not in a.batch
 out=BASE/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists()
 rp=BASE/'government-xl-elegant-garden-sixteen-original-updated-terrain-plan-v1-20261028.json';resources=set(read(rp)['resources'])
 if not a.owned:
  assert not local.exists();claim=reservations.claim('assembly-boundary-allocation-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 groups=take(ASSEMBLY,'summary.json')['rows'];selected={r['uid']:r for r in take(CAP,'selection.json.gz')['rows']};forms=take(SCOPE,'form-obligations.json.gz');rows=[]
 for group in groups:
  uids=group['uids'];triangles={};projections={};target=shapely.union_all([Polygon(selected[u]['source']['building']['rings'][0],selected[u]['source']['building']['rings'][1:])for u in uids])
  for uid in uids:
   source=selected[uid];asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset);t=decode_original_world_triangles(asset.read_bytes());triangles[uid]=t
   projections[uid]=[shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in t]
  excess=shapely.union_all([p for polys in projections.values()for p in polys]).difference(target);actors=[]
  for b in forms:
   if b['uid']in uids:continue
   intersection=excess.intersection(Polygon(b['rings'][0],b['rings'][1:]));area=intersection.area
   if area<=1e-10:continue
   contributions=[]
   for uid,polys in projections.items():
    ids=[i for i,p in enumerate(polys)if p.intersection(intersection).area>1e-10]
    if ids:
     t=triangles[uid][ids];contributions.append(dict(sourceUid=uid,sourceFaces=ids,completeFacetYRange=[float(t[:,:,1].min()),float(t[:,:,1].max())]))
   actors.append(dict(uid=b['uid'],name=b.get('name'),csuid=b.get('buildingCSUID'),parent=b.get('parent'),structureType=b.get('structureType'),recordedBase=b['base'],recordedTop=b['base']+b['height'],overlapAreaM2=area,selectedOriginal=b['uid']in selected,originalBounds=selected[b['uid']]['native']['model']['worldBounds']if b['uid']in selected else None,contributions=contributions))
  union=shapely.union_all([excess.intersection(Polygon(b['rings'][0],b['rings'][1:]))for b in forms if b['uid']not in uids]);assert abs(union.area-group['measures']['unrelatedExcessM2'])<1e-7
  actors.sort(key=lambda r:-r['overlapAreaM2']);record=dict(permit=group['permit'],uids=uids,totalUnrelatedUnionM2=union.area,actors=actors,sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False)
  save(out/(group['permit'].replace('/','-')+'.json'),record);rows.append(record)
  print(dict(permit=group['permit'],actors=[dict(uid=r['uid'],area=r['overlapAreaM2'],sourceY=[c['completeFacetYRange']for c in r['contributions']])for r in actors]),flush=True)
 result=dict(uids=sorted({u for g in groups for u in g['uids']}),rows=rows,sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Exact current baseline forms and every positive-area original projected-facet contributor to the existing assembly excess. Full facetYbounds are conservative and are NOT clipped column/solid certificates. Overlap areas per form may overlap each other; the union is separately verified. No ownership reassignment, suppression, source-face removal, collision clearance or acceptance.')
 save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py');assert reservations.owns(lease)
 module('boundary_allocation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-permit-original-boundary-excess-allocation',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
