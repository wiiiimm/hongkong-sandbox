"""Identify the exact remaining original-TIN foundation failures; never approve them."""
from pathlib import Path
import uuid
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    batch = 'government-xl-west-kowloon-north-original-tin-failing-facets-v1-20261027'
    uid = 'landsd/182397:0'
    base = ROOT/'docs/astra-city/government-import'
    out = base/batch
    assert not out.exists()
    refs = [Path(__file__), HERE/'xl-final-script-pass.py', HERE/'exact_packed_world_geometry_20261009.py']
    pins = {}
    def take(name, path):
        if name not in pins:
            pins[name] = authenticate(base/name)[1]
            refs.append(base/name/'result.json')
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    runtime = 'government-xl-after-dragon-next-five-ground-v1-20261026'
    terrain_batch = 'government-xl-after-dragon-next-five-west-kowloon-wide-terrain-v1-20261026'
    source = next(r for r in take(runtime, base/runtime/'selection.json.gz')['rows'] if r['uid'] == uid)
    terrain_result = take(terrain_batch, base/terrain_batch/'summary.json')
    prior = next(r for r in terrain_result['rows'] if r['uid'] == uid)
    assert prior['geometryBasis'] == 'original-source-world' and not prior['actualRendererAcceptance']
    ground_record = take(terrain_batch, HERE/'local'/terrain_batch/'original-terrain.json.gz')
    assert ground_record['sourceTerrainPaths'] == prior['sourceTerrainPaths']
    asset = ROOT/source['candidate']['path']
    assert digest(asset.read_bytes()) == source['sourceSHA256'] == prior['sourceSHA256']
    refs.append(asset)
    claim = reservations.claim(batch+'-'+str(uuid.uuid4()), ['building:'+uid, 'source-terrain:11-NW-19C'], batch=batch, ttl=1800)
    assert claim['ok']
    lease = claim['reservation']
    try:
        tri = decode_original_world_triangles(asset.read_bytes())
        ground = np.asarray(ground_record['triangles'], dtype=float)
        final = module('west_kowloon_exact_foundation_replay', HERE/'xl-final-script-pass.py')
        b = source['source']['building']
        fresh = final.foundation_context(tri, ground, Polygon(b['rings'][0], b['rings'][1:]))
        assert fresh == prior['originalTerrainFoundation'], 'Stored source-TIN diagnostic did not reproduce exactly'
        lo, hi = tri.min((0,1)), tri.max((0,1))
        native = ground[(ground[:,:,0].max(1)>=lo[0]-1)&(ground[:,:,0].min(1)<=hi[0]+1)&(ground[:,:,2].max(1)>=lo[2]-1)&(ground[:,:,2].min(1)<=hi[2]+1)]
        polygons = shapely.polygons(native[:,:,[0,2]])
        valid = shapely.area(polygons)>1e-10
        native, polygons = native[valid], polygons[valid]
        points = np.concatenate([tri, tri.mean(1)[:,None,:]], axis=1)
        heights = final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2), native, shapely.STRtree(polygons)).reshape(-1,4)
        gaps = points[:,:,1]-heights
        buried = np.isfinite(heights).all(1)&(gaps<-.5).all(1)
        normals = np.cross(tri[:,1]-tri[:,0], tri[:,2]-tri[:,0])
        length = np.linalg.norm(normals, axis=1)
        upward = normals[:,1]>.25*length
        assert int(buried.sum()) == fresh['fullyBuriedTriangles'] == 35
        assert int((buried&upward).sum()) == fresh['fullyBuriedUpwardTriangles'] == 24
        rows = [dict(sourceFace=int(i), originalTriangle=tri[i].tolist(), sampleTerrainHeightsHKPD=heights[i].tolist(), sampleGapsM=gaps[i].tolist(), upwardUnderExistingPolicy=bool(upward[i]), areaM2=float(length[i]/2), signedNormalYRatio=float(normals[i,1]/length[i]) if length[i]>0 else None) for i in np.flatnonzero(buried)]
        components = [dict(sourceFaces=list(map(int,ids)), upwardSourceFaces=[int(i) for i in ids if upward[i]], bounds=[tri[ids].min((0,1)).tolist(),tri[ids].max((0,1)).tolist()]) for ids in final.connected_components(tri,buried)]
        assert reservations.owns(lease)
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']
    result = dict(uids=[uid], sourceSHA256=source['sourceSHA256'], sourceWorldSHA256=digest(tri.astype('<f8').tobytes()), originalTerrainSHA256=digest(ground.astype('<f8').tobytes()), exactPriorFoundationReproduced=True, foundation=fresh, rows=rows, components=components, sourceGeometryChanges=0, terrainGeometryChanges=0, physicalAcceptance=False, actualRendererAcceptance=False, installationApproved=False, publication=False, qualification='Exact unchanged original-TIN foundation policy replay, with all35 failing source facet IDs, four original policy witnesses each and both connected components retained. Twenty-four upward facets remain failures. No policy threshold, source or terrain edit; this original-source-world diagnostic is not current renderer or installation approval.')
    save(out/'summary.json', result)
    module('west_kowloon_failing_facets_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch, 'exact-original-tin-whole-buried-facet-context', refs, result)
    print(dict(failingFacets=len(rows), upward=24, components=len(components)), flush=True)


if __name__ == '__main__':
    main()
