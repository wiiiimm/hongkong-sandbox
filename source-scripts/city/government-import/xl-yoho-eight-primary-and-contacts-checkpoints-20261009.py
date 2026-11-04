"""Durable source-only Yoho primary relation and original-contact checkpoints."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,digest
BASE=ROOT/'docs/astra-city/government-import'
PRIMARY='government-xl-yoho-eight-primary-podium-discovery-20261009'
CONTACT='government-xl-yoho-eight-original-podium-contacts-20261009'
def main():
 spec=importlib.util.spec_from_file_location('yoho_originals_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 p=BASE/PRIMARY;d=read(p/'original-source-lookup.json.gz');assert len(d['exactRelations'])==2 and len({x['attributes']['BuildingStructureID'] for x in d['exactRelations']})==2
 assert {x['attributes']['OPNo'] for x in d['exactStructures']}=={'NT21/2004(OP)'}
 (p/'README.md').write_text('''# Yoho Town Block 8 and original podium primary discovery

Fresh authoritative provider records uniquely identify Tower8 CSUID
2179133649T20050430 / BuildingID1105737045 and podium CSUID2187833636P20050609.
Both original assets were already captured unchanged in the native government
model cache; no new mesh authoring or remodelling occurred. Exact current
relationships resolve Tower8 to structure5285253 and podium to5285219 under
occupation permit NT21/2004(OP). These are distinct structure identifiers.
The common permit provides site context only, not ownership or support credit.

Raw provider responses, exact request parameters, full native source metadata,
original source hashes and related structure responses are retained. No current
model metadata, source placement, geometry, acceptance state, or catalogue changed.
No whole-source or foreign actor gate is waived. The carved podium footprint
must be investigated using full original geometry and independent physical gates.
''')
 paths=[Path(__file__),HERE/'xl-yoho-eight-primary-podium-discovery-20261009.py']
 m.freeze(PRIMARY,'fresh-distinct-original-tower8-and-podium-primary-relations-v1',paths,{'uids':['landsd/146396:0','landsd/231756:0'],'identityAccepted':False,'scriptFullAcceptancePassed':False,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'complete-original-component-ownership-and-current-physical-route-unproved','nextStep':'Compare all untouched original components and preserve distinct primary structures. Same permit alone cannot remove actor or support gates.'})
 p=BASE/CONTACT;d=read(p/'diagnostic.json.gz');s=read(p/'summary.json')
 for r in d['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 (p/'README.md').write_text('''# Yoho Tower 8 complete original podium contacts

All14,792 Tower8 faces /953 exact-edge components were compared with all7,731
unchanged original podium faces, using inclusive unpadded bounds and exact
rational intersections. The2084-face main tower component has42 exact
positive line contacts to the original podium. Each other component is retained
and requires complete original tower-body interface/role accounting; a lack of
direct podium contact is not automatic proof of a defective component.

The fresh primary Tower8 footprint lies353.9823873966452 square metres outside
the carved primary podium footprint. Its recorded base lies inside the podium
vertical span, but the simple entire-footprint-contained alternate identity route
correctly does not apply. Distinct OP structures remain distinct. These metrics
do not justify a same-permit blanket exception or any current actor suppression.

Exact source bytes, complete source-world hashes, every original component and
all original podium contacts remain in diagnostic.json.gz. This is source-only
research: an original podium absent at runtime grants no current support credit.
Fresh full physical, current ownership, foreign, runtime and browser acceptance
remain independently required. No source/terrain edits or installation occurred.
''')
 paths=[Path(__file__),HERE/'xl-yoho-eight-original-podium-contacts-20261009.py',*[ROOT/r['path'] for r in d['evidenceRefs']],BASE/PRIMARY/'result.json']
 m.freeze(CONTACT,'complete-original-tower8-to-podium-interfaces-v1',paths,{'uids':['landsd/146396:0','landsd/231756:0'],'identityAccepted':False,'scriptFullAcceptancePassed':False,'completeOriginalFaces':[14792,7731],'towerOriginalComponents':953,'componentsWithDirectOriginalPodiumContact':1,'mainBodyPositiveOriginalContacts':42,'primaryTowerOutsidePodiumAreaM2':d['primaryTowerOutsidePodiumAreaM2'],'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'carved-primary-podium-relation-and-complete-original-component-support-unproved','nextStep':'Trace complete original component contacts through the main tower and exact podium geometry, retaining all source faces/current actors. Fresh current runtime support cannot use an absent original podium.'})
 print(json.dumps({'stages':[PRIMARY,CONTACT],'publication':False}),flush=True)
if __name__=='__main__':main()
