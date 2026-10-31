"""Exact five-source identity review using complete official permit membership."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_source_assembly_diagnostic import COVERAGE_REASONS
BASE=ROOT/'docs/astra-city/government-import'
def main():
 batch='government-xl-fu-tor-loy-assembly-identity-review-v1-20261023';out=BASE/batch;assert not out.exists();refs=[Path(__file__)];cache={}
 def take(name,path):
  if name not in cache:cache[name]=authenticate(BASE/name)[1];refs.append(BASE/name/'result.json')
  assert digest(path.read_bytes())==cache[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 capture='government-xl-fu-tor-loy-five-originals-current-v1-20261023-runtime';selection=take(capture,BASE/capture/'selection.json.gz');rows=selection['rows'];uids={r['uid']for r in rows};assert len(uids)==5
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 primary='government-xl-fu-tor-loy-primary-records-v2-20261023';summary=take(primary,BASE/primary/'summary.json');assert summary['completePermit']=='K44/80' and set(summary['requestedUIDs'])==uids
 features=take(primary,BASE/primary/'footprints.json')['features'];official={f['attributes']['BuildingCSUID']:f['attributes']for f in features}
 structures=take(primary,BASE/primary/'complete-permit-structures.json')['features'];relations=take(primary,BASE/primary/'complete-permit-relations.json')['features']
 assert len(structures)==len(relations)==5 and all(f['attributes']['OPNo']=='K44/80'for f in structures)
 csuids={r['source']['building']['buildingCSUID']for r in rows};assert set(official)==csuids==set(summary['completePermitCSUIDs'])=={f['attributes']['BuildingCSUID']for f in relations}
 assert len({f['attributes']['BuildingStructureID']for f in structures})==5
 identity='government-xl-fu-tor-loy-five-originals-current-v1-20261023-identity';raw={};projections=[];targets=[];vertices=[]
 for r in rows:
  b=r['source']['building'];uid=r['uid'];p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p);t=decode_original_world_triangles(p.read_bytes())
  proof=take(identity,BASE/identity/uid.split('/')[1]/'identity.json');raw[uid]=proof
  assert proof['sourceSHA256']==r['sourceSHA256'] and digest(t.tobytes())==proof['worldTrianglesSHA256'] and len(t)==r['triangles']
  assert not(set(proof['reasons'])-COVERAGE_REASONS) and proof['freshCurrentIdentity']['exactObjectAndCSUID']
  assert proof['geographicCell']['targetCoversWholeCell'] and proof['geographicCell']['originalProjectionCoversWholeCell']
  f=official[b['buildingCSUID']];assert f['Status']=='Active' and f['BuildingBlockType']==b['structureType']
  assert f['BaseHeight']==b['base'] and abs(f['TopHeight']-(b['base']+b['height']))<1e-8
  projections.append(shapely.union_all(shapely.polygons(t[:,:,[0,2]])));targets.append(Polygon(b['rings'][0],b['rings'][1:]));vertices.append(t[:,:,[0,2]].reshape(-1,2))
 source=shapely.union_all(projections);target=shapely.union_all(targets);excess=source.difference(target)
 scope='government-xl-fu-tor-loy-five-originals-current-v1-20261023-scope';forms=take(scope,BASE/scope/'form-obligations.json.gz');assert len(forms)==613
 others=shapely.union_all([Polygon(b['rings'][0],b['rings'][1:])for b in forms if b['uid']not in uids])
 measures=dict(coverage=source.intersection(target).area/target.area,maximumExtentM=float(shapely.distance(shapely.points(np.concatenate(vertices)),target).max()),unrelatedExcessM2=excess.intersection(others).area,sourceFaces=sum(r['triangles']for r in rows))
 assert measures['coverage']>=.95 and measures['maximumExtentM']<=10 and measures['unrelatedExcessM2']<=1 and measures['sourceFaces']==28572
 imagebatch='government-xl-fu-tor-loy-five-originals-context-plots-v3-20261023';_,pins=authenticate(BASE/imagebatch);p=BASE/imagebatch/'complete-original-assembly.png';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([BASE/imagebatch/'result.json',p])
 result=dict(uids=sorted(uids),reviewer='Codex ROOT',identityOnlyApproved=True,sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},currentManifestSHA256=selection['manifestSHA256'],completeOfficialPermit='K44/80',measures=measures,rawIndividualIdentity=raw,imagesActuallyViewed=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))],sourceGeometryChanges=0,installationApproved=False,basis='Bounded identity of the complete original five-source assembly. Fresh official complete permit membership is exactly the one podium/four towers, with five distinct structure IDs and active exact CSUIDs/types/heights; no legal ownership or structural engineering conclusion. Original unique object/CSUID routes, full one-metre georef cells and source hashes remain valid. Only the individual footprint coverage failures are interpreted over the complete permit assembly; all 608 other scoped forms remain unrelated, with no same-parent exclusion. Existing 95%/10m/1m2 geometric limits pass. Raw identity/support negatives retained. Physical, component, terrain, browser and publication acceptance remain independent.')
 save(out/'review.json',result);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','original_source_assembly_diagnostic.py'])
 module('fu_tor_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'bounded-five-source-official-permit-identity-review',refs,result);print(measures,flush=True)
if __name__=='__main__':main()
