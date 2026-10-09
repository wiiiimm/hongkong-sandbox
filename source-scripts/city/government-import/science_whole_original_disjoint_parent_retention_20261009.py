"""Exact parent-ground retention only under whole-original-disjoint current forms."""
import importlib.util,json,numpy as np,shapely
from run import ROOT,HERE,read,digest
from science_attached_open_canopy_identity_20261009 import UID
UIDS={UID}
DOC=ROOT/'docs/astra-city/government-import/government-xl-science-attached-open-canopy-current-identity-20261009'
def preserve(patch,bounds,sampler,projection,current_forms,patches):
 selected=read(DOC/'selection.json.gz');assert {r['uid'] for r in selected['rows']}==UIDS;spec=importlib.util.spec_from_file_location('science_exact_retention_decode',HERE/'xl-second-pass.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d);d.LOCAL=HERE/'local/government-xl-science-attached-canopy-complete-original-physical-20261009';parts=[]
 for r in selected['rows']:
  assert digest((ROOT/r['candidate']['path']).read_bytes())==r['sourceSHA256'];r['triangles']=r['native']['model']['triangles'];t=d.glb_triangles(r);parts.append(shapely.union_all(shapely.polygons(t[:,:,[0,2]])))
 whole=shapely.union_all(parts);assert whole.symmetric_difference(projection).area<1e-8;protected=[];rows=[];intersecting=[]
 for b,_,tile in current_forms:
  if b['uid'] in UIDS:continue
  shape=shapely.Polygon(b['rings'][0],b['rings'][1:]);region=shape.buffer(.01,join_style='mitre');overlap=region.intersection(whole).area;distance=region.distance(whole)
  if overlap==0 and distance>0:
   protected.append(region);rows.append({'uid':b['uid'],'wholeCurrentForm':b,'protectedRegionGeoJSON':json.loads(shapely.to_geojson(region)),'wholeMuseumOriginalIntersectionM2':0,'minimumWholeOriginalDistanceM':distance,'currentTile':tile,'currentTileSHA256':digest((ROOT/'3d-viewer'/tile).read_bytes())})
  else:intersecting.append({'uid':b['uid'],'wholeCurrentForm':b,'rawOriginalIntersectionM2':overlap,'minimumOriginalDistanceM':distance,'currentPhysicalExemption':False})
 assert protected;region=shapely.union_all(protected);assert region.intersection(whole).area==0;proof=patches.preserve_parent_under_projection(patch,bounds,region,sampler);proof.update(rows=rows,intersectingUnchangedActors=intersecting,sourceProjectionIntersectionM2=0,allCurrentFormsRetained=True,sourceGeometryChanges=0);return proof
