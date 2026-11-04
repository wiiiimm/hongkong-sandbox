"""Bounded ROOT source-association and specific native-interface judgements."""
import argparse,sys,uuid,json
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-elegant-garden-'
EXPECTED={'landsd/171904:0','landsd/224123:0','landsd/236367:0','landsd/100673:0','landsd/234554:0','landsd/215726:0','landsd/255031:0','landsd/224121:0'}
ALLOWED={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage','fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent','current-target-does-not-cover-whole-georef-cell','original-source-does-not-cover-whole-georef-cell'}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert a.batch.startswith(PREFIX)and '/'not in a.batch
 out,local=BASE/a.batch,HERE/'local'/a.batch;assert not out.exists()
 rp=BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json');resources=set(read(rp)['resources']);lp=local/'reservation.json'
 if not a.owned:
  assert not local.exists();claim=reservations.claim('root-eight-associations-four-boundaries-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 packet_batch=PREFIX+'eight-identity-packet-v1-20261028';packet=take(packet_batch,'summary.json');assert set(packet['uids'])==EXPECTED
 image=ROOT/packet['image']['path'];assert digest(image.read_bytes())==packet['image']['sha256'];refs.append(image)
 selection=take(PREFIX+'sixteen-original-updated-runtime-v1-20261028','selection.json.gz');sources={r['uid']:r for r in selection['rows']};manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 identities=[]
 for uid in packet['uids']:
  row=take(packet_batch,uid.split('/')[1]+'-packet.json');raw=row['rawIdentityVerbatim'];assert set(raw['reasons'])<=ALLOWED and not raw['passed']
  assert raw['originalOwnership']['sourceGraphVerified']and raw['exactCurrentComponentRoute']['qualified']and raw['freshCurrentIdentity']['exactObjectAndCSUID']and raw['completeRecordProjection']
  source=sources[uid];asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==source['sourceSHA256'];refs.append(asset)
  tile=ROOT/row['tile'];assert digest(tile.read_bytes())==row['tileSHA256'];refs.append(tile);b=next(r for r in read(tile)['buildings']if r['uid']==uid)
  assert digest(json.dumps(b,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode())==row['sourceFormSHA256']
  assert source['modelId'][1:11]==b['buildingCSUID'][:10]and source['modelId'][11:13]==('01'if b['structureType']=='Tower'else'02')
  record=row['officialRecord'];assert record['Status']=='Active'and record['BuildingCSUID']==b['buildingCSUID']and record['BuildingBlockType']==b['structureType']
  if uid!='landsd/100673:0':assert raw['geographicCell']['targetCoversWholeCell']and raw['geographicCell']['originalProjectionCoversWholeCell']
  else:
   assert not raw['geographicCell']['targetCoversWholeCell']and not raw['geographicCell']['originalProjectionCoversWholeCell']
   assert raw['freshCurrentIdentity']['targetCoveredBySourceProjection']==0.9028419636791262
  review=dict(uid=uid,reviewer='Codex ROOT',reviewType='exact-direct-registered-government-source-association-only',modelId=source['modelId'],sourceSHA256=row['sourceSHA256'],sourceFormSHA256=raw['sourceFormSHA256'],sourceFormHashDomain='existing current identity diagnostic captured-form JSON',exactLivePythonCanonicalFormSHA256=row['sourceFormSHA256'],tileSHA256=row['tileSHA256'],worldTrianglesSHA256=row['worldTrianglesSHA256'],currentManifestSHA256=selection['manifestSHA256'],
   identityOnlyApproved=True,identityReviewApproved=True,sourceIdentityReviewed=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),uniqueOfficialActiveCSUID=record['BuildingCSUID'],officialRecord=record,rawIdentityVerbatim=raw,rawReasonsRetained=raw['reasons'],rawGenericIdentityPassed=False,spatialLimitsNotDeclaredPassed=True,imagesActuallyInspected=[packet['image']],sourceYRange=row['sourceYRange'],recordedYRange=[b['base'],b['topHeightHKPD']],sourceShapeAndHeightCompletenessNotApproved=True,
   requiresIndependentBoundaryPlacementReview=True,outsideAssemblySuppressionApproved=False,boundaryOwnershipApproved=False,sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,placementReviewed=False,physicalAccepted=False,publicationApproved=False,installationApproved=False,
   basis=[
    'ROOT inspected the eight complete original-projection/current-footprint maps. These identify the same registered feature and typed source unit, with matching position/orientation and the exact active official CSUID. Each complete unchanged government graph is bound to its exact modelId/georef/type, source asset SHA and current viewer form; no name/proximity-only substitution, source clipping or current-OBJECTID rewrite is used.',
    'This accepts which exact government source unit belongs to this viewer feature. It does not assert equality between a complete3Dsource projection and the simpler2Dfootprint proxy. West Grand podium extends across the same complex where the native tower is narrower; their individual raw extent/coverage failures remain explicit physical/completeness obligations, not legal ownership assignments.',
    'All original source heights and every raw coverage/excess/cell failure remain unchanged. In particular224123has a lower source height than recorded metadata, and its official six-storey/basement context does not make the skyline discrepancy disappear. No resizing, datum shift, missing-source inference or full current-building completeness approval follows from association.',
    'Small100673is a narrow rotated2.4mclass part: both its current footprint and the registered original fail the whole1metre-cell proxy, while the exact typed source/current active CSUID and the mutually aligned footprints identify the same unit. ROOT accepts this exact association, without making the raw cell test true or introducing a general coverage tolerance.',
    'Fourteen independent original/source physical, support, collision, runtime and visual obligations are not replaced by this association judgement. Any actual unrelated overlap, missing source support, unresolved source role or mixed fallback state remains required to resolve. This is not publication permission.'
   ])
  save(out/(uid.split('/')[1]+'-identity-review.json'),review);identities.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],identityOnlyApproved=True,requiresIndependentBoundaryPlacementReview=True))
 columns=take(PREFIX+'noncontact-column-order-v1-20261028','summary.json');boundaries=[]
 for left,right in [('landsd/236170:0','landsd/236367:0'),('landsd/173764:0','landsd/224121:0')]:
  rows=[r for r in columns['rows']if r['sourceUid']==left and r['otherUid']==right];assert len(rows)==4 and all(r['exactClosedProjectionPairs']==r['exactPositiveAreaProjectionPairs']==0 for r in rows)
  for row in rows:take(PREFIX+'noncontact-column-order-v1-20261028',row['proof'])
  review=dict(sourceUid=left,otherUid=right,reviewer='Codex ROOT: complete exact closed-projection proof',reviewType='exact-complete-original-surface-closed-XZ-projection-separation',interfaceSeparationApproved=True,rows=rows,sourceSHA256ByUid={u:sources[u]['sourceSHA256']for u in [left,right]},sourceGeometryChanges=0,sourcePoseChanges=0,physicalAccepted=False,installationApproved=False,publication=False,
   basis='Every closed projected primitive, including collapsed source facets and boundary points, is disjoint in all4coordinate streams. This resolves surface interference for this exact original pair; the older BASIC-footprint overlap is not an actual common source column. Source support, collision-interior/runtime behaviour, mixed BASIC states and whole-assembly acceptance remain separate. No arbitrary gap, epsilon or omitted source face is used.')
  save(out/(left.split('/')[1]+'--'+right.split('/')[1]+'-separation-review.json'),review);boundaries.append(dict(sourceUid=left,otherUid=right,interfaceSeparationApproved=True))
 context_batch=PREFIX+'active-boundary-context-v1-20261028';context=take(context_batch,'summary.json');basic_review=take(context_batch,'block2-basic-podium-separation-review.json');assert basic_review['interfaceSeparationApproved'];boundaries.append(dict(sourceUid=basic_review['sourceUid'],otherUid=basic_review['otherUid'],interfaceSeparationApproved=True))
 contact_batch=PREFIX+'active-boundary-contacts-v1-20261028';contacts=take(contact_batch,'summary.json');seam=[]
 for mode in ['original','literal','leftF32','balancedF32']:
  row=next(r for r in contacts['rows']if r['sourceUid']=='landsd/236170:0'and r['otherUid']=='landsd/173767:0'and r['mode']==mode);assert row['contacts']==11 and row['contactDimensions']=={'1':11};proof=take(contact_batch,row['proof']);assert {c['sourceFaceA']for c in proof['contacts']}=={597,1376}and {c['sourceFaceB']for c in proof['contacts']}=={1277,1278,1281,1282,1285,1286,1290,1291,1292}
  seam.append(dict(mode=mode,proof=row['proof'],contacts=proof['contacts']))
 seam_images=[r for r in context['figures']if r['otherUid']=='landsd/173767:0'];assert len(seam_images)==3
 for r in seam_images:path=ROOT/r['path'];assert digest(path.read_bytes())==r['sha256'];refs.append(path)
 review=dict(sourceUid='landsd/236170:0',otherUid='landsd/173767:0',reviewer='Codex ROOT',reviewType='exact-original-opaque-podium-edge-adjacent-façade-joint-only',boundaryInterfaceRoleApproved=True,sourceAuthoredOpaqueBoundaryInterfaceAccepted=True,requiresBothReviewedOriginalsActive=True,mixedBasicStatesNotApproved=True,requiresRuntimeDependencyOrCoupledActivation=True,sourceSHA256ByUid={u:sources[u]['sourceSHA256']for u in ['landsd/236170:0','landsd/173767:0']},rawContactsRetained=seam,imagesActuallyInspected=seam_images,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAccepted=False,installationApproved=False,publication=False,evidenceInterpretationUsedAI=True,aiGeometryModelling=False,
  basis='ROOT inspected all3exact source-seam views. The11line contacts in each of4streams lie at the adjacent lower façade/podium-edge band: source597is the horizontal edge cap and1376its near-vertical boundary fascia; all9counterpart facets are vertical/near-vertical opaque façade faces. They form the source-authored edge junction, not a roof/stair/passage surface cutting through an unrelated tower interior. ROOT accepts this bounded original/original opaque boundary joint while retaining every crossing. No penetration-depth tolerance, structural/cadastral claim, mesh repair, separation proof, mixed BASIC clearance or full collision/whole-scene approval is introduced.')
 save(out/'louis-opaque-source-joint-review.json',review);boundaries.append(dict(sourceUid=review['sourceUid'],otherUid=review['otherUid'],boundaryInterfaceRoleApproved=True,requiresBothReviewedOriginalsActive=True))
 raw_pass={'landsd/173767:0','landsd/213816:0','landsd/255231:0','landsd/257493:0'};previous={'landsd/173532:0','landsd/173768:0','landsd/236170:0','landsd/173764:0'}
 for uid in previous:
  r=take(PREFIX+'five-exact-source-identity-review-v1-20261028',uid.split('/')[1]+'-review.json');assert r['identityOnlyApproved']and r['sourceSHA256']==sources[uid]['sourceSHA256']
 for uid in raw_pass:
  matches=[]
  for path in BASE.glob(PREFIX+'*/*/identity.json'):
   r=read(path)
   if r.get('uid')==uid and r.get('sourceSHA256')==sources[uid]['sourceSHA256']and r.get('exactRouteManifestSHA256')==selection['manifestSHA256']:matches.append(path)
  assert len(matches)==1;path=matches[0];r=take(path.parent.parent.name,str(path.relative_to(path.parent.parent)));assert r['passed']and not r['reasons']
 assert EXPECTED|raw_pass|previous==set(sources)and len(EXPECTED)+len(raw_pass)+len(previous)==16
 result=dict(uids=sorted(sources),newSourceAssociations=identities,reusedRawIdentityPasses=sorted(raw_pass),reusedPriorIdentityReviews=sorted(previous),allSixteenSourceAssociationsQualified=True,boundedBoundaryReviews=boundaries,remainingActiveBoundaryCase='Main podium / BASIC canopy99061 needs a source-backed duplicate-feature decision; its native pavilion is already present. Do not approve coexistence or suppress solely from projection coverage.',sourceGeometryChanges=0,sourcePoseChanges=0,sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,physicalAccepted=False,placementReviewed=False,publicationApproved=False,installationApproved=False,publication=False)
 save(out/'summary.json',result);assert reservations.owns(lease)
 refs.append(HERE/'exact_packed_world_geometry_20261009.py')
 module('identity_boundary_reviews_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'root-eight-source-associations-and-four-bounded-boundary-reviews',list(dict.fromkeys(refs)),read(out/'summary.json'))

if __name__=='__main__':main()
