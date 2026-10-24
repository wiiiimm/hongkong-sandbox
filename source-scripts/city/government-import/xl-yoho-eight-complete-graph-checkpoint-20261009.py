"""Fence whole-original graph preserving disconnected components and raw failures."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BATCH='government-xl-yoho-eight-complete-original-component-graph-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
def main():
 d=read(DOC/'diagnostic.json.gz');s=read(DOC/'summary.json');assert d['completeOriginalFaceCount']==14792 and d['completeOriginalComponentCount']==953 and s['positivePathsToOriginalPodium']==810
 assert sorted(i for r in d['originalComponentOutcomes'] for i in r['originalFaces'])==list(range(14792))
 for r in d['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 save(DOC/'progress.json',{'completeOriginalFaces':14792,'facesProcessed':14792,'exactIntercomponentCandidatePairs':d['exactIntercomponentCandidatePairs'],'exactContacts':len(d['completeExactOriginalInterfaces']),'complete':True,'geometryChanges':0})
 (DOC/'README.md').write_text('''# Yoho Town Block 8 complete original component graph

All14,792 original faces /953 exact-edge components were independently compared
for cross-component interfaces. The complete inclusive unpadded bounds pass
yielded64,282 candidate pairs, each checked with exact rational intersections.
7,796 positive-dimensional contacts connect810 components through the exact
original2084-face main tower to its42 positive original podium interfaces.
699 point contacts remain without bridge credit. Every face and every disconnected
component remains in the evidence; no mesh welding or tolerance merging occurred.

143 components remain disconnected from that original chain:66 components of34
faces,14 of16 faces,59 of4 faces,2 of2 faces,2 of1 face. Their small size is not
a rejection reason or a structural/decorative classification. Original hierarchy,
full-surface role and current physical support require further causal evidence.

The original main tower itself has193 boundary edges and15 nonmanifold edges;
no closed-solid or point-containment certificate is claimed. The original podium
is absent at runtime, so the positive source-only graph cannot confer current
support credit. Exact distinct primary structures and every current/foreign actor
remain independent. No identity/physical acceptance, source geometry changes,
model installation, terrain changes, or permanent rejection occurred.
''')
 paths=[Path(__file__),HERE/'xl-yoho-eight-complete-original-component-graph-20261009.py',*[ROOT/r['path'] for r in d['evidenceRefs']],ROOT/'docs/astra-city/government-import/government-xl-yoho-eight-original-podium-contacts-20261009/result.json']
 spec=importlib.util.spec_from_file_location('yoho_graph_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'whole-original-cross-component-positive-contact-graph-v1',paths,{'uids':['landsd/146396:0','landsd/231756:0'],'identityAccepted':False,'scriptFullAcceptancePassed':False,'completeOriginalFaces':14792,'completeOriginalComponents':953,'positiveSourceOnlyPaths':810,'unattachedOriginalComponents':143,'exactCandidatePairs':64282,'positiveOriginalContacts':7796,'pointContactsExcludedFromBridgeCredit':699,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'143-source-detached-parts-original-surface-role-and-complete-current-podium-support-unproved','nextStep':'Identify source-authored facade/surface roles using complete source topology/materials and primary imagery, then independently establish actual current support and all unchanged physical/foreign/runtime/browser gates. Retain every original component.'})
 print(json.dumps({'batch':BATCH,'positiveSourceOnlyPaths':810,'unattachedComponents':143}),flush=True)
if __name__=='__main__':main()
