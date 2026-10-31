"""Preserve completed private ground recovery independently of ongoing contacts."""
from pathlib import Path
import shutil
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying181489-five-ground-recovery-checkpoint-v1-20261029'
PHASES=['government-xl-after-peninsula-native-bounds-v1-20261029','government-xl-fuying181489-five-member-boundary-contract-v1-20261029','government-xl-fuying181489-five-boundary-witnesses-v2-20261029','government-xl-fuying181489-five-boundary-incident-faces-v1-20261029','government-xl-fuying181489-boundary-local-plane-nomination-v1-20261029','government-xl-fuying181489-five-member-boundary-contract-v2-20261029','government-xl-fuying181489-five-member-runtime-v2-20261029','government-xl-fuying181489-five-member-attributes-v1-20261029','government-xl-fuying181489-six-foundation-sequence-v1-20261029','government-xl-fuying181489-five-member-full-scope-v1-20261029','government-xl-fuying181489-five-member-neighbours-v1-20261029','government-xl-fuying233291-current-original-lookup-v1-20261029','government-xl-fuying233291-raw-source-context-v1-20261029','government-xl-fuying181489-complete-source-scope-v1-20261029']
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];evidence={}
 for name in PHASES:
  receipt,pins=authenticate(BASE/name);evidence[name]=receipt['jobId'];refs.append(BASE/name/'result.json')
  for filename in ['summary.json','scope.json','lookup.json']:
   path=BASE/name/filename
   if path.exists():assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path)
 ground=read(BASE/PHASES[5]/'summary.json');assert ground['allTerrainValidatorsPassed']and ground['allFiveEffectiveMembersVerified']
 foundations=read(BASE/PHASES[8]/'summary.json');assert foundations['allSixFourWorldFoundationsComplete']and foundations['allEstablishedFoundationPoliciesPassed']
 neighbours=read(BASE/PHASES[10]/'summary.json');assert neighbours['allNeighbourRegressionsResolved']and neighbours['forms']==40 and len(neighbours['allNativeRows'])==9
 refs.extend(HERE/n for n in ['fuying_whole_parent_five_boundary_v1_20261029.py','fuying_private_boundary_connectors_v1_20261029.py','test_fuying_whole_parent_five_boundary_v1_20261029.py','test_fuying_private_boundary_connectors_v1_20261029.py','fuying_source_contacts_sequence_v1_20261029.py'])
 out.mkdir();shutil.copyfile('/tmp/astra-fuying-boundary-all-tests-20261029.log',out/'tests.log')
 result=dict(uids=['landsd/181489:0'],sourceSHA256ByUid=ground['sourceSHA256ByUid'],evidence=evidence,installedXL=405,exactCurrentSourceTerminalXL=3,outstandingXL=113,fixedXLCohort=521,currentDetailedActors=7021,newlyInstalled=0,privateFiveTerrainValidatorsPassed=True,privateAllSixFourWorldFoundationsPassed=True,privateAll40FormsAnd9NativeRegressionsPassed=True,wholePriorTerrainPositionsAndIndicesPreserved=True,derivedConnectorFacetsAdded=39,aggregateDerivedTerrainFaces=49109,testsPassed=19,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,heldReason='Four original spatial/identity warnings remain pending exact foreign/basic/native contact and authored-role interpretation; private terrain/body checks do not grant installation.',nextStep='Continue active source-contact sequence (session32836, native worker3236173 observed CPU-active). Do not restart or edit it. Then inspect all contacts, complete exact source identity/physical roles, private390/1280 viewer and retained-native views, explicit five-member whole-parent publisher/live/readback gates. Keep current model and runtime terrain unchanged until installation.',activeWorker=dict(batch='government-xl-fuying181489-source-contact-sequence-v1-20261029',sessionId=32836,nativeWorkerPid=3236173,log='/tmp/astra-fuying-source-contacts-v1-20261029.log',publication=False))
 save(out/'summary.json',result);module('fuying_ground_checkpoint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-derived-ground-recovered-full-actor-scope-foundations-neighbours-checkpoint',refs,result)
if __name__=='__main__':main()
