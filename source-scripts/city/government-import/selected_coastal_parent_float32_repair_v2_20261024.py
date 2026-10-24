"""Private exact coastal-return rounding repair; original inputs and gates unchanged."""
import argparse,copy,subprocess,traceback
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from coastal_parent_float32_repair_v1_20261024 import audit,repaired_positions,MAXIMUM_LIFT_M
from coastal_return_scope_v1_20261024 import verify_return_scope


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','patch','capture','uid']:p.add_argument('--'+key,required=True)
    a=p.parse_args();assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.patch,a.capture])
    base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;local=HERE/'local'/a.batch
    assert not doc.exists()and not local.exists();refs=[Path(__file__),HERE/'coastal_parent_float32_repair_v1_20261024.py'];pins={}
    def take(batch,path):
        if batch not in pins:
            result,pins[batch]=authenticate(base/batch);refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    old=take(a.patch,base/a.patch/'summary.json')
    assert old['status']=='private-terrain-validator-passed'and old['uids']==[a.uid]
    original=ROOT/old['candidate']['path'];patch=copy.deepcopy(take(a.patch,original));original_sha=digest(original.read_bytes())
    scope=take(a.patch,base/a.patch/'scope.json');lineage=take(a.patch,base/a.patch/'lineage.json.gz')
    selection=take(a.capture,base/a.capture/'selection.json.gz');row=next(r for r in selection['rows']if r['uid']==a.uid)
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';current_sha=digest(manifest.read_bytes());assert current_sha==selection['manifestSHA256'];refs.append(manifest)
    terrainpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(terrainpath)
    assert digest(terrainpath.read_bytes())==patch['meta']['parentSha256'];refs.append(terrainpath)
    assert patch['meta']['targetUids']==[a.uid]
    save(doc/'scope.json',scope)
    tool=HERE/'selected_original_parent_capture_v2.mjs'
    subprocess.run(['node',str(tool),str((doc/'scope.json').relative_to(ROOT)),str((local/'parent.json').relative_to(ROOT))],cwd=ROOT,check=True)
    captured=read(local/'parent.json');assert captured['domain']==scope['bounds'];refs.extend([tool,local/'parent.json'])
    for path,sha in captured['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],sourceGeometryChanges=0,sourcePoseChanges=0,originalBuildingGeometryChanges=0,originalTerrainSourceFileChanges=0,publication=False,installationApproved=False,newlyInstalled=0,currentManifestSHA256=current_sha)
    try:
        mesh=patch['nativeMesh'];before_positions=copy.deepcopy(mesh['position']);before_index=copy.deepcopy(mesh['index'])
        before=audit(before_positions,before_index,captured['triangles']);save(doc/'before-exact-coastal-proof.json.gz',before)
        assert before and any(not r['passed']for r in before)
        faces=np.asarray(before_index).reshape(-1,3)
        assert len(lineage['outputLineage'])==len(faces)
        for r in before:assert lineage['outputLineage'][r['candidateFace']]['kind']in ['unchanged','parent-fragment']
        positions,change=repaired_positions(before_positions,before_index,before)
        changed=set(change['changedVertexIndices']);changed_faces=[i for i,face in enumerate(faces)if any(int(v)in changed for v in face)]
        # Do not alter original-TIN contributions or their blends to clear a model.
        core=shapely.from_wkt(lineage['coreWKT'])
        scope_certificate=verify_return_scope(positions,before_index,lineage['outputLineage'],changed_faces,core)
        save(doc/'return-scope-certificate.json',scope_certificate)
        distances=[shapely.Point(positions[i,[0,2]]).distance(core)for i in changed]
        assert distances and min(distances)>.01,'repair-touches-model-protected-source-core'
        mesh['position']=positions.reshape(-1).tolist();assert mesh['index']==before_index
        after=audit(mesh['position'],mesh['index'],captured['triangles']);save(doc/'after-exact-coastal-proof.json.gz',after)
        assert all(r['passed']for r in after),'exact-coastal-nonregression-failed'
        repair=dict(**change,maximumPermittedLiftM=MAXIMUM_LIFT_M,changedFaces=changed_faces,minimumDistanceFromProtectedCoreM=min(distances),originalCandidate=dict(path=str(original.relative_to(ROOT)),sha256=original_sha),currentParentCapture=dict(path=str((local/'parent.json').relative_to(ROOT)),sha256=digest((local/'parent.json').read_bytes())),beforeRegressingFaces=[r['candidateFace']for r in before if not r['passed']],allAfterSubFloorRegionsExactlyNonregressing=True,policy='Exact finite-column counterexample deficits are rounded upward to the next sufficient Float32 height. All shared rendered vertex occurrences receive the same result. Only derived parent-fragment/exterior-blend return vertices whose whole affected faces remain strictly outside the model-protected core may change, by at most1mm. No horizontal/index/topology/source-model/source-TIN-input change and no tolerance waiver.')
        save(doc/'repair.json',repair)
        for metadata in [mesh['source'],patch['meta']['source']]:metadata['coastalParentFloat32Repair']=dict(path=str((doc/'repair.json').relative_to(ROOT)),sha256=digest((doc/'repair.json').read_bytes()))
        mesh['source'].pop('numericalCoverageGap',None)
        from native_patch_resolution import projected_context
        from float32_coverage import approve_roundoff
        _,polygons,_,_=projected_context(patch,scope['bounds'])
        if shapely.union_all(polygons).symmetric_difference(shapely.box(*scope['bounds'])).area:save(doc/'coverage-roundoff.json',approve_roundoff(patch,scope['bounds']))
        overlap=module('coastal_repair_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=doc
        overlap.overlap_proof(patch,[original,local/'parent.json',doc/'repair.json',Path(__file__)])
        builder=module('coastal_repair_final_validator',HERE/'resolve_pass_indexed_parent_clipping_v2.py');builder.validate_patch(patch,parent)
        assert len(mesh['index'])//3<=25000
        path=local/'candidate-terrain.json';save(path,patch);refs.append(path)
        result.update(status='private-terrain-validator-passed',candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),terrainTriangles=len(mesh['index'])//3,changedParentFaces=len(changed_faces),derivedCoastalReturnVerticesChanged=len(changed),maximumCoastalLiftM=change['maximumLiftM'],allSubFloorRegionsNonregressing=True)
    except Exception as error:
        save(doc/'failure.json',dict(errorType=type(error).__name__,message=str(error),traceback=traceback.format_exc()))
        result.update(status='coastal-parent-roundoff-investigation',reason=str(error),errorType=type(error).__name__,permanentRejection=False)
    assert digest(manifest.read_bytes())==current_sha and digest(original.read_bytes())==original_sha and digest(asset.read_bytes())==row['sourceSHA256']
    save(doc/'summary.json',result)
    refs.extend(HERE/n for n in ['coastal_return_scope_v1_20261024.py','exact_below_floor_triangle_gap_v1_20261023.py','exact_original_projection_coverage_v2_20261010.py','float32_coverage.py','native_patch_resolution.py','resolve_pass_indexed_parent_clipping_v2.py','sham_shui_po_pool_shared_terrain_v2_20261016.py'])
    module('coastal_parent_roundoff_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'private-exact-Float32-coastal-parent-return-roundoff-repair',list(dict.fromkeys(refs)),result)
    print(result,flush=True)


if __name__=='__main__':main()
