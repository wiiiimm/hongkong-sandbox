"""Persist the validated small original-TIN repair and exact remaining obligations."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-next-repairs-west-kowloon-bus-';batch=prefix+'bounded-inset-progress-v1-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={};jobs={}
    def take(name,file):
        if name not in pins:
            receipt,pins[name]=authenticate(base/name);jobs[name]=receipt['jobId'];refs.append(base/name/'result.json')
        path=base/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    patch=prefix+'all-buried-local-inset-v1-20261024';q=take(patch,'summary.json');assert q['status']=='private-terrain-validator-passed' and q['terrainTriangles']==2615 and q['changedParentFaces']==14
    current=take(prefix+'all-buried-inset-runtime-v1-20261024','summary.json')['rows'][0];assert current['triangles']==current['completeTerrainTriangles']==15430 and current['fullyBuriedTriangles']==current['fullyBuriedUpwardTriangles']==0
    identity=take(prefix+'all-buried-inset-identity-v1-20261024','summary.json');assert identity['rows'][0]['passed']
    scope_name=prefix+'all-buried-inset-scope-v1-20261024';scope=take(scope_name,'scope.json');assert scope['intersectingForms']==6 and not scope['touchingNativeUids'] and not scope['terrainContacts']
    neighbours=take(prefix+'all-buried-inset-neighbours-v1-20261024','summary.json');assert len(neighbours['flagged'])==1 and neighbours['flagged'][0]['uid']=='landsd/37934:0'
    support=take(prefix+'retained-basic37934-support-probe-v1-20261024','summary.json');assert not support['allFourStrictSupportPassed'] and all(r['proof']['samples']==23 and r['proof']['strictContacts']==0 for r in support['rows'])
    suite=take(prefix+'all-buried-inset-prephysical-v1-20261024','summary.json');assert suite['stoppedAt']=='rims'
    lineage=take(patch,'lineage.json.gz');forms=take(scope_name,'form-obligations.json.gz');form=next(r for r in forms if r['uid']=='landsd/37934:0');core=shapely.from_wkt(lineage['coreWKT']);foot=shapely.Polygon(form['rings'][0],form['rings'][1:]);distance=core.distance(foot);area=core.intersection(foot).area;assert distance>1 and area==0
    result=dict(uids=['landsd/255415:0'],status='held-for-compute-neighbour-return-and-partial-wall-resolution',heldForCompute=True,heldForHumanDecision=False,aiGeometryModellingRequired=False,permanentRejection=False,installationApproved=False,publication=False,newlyInstalled=0,sourceGeometryChanges=0,sourcePoseChanges=0,privateTerrainOnly=True,evidence=jobs,validatedPrivateTerrain=q['candidate'],completeSourceFaces=15430,whollyBuriedFaces=0,upwardWhollyBuriedFaces=0,neighbourForms=6,flaggedBasicUid=form['uid'],retainedBasicStrictContactsByMode=[dict(mode=r['mode'],samples=r['proof']['samples'],strictContacts=r['proof']['strictContacts'],unresolved=len(r['proof']['unresolved']))for r in support['rows']],basicFootprintToRequiredInsetCoreDistanceM=distance,basicFootprintCoreOverlapAreaM2=area,
        completed='Local authenticated buried-surface original-TIN inset passes all existing terrain validators without coastal clamp changes. All14fullyburied original faces clear, including2upward surfaces. Identity passes. No existing native or terrain patch touches the full coarse replacement domain.',
        remaining=['Basic37934groundgap increases by0.91081m on the present3mreturn; do not waive its raw failure. Actual canonical original-podium support probes fail0/23strictcontacts in allfourworlds, so no support credit or dependency binding is allowed.','Originalsource partial-wall minimum remains-3.4775m; whole-source finite grade/cap/physical and sourceappearance evidence still required.','Current scene/manifest/native inventory must be freshly rebound after University Hall installation before any acceptance or publication. Historical source evidence remains diagnostic.'],
        nextActions=['Investigate a terrain return constrained to preserve the complete closed current BASIC37934footprint. The required authentic inset core is disjoint with1.1887mseparation, so a protected return is geometrically possible to investigate; no slope/Float32/neighbour acceptance is implied. Preserve all sourcevertices and all terrain validators, including exact coastal/ground nonregression.','If a protected return cannot meet unchanged guards, recover the exact additional original37934and its actual lower source context; do not invent an anchor or call it permanently unfixable.'],
        qualification='Source-backed local computation progress only. Existing coastal/terrain/contact/identity/placement gates retained, no production terrain edited, no source geometry generated, and no new installation credit.')
    save(out/'summary.json',result);module('west_bounded_progress_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'west-kowloon-zero-burial-private-terrain-and-real-next-compute-gates',refs,result)

if __name__=='__main__':main()
