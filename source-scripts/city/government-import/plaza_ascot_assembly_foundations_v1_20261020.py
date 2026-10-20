"""Diagnostic original-source terrain checks; no publication or geometry changes."""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from china_ferry_current_foundations_v1_20261020 import face_diagnostics
BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-plaza-ascot-assembly-foundations-v1-20261020'
DOC = BASE / BATCH
RECOVERY = BASE / 'government-xl-plaza-ascot-assembly-original-recovery-v1-20261020'
GROUND = BASE / 'government-xl-plaza-ascot-domain-ground-v1-20261020'

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
    ground = np.asarray(checked(GROUND, HERE/'local'/GROUND.name/'258411:0-ground.json.gz')['completeAdjoiningTerrain'])
    final = module('mount_sterling_nine_foundations', HERE/'xl-final-script-pass.py')
    results = []
    world={}
    for row in rows:
        asset=ROOT/row['assetPath'];assert digest(asset.read_bytes())==row['sourceSHA256']==pins[RECOVERY][row['assetPath']];refs.append(asset);world[row['uid']]=decode_original_world_triangles(asset.read_bytes())
    for row in rows:
        asset = ROOT/row['assetPath']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == pins[RECOVERY][row['assetPath']]
        refs.append(asset)
        triangles = decode_original_world_triangles(asset.read_bytes())
        support_uid = None if row['uid'] in ['landsd/258411:0','landsd/228446:0'] else ('landsd/228446:0' if row['uid']=='landsd/127447:0' else 'landsd/258411:0')
        support = ground if support_uid is None else np.concatenate([ground,world[support_uid]])
        diagnostic = face_diagnostics(final, triangles, support)
        save(DOC/(row['modelId']+'-faces.json.gz'), diagnostic)
        result = dict(uid=row['uid'], modelId=row['modelId'], sourceSHA256=row['sourceSHA256'],
                      supportUid=support_uid, faces=len(triangles), coveredFaces=diagnostic['completeTerrainTriangles'],
                      buriedFaces=len(diagnostic['buriedFaces']),
                      upwardBuriedFaces=sum(x['upward'] for x in diagnostic['buriedFaces']))
        results.append(result)
        print(result, flush=True)
    summary = dict(uids=sorted({r['uid'] for r in rows}), rows=results,
                   sourceGeometryChanges=0, installationApproved=False,
                   interpretation='Exact complete ground plus nominated original podium foundation diagnostics. Raw burial retained; no installation approval.')
    save(DOC/'summary.json', summary)
    module('mount_sterling_nine_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'complete-original-assembly-ground-and-podium-foundation-diagnostics', refs, summary)

if __name__ == '__main__':
    main()
