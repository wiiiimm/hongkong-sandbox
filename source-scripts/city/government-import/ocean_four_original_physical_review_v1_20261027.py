"""Compose exact-source architectural physical review; never publish or edit geometry."""
from pathlib import Path
from itertools import combinations
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from ocean_four_original_identity_review_v1_20261027 import SOURCES,P
BATCH='government-xl-ocean-four-original-physical-review-v1-20261027';UP='landsd/156599:0';MAIN='landsd/234188:0';MODES={'original','literal','leftF32','balancedF32'}
def verify_upper_attachment(worlds,ids):
 assert set(worlds)==MODES and len(ids)==50
 expected={(face,label)for face in ids for label in ['0','1','2','centroid']}
 for mode,data in worlds.items():
  assert data['mode']==mode and len(data['rows'])==200
  assert {(p['witness']['sourceFace'],p['witness']['pointKind'])for p in data['rows']}==expected
  for path in data['rows']:
   assert path['hasUnrestrictedFiniteAttachment']and path['passesExistingEndpointHeight']and path['riseAboveEndpointsM']==0 and path['maximumResidualM']<=.001
   assert path['incidentFaces']==[path['witness']['sourceFace']] and path['faces'][0]==path['witness']['sourceFace']
   assert path['terminal']['kind']=='exact-finite-intersection'and path['terminal']['contact']['peerUid']==MAIN
 return True

def main():
 base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not out.exists();pins={};refs=[Path(__file__)];
 def take(name,file='summary.json'):
  if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
  path=base/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 identity=take(P+'identity-review-v1-20261027');assert identity['identityAccepted']and identity['sourceSHA256ByUid']==SOURCES
 selection=take(P+'runtime-v1-20261027','selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
 geometry=take(P+'runtime-v1-20261027',str((HERE/'local'/(P+'runtime-v1-20261027')/'runtime-geometry.json.gz').relative_to(base/(P+'runtime-v1-20261027')))) if False else None
 # Runtime geometry is fenced under its local path, not relative to the doc folder.
 runtime=P+'runtime-v1-20261027';gp=HERE/'local'/runtime/'runtime-geometry.json.gz';assert digest(gp.read_bytes())==pins[runtime][str(gp.relative_to(ROOT))];refs.append(gp);ground={r['uid']:np.asarray(r['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)for r in read(gp)['rows']}
 for source in selection['rows']:
  path=ROOT/source['candidate']['path'];assert digest(path.read_bytes())==SOURCES[source['uid']];refs.append(path)
 foundations={}
 for uid in SOURCES:
  data=take(P+uid.split('/')[1].split(':')[0]+'-foundations-v1-20261027');assert data['establishedFoundationPolicyPassed']and len(data['rows'])==4
  assert all(r['uid']==uid and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 and r['completeTerrainTriangles']==r['triangles']for r in data['rows']);foundations[uid]=data
 caps={}
 for uid in set(SOURCES)-{UP}:
  data=take(P+uid.split('/')[1].split(':')[0]+'-cap-paths-v1-20261027');assert data['sourceSHA256']==SOURCES[uid]and len(data['rows'])==4
  for row in data['rows']:
   assert row['completeDrawnGroundSHA256']==digest(ground[uid].tobytes())
   proof=row['completeGroundClearancePartition'];assert all(p['hasExactSharedEdgeClearCapPath']for p in proof['paths'])
   if uid==MAIN:assert len(proof['paths'])==10 and proof['negativeNonWallFaces']==[225,226,227,1436,1437]
   else:assert proof['negativeSourceFaces']==proof['negativeNonWallFaces']==proof['paths']==[]
  caps[uid]=data
 slopes=take('government-xl-ocean-five-sloping-base-coverage-v3-20261027');assert len(slopes['rows'])==20 and slopes['sourceFaces']==[225,226,227,1436,1437]
 for row in slopes['rows']:
  assert row['groundSHA256']==digest(ground[MAIN].tobytes())and row['coverage'][1]['exactSumBarycentricArea']=='0'
  assert row['severePairs']and all(p['exactNormalY']==p['exactSevereSourceBarycentricArea']=='0'for p in row['severePairs'])
 views=take('government-xl-ocean-upper-compound-role-views-v2-20261027');assert views['sourceSHA256ByUid']=={UP:SOURCES[UP],MAIN:SOURCES[MAIN]}and sorted(r['completeComponentFaces']for r in views['rows'])==[52,69,10113]
 ids=views['flaggedFaces'];assert len(ids)==50;images=[]
 for r in views['rows']:
  image=r['image'];assert digest((ROOT/image['path']).read_bytes())==image['sha256'];refs.append(ROOT/image['path']);images.append(image)
  if r['completeComponentFaces']==69:assert r['flaggedFaceIds']==[59,111]and r['componentNormalCounts']==dict(upward=0,downward=69,wallLike=0)
 context='government-xl-after-waterfront-ocean-pair-compound-context-v1-20261027';bound={m:take(context,m+'.json.gz')for m in MODES}
 for mode,c in bound.items():
  assert sorted(r['sourceFace']for r in c['faces'])==ids
  assert sum(abs(r['signedNormalYRatio'])<.25 for r in c['faces'])==48 and sorted(r['sourceFace']for r in c['faces']if r['signedNormalYRatio']<=-.25)==[59,111]
 new='government-xl-ocean-upper-buried-facet-attachment-v2-20261027';attachment=take(new);worlds={m:take(new,m+'.json.gz')for m in MODES};assert verify_upper_attachment(worlds,ids)and attachment['allWitnessesAttachedWithinEndpointHeight']
 for mode in MODES:assert worlds[mode]['sourceWorldSHA256']==bound[mode]['sourceWorldSHA256']
 canonical=take(P+'upper-attachment-revalidation-v1-20261027');assert canonical['sourceOnlyAttachmentEvidenceRevalidated']and len(canonical['rows'])==4 and all(r['witnesses']==r['finiteAttachmentPaths']==r['pathsWithinEndpointHeight']==608 and r['disconnected']==0 for r in canonical['rows'])
 native_role=take('government-xl-ocean-native-junction-role-review-v1-20261027','ROOT-JUNCTION-ROLE-REVIEW.json');assert native_role['sourceSpecificArchitecturalInterfaceInterpretationAccepted']and native_role['sourceSHA256ByUid']==SOURCES
 # Every unordered co-import pair is retained; none is silently treated as clear.
 coimport=[]
 for a,b in combinations(sorted(SOURCES),2):
  order=[MAIN,b if a==MAIN else a]if MAIN in[a,b]else[a,b];name='government-xl-after-waterfront-ocean-four-junction-'+order[0].split('/')[1].split(':')[0]+'-'+order[1].split('/')[1].split(':')[0]+'-roles-v1-20261027'
  data=take(name);assert set(data['uids'])=={a,b}and data['sourceSHA256ByUid']=={a:SOURCES[a],b:SOURCES[b]}and len(data['rows'])==4 and {r['mode']for r in data['rows']}==MODES;coimport.append(data)
 foreign=take(P+'foreign-contacts-v1-20261027');assert foreign['foreignPairs']==len(foreign['rows'])==14
 for row in foreign['rows']:
  if row['foreignUid']not in SOURCES:assert all(r['allFiniteContactPairs']==0 for r in row['modes']if r['mode']!='before-basic')
 regress=take(P+'retained-regressions-v1-20261027');assert len(regress['nativeRows'])==27 and set(regress['nativeResolved'])==set(regress['requiredNativeUids'])and all(r['passed']for r in regress['nativeRows']);assert regress['basicFlags']==[dict(uid=UP,reasons=['increased-neighbour-ground-gap'])]
 scope=take(P+'regression-scope-v1-20261027','scope.json');forms=take(P+'regression-scope-v1-20261027','form-obligations.json.gz');assert len(forms)==scope['forms']==39 and scope['allInstalledActorsAccounted']==6985
 patch=take('government-xl-after-waterfront-ocean-four-nested-pair-surface-v1-20261027');assert patch['status']=='private-nested-coordinated-surface-validator-passed'and set(patch['uids'])==set(SOURCES)-{UP}and patch['bothEffectiveMembersRequired']and patch['newlyDerivedTerrainWorkFaces']<=25000
 admission=take(P+'diagnostic-admission-v1-20261027','ROOT-DIAGNOSTIC-ADMISSION.json');assert admission['supportByUid']=={UP:MAIN}and set(admission['retainedNativeUids'])==set(regress['requiredNativeUids'])
 atomic=take('government-xl-ocean-four-atomic-lifecycle-browser-v1-20261027','report.json');assert atomic['passed']and len(atomic['cases'])==5 and not atomic['pageErrors']and all(not c['audit']['violations']for c in atomic['cases'])
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==native_role['currentManifestSHA256'];refs.append(manifest)
 review=dict(uids=list(SOURCES),requiredOriginalAssembly=SOURCES,sourceSHA256ByUid=SOURCES,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),currentManifestSHA256=selection['manifestSHA256'],identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,physicalAcceptance=True,companionRootsApproved=True,rawCanonicalFailuresPreserved=True,rawPhysicalFailuresPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,nativeMetadataChanges=0,installedMetadataChanges=0,supportByUid={UP:MAIN},activationGroup=sorted(SOURCES),groundOwnerUids=sorted(set(SOURCES)-{UP}),retainedNativeUids=regress['requiredNativeUids'],retainedNativeRegression=regress,retainedNativeEntries=native_role['retainedNativeEntries'],leaseResources=admission['leaseResources'],currentNativeActors=6985,sourceFoundations=foundations,rawGroundCaps=caps,acceptedUpperCompoundFaces=ids,upperFacetAttachment=attachment,canonicalAttachment=canonical,acceptedOriginalCoimportInterfaces=coimport,acceptedOriginalNativeInterfaces=native_role['pairs'],unresolvedExternalBasicContacts=[],imagesActuallyViewed=images,reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,visualAcceptance=False,qualifiedForLiveVerification=False,installationApproved=False,publication=False,basis=[
 'All four complete immutable originals retain exact source identity and fixed1x placement. The three ground owners pass complete four-world terrain-only foundations. The upper source depends explicitly on the main original podium, not an independently moved support.',
 'The main source has ten original grade-crossing wall continuations with verified source-owned clear-cap paths. Its five flagged sloping surfaces have ordinary shallow grade contact; every below-minus0.5m witness is a zero-horizontal-area vertical terrain seam with exactly zero deep source-surface area. Raw negative column distances remain recorded. The two small originals have no severe ground-negative facets in the complete partitions.',
 'ROOT inspected all three complete upper-component views with flagged-only panels. Faces59/111 belong to the thin downward-facing U-shaped lower closure/underside surface, not upward occupied-floor geometry. The48 near-vertical flagged facets are lower facade/trim continuations within the original core and small curved strip component. Accept only these exact50original lower-interface faces against the original podium; the raw50compound burial flags and zero upward buried count remain unchanged.',
 'All200vertex/centroid witnesses on those50facets, and all608canonical strict-support failures, reach original positive finite podium intersections in every coordinate stream along original shared edges, with no intercomponent joins, no extra rise and residual below the existing1mm gate. These are lower-interface attachment observations and source-role interpretation, not an engineering certification or proof for arbitrary connected meshes.',
 'The complete original U-shaped upper/main assembly and lower companion structures were inspected previously. Their exact original shared-plane/crossing joins are interpreted as the same source-authored stepped podium and connecting arcade interfaces; all six coimport pair reports and the separately reviewed four native interfaces remain explicit. Native-role context uses the operator floor plan only qualitatively, not as exact survey registration.',
 'All39affected forms and all27retained natives remain covered by the preserved terrain/regression scope. The lone basic regression flag is the upper source being replaced in this exact assembly, not an unrelated retained building. All non-coimport final source/BASIC contacts are zero. The4sources must activate/fall back together; successful all-peer failure/retry lifecycle evidence is separately bound. No original is safe to publish independently under this review.'
 ],remaining=['Fresh current staged desktop/mobile source and all27retained native views, picking/collision and atomic fallback tests','Guarded supported-coimport retained-terrain publisher: three ground owners, four original sources, no installed support metadata rewrite','Live verification, exact all521XL and all6985oldactor readback, Neon installed acceptance, commit and push'])
 save(out/'ROOT-PHYSICAL-REVIEW.json',review);save(out/'summary.json',dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,physicalAcceptance=True,sourceSpecificPhysicalInterpretationAccepted=True,companionRootsApproved=True,visualAcceptance=False,installationApproved=False,publication=False))
 module('ocean_original_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-original-ocean-assembly-bounded-physical-source-review-v1',refs,dict(uids=list(SOURCES),sourceSpecificPhysicalInterpretationAccepted=True,physicalAcceptance=True,companionRootsApproved=True,visualAcceptance=False,installationApproved=False))
if __name__=='__main__':main()
