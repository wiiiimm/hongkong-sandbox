"""Fence complete original podium/current-ground graph and unresolved pair gates."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read,digest,save
BASE=ROOT/'docs/astra-city/government-import';GROUND='government-xl-yoho-original-podium-current-ground-20261010';GRAPH='government-xl-yoho-original-podium-strict-anchor-paths-20261010';EXPAND='government-xl-yoho-original-podium-complete-drawn-ground-20261010'
def main():
 x=read(BASE/GRAPH/'diagnostic.json.gz');g=read(BASE/GROUND/'diagnostic.json.gz');foot=read(BASE/GROUND/'complete-original-podium-ground-interfaces.json.gz');original=read(BASE/'government-xl-yoho-eight-actual-current-podium-support-20261009/complete-current-rendered-podium-inputs.json.gz');expanded=read(BASE/EXPAND/'complete-current-rendered-podium-inputs.json.gz');assert original['drawnGroundGeometry']==expanded['drawnGroundGeometry'];s=x['summary'];assert len(s['strictOriginalCurrentGroundAnchors'])==13 and s['positiveOriginalAnchorPaths']==111 and s['componentsWithoutPositiveAnchorPath']==[99,100,107,108]
 save(BASE/EXPAND/'bounds-replay.json',{'completeExpandedOriginalPodiumBounds':expanded['completeOriginalPodiumExtractionBounds'],'expandedWholeOriginalGroundEqualsEarlierGroundExactly':True,'completeGroundFaces':len(expanded['drawnGroundGeometry']['index'])//3,'unchanged7731FaceRerunAvoided':True,'initialCropSuspicionRejected':True,'qualification':'Expanded original bounds produce identical2038 current drawn facets. The68 coverage failures are exact no-buffer clipped projection diagnostics, not proof of omitted source bounds or terrain/source corruption.'})
 paths=[Path(__file__)]+[HERE/p for p in ['xl-yoho-original-podium-current-ground-20261010.py','xl-yoho-original-podium-complete-drawn-ground-20261010.mjs','xl-yoho-original-podium-ground-interfaces-20261010.mjs','xl-yoho-original-podium-ground-anchor-paths-20261010.py','original_face_ground_crossing_v2_20261009.py','original_face_ground_crossing_20261009.py','original_degenerate_ground_context_20261009.py','source_closed_components.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py','support-interface.mjs','support-contact.mjs','triangle-point-index.mjs']]
 for d in [g,x,expanded]:paths.extend(ROOT/p for p in d['inputHashes'])
 paths.extend(p for p in (BASE/EXPAND).rglob('*') if p.is_file())
 (BASE/GROUND/'README.md').write_text('''# Complete untouched Yoho original podium versus current ground

All7731 unchanged original podium faces and115 original components are retained.
Actual current drawn ground was independently expanded to every original podium
bound and produced exactly the same2038 facets as the earlier export (2022 have
positive projected area). An initial crop suspicion was rejected; no expensive
unchanged7731-face rerun occurred.68 no-buffer face projection coverage diagnostics
remain, e.g. face233 missing0.0003313m²; they do not prove source corruption or
omitted extraction bounds.256 faces reach below−0.5m; two upward faces183/184
reach−0.752262/−0.675142m. All full continuous witnesses are retained.

The original differs materially from the failed basic podium:13 original parts
pass strict whole current-ground footing. Those are positive diagnostics, not
load-bearing/collision approval. Whole original pair current/primary target
coverage98.243%, raw12.6304m extent and7.20946m² foreign excess remain unresolved.
The original pair/terrain/support/runtime route must clear these independently.
''')
 (BASE/GRAPH/'README.md').write_text('''# Yoho complete original podium strict-anchor component graph

Full7731-face original podium cross-component interfaces were examined with
inclusive unpadded bounds and exact rational coordinates:16126candidate pairs,
2001positive interfaces and969point contacts (zero bridge credit). Complete115
components remain;13strict original current-ground footing parts seed111positive
paths, including the complete4019-face mainbody via component29. The four unrooted
source parts99/100/107/108 contain2/8/2/8faces, remain retained and need original
surface-role interpretation. Graph/contact reachability alone is not load bearing.

The exact unrelated current actors remain: open-sided structure55568 overlaps
4.79850m² across22original source faces; YohoTownBlock7/121143 overlaps2.41035m²
across9faces; tiny Tower4757 contributes0.000605m² across12faces. Same parent or
same site does not exempt them. All polygons/face IDs/vertices are recorded.
Original Block7 source exists15384faces; no exact open-sided55568original was
found in the bounded indexed native model query, which is not territory absence.

Next work: authentic original source-TIN comparison, explicit original neighbouring
source/role evidence, continuous ground-gap explanation, four detached podium and
143 detached Tower8 source surface roles. No source geometry edits, actor omission,
threshold waiver, physical/runtime/browser acceptance or installation occurs.
''')
 spec=importlib.util.spec_from_file_location('yoho_original_current_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(GROUND,'every-original-podium-face-component-current-ground-and-fullpair-foreign-context-v1',paths,{'uids':['landsd/146396:0','landsd/231756:0'],'identityAccepted':False,'scriptFullAcceptancePassed':False,'completeOriginalPodiumFaces':7731,'completeOriginalPodiumComponents':115,'strictOriginalCurrentGroundAnchors':13,'uncoveredOriginalFaces':68,'buriedUpwardOriginalFaces':[183,184],'rawFullPairExtentM':g['summary']['sourcePairSpatial'][0]['completePairMaximumExtentM'],'rawFullPairForeignExcessM2':g['summary']['sourcePairSpatial'][0]['completePairForeignExcessM2'],'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'original-pair-extent-and-exact-foreign-actors-plus-original-ground-surface-roles','nextStep':'Recover authentic original source TIN and named neighbouring source ownership; retain independent component/foreign/runtime/browser gates.'})
 m.freeze(GRAPH,'all-exact-original-podium-interfaces-and-strict-current-ground-anchor-paths-v1',paths+[BASE/GROUND/'result.json'],{'uids':['landsd/146396:0','landsd/231756:0'],'identityAccepted':False,'scriptFullAcceptancePassed':False,'completeOriginalPodiumComponents':115,'strictOriginalGroundAnchorComponents':s['strictOriginalCurrentGroundAnchors'],'completePositiveOriginalPodiumPaths':111,'remainingOriginalPodiumComponents':[99,100,107,108],'rawForeignActors':s['foreignExcessActors'],'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'four-source-podium-surface-roles-plus-exact-neighbouring-source-and-fullpair-physical-gates','nextStep':'Continue source TIN and explicit original neighbour/facade interpretations. Grounded originals and exact contacts are evidence, not acceptance or a basic actor bypass.'})
if __name__=='__main__':main()
