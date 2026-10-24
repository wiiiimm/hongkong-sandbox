"""Fence positive actual current contacts and their independently failing footing."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read,digest
BATCH='government-xl-miami-three-current-rendered-podium-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
UIDS=['landsd/202599:0','landsd/203438:0','landsd/203441:0']
def main():
 x=read(DOC/'complete-current-rendered-podium-inputs.json.gz');foot=read(DOC/'complete-current-rendered-podium-footing.json.gz');assert not foot['strictCurrentDrawnGroundAnchor'];summary=read(DOC/'summary-v2.json');assert all(r['remaining']==0 for r in summary['rows']);assert {r['uid'] for r in summary['rows']}==set(UIDS)
 paths=[ROOT/p for p in x['inputHashes']]+[Path(__file__)]+[HERE/p for p in ['xl-miami-three-current-podium-inputs-20261009.mjs','xl-miami-three-current-podium-contacts-20261009.py','xl-miami-three-current-podium-contacts-v2-20261009.py','xl-miami-three-current-podium-footing-20261009.mjs','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py','support-interface.mjs','support-contact.mjs','triangle-point-index.mjs']]
 selected=read(DOC.parent/'government-xl-miami-fourteen-original-current-diagnostic-20261009/selection.json.gz')
 for row in selected['rows']:
  if row['uid'] in UIDS:asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];paths.append(asset)
 for uid in UIDS:paths.append(DOC.parent/'government-xl-miami-complete-edge-attachment-20261009'/(uid.split('/')[1].replace(':','-')+'-complete-edge-attachment.json.gz'))
 spec=importlib.util.spec_from_file_location('miami_current_podium_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'complete-original-current-podium-paths-and-independent-drawn-ground-root-failure-v1',paths,{'uids':UIDS,'positiveCompleteCurrentRenderedPodiumPaths':summary['rows'],'strictCurrentRenderedPodiumRootPassed':False,'currentRendererPodiumUID':foot['uid'],'currentFooting':{'samples':foot['result']['samples'],'strictContacts':foot['result']['strictContacts'],'wallIntersections':foot['result']['wallIntersections'],'missing':foot['result']['strictLowRim']['missing'],'minGapM':foot['result']['strictLowRim']['minGap'],'maxGapM':foot['result']['strictLowRim']['maxGap']},'originalZeroAreaFacesRetainedWithoutContactCredit':True,'firstTriangleGuardFailurePreserved':True,'physicalSupportAccepted':False,'scriptFullAcceptancePassed':False,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'requiresMoreComputeOrSourceEvidence':True,'remainingReason':'actual-retained-basic-podium-complete-drawn-ground-rooting-fails','nextStep':'Continue actual supported original podium assembly or independently valid unchanged source-TIN placement. No support credit through an absent original podium, current root failure or point/zero-area face; do not change original geometry or other actors.'})
if __name__=='__main__':main()
