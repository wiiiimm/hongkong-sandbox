"""Bind every failed North-pair boundary vertex to the existing unchanged mate.

Diagnostic only. Existing pair approval never transfers to a changed terrain body.
"""
import sys
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
INTEGRATION=HERE.parent/'island-detail-integration'
if str(INTEGRATION)not in sys.path:sys.path.insert(0,str(INTEGRATION))
from coordinated_native_boundary import coordinated_boundary,canonical_sha

def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-west-kowloon-north-pair-after-ocean-'
    failed=base/(prefix+'canonical-surface-v1-20261027');receipt,pins=authenticate(failed)
    assert receipt['status']=='private-canonical-surface-investigation' and receipt['reason']=='Native terrain boundary does not join parent heights'
    path=failed/'boundary-witness-diagnostic.json';diagnostic=read(path)
    assert diagnostic['failedVertexCount']==44 and len(diagnostic['witnesses'])==44
    unbound=HERE/'local'/(prefix+'canonical-surface-v1-20261027')/'south-unbound.json'
    assert digest(unbound.read_bytes())==pins[str(unbound.relative_to(ROOT))]
    candidate=read(unbound);captured=read(ROOT/diagnostic['candidate'])
    assert candidate['nativeMesh']['position']==captured['nativeMesh']['position'] and candidate['nativeMesh']['index']==captured['nativeMesh']['index']
    rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=read(rootpath)
    paths={name:ROOT/('3d-viewer/city/data/government-native-island-cheong-shing-'+name+'-v1-20261023.json')for name in ['north','south']}
    old=read(paths['north']);marker=old['nativeMesh']['source']['coordinatedBoundary'];proofpath=ROOT/marker['proof']['path']
    assert digest(proofpath.read_bytes())==marker['proof']['sha256'];proof=read(proofpath)
    assert set(proof['members'])=={'north','south'}
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath)
    for name,p in paths.items():
        node=read(p)
        assert canonical_sha(node)==proof['members'][name]['canonicalSHA256']
        assert sum(e['url']==str(p.relative_to(ROOT/'3d-viewer'))for e in manifest['terrainPatches'])==1
        assert node['meta']['parentSha256']==digest(rootpath.read_bytes())
    callback=coordinated_boundary(old,root)
    vertices={tuple(v)for v in np.asarray(old['nativeMesh']['position'],np.float32).astype(float).reshape(-1,3)}
    rows=[]
    for witness in diagnostic['witnesses']:
        point=tuple(witness[k]for k in ['x','y','z'])
        assert point in vertices and callback(*point)
        assert abs(point[2]+4027.5)<.002  # Same edge-vertex band as native_terrain_validation.
        rows.append(dict(**witness,exactOldRenderedVertex=True,existingMateBoundaryCovered=True))
    result=dict(uids=['landsd/182397:0','landsd/309340:0'],failedCanonicalJob=receipt['jobId'],witnesses=rows,
        all44AreExactUnchangedOldBoundaryVertices=True,existingMateURL=str(paths['south'].relative_to(ROOT/'3d-viewer')),
        existingMateTargets=read(paths['south'])['meta']['targetUids'],installationApproved=False,sourceGeometryChanges=0,
        qualification='All failed vertices belong to the existing retained boundary with its exact currently installed mate. This explains the canonical failure; it does not approve a changed body or waive root-height checks. Next candidate must bind the old mate as well as the new northern pair.')
    out=base/(prefix+'existing-boundary-lineage-v1-20261027');assert not out.exists();save(out/'summary.json',result)
    refs=[HERE/'north_pair_existing_boundary_lineage_v1_20261027.py',failed/'result.json',path,unbound,ROOT/diagnostic['candidate'],proofpath,rootpath,manifestpath,*paths.values(),INTEGRATION/'coordinated_native_boundary.py']
    module('north_existing_boundary_lineage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name,'exact-retained-boundary-failure-lineage',refs,result)
    print(dict(exactOldBoundaryVertices=len(rows),existingMate=result['existingMateURL']),flush=True)

if __name__=='__main__':main()
