"""Restore bounded foundation terrain from retained source TIN grids.

The original combined patch and source grids remain immutable. This candidate
removes the archival DTM mask/edge blend only where it corrupted mapped island
or footing land. It is not a smoothing filter and introduces no new elevations.
"""
import collections, copy, hashlib, json, pathlib, sys
import numpy as np
from shapely import intersects_xy
from shapely.geometry import Point, Polygon, box, mapping
from shapely.ops import unary_union
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / 'foundation-candidate'
DOC = ROOT / 'docs/astra-city/ting-kau/foundations'
sys.path.insert(0, str(HERE.parent / 'tai-o-completion'))
from hydro_terrain import prepare_terrain
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
ISLANDS = [('tsing-ma', 'Ma Wan tower island', [-9500, -6860]),
           ('ting-kau', 'Central tower island', [-8229.83, -8485.528])]
SOUTH = [-8019.633, -8059.256]
GUARD = 8.0  # >5*sqrt(2): includes all vertices of a triangle touching the land.
ROUNDING_TOLERANCE = .006  # Original grid rounds heights to 0.01 m.


def source_grid(patch):
    """Align retained 5 m native HK1980 grids; never interpolate between sources."""
    g = patch['meta']['georef']; shape = (patch['h'], patch['w'])
    values = np.full(shape, np.nan); owners = np.full(shape, -1, dtype=np.int16)
    sources = []
    for fp in sorted((HERE / 'combined/terrain/staged').glob('*/terrain-source-5m.json')):
        data = read(fp); sg = data['meta']['georef']
        assert sg['aE'] == 5 and sg['aN'] == -5
        dc = round((sg['bE'] - g['bE']) / 5); dr = round((g['bN'] - sg['bN']) / 5)
        assert abs(sg['bE'] - g['bE'] - dc*5) < 1e-6
        assert abs(g['bN'] - sg['bN'] - dr*5) < 1e-6
        c0, r0 = max(0, dc), max(0, dr)
        c1, r1 = min(patch['w'], dc + data['w']), min(patch['h'], dr + data['h'])
        if c0 >= c1 or r0 >= r1: continue
        src = np.array(data['elev'], dtype=float).reshape(data['h'], data['w'])[r0-dr:r1-dr, c0-dc:c1-dc]
        dest = values[r0:r1, c0:c1]; valid = np.isfinite(src)
        overlap = valid & np.isfinite(dest)
        assert not overlap.any(), 'Unexpected overlapping source ownership'
        dest[valid] = src[valid]; owners[r0:r1, c0:c1][valid] = len(sources)
        sources.append({'sheet': fp.parent.name, 'path': str(fp.relative_to(ROOT)), 'sha256': sha(fp)})
    assert len(sources) == 13
    return values, owners, sources


def components(mask):
    """Four-neighbour connected defects end where the existing source matches."""
    pending = set(map(tuple, np.argwhere(mask)))
    while pending:
        start = min(pending); pending.remove(start); todo = [start]; result = []
        while todo:
            r, c = todo.pop(); result.append((r, c))
            for q in [(r-1,c), (r+1,c), (r,c-1), (r,c+1)]:
                if q in pending: pending.remove(q); todo.append(q)
        yield result


def masks(patch, source):
    g = patch['meta']['georef']; xs = g['bE'] + np.arange(patch['w'])*5 - 834500
    zs = 816500 - g['bN'] + np.arange(patch['h'])*5
    xx, zz = np.meshgrid(xs, zs)
    regional = {name: read(HERE.parent/name/f'hydro-{name}.json') for name in ['tsing-ma', 'ting-kau']}
    lands = {name: box(*data['bounds']).difference(unary_union([Polygon(p['rings'][0], p['rings'][1:]) for p in data['water']])) for name, data in regional.items()}
    land = unary_union(list(lands.values())); island_shapes = []
    for name, label, seed in ISLANDS:
        candidates = list(lands[name].geoms) if hasattr(lands[name], 'geoms') else [lands[name]]
        polygon = next(p for p in candidates if p.covers(Point(seed)))
        assert polygon.area < 25000, 'Expected detached source island, not a whole shore'
        island_shapes.append((label, polygon))
    old = np.array(patch['elev']).reshape(source.shape)
    bad = np.isfinite(source) & intersects_xy(land, xx, zz) & (abs(old-source) > ROUNDING_TOLERANCE)
    # This radius selects the known footing problem; it is not a geographic border.
    seeds = unary_union([p for _, p in island_shapes] + [Point(SOUTH).buffer(45)])
    selected = []; remainder = []
    for points in components(bad):
        (selected if any(seeds.covers(Point(xs[c], zs[r])) for r,c in points) else remainder).append(points)
    def geometry(groups):
        cells = [box(xs[c]-2.5,zs[r]-2.5,xs[c]+2.5,zs[r]+2.5) for group in groups for r,c in group]
        return unary_union([p for _,p in island_shapes] + cells)
    # If the guard meets another contaminated component, include it in full so
    # the correction never stops halfway through a corrupted attached land strip.
    while True:
        area = geometry(selected).buffer(GUARD)
        extra = [group for group in remainder if any(area.covers(Point(xs[c],zs[r])) for r,c in group)]
        if not extra: break
        for group in extra: remainder.remove(group)
        selected.extend(extra)
    area = geometry(selected).buffer(GUARD)
    mask = intersects_xy(area, xx, zz)
    assert np.isfinite(source[mask]).all(), 'Missing original source in correction/triangle guard'
    assert land.boundary.intersection(box(*land.bounds).boundary).distance(area) > 20
    assert not np.any((~np.array([v is None for v in patch['renderedElev']]).reshape(source.shape)) & mask), 'Do not alter the outer coarse transition'
    groups = [{'nodes':len(group), 'bounds':[float(min(xs[c] for r,c in group)),float(min(zs[r] for r,c in group)),float(max(xs[c] for r,c in group)),float(max(zs[r] for r,c in group))]} for group in selected]
    return mask, area, land, island_shapes, xx, zz, groups, geometry(selected)


def build():
    OUT.mkdir(exist_ok=True); DOC.mkdir(parents=True, exist_ok=True)
    original_path = HERE/'combined/terrain-tsing-ma-ting-kau.json'; original = read(original_path)
    source, owners, sources = source_grid(original)
    mask, area, land, islands, xx, zz, groups, core = masks(original, source)
    old = np.array(original['elev']).reshape(source.shape); corrected = old.copy()
    corrected[mask] = np.round(source[mask], 2)
    changed = mask & (corrected != old)
    assert np.array_equal(old[~mask], corrected[~mask])
    candidate = copy.deepcopy(original); candidate['elev'] = corrected.ravel().tolist()
    policy = {'method':'Retained original 5 m source TIN heights override archival DTM water-mask holes and their blend only within two mapped foundation islands and connected contaminated southern-footing land, with an 8 m triangle guard.', 'verticalDatum':'Hong Kong Principal Datum (HKPD)', 'sourceFieldsUnchanged':True, 'guardMetres':GUARD, 'selectionRadiusMetres':45, 'selectionRadiusNote':'Selects connected contamination at the southern footing; not a surveyed feature boundary.', 'heightRoundingMetres':.01, 'changedVertices':int(changed.sum()), 'sourceGrids':[s for i,s in enumerate(sources) if np.any(mask & (owners == i))]}
    candidate['meta']['foundationRestoration'] = policy
    patch_path = OUT/'terrain-tsing-ma-ting-kau.json'
    patch_path.write_text(json.dumps(candidate,separators=(',',':'))+'\n')
    base = read(ROOT/'3d-viewer/city/data/terrain.json'); base.pop('hydro', None)
    old_hydro = read(HERE/'combined/hydro-tsing-ma-ting-kau.json'); pieces = []
    for name in ['tsing-ma','ting-kau']:
        regional = read(HERE.parent/name/f'hydro-{name}.json')
        result = prepare_terrain(regional, base, [candidate])
        assert result['water'] == regional['water']
        # Bed is unchanged geometry, retained byte-for-byte from native polygons;
        # do not retriangulate its rounded serialised outline for this height repair.
        result['bedTriangles'] = regional['bedTriangles']
        pieces.append(result)
    cuts = {}
    for piece in pieces:
        for cut in piece['terrainCuts']:
            key = json.dumps(cut['georef'],sort_keys=True)
            target = cuts.setdefault(key,{**cut,'cells':[],'removedAreaM2':0})
            target['cells'].extend(cut['cells']); target['removedAreaM2'] += cut['removedAreaM2']
    for cut in cuts.values():
        keys = [(c['c'],c['r']) for c in cut['cells']]; assert len(keys) == len(set(keys))
    hydro = copy.deepcopy(old_hydro)
    hydro['terrainCuts'] = list(cuts.values()); hydro['bankTriangles'] = [v for p in pieces for v in p['bankTriangles']]
    hydro['source']['foundationRestoration'] = policy
    assert hydro['water'] == old_hydro['water'] and hydro['bedTriangles'] == old_hydro['bedTriangles']
    hydro_path = OUT/'hydro-tsing-ma-ting-kau.json'; hydro_path.write_text(json.dumps(hydro,separators=(',',':'))+'\n')
    scope = {'type':'FeatureCollection','features':[{'type':'Feature','properties':{'role':'correction-and-triangle-guard','guardMetres':GUARD},'geometry':mapping(area)},{'type':'Feature','properties':{'role':'source-restoration-core'},'geometry':mapping(core)}]+[{'type':'Feature','properties':{'role':'mapped-foundation-island','name':name},'geometry':mapping(p)} for name,p in islands]}
    (OUT/'foundation-scope.geojson').write_text(json.dumps(scope,separators=(',',':'))+'\n')
    island_stats = []
    for name,p in islands:
        keep = intersects_xy(p,xx,zz)
        island_stats.append({'name':name,'mappedAreaM2':p.area,'bounds':list(p.bounds),'nodes':int(keep.sum()),'sourceCoveredNodes':int(np.isfinite(source[keep]).sum()),'formerZeroNodes':int((old[keep]==0).sum()),'oldGridRangeHKPD':[float(old[keep].min()),float(old[keep].max())],'sourceGridRangeHKPD':[float(source[keep].min()),float(source[keep].max())],'correctedGridRangeHKPD':[float(corrected[keep].min()),float(corrected[keep].max())]})
    report = {'status':'staged-awaiting-independent-verification','policy':policy,'selectedContaminationComponents':groups,'correctionGuardNodes':int(mask.sum()),'changedNodes':int(changed.sum()),'formerZeroNodesRestored':int((changed & (old==0)).sum()),'maximumChangeMetres':float(abs(old[changed]-corrected[changed]).max()),'islands':island_stats,'sourceGrids':sources,'originalCombined':{'path':str(original_path.relative_to(ROOT)),'sha256':sha(original_path)},'candidateTerrain':{'path':str(patch_path.relative_to(ROOT)),'sha256':sha(patch_path)},'candidateHydro':{'path':str(hydro_path.relative_to(ROOT)),'sha256':sha(hydro_path)},'waterPolygonsUnchanged':True,'originalBridgeModelsUnchanged':True,'livePublished':False}
    (DOC/'staging.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='sourceGrids'},indent=2))
    return report

if __name__ == '__main__': build()
