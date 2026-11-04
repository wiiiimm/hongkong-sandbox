"""Measure complete Tower/Podium family coverage without filling source holes."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_projection_coverage_v2_20261010 import exact_coverage
COVERAGE={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage','original-source-does-not-cover-whole-georef-cell'}


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-island-industrial-complete-family-coverage-v1-20261023';out=base/batch;assert not out.exists();refs=[Path(__file__)];cache={}
    def take(batch,name):
        if batch not in cache:cache[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=base/batch/name;assert digest(p.read_bytes())==cache[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    runtime='government-xl-island-cheong-shing-four-original-runtime-v2-20261023';selection=take(runtime,'selection.json.gz');metadata=take('government-xl-island-industrial-three-primary-identity-v1-20261023','summary.json');typed='government-xl-island-industrial-typed-primary-routing-v2-20261023';typeproof=take(typed,'summary.json');assert typeproof['typedMetadataRoutesQualified']
    family=['landsd/20270:0','landsd/159422:0'];sources=[next(r for r in selection['rows']if r['uid']==uid)for uid in family];assert {r['modelId']for r in sources}=={'B348962051701063C0','B348962051702063C0'}
    records=[r for r in metadata['rows']if r['uid']in family];assert len(records)==2 and all(r['occupationPermits']==['K28/80']for r in records)
    structures=[r for r in metadata['completePermitStructures']if r.get('OPNo')=='K28/80'];ids={int(r['BuildingStructureID'])for r in structures};assert len(ids)==len(structures)==2
    relations=[r for r in metadata['completePermitRelations']if int(r['BuildingStructureID'])in ids];assert len(relations)==2 and {r['BuildingCSUID']for r in relations}=={r['source']['building']['buildingCSUID']for r in sources}
    forms=[r['building']for r in take('government-xl-island-industrial-paired-current-neighbours-v1-20261023','neighbour-inputs.json.gz')['rows']];assert len(forms)==len({r['uid']for r in forms})==774
    for r in sources:assert next(f for f in forms if f['uid']==r['uid'])==r['source']['building']
    triangles=[];pinned={}
    for row in sources:
        p=ROOT/row['candidate']['path'];raw=p.read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(p);t=decode_original_world_triangles(raw);assert len(t)==row['triangles'];triangles.append(t);pinned[row['uid']]=row['sourceSHA256']
    complete=np.concatenate(triangles);projection=shapely.union_all([shapely.MultiPoint(t[:,[0,2]]).convex_hull for t in complete]);polygons=[shapely.Polygon(r['source']['building']['rings'][0],r['source']['building']['rings'][1:])for r in sources];target=shapely.union_all(polygons)
    coverage=projection.intersection(target).area/target.area;extent=float(shapely.distance(shapely.points(complete[:,:,[0,2]].reshape(-1,2)),target).max());assert coverage>=.95 and extent<=10
    identities='government-xl-island-cheong-shing-four-original-identities-v1-20261023';raw=[take(identities,uid.split('/')[1]+'/identity.json')for uid in family];cells=[r['geographicCell']for r in raw];assert all(r['precisionMetres']==1 and r['targetCoversWholeCell']for r in cells);assert cells[0]['worldXZBounds']==cells[1]['worldXZBounds'];x0,z0,x1,z1=cells[0]['worldXZBounds'];corners=np.array([[x0,0,z0],[x1,0,z0],[x1,0,z1],[x0,0,z1]]);cellproof=[exact_coverage(corners[ids],complete)for ids in [[0,1,2],[0,2,3]]];assert all(p['exactProjectionCovered']for p in cellproof)
    foreign=[]
    for form in forms:
        if form['uid']in family:continue
        poly=shapely.Polygon(form['rings'][0],form['rings'][1:]);area=float(projection.difference(target).intersection(poly).area)
        if area>0:foreign.append(dict(uid=form['uid'],sourceExcessOverlapM2=area,structureType=form.get('structureType'),buildingCSUID=form.get('buildingCSUID')))
    rows=[]
    for uid in family:
        p=next(r for r in typeproof['rows']if r['uid']==uid);rows.append(dict(uid=uid,rawTypedReasons=p['reasons'],familyCoverageReasonsEligibleForInterpretation=sorted(set(p['reasons'])&COVERAGE),remainingReasons=[r for r in p['reasons']if r not in COVERAGE],identityAccepted=False))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    result=dict(uids=family,rows=rows,completeSourceFaces=len(complete),coInstallationRequired=pinned,currentManifestSHA256=selection['manifestSHA256'],familyProjectionQualified=True,wholeFamilyCurrentTargetCoverage=coverage,maximumFullFamilyExtentM=extent,uncoveredTargetAreaM2=float(target.difference(projection).area),sourceOutsideFamilyFootprintM2=float(projection.difference(target).area),exactWholeGeoRefCellProofs=cellproof,foreignExcessOverlaps=foreign,all774CurrentFormsRetained=True,sourceGeometryChanges=0,identityAccepted=False,installationApproved=False,qualification='Two exact typed official Tower/Podium originals under one complete K28/80 permit jointly cover the current feature family and its reference cell under existing 95%/10m gates. Original partial-podium projection/cell failures retained. This interpretation requires both exact originals co-installed; no hole fill, asset merge, source edit, foreign overlap, physical, terrain, collision or publication exemption. Remaining unrelated-form reasons still prevent full identity acceptance.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_projection_coverage_v2_20261010.py']);module('family_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'complete-typed-original-feature-family-coverage-context',refs,result);print({k:result[k]for k in ['completeSourceFaces','wholeFamilyCurrentTargetCoverage','maximumFullFamilyExtentM','foreignExcessOverlaps','rows']},flush=True)

if __name__=='__main__':main()
