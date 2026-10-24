"""Checkpoint exact protected terrain and recovered assembly; preserve raw holds."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-next-repairs-west-kowloon-bus-';batch=prefix+'bounded-inset-progress-v2-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={};jobs={}
    def take(s,f='summary.json'):
        n=prefix+s
        if n not in pins:
            receipt,pins[n]=authenticate(base/n);jobs[n]=receipt['jobId'];refs.append(base/n/'result.json')
        p=base/n/f;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    patch=take('protected-return-inset-v1-20261024');assert patch['terrainValidationPassed']if 'terrainValidationPassed'in patch else patch['status']=='private-terrain-validator-passed';assert patch['terrainTriangles']==2624 and patch['changedParentFaces']==14
    neighbours=take('protected-return-neighbours-v1-20261024');assert not neighbours['flagged']
    runtime=take('protected-return-runtime-v1-20261024');assert len(runtime['rows'])==1 and runtime['rows'][0]['fullyBuriedTriangles']==runtime['rows'][0]['fullyBuriedUpwardTriangles']==0
    low=take('protected-return-low-faces-v1-20261024');assert len(low['rows'])==4 and all(len(r['exactAffectedFaces'])==527 and r['allAffectedWallLike']for r in low['rows'])
    caps=take('complete-ground-cap-paths-v2-20261024');assert caps['allFourCompleteGroundClearCapPaths']
    views=take('wall-source-views-v2-20261024');assert len(views['views'])==6;images=[]
    for r in views['views']:
        p=ROOT/r['image'];assert digest(p.read_bytes())==r['sha256'];refs.append(p);images.append(dict(path=r['image'],sha256=r['sha256']))
    foreign=take('protected-full-foreign-v1-20261024');assert foreign['foreignPairs']==10
    roles=take('foreign-contact-views-v1-20261024');assert len(roles['rows'])==5
    for r in roles['rows']:
        p=ROOT/r['image'];assert digest(p.read_bytes())==r['imageSHA256'];refs.append(p);images.append(dict(path=r['image'],sha256=r['imageSHA256']))
    recovery=take('three-companion-acquire-v1-20261024');assert recovery['sourceRecovered']and len(recovery['rows'])==3
    selected=take('five-original-selection-v1-20261024','selection.json.gz');assert len(selected['rows'])==5 and sum(r['triangles']for r in selected['rows'])==18280
    identity=take('five-original-identity-v1-20261024');assert all(r['passed']for r in identity['rows'])
    pair_rows=[]
    for name in ['roof231056-support-v1-20261024','roof267223-support-v1-20261024']:
        report=take(name);assert not report['allFourModesPassed'];pair_rows.append(dict(supportedUid=report['supportedUid'],rows=[dict(mode=r['mode'],passed=r['passed'],samples=r['support']['samples'],strictContacts=r['support']['strictContacts'],unresolved=len(r['support']['unresolved']),fullyBuriedTriangles=r['compoundFoundation']['fullyBuriedTriangles'])for r in report['rows']]))
    exact=take('five-original-exact-contacts-v1-20261024');assert len(exact['rows'])==10
    current_foreign=take('five-original-foreign-v1-20261024');assert current_foreign['foreignPairs']==16
    plots=take('five-original-plots-v1-20261024');assert plots['completeOriginalFaces']==18280
    for f in ['complete-original-assembly.png','base-only-diagnostic.png']:
        n=prefix+'five-original-plots-v1-20261024';p=base/n/f;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    result=dict(uids=[r['uid']for r in selected['rows']],primaryXLUid='landsd/255415:0',status='held-for-compute-original-assembly-interfaces-and-browsers',heldForCompute=True,heldForHumanDecision=False,aiGeometryModellingRequired=False,permanentRejection=False,installationApproved=False,publication=False,newlyInstalled=0,sourceGeometryChanges=0,sourcePoseChanges=0,currentManifestSHA256=selected['manifestSHA256'],privateTerrainOnly=True,evidence=jobs,validatedPrivateTerrain=patch['candidate'],originalFaces=18280,sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in selected['rows']},rawSupportNegatives=pair_rows,imagesActuallyViewedByROOT=images,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,
        completed=['Protected original-TIN return clears every wholly buried/upward main-source face and preserves all six current neighbour checks; BASIC37934 regression resolved without support credit.','All527 finite lower-wall negatives retain exact all-ground/all-four-world ordinary-clear original cap paths, including positive partial original contacts; no filtered zero-XZ ground omissions. ROOT inspected all six representative two-angle exports, not every wall separately.','Full current source scope revealed five basic overlaps. Exact originals for four companions now available: one local and three recovered directly from pinned government ZIP members with exact prepared compressed hashes/bytes/face counts. All five fresh identity checks pass; complete assembly has18280faces.','All ten original pair contacts and sixteen full source/current-basic pair diagnostics completed; ROOT inspected all five crossing diagrams and full/base-only assembly views. No suppression or physical acceptance inferred from overlap.'],
        remaining=['Roof231056 strict support376/433 leaves57unresolved; compound context has4fully buried vertical faces (0upward), minimum-.993421m. Roof267223 strict402/404 leaves2unresolved, no whole buried face, minimum-.415449m. Resolve source-specific actual original roof/parapet interfaces while preserving raw strict failures; do not waive or alter geometry.','Two small original shafts have partial lower-wall/current-ground warnings; complete source/compound four-world clearance and role evidence remains.','New2025basic292042 has4original finite contacts/.00480285m2 projection overlap (before-basic12/.00872672m2). No same-sheet prepared original GeoRef counterpart found. Retain the actor and investigate exact boundary interaction, not a blanket size waiver.','Final effective five-original scene, retained dependencies, complete foundations/current neighbours and staged/live desktop/mobile day/night picking/collision/failure/retry remain required before installation.'],
        qualification='Actionable source-backed compute checkpoint, not installation or approval. Fixed521XL scope remains340installed/181unfinished,6864catalogueactors. No production terrain/catalogue/dependency edits in this checkpoint, optimisation, geometry modelling or permanent rejection.')
    save(out/'summary.json',result);module('west_progress_v2_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'protected-terminus-terrain-and-exact-companion-assembly-compute-checkpoint',refs,result)

if __name__=='__main__':main()
