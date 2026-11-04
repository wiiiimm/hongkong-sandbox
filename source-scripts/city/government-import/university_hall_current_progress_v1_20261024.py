"""Persist actionable University Hall current-ground evidence without placement approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-next-repairs-university-hall-93417-';batch=prefix+'current-progress-v1-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];jobs={}
    names=[prefix+'current-prephysical-v1-20261024']
    names += [prefix+'current-prephysical-v1-20261024-'+phase for phase in ['attributes','foundations','plots','boundary','continuous','coverage']]
    names += [prefix+suffix+'-v1-20261024' for suffix in ['four-world-low-faces','literal-clear-cap-paths','four-world-wall-grade','four-world-cap-equivalence','current-model-scope','current-foreign-contacts']]
    for name in names:
        receipt,pins=authenticate(base/name);jobs[name]=receipt['jobId'];refs.append(base/name/'result.json');path=base/name/'summary.json'
        if path.exists():assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path)
    result=dict(uids=['landsd/93417:0'],status='held-for-bounded-original-wall-role-and-placement-acceptance',heldForCompute=True,heldForHumanDecision=False,aiGeometryModellingRequired=False,permanentRejection=False,installationApproved=False,publication=False,newlyInstalled=0,sourceGeometryChanges=0,sourcePoseChanges=0,terrainChanges=0,evidence=jobs,completed=[
        'All14777sourcefaces terrain-covered/no whollyburied/no upwardburied facets in allfourcoordinate streams on unchanged currentterrain.',
        'Allfour complete sourceworld triangle arrays are byte-identical. Authenticated literal clear-cap paths therefore apply to the same exact inputs across allfourrepresentations; no tolerance or approval transfer to changed bytes.',
        'Exactly14sourcefaces exceed ordinary-.5m clearance; allverticalwall-like, allhave highestoriginalvertex above every finite overlapping groundfacet. Allotherfaces accounted by exactheight-bound or completefinitepair checks.14662faces globallypruned,242exactfinitepairs perworld.',
        'All14affected literalwalls have exactshared-edge paths to ordinarilyclear upwardsourcecaps and no rawexposurefailures.15genuine zero-gap finite upper-ground intervals for those14walls in each4world; complete actual groundfacets retained withno zeroXZomissions.',
        'Complete current model-only scope checks6863nativeactors: zero nativecandidates,2currentforms. Sole foreignbasic121501 haszero positivecontacts/zero projectedoverlap before and in allfourproposedworlds.',
        'ROOT inspected complete two-angle sourceperspectives and fullsourceplan. Lowerfacets still need actual source-specific wall-role interpretation; no terrainshift or remodelling.'
    ],remaining=[
        'Prephysical suite intentionally stops at canonical rims because14realwallclearance failures persist. Preserve them; qualify actual exposed originalwall role with finitegrade/cap/context evidence under existing rules, plus fullcontact/foundation acceptance.',
        'Complete source-specific current-scene and staged/live desktop/mobile/picking/fallback/publication checks before installation. Do not add component engineering or globalwatertightness gates.',
        'Original TIN changes are unnecessary unless a concrete unresolved currentterrain failure justifies them: current source haszero whollyburied faces; broad originalTIN trial had11buriedwalls and missing13024m2rectangle. Do not fill large gaps or clamp authenticterrain.'
    ],fixedXL=dict(total=521,installed=339,unfinished=182),currentDetailedActors=6863,scriptExternalAICalls=0,qualification='Evidence checkpoint only. Existing original mesh/pose/terrain unchanged; no model installed or declared permanently unfixable.')
    save(out/'summary.json',result);module('university_current_progress_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'university-hall-current-whole-source-exact-wall-and-foreign-progress',refs,result)

if __name__=='__main__':main()
