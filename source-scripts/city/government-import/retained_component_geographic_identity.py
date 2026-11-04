"""Identity diagnostics for 14 pinned originals with existing positive source matches.

Replaces singleton extent with measured whole-building extent only. All original
byte/graph/pose/GeoRef/unique identifiers and existing spatial limits remain.
"""
import importlib.util
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT, HERE, read, digest
from routed_original_cell_identity import verify as routed_verify

POLICY = 'original-exact-retained-component-geographic-context-v1'
UIDS = frozenset('landsd/'+str(n)+':0' for n in (227380,313033,285509,273672,91827,104302,195849,264206,227099,228219,134332,280084,235076,258470))
REPLACED = frozenset({'full-source-maximum-extent', 'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM'})
DOC = ROOT / 'docs/astra-city/government-import/government-xl-22-complete-group-official-context-v2-20261008'
REVIEW = DOC/'context.json.gz'


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result); return result


def verify_files(row, context, local):
    uid = row['uid']; assert uid in UIDS
    saved = next(r for r in read(REVIEW)['rows'] if r['uid'] == uid)
    official=read(DOC/'official-context.json')
    frozen = next(r for r in read(DOC/'physical-selection.json.gz')['rows'] if r['uid']==uid)
    assert row['modelId']==frozen['modelId'] and row['sourceSHA256']==frozen['sourceSHA256']
    assert len(saved['groupForms'])>=2
    for key in ('buildingCSUID','recordedBaseHeight','recordedTopHeight'):
        assert key in row['candidate']['entry'] and row['candidate']['entry'][key]==frozen['candidate']['entry'][key]
    assert row['candidate']['entry']['buildingCSUID']==row['source']['building']['buildingCSUID']
    assert row['candidate']['entry']['recordedBaseHeight']==row['source']['building']['baseHeightHKPD']
    assert row['candidate']['entry']['recordedTopHeight']==row['source']['building']['topHeightHKPD']
    matching=row['native']['model']['matching']
    assert len(matching['officialMatches'])==len(matching['viewerMatches'])==1
    assert matching['viewerMatches'][0]['uid']==uid
    assert saved['sourceSHA256'] == row['sourceSHA256']
    raw = (ROOT / row['candidate']['path']).read_bytes(); assert digest(raw) == row['sourceSHA256']
    local = Path(local); assert local.resolve().is_relative_to(HERE / 'local')
    dest = local / 'assets' / (row['sourceSHA256'] + '.glb.gz'); dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(raw)
    decoder = module('complete_market_decoder', 'xl-second-pass.py'); decoder.LOCAL = local
    tri = decoder.glb_triangles(row)
    final = module('complete_market_current_context', 'xl-final-script-pass.py')
    lo, hi = tri.min(axis=(0, 1)), tri.max(axis=(0, 1))
    forms = final.load_forms([lo[0]-2, lo[2]-2, hi[0]+2, hi[2]+2])
    current = {b['uid']: b for b, _, _ in forms}
    for path, sha in context['neighbourTileHashes'].items(): assert digest((ROOT / '3d-viewer' / path).read_bytes()) == sha
    assert digest((ROOT / '3d-viewer' / row['source']['tile']).read_bytes()) == row['source']['tileSHA256']
    assert current[uid] == row['source']['building']
    sources = []
    for tile in read(ROOT / '3d-viewer/city/data/manifest.json')['tiles']:
        path = ROOT / '3d-viewer' / tile['url']; data = read(path)
        for b in data['buildings']:
            if str(b.get('buildingCSUID') or '')[:10] == row['modelId'][1:11]:
                sources.append({'building': b, 'tile': tile['url'], 'tileSHA256': digest(path.read_bytes())})
    identity = final.identity_context(row, tri, forms)
    # Bind the newly computed physical input, not the historical singleton context.
    fresh_context = {**context, 'identity': identity}
    individual = routed_verify(raw, row, fresh_context, tri, current_identity=identity, sources=sources)
    reasons = [r for r in individual['reasons'] if r not in REPLACED]
    group = saved['groupForms']; parent = current[uid].get('parent')
    expected_group = [b for b, _, _ in forms if b['uid'] == uid or parent and b.get('parent') == parent]
    if sorted(expected_group, key=lambda b:b['uid']) != sorted(group, key=lambda b:b['uid']): reasons.append('complete-current-group-changed')
    official_by_uid = {r['uid']:r for r in official['rows']}
    for b in group:
        record = official_by_uid[b['uid']]
        if (current.get(b['uid']) != b or not record['uniqueOfficialRecord'] or not record['uniquePolygon'] or record['csuid'] != b['buildingCSUID'] or record['hausdorffDistanceM'] > .002 or record['officialAttributes']['Status'] != 'Active'):
            reasons.append('official-complete-component:'+b['uid'])
        if b.get('parent') != parent or not parent or not set(b.get('osmRefs', [])) & set(current[uid].get('osmRefs', [])): reasons.append('complete-component-ownership:'+b['uid'])
    projection = shapely.union_all(shapely.polygons(tri[:, :, [0, 2]]))
    shape = shapely.union_all([Polygon(b['rings'][0], b['rings'][1:]) for b in group])
    others = shapely.union_all([p for b, p, _ in forms if b['uid'] not in {g['uid'] for g in group}])
    measures = {'targetCoveredBySourceProjection': float(shape.intersection(projection).area / shape.area),
        'sourceExcessMaximumDistanceFromTargetM': float(shapely.distance(shapely.points(tri[:, :, [0, 2]].reshape(-1, 2)), shape).max()),
        'sourceExcessCoveredByUnrelatedFormsM2': float(projection.difference(shape).intersection(others).area)}
    for key, low, high in [('targetCoveredBySourceProjection', .95, 1.000000001), ('sourceExcessMaximumDistanceFromTargetM', 0, 10), ('sourceExcessCoveredByUnrelatedFormsM2', 0, 1)]:
        if not low <= measures[key] <= high: reasons.append('complete-group-spatial-bound:'+key)
    cell = individual.get('geographicCell', {})
    if not cell.get('targetCoversWholeCell') or not cell.get('originalProjectionCoversWholeCell'): reasons.append('individual-whole-georef-cell')
    passed = not reasons
    return {**individual, 'policy': POLICY, 'passed': passed, 'reasons': sorted(set(reasons)),
        'rawIndividualIdentity': individual, 'replacedSingletonExtentReasons': sorted(set(individual['reasons']) & REPLACED),
        'completeGroupForms': group, 'completeGroupMeasures': measures,
        'proof': {'exactObjectId': passed, 'exactBuildingCSUID': passed, 'uniqueViewerMatch': passed, 'identityAccepted': passed},
        'installationApproved': False, 'modelGeometryChanges': 0,
        'qualification': 'Identity only for this byte-pinned complete original source with all other forms retained. Each original root, pose, exact unique GeoRef/type/CSUID and full cell remains mandatory. Fresh official component records and current same-parent forms support measuring unchanged 95% coverage, 10m extent and 1m2 unrelated overlap limits over the whole source footprint scope. All other current forms must be retained; component suppression is not approved. Source singleton failures remain recorded. All physical, runtime, neighbour and publication gates remain.'}
