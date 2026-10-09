"""Preserve real current basic root failure and complete positive source paths."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read,digest
BATCH='government-xl-yoho-eight-actual-current-podium-support-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
def main():
 x=read(DOC/'complete-original-to-actual-podium-paths.json.gz');f=read(DOC/'complete-current-rendered-podium-footing.json.gz');assert x['completeOriginalComponents']==953 and len(x['completePositivePathsToActualCurrentPodium'])==810 and len(x['remainingComponents'])==143;assert not f['strictCurrentDrawnGroundAnchor'] and f['result']['strictContacts']==0
 paths=[ROOT/p for p in x['inputHashes']]+[Path(__file__)]+[HERE/p for p in ['xl-yoho-eight-current-podium-source-inputs-20261009.py','xl-yoho-eight-current-podium-ground-20261009.mjs','xl-yoho-eight-current-podium-exact-paths-20261009.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py','yoho_eight_current_bound_identity_20261009.py']]
 inp=read(DOC/'complete-original-source-inputs.json.gz');paths.extend(ROOT/p for p in inp['inputHashes'])
 (DOC/'README.md').write_text('''# Yoho Tower8 exact actual basic podium support diagnosis

All14792 original Tower8 faces and all332 current drawn basic podium faces are
retained. Complete unpadded exact rational triangle intersections yield71 positive
line contacts from the original mainbody (292 candidate pairs). The full953-part
original graph gives810 parts a path to the actual current body;143 parts remain
detached. Point and zero-area faces grant no contact credit. These are geometric
interfaces, not load-bearing or collision approvals.

The actual current basic podium independently fails its strict full drawn-ground
anchor: all3437 samples have covered ground but zero strict contacts, and footing
gaps range from−3.430261 to−1.600036m. Full2038 current drawn terrain facets were
exported through the unchanged actual renderer, with terrain/manifest/code hashes.
No current podium, model, terrain or source edits or burial waivers occurred.

This negative only concerns the existing basic podium. It does not reject the
untouched7731-face government original or whole Yoho building. Its full source
surfaces, component rooting and original pair/foreign scope are investigated in
a separate fresh checkpoint. Identity acceptance remains separate; no installation
or physical support credit is granted through the absent original podium.
''')
 s=importlib.util.spec_from_file_location('yoho_basic_podium_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'complete-exact-actual-podium-source-paths-and-drawn-ground-root-failure-v1',paths,{'uids':['landsd/146396:0','landsd/231756:0'],'identityAccepted':False,'positiveCompleteActualCurrentPodiumPaths':810,'completeOriginalComponents':953,'remainingOriginalComponents':143,'currentBasicPodiumStrictGroundAnchor':False,'currentBasicPodiumFootingSamples':3437,'currentBasicPodiumStrictContacts':0,'currentBasicPodiumMinimumGapM':f['result']['strictLowRim']['minGap'],'currentBasicPodiumMaximumGapM':f['result']['strictLowRim']['maxGap'],'physicalSupportAccepted':False,'scriptFullAcceptancePassed':False,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'actual-basic-podium-buried-footing-and143-original-detached-components-unresolved','nextStep':'Measure complete7731-face original podium against current drawn ground/source TIN and every foreign actor, then seek full supported original assembly. Do not equate basic actor failure with original source impossibility.'})
if __name__=='__main__':main()
