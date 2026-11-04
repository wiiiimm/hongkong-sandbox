"""Source-specific stable lineage and complete three-part identity; raw failures retained."""
from pathlib import Path
from datetime import datetime,timezone
import numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-stable-assembly-identity-v1-20261017';DOC=BASE/BATCH;IDENT=BASE/'government-xl-opus-current-identity-v1-20261017';CONTACT=BASE/'government-xl-opus-complete-contact-account-v1-20261017';ROLE=BASE/'government-xl-opus-original-patch-roles-v1-20261017'
UIDS={'landsd/248432:0','landsd/319559:0','landsd/322573:0'}
ALLOWED={'exact-officialCandidates','exact-officialMatches','fresh-exact-component-route-not-unique-or-differs','unique-viewerMatches','current-target-does-not-cover-whole-georef-cell','original-source-does-not-cover-whole-georef-cell','fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage','fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [IDENT,CONTACT,ROLE]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for x in r['evidenceRefs']:pins.setdefault(x['path'],set()).add(x['sha256'])
 def consume(p):
  assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 selection=consume(IDENT/'selection.json.gz');rows=selection['rows'];assert {r['uid'] for r in rows}==UIDS;provider=consume(IDENT/'provider.json');request=consume(IDENT/'provider.request.json');assert request['sha256']==digest((IDENT/'provider.json').read_bytes());assert request['url']=='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'
 assert len(provider['features'])==3 and not provider.get('exceededTransferLimit');contacts=consume(CONTACT/'account.json.gz')['rows'];assert len(contacts)==8 and all(r['allSamplesAccounted'] for r in contacts);roles=consume(ROLE/'ROOT-SOURCE-REVIEW.json');assert roles['sourceRoleInterpretationAccepted'] and roles['foundation']['completeTerrainTriangles']==13557 and roles['foundation']['fullyBuriedUpwardTriangles']==0
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifestpath.read_bytes())==selection['manifestSHA256'];manifest=read(manifestpath);refs.append(manifestpath);allforms=[]
 for tile in manifest['tiles']:
  p=ROOT/'3d-viewer'/tile['url'];forms=read(p)['buildings'];matching=[b for b in forms if b.get('buildingCSUID') in {r['source']['building']['buildingCSUID'] for r in rows}]
  if matching:allforms.extend(matching);refs.append(p)
 assert len(allforms)==3 and {b['uid'] for b in allforms}==UIDS
 triangles={};projections={};measurements=[];raws={};helper=module('opus_assembly_forms',HERE/'xl-final-script-pass.py');conv=module('opus_stable_converter',HERE.parent/'citywide-native/convert.py')
 for r in rows:
  asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==r['triangles'];triangles[r['uid']]=tri;projections[r['uid']]=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));raw=consume(IDENT/(r['uid'].replace('/','-').replace(':','-')+'.json'))['proof'];assert raw['originalOwnership']['sourceGraphVerified'];assert set(raw['reasons'])<=ALLOWED;raws[r['uid']]=raw
 assembly=shapely.union_all(list(projections.values()));complete=np.concatenate(list(triangles.values()));lo=complete.min((0,1));hi=complete.max((0,1));forms=helper.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);foreign=shapely.union_all([p for b,p,_ in forms if b['uid'] not in UIDS]);refs.extend(ROOT/'3d-viewer'/url for _,_,url in forms)
 for r in rows:
  b=r['source']['building'];uid=r['uid'];assert b in allforms;matches=[f for f in provider['features'] if f['attributes']['BuildingCSUID']==b['buildingCSUID']];assert len(matches)==1;feature=matches[0];a=feature['attributes'];assert (a['GeoRefNo'],a['BuildingID'],a['BuildingBlockType'],a['BaseHeight'],a['TopHeight'],a['Status'])==(r['modelId'][1:11],b['buildingId'],b['structureType'],b['baseHeightHKPD'],b['topHeightHKPD'],'Active');assert datetime.fromtimestamp(a['DateCreate']/1000,timezone.utc).strftime('%Y%m%d')==b['buildingCSUID'][11:]
  target=Polygon(b['rings'][0],b['rings'][1:]);primary=conv.official_shape(feature);p=projections[uid];excess=p.difference(target);identity=raws[uid]['originalOwnership']['fullProjection'];m=dict(uid=uid,historicalObjectId=b['objectId'],currentProviderObjectId=a['OBJECTID'],buildingCSUID=b['buildingCSUID'],buildingId=b['buildingId'],sourceSHA256=r['sourceSHA256'],sourceGraphVerified=True,sourceRoot=r['modelId'],rawOwnCoverage=identity['targetCoveredBySourceProjection'],assemblyCoverage=assembly.intersection(target).area/target.area,primaryAssemblyCoverage=assembly.intersection(primary).area/primary.area,foreignExcessM2=excess.intersection(foreign).area,sourceExtentM=identity['sourceExcessMaximumDistanceFromTargetM'],providerViewerSymmetricDifferenceM2=primary.symmetric_difference(target).area,providerViewerHausdorffM=primary.hausdorff_distance(target),ownMissingCoveredByOtherOriginalPartsM2=target.difference(p).intersection(shapely.union_all([q for u,q in projections.items() if u!=uid])).area)
  assert m['assemblyCoverage']>=.95 and m['primaryAssemblyCoverage']>=.95 and m['foreignExcessM2']<=1 and m['sourceExtentM']<=10;measurements.append(m)
 review=dict(sourceIdentityRelationshipAccepted=True,measurements=measurements,rawIdentityProofs=raws,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,fullAcceptance=False,publicationApproved=False,basis='Unique live Active records match stable CSUID, creation date, BuildingID, GeoRef, structure type and surveyed heights; numeric service ObjectIDs changed and remain explicitly recorded rather than rewritten. Each immutable asset retains its exact named government root. Complete three-original geometry meets existing 95% coverage and 10m extent/1m2 unrelated-excess bounds; podium missing projection is predominantly occupied by the independently identified original companion/tower. All77 rim samples are accounted in four worlds and full terrain/foundation evidence is bound. Source-only junction views were inspected in the preceding contact-account review.',scope='Only these three exact original source hashes and current forms/provider records, installed together. Whole-cell and own-part coverage negatives remain raw diagnostics; the affirmative alternative is stable primary lineage plus complete original assembly geometry and measured contacts. No global threshold changes, arbitrary landmark rename, suppression of other forms, geometry edits or publication permission.')
 DOC.mkdir();save(DOC/'ROOT-SOURCE-REVIEW.json',review);refs += [Path(helper.__file__),Path(conv.__file__),HERE/'exact_packed_world_geometry_20261009.py']
 result=module('opus_stable_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-stable-primary-three-part-identity-review-v1',refs,dict(uids=sorted(UIDS),sourceIdentityRelationshipAccepted=True,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId'],measurements=measurements),flush=True)
if __name__=='__main__':main()
