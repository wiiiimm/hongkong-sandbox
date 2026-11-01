"""Record an exact-source boundary identity review; no physical/publication waiver."""
import sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-silvercord-lippo-bounded-identity-review-v2-20261101';LOCAL=HERE/'local'/BATCH
IDENTITY='government-xl-silvercord-lippo-current-checks-v1-20261101-identity';RUNTIME='government-xl-silvercord-lippo-current-checks-v1-20261101-runtime';PRIMARY='government-xl-silvercord-lippo-primary-records-v1-20261101';VIEWS='government-xl-silvercord-lippo-complete-source-views-v1-20261101';CONTACTS='government-xl-silvercord-lippo-original-contacts-v1-20261101';JUNCTION='government-xl-silvercord-lippo-original-contact-views-v1-20261101'
EXPECTED={'landsd/233997:0':('11b03482304ea9f139e6863d259891f06aecc5def1df2e18abd921e0a0aebc5d','B355041762402063C0',12258,'landsd/231645:0'),'landsd/231645:0':('cfe390f024ac815a8c8ae3f422724fd72e4cd5c164e7325f9404cd81fc1b46da','B355141753102063C0',13725,'landsd/233997:0')}
ALLOWED={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);pins={};refs=[Path(__file__)]
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 selected=take(RUNTIME,'selection.json.gz');rows={r['uid']:r for r in selected['rows']};assert set(rows)==set(EXPECTED)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
 official=take(PRIMARY,'footprints.json')['features'];assert len(official)==2
 revision=take('government-xl-silvercord-lippo-primary-revision-context-v1-20261101','summary.json');revision_by={r['uid']:r for r in revision['rows']}
 primary={f['attributes']['BuildingCSUID']:f['attributes']for f in official};views=take(VIEWS,'summary.json');contacts=take(CONTACTS,'summary.json');junction=take(JUNCTION,'summary.json')
 assert contacts['sourceSHA256ByUid']=={u:v[0]for u,v in EXPECTED.items()}and all(r['allPairsExamined']and r['sourceFacesOmitted']==0 for r in contacts['rows'])
 assert junction['allSavedOriginalContactsDisplayed']
 images=[]
 for uid in EXPECTED:
  key=uid.split('/')[1].replace(':','-')
  for suffix in ['plan','oblique-35']:
   name=key+'-'+suffix+'.png';p=BASE/VIEWS/name;assert digest(p.read_bytes())==pins[VIEWS][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),actuallyInspectedByRoot=True))
 for row in junction['exports']:
  p=ROOT/row['image']['path'];assert digest(p.read_bytes())==row['image']['sha256'];refs.append(p);images.append({**row['image'],'actuallyInspectedByRoot':True})
 decisions=[]
 for uid,(sha,model,faces,other)in EXPECTED.items():
  source=rows[uid];raw=take(IDENTITY,uid.split('/')[1]+'/identity.json');ctx=take(IDENTITY,uid.split('/')[1]+'/context.json')['identity'];asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==sha==source['sourceSHA256']==raw['sourceSHA256'];refs.append(asset)
  assert source['modelId']==model and source['triangles']==faces and raw['originalOwnership']['originalRootName']==model and raw['originalOwnership']['sourceGraphVerified']and raw['exactWholeCellCoverage']['covered']
  assert set(raw['reasons'])==ALLOWED and raw['passed']is False and ctx==raw['freshCurrentIdentity']and ctx['exactObjectAndCSUID']
  assert ctx['targetCoveredBySourceProjection']>=.95 and ctx['sourceExcessMaximumDistanceFromTargetM']<=10
  assert {r['uid']for r in ctx['intersectingForms']if not r['sameParent']}=={other}
  csuid=source['source']['building']['buildingCSUID'];fresh=primary[csuid];change=revision_by[uid]
  assert csuid==ctx['target']['buildingCSUID']and fresh['BuildingID']==source['source']['building']['buildingId']and fresh['GeoRefNo']==model[1:11]
  assert fresh['BuildingBlockType']=='Podium'and fresh['Status']=='Active'and fresh['BaseHeight']==source['source']['building']['baseHeightHKPD']and fresh['TopHeight']==source['source']['building']['topHeightHKPD']
  assert change['objectIdExact']is False and change['buildingIdExact']and change['modelGeoRefExact']and change['baseAndTopHeightsExact']
  assert change['cachedObjectId']==source['source']['building']['objectId']and change['currentProviderObjectId']==fresh['OBJECTID']
  assert fresh['OBJECTID']=={'landsd/233997:0':233626,'landsd/231645:0':231275}[uid]
  assert change['sourceSHA256']==sha and change['buildingCSUID']==csuid
  tile=ROOT/'3d-viewer'/source['source']['tile'];assert digest(tile.read_bytes())==source['source']['tileSHA256'];refs.append(tile)
  decisions.append(dict(uid=uid,sourceSHA256=sha,modelId=model,completeOriginalFaces=faces,worldTrianglesSHA256=raw['worldTrianglesSHA256'],foreignBoundaryUid=other,identityOnlyApproved=True,providerObjectIdExact=False,legacyObjectIdExactClaimed=False,currentProviderObjectId=fresh['OBJECTID'],cachedViewerObjectId=source['source']['building']['objectId'],providerRevisionContext=change,rawIdentityReasonsRetained=sorted(ALLOWED),rawIdentityVerbatim=raw,physicalAccepted=False,placementApproved=False,collisionExemption=False,installationApproved=False,publication=False,sourceGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,reviewer='Codex ROOT',interpretation='The uniquely routed original podium matches its stable government CSUID/BuildingID, source GeoRef/subtype and complete GeoRef cell. Current provider OBJECTIDs differ from cached viewer keys; both revisions and all measured footprint changes are explicitly retained. No exact current-provider OBJECTID claim is made. ROOT inspected complete source plans/obliques and every saved original junction. The sole foreign footprint overlap is the narrow authored adjoining exterior wall/roof-edge boundary with the other exact podium in this pair. Accept only this exact source association; preserve all original facets and raw overlap/contact evidence. This is not common ownership, a duplicate-suppression instruction or a clearance/support/collision/terrain/publication waiver. Four-world contact differences, including Float32 area contacts, remain physical follow-up.'))
 doc=BASE/BATCH;save(doc/'decisions.json',dict(decisions=decisions,imagesActuallyInspected=images,currentManifestSHA256=selected['manifestSHA256'],physicalAccepted=False,installationApproved=False))
 summary=dict(uids=sorted(EXPECTED),sourceSHA256ByUid={u:v[0]for u,v in EXPECTED.items()},identityOnlyReviewRecorded=True,positiveRuntimeIdentityAdapterImplemented=False,physicalAcceptance=False,placementApproved=False,installationApproved=False,publication=False,sourceGeometryChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,qualification='Bounded exact-source identity review only. Current raw numeric identity failures and the fresh provider OBJECTID revision remain verbatim; future runtime consumption requires exact fresh revalidation. Every terrain, foreign, support, collision, runtime and browser/publication gate remains.')
 save(doc/'summary.json',summary);assert reservations.owns(lease)and digest(manifest.read_bytes())==selected['manifestSHA256']
 module('silvercord_lippo_identity_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-adjoining-podium-source-identity-review',refs,summary);print(summary,flush=True)
if __name__=='__main__':
 if '--owned'in sys.argv:owned()
 else:
  assert not LOCAL.exists()and not(BASE/BATCH).exists()
  c=reservations.claim('silvercord-lippo-bounded-identity-'+str(uuid.uuid4()),['building:'+u for u in EXPECTED]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],c
  execute_reserved(c['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
