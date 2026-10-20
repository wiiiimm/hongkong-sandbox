"""Diagnostic original-source terrain checks; no publication or geometry changes."""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from china_ferry_current_foundations_v1_20261020 import face_diagnostics
BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-mount-sterling-nine-foundations-v1-20261020'
DOC = BASE / BATCH
RECOVERY = BASE / 'government-xl-mount-sterling-nine-original-recovery-v1-20261020'
GROUND = BASE / 'government-xl-mount-sterling-adjoining-ground-v1-20261020'

def main():
    assert not DOC.exists(), 'Preserve completed or failed producer; use a new version'
    refs = [Path(__file__), HERE/'exact_packed_world_geometry_20261009.py',
            HERE/'china_ferry_current_foundations_v1_20261020.py', HERE/'xl-final-script-pass.py']
    pins = {}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in (RECOVERY, GROUND):
            receipt = read(folder/'result.json')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                              (receipt['jobId'],)).fetchone() == ('complete', receipt)
            refs.append(folder/'result.json')
            pins[folder] = {e['path']: e['sha256'] for e in receipt['evidenceRefs']}
    def checked(folder, path):
        assert digest(path.read_bytes()) == pins[folder][str(path.relative_to(ROOT))], str(path)
        refs.append(path)
        return read(path)
    rows = checked(RECOVERY, RECOVERY/'recovery.json')['rows']
    ground = np.asarray(checked(GROUND, HERE/'local'/GROUND.name/'289787:0-ground.json.gz')['completeAdjoiningTerrain'])
    final = module('mount_sterling_nine_foundations', HERE/'xl-final-script-pass.py')
    results = []
    for row in rows:
        asset = ROOT/row['assetPath']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == pins[RECOVERY][row['assetPath']]
        refs.append(asset)
        triangles = decode_original_world_triangles(asset.read_bytes())
        diagnostic = face_diagnostics(final, triangles, ground)
        save(DOC/(row['modelId']+'-faces.json.gz'), diagnostic)
        result = dict(uid=row['uid'], modelId=row['modelId'], sourceSHA256=row['sourceSHA256'],
                      faces=len(triangles), coveredFaces=diagnostic['completeTerrainTriangles'],
                      buriedFaces=len(diagnostic['buriedFaces']),
                      upwardBuriedFaces=sum(x['upward'] for x in diagnostic['buriedFaces']))
        results.append(result)
        print(result, flush=True)
    summary = dict(uids=sorted({r['uid'] for r in rows}), rows=results,
                   sourceGeometryChanges=0, installationApproved=False,
                   interpretation='Terrain diagnostics only. Elevated companion bodies may require original podium support; terrain gaps alone do not reject them.')
    save(DOC/'summary.json', summary)
    module('mount_sterling_nine_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'nine-original-source-terrain-diagnostics', refs, summary)

if __name__ == '__main__':
    main()
