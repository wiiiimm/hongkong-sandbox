"""Read-only exact runtime plane census of an installed terrain; no derived terrain output."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_runtime_coplanar_groups_20261010 import groups
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',required=True);p.add_argument('--terrain',required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-')and '/'not in a.batch and not out.exists()
    manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(manifest.read_bytes())
    assert a.terrain in {v['url']for v in read(manifest)['terrainPatches']}
    source=ROOT/'3d-viewer'/a.terrain;source_sha=digest(source.read_bytes());data=read(source)
    assert data.get('nativeMesh')and not data.get('patches')
    mesh=data['nativeMesh'];tri=np.asarray(mesh['position'],dtype='<f4').astype('<f8').reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)]
    census=groups(tri);assert census['faces']==len(tri)
    summary={k:v for k,v in census.items()if k not in ['rows','degenerateFaceIds']}
    summary['degenerateFaces']=len(census['degenerateFaceIds'])
    save(out/'exact-plane-groups.json.gz',census)
    result=dict(uids=data['meta']['targetUids'],sourceTerrainURL=a.terrain,sourceTerrainSHA256=source_sha,
                currentManifestSHA256=manifest_sha,planeCensus=summary,sourceRuntimeWorldSHA256=digest(tri.tobytes()),
                sourceGeometryChanges=0,terrainGeometryChanges=0,derivedTerrainCreated=False,
                simplificationPerformed=False,physicalAcceptance=False,installationApproved=False,publication=False,
                qualification='Exact dyadic oriented plane groups of every actual Float32 triangle, with individual degenerate IDs preserved. Plane grouping alone does not establish connected finite regions, multiplicity preservation, normals, seams, collisions or permission to consolidate. No derived model, terrain candidate or optimisation variant produced.')
    assert digest(source.read_bytes())==source_sha and digest(manifest.read_bytes())==manifest_sha
    save(out/'summary.json',result)
    module('current_terrain_exact_plane_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch,'read-only-current-native-exact-runtime-plane-census',[Path(__file__),source,manifest,HERE/'exact_runtime_coplanar_groups_20261010.py'],result)
    print(summary,flush=True)


if __name__=='__main__':main()
