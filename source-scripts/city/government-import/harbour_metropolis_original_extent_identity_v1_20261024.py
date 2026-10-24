"""Bound exact source-owned hotel extent to the retained original podium context.
Identity interpretation only; physical, support, browser and publication separate.
"""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-harbour-metropolis-bounded-extent-identity-v1-20261024'
UID, PARENT = 'landsd/259378:0', 'landsd/240841:0'
SHA = '1f7f3f42844aa20b23bf30f398b7f67035953c98b1b530d5529c8be4dd4c8034'
PREFIX = 'government-xl-next-three-after-ventilation-'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selection = take(PREFIX + 'runtime-v1-20261024', 'selection.json.gz')
    row = next(r for r in selection['rows'] if r['uid'] == UID)
    raw = take(PREFIX + 'identity-v1-20261024', '259378:0/identity.json')
    assert raw['sourceSHA256'] == row['sourceSHA256'] == SHA
    assert raw['originalOwnership']['sourceGraphVerified']
    assert raw['originalOwnership']['originalRootName'] == row['modelId'] == 'B369271804901063C0'
    assert raw['exactCurrentComponentRoute']['qualified'] and raw['exactCurrentComponentRoute']['uid'] == UID
    assert raw['exactWholeCellCoverage']['covered'] and raw['completeRecordProjection']
    expected = ['fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM', 'full-source-maximum-extent']
    assert sorted(raw['reasons']) == expected
    scope = take(PREFIX + 'model-scope-v1-20261024', 'summary.json')
    forms = take(PREFIX + 'model-scope-v1-20261024', '259378:0-forms.json.gz')
    by_uid = {r['building']['uid']: r for r in forms}
    assert set(by_uid) == {UID, PARENT, 'landsd/259576:0'}
    for form in forms:
        path = ROOT / '3d-viewer' / form['tile']
        assert digest(path.read_bytes()) == form['tileSHA256']
        assert next(b for b in read(path)['buildings'] if b['uid'] == form['building']['uid']) == form['building']
        refs.append(path)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == scope['currentManifestSHA256']
    refs.append(manifest)
    parent_entries = []
    for url in read(manifest)['officialModelCatalogues']:
        cat = ROOT / '3d-viewer' / url
        for entry in read(cat)['models']:
            if entry['uid'] == PARENT:
                parent_entries.append(entry)
                refs.append(cat)
    assert len(parent_entries) == 1
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == SHA
    refs.append(asset)
    triangles = decode_original_world_triangles(asset.read_bytes())
    assert len(triangles) == row['triangles'] == 14504
    projection = shapely.union_all(shapely.polygons(triangles[:, :, [0, 2]]))
    def polygon(uid):
        rings = by_uid[uid]['building']['rings']
        return shapely.Polygon(rings[0], rings[1:])
    target, parent, foreign = polygon(UID), polygon(PARENT), polygon('landsd/259576:0')
    excess = projection.difference(target)
    metrics = dict(targetCoverage=projection.intersection(target).area / target.area,
                   sourceExcessAreaM2=excess.area,
                   excessOutsideRetainedPodiumM2=excess.difference(parent).area,
                   sourceOverlapUnrelatedM2=projection.intersection(foreign).area,
                   maximumOriginalExtentM=float(shapely.distance(shapely.points(triangles[:, :, [0, 2]].reshape(-1, 2)), target).max()))
    assert .999 <= metrics['targetCoverage'] <= 1.000000001
    assert metrics['excessOutsideRetainedPodiumM2'] == metrics['sourceOverlapUnrelatedM2'] == 0
    assert 23 < metrics['maximumOriginalExtentM'] < 24
    result = dict(uids=[UID], uid=UID, sourceSHA256=SHA, requiredInstalledPodiumUid=PARENT,
                  requiredInstalledPodiumEntry=parent_entries[0], rawIdentity=raw, metrics=metrics,
                  identityAccepted=True, reviewer='ROOT', sourceEvidenceInterpretationUsedAI=True,
                  aiGeometryModelling=False, sourceGeometryChanges=0, sourcePoseChanges=0,
                  installationApproved=False, physicalSupportAccepted=False,
                  interpretation='The exact uniquely routed Harbour Plaza Metropolis original extends beyond its smaller current footprint onto the already installed Fortune Metropolis podium. Complete owned source graph and whole GeoRef cell establish association; every excess projected point is within that exact podium footprint and there is zero unrelated source overlap. ROOT inspected the complete original hotel/podium diagram and source desktop day/night exports. This bounded extent interpretation preserves the raw two failures and does not establish engineering support, property boundaries, source wall clearance, collision, mobile appearance or publication.')
    save(out / 'identity.json', result)
    module('harbour_identity_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'bounded-original-hotel-extent-on-exact-retained-podium-identity', refs, result)
    print(metrics)


if __name__ == '__main__': main()
