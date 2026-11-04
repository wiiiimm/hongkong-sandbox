"""Test retained government terrain against the complete hotel, without publication."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module

BATCH = 'government-xl-disney-hotel-original-terrain-feasibility-v1-20261015'
DOC = ROOT/'docs/astra-city/government-import'/BATCH
PRIOR = ROOT/'docs/astra-city/government-import/government-xl-disney-hotel-current-ground-v1-20261015'
TERRAIN = HERE/'local/government-discovery-bay-1103-20260921/source-terrain/10-NE-21A'

def main():
    assert not DOC.exists()
    receipt = read(PRIOR/'result.json')
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
    refs = [Path(__file__), PRIOR/'result.json', TERRAIN/'download.json']
    for ref in receipt['evidenceRefs']:
        assert digest((ROOT/ref['path']).read_bytes()) == ref['sha256']
        refs.append(ROOT/ref['path'])
    provenance = read(TERRAIN/'download.json')
    for entry in provenance['entries']:
        path = TERRAIN/'decoded'/entry['name']
        assert digest(path.read_bytes()) == entry['sha256']
        refs.append(path)
    paths = list((TERRAIN/'decoded').rglob('*.gltf')); assert len(paths) == 1
    decoder = module('disney_retained_terrain_decoder', HERE/'xl-second-pass.py')
    terrain = decoder.context.triangles(paths[0])
    source = read(HERE/'local'/PRIOR.name/'runtime-geometry.json.gz')['rows'][0]
    triangles = np.asarray(source['position']).reshape(-1,3)[np.asarray(source['index']).reshape(-1,3)]
    lo = triangles.min(axis=(0,1)); hi = triangles.max(axis=(0,1))
    selected = (terrain[:,:,0].max(axis=1)>=lo[0]-1)&(terrain[:,:,0].min(axis=1)<=hi[0]+1)&(terrain[:,:,2].max(axis=1)>=lo[2]-1)&(terrain[:,:,2].min(axis=1)<=hi[2]+1)
    ground = terrain[selected]; assert len(ground)
    row = read(PRIOR/'selection.json.gz')['rows'][0]; building = row['source']['building']
    helper = module('disney_original_terrain_foundation', HERE/'xl-final-script-pass.py')
    foundation = helper.foundation_context(triangles, ground, Polygon(building['rings'][0], building['rings'][1:]))
    DOC.mkdir()
    save(DOC/'feasibility.json', dict(uid=row['uid'], sourceSHA256=source['sourceSHA256'], terrainSheet='10-NE-21A', terrainRevision=provenance['revisionDate'], completeOriginalTerrainFaces=len(terrain), intersectingOriginalTerrainFaces=len(ground), originalTerrainBounds=[terrain.min(axis=(0,1)).tolist(),terrain.max(axis=(0,1)).tolist()], foundation=foundation, fullAcceptance=False, terrainPublished=False, qualification='Original source terrain only; no composed current replacement, neighbour acceptance, or publication.'))
    refs += [HERE/'xl-second-pass.py', HERE/'xl-final-script-pass.py', Path(decoder.context.__file__)]
    result = module('disney_original_terrain_freezer', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'complete-hotel-retained-original-terrain-feasibility-v1', refs, dict(uids=[row['uid']], foundation=foundation, fullAcceptance=False, newlyInstalled=0, sourceGeometryChanges=0))
    print(dict(jobId=result['jobId'], sourceFaces=len(triangles), terrainFaces=len(ground), fullyBuriedTriangles=foundation['fullyBuriedTriangles'], fullyBuriedUpwardTriangles=foundation['fullyBuriedUpwardTriangles'], minimumGapM=foundation['minimumGapM']), flush=True)

if __name__ == '__main__':
    main()
