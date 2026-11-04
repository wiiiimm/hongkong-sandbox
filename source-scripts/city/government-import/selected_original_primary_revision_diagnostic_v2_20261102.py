"""Compare exact current-viewer source records with fresh official footprint records.

Records identifier/geometry revisions only. No identity/physical approval or edits.
"""
import argparse,sys,uuid
from pathlib import Path
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
def provider_single_shell(rings):
 assert rings
 world=[[(float(x)-834500,816500-float(y))for x,y in ring]for ring in rings]
 parts=[shapely.Polygon(ring)for ring in world]
 assert all(p.is_valid and p.area>0 for p in parts)
 # Official ArcGIS clockwise shell / counterclockwise holes become reversed
 # by the northing-to-viewer-Z transform. Reject multipart/ambiguous layouts.
 assert shapely.is_ccw(parts[0].exterior)
 for i,hole in enumerate(parts[1:],1):
  assert not shapely.is_ccw(hole.exterior)
  assert parts[0].contains_properly(hole)
  assert all(hole.disjoint(other)for other in parts[1:i])
 result=shapely.Polygon(world[0],world[1:])
 assert result.is_valid and result.area>0
 return result
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','capture','primary']:p.add_argument('--'+k,required=True)
 p.add_argument('--owned',action='store_true');a=p.parse_args();assert all(x.startswith('government-xl-')and '/'not in x for x in [a.batch,a.capture,a.primary])
 _,cp=authenticate(BASE/a.capture);sp=BASE/a.capture/'selection.json.gz';assert digest(sp.read_bytes())==cp[str(sp.relative_to(ROOT))];selection=read(sp);rows=selection['rows'];assert 0<len(rows)<=40
 local=HERE/'local'/a.batch;lease=local/'reservation.json'
 if not a.owned:
  assert not local.exists()and not(BASE/a.batch).exists()
  c=reservations.claim('primary-source-revision-diagnostic-'+str(uuid.uuid4()),['building:'+r['uid']for r in rows]+['immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert c['ok'],c
  execute_reserved(c['reservation'],lease,[sys.executable,__file__,*sys.argv[1:],'--owned']);return
 assert reservations.owns(read(lease));_,pp=authenticate(BASE/a.primary);fp=BASE/a.primary/'footprints.json';assert digest(fp.read_bytes())==pp[str(fp.relative_to(ROOT))];features=read(fp)['features'];csuids=[f['attributes']['BuildingCSUID']for f in features];assert len(csuids)==len(set(csuids));by={f['attributes']['BuildingCSUID']:f for f in features}
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs=[Path(__file__),BASE/a.capture/'result.json',sp,BASE/a.primary/'result.json',fp,manifest];outcomes=[]
 for row in rows:
  old=row['source']['building'];uid=row['uid'];f=by[old['buildingCSUID']];attrs=f['attributes'];rings=f['geometry']['rings']
  new=provider_single_shell(rings);cached=shapely.Polygon(old['rings'][0],old['rings'][1:]);assert cached.is_valid and new.is_valid and cached.area>0 and new.area>0
  tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];refs.append(tile)
  outcomes.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],modelId=row['modelId'],buildingCSUID=old['buildingCSUID'],cachedObjectId=old['objectId'],currentProviderObjectId=attrs['OBJECTID'],objectIdExact=old['objectId']==attrs['OBJECTID'],cachedBuildingId=old['buildingId'],currentProviderBuildingId=attrs['BuildingID'],buildingIdExact=old['buildingId']==attrs['BuildingID'],providerGeoRef=attrs['GeoRefNo'],modelGeoRefExact=row['modelId'][1:11]==attrs['GeoRefNo'],providerBlockType=attrs['BuildingBlockType'],cachedBlockType=old.get('structureType'),providerStatus=attrs['Status'],cachedBaseHeight=old['baseHeightHKPD'],providerBaseHeight=attrs['BaseHeight'],cachedTopHeight=old['topHeightHKPD'],providerTopHeight=attrs['TopHeight'],baseAndTopHeightsExact=old['baseHeightHKPD']==attrs['BaseHeight']and old['topHeightHKPD']==attrs['TopHeight'],cachedFootprintAreaM2=cached.area,providerFootprintAreaM2=new.area,footprintSymmetricDifferenceM2=cached.symmetric_difference(new).area,footprintHausdorffM=cached.hausdorff_distance(new),footprintIntersectionOverUnion=cached.intersection(new).area/cached.union(new).area,providerRingCount=len(rings),providerHoleCount=len(rings)-1,providerFootprintWorldWKT=new.wkt,identityAccepted=False,installationApproved=False))
 result=dict(uids=[r['uid']for r in rows],rows=outcomes,sourceGeometryChanges=0,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Exact CSUID-bound current-provider versus cached-viewer field/geometry measurements. Changed OBJECTID is recorded verbatim, never labelled exact or automatically waived. Stable fields and close geometry alone do not approve current source identity, physical checks or publication.')
 save(BASE/a.batch/'summary.json',result);assert reservations.owns(read(lease))and digest(manifest.read_bytes())==selection['manifestSHA256']
 module('source_primary_revision_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'current-official-source-identifier-revision-diagnostic',refs,result);print([{k:r[k]for k in ['uid','cachedObjectId','currentProviderObjectId','objectIdExact','buildingIdExact','modelGeoRefExact','baseAndTopHeightsExact','footprintHausdorffM']}for r in outcomes],flush=True)
if __name__=='__main__':main()
