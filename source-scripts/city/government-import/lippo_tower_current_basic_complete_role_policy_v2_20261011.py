"""Narrow current Lippo role composition; file/provenance adapter mandatory.
No generic source collisions or unknown ordinary failures are cleared.
"""
from copy import deepcopy
from lippo_tower_current_basic_mainbody_join_role_v1_20261011 import TOWER,CARRIER,SOURCE
DEPENDENCY=dict(uid=CARRIER,csuid='3551417531P20050812',state='surveyed-footprint-fallback')
def validate_semantics(identity,physical,separation,role,current_manifest):
 assert identity['passed'] is True and identity['reasons']==[]
 assert physical['uid']==TOWER and physical['currentManifest']==current_manifest
 assert physical['ordinaryNumericReasons']==['ground-contact-unresolved']
 assert physical['strictFoundationAccepted'] is True and physical['completeOwnedFaces']==3597
 assert physical['loaderAccepted']==physical['runtimeChecksPassed']==1 and physical['runtimeExceptions']==0
 assert physical['neighbourRegressionReasons']==[] and physical['currentNeighbourForms']==21
 assert physical['terrainGeometryChanges']==physical['sourceGeometryChanges']==0
 raw=physical['rawRuntimeConcerns'];assert len(raw)==1 and raw[0]['uid']==TOWER and raw[0]['triangles']==3597
 assert raw[0]['concerns']==['sampled-ground-gap-below-model-bottom']
 native=physical['rawNativeNeighbourChecks'];assert native['blocked']==[] and native['modelGeometryChanges']==0
 assert separation['currentManifest']==current_manifest and separation['uid']==TOWER and separation['sourceSHA256']==SOURCE
 cert=separation['completeNativeActualBoundsCertificate'];assert cert['completeForeignNativeActors']==6639 and len(cert['rows'])==6639
 assert cert['allFourOwnedByThreeActualNativeWorldBoundsStrictlyDisjoint'] is True and cert['noToleranceOrGeographicBufferCredit'] is True
 assert role['uid']==TOWER and role['carrierUid']==CARRIER and role['sourceSHA256']==SOURCE
 assert role['sourceRoleProposal'] is True and role['sourceGeometryChanges']==role['terrainGeometryChanges']==role['thresholdChanges']==0
 assert role['wholeBasicReaccepted'] is False and role['governmentPodiumUsedAsRuntimeSupport'] is False
 assert len(role['rows'])==4 and all(r['completeSourceFaces']==3597 and r['mainbodyFaces']==3459 and r['completeMainbodyNonzeroEdgePathProved'] is True for r in role['rows'])
 return dict(uid=TOWER,reasons=[],scriptChecksPassed=True,acceptanceReadyForStaging=True,physicalAccepted=True,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,rawOrdinaryNumericReasons=physical['ordinaryNumericReasons'],rawRuntimeConcerns=raw,currentBasicCarrierDependency=deepcopy(DEPENDENCY),wholeBasicReaccepted=False,originalGovernmentPodiumUsedAsRuntimeSupport=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,qualification='Only exact named connected lower-mainbody/current BASIC carrier join and bounded exposed grade/clear-cap paths resolve the recorded ordinary lowest-bottom gap. Complete source/current/foreign/runtime/whole-foundation checks remain bound; all raw warnings/contact/interior records retained. Availability metadata reserves existing BASIC, not legal ownership or whole BASIC/load-bearing certification. Staged/live/browser/current publication gates remain independent.')

def staged_entry(original):
 assert original['uid']==TOWER and original['sha256']==SOURCE and original['buildingCSUID']=='3551817554T20050430'
 assert original['modelId']=='B355181755401063C0' and original['triangles']==3597
 assert original.get('supportDependencies',[])==[]
 out=deepcopy(original)
 out.update(priority='detail',proceduralWindows=False,placementReviewed=True,identityReviewApproved=True,sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,publicationApproved=True,supportDependencies=[deepcopy(DEPENDENCY)],placementReview='Complete unchanged original Lippo Tower. All3597 source faces and4 zero-area records retained; five real components have complete source/actual bounded BASIC wall-grade-to-strict-clear-cap paths. Only exact connected mainbody6 lower interface is interpreted as authored join to actual retained BASIC231645, preserving every raw contact and exact original/F32 3/2m versus literal Fraction depth; other current actors remain foreign. Full original/literal/two declared Float32 finite clearance, all6639 actual native unused-POSITION bounds, current full neighbour/runtime/foundation and stage/live gates remain independent. BASIC dependency reserves availability only; whole BASIC bottom/rim is not reapproved. No AI geometry modelling.')
 assert out['sha256']==original['sha256'] and out['worldBounds']==original['worldBounds'] and out['rootTranslation']==original['rootTranslation']
 return out
