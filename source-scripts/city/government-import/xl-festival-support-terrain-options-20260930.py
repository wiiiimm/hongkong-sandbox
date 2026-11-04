"""Bound what retaining existing terrain can solve, without changing source meshes."""
import importlib.util
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


final = module('festival_options_final', 'xl-final-script-pass.py')
patches = module('festival_options_patch', 'native_patch_resolution.py')
BASE = ROOT / 'docs/astra-city/government-import/government-xl-remaining-20260923'
DOC = BASE / 'festival-walk-terrain-diagnostic-20260925'


def run():
    row = next(r for r in read(DOC / 'selection.json.gz')['rows'] if r['uid']=='landsd/91827:0')
    entry = row['candidate']['entry']
    final.s.LOCAL = HERE / 'local/government-xl-festival-walk-terrain-20260925/candidates'
    model = final.s.glb_triangles({**row['native']['model'], 'sourceSHA256': entry['sha256'],
                                  'modelId': entry['modelId'], 'native': row['native']})
    terrain_path = ROOT / '3d-viewer/city/data/terrain.json'
    parent = read(terrain_path)
    sampler = final.s.resolution.terrain.fine.DemSampler(parent, rendered=True)
    sampler.parent_height_floor = 1.2
    lo, hi = model.min(axis=(0, 1)), model.max(axis=(0, 1))
    extent = shapely.box(lo[0] - 2, lo[2] - 2, hi[0] + 2, hi[2] + 2)
    original = np.asarray(patches.grid_surface_faces(sampler, extent))
    candidate = next(r for r in read(BASE / 'complex-mask-foundations-20260929.json')['rows'] if r['site']=='festival-walk')['candidatePatch']
    result = {'patchPath':candidate['path'],'patchSHA256':candidate['sha256']}
    path = ROOT / result['patchPath']
    assert digest(path.read_bytes()) == result['patchSHA256']
    native = patches._faces(read(path))
    points = np.concatenate([model, model.mean(axis=1)[:, None, :]], axis=1)
    all_gaps = []
    for terrain in (original, native):
        polys = shapely.polygons(terrain[:, :, [0, 2]])
        valid = shapely.area(polys) > 1e-10
        heights = final.s.context.shared.samples(points[:, :, [0, 2]].reshape(-1, 2), terrain[valid], shapely.STRtree(polys[valid])).reshape(-1, 4)
        assert np.isfinite(heights).all()
        all_gaps.append(points[:, :, 1] - heights)
    cross = np.cross(model[:, 1] - model[:, 0], model[:, 2] - model[:, 0])
    upward = cross[:, 1] > .25 * np.linalg.norm(cross, axis=1)
    old, new = [(gap < -.5).all(axis=1) for gap in all_gaps]
    # Even choosing the lower of both unchanged surfaces at every sample cannot
    # rescue these faces. This is a diagnostic bound, never a candidate surface.
    unavoidable = (np.maximum(*all_gaps) < -.5).all(axis=1)
    building = row['source']['building']
    footprint = shapely.Polygon(building['rings'][0], building['rings'][1:])
    report = {'uid': row['uid'], 'sourceSHA256': entry['sha256'],
              'parentSHA256': digest(terrain_path.read_bytes()), 'nativePatchSHA256': result['patchSHA256'],
              'parentFoundation': final.foundation_context(model, original, footprint),
              'nativeBuriedUpwardTriangles': int((new & upward).sum()),
              'parentBuriedUpwardTriangles': int((old & upward).sum()),
              'buriedUpwardEvenWithPointwiseLowerSurface': int((unavoidable & upward).sum()),
              'nativeBuriedUpwardRescuableByParent': int((new & ~old & upward).sum()),
              'qualification': 'Pointwise minimum is a bound only, not generated terrain or permission to change geometry.',
              'aiCalls': 0, 'modelGeometryChanges': 0, 'publication': False}
    # Diagnostic only: retain the original parent surface solely under the
    # exact source faces for which the independent comparison proves a benefit.
    rescue = shapely.union_all(shapely.polygons(model[new & upward][:, :, [0, 2]])).buffer(.01, join_style="mitre")
    candidate_patch = read(path)
    g=candidate_patch['meta']['georef']
    bounds=sorted([g['bE']-834500,g['bE']+g['aE']*(candidate_patch['w']-1)-834500])
    zs=sorted([816500-g['bN'],816500-(g['bN']+g['aN']*(candidate_patch['h']-1))])
    extent_bounds=[bounds[0],zs[0],bounds[1],zs[1]]
    repair=patches.preserve_parent_under_projection(candidate_patch,extent_bounds,rescue,sampler)
    candidate_path=HERE/'local/government-xl-festival-support-options-20260930/diagnostic-parent-rescue.json'
    save(candidate_path,candidate_patch)
    report['diagnosticParentRescue']={'preservation':repair,'candidatePatch':{'path':str(candidate_path.relative_to(ROOT)),'sha256':digest(candidate_path.read_bytes())},'foundation':final.foundation_context(model,patches._faces(candidate_patch),footprint),'publication':False,'requiredChecks':['coverage-and-overlap','neighbors','source-pair-contact','runtime','browser']}
    save(BASE / 'festival-support-terrain-options-20260930.json', report)
    print({k: v for k, v in report.items() if k != 'parentFoundation'}, flush=True)


if __name__ == '__main__':
    run()
