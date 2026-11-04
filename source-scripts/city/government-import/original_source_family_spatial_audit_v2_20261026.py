"""Measure an explicit original-source group against current forms; diagnostic only."""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module


def polygon(form):
    result = shapely.Polygon()
    for ring in form['rings']:
        result = result.symmetric_difference(shapely.Polygon(ring))
    assert result.is_valid and result.area > 0
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['batch', 'selection']:
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--identity', action='append', required=True)
    args = parser.parse_args()
    assert all(v.startswith('government-xl-') and '/' not in v for v in [args.batch, args.selection, *args.identity])
    base = ROOT / 'docs/astra-city/government-import'
    out = base / args.batch
    assert not out.exists()
    refs = [Path(__file__), HERE / 'exact_packed_world_geometry_20261009.py']
    receipts = {}
    identity_owners = {}
    for name in [args.selection, *args.identity]:
        receipt, pins = authenticate(base / name)
        receipts[name] = pins
        refs.append(base / name / 'result.json')
        if name in args.identity:
            for uid in receipt['uids']:
                assert uid not in identity_owners
                identity_owners[uid] = name
    def take(name, path):
        assert digest(path.read_bytes()) == receipts[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selected = take(args.selection, base / args.selection / 'selection.json.gz')
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selected['manifestSHA256']
    refs.append(manifest)
    rows = {r['uid']: r for r in selected['rows']}
    assert len(rows) == len(selected['rows']) and len(rows) > 1
    identities, tiles = {}, {}
    for uid, row in rows.items():
        identity_batch = identity_owners[uid]
        identity = take(identity_batch, base / identity_batch / uid.split('/')[1] / 'identity.json')
        context = take(identity_batch, base / identity_batch / uid.split('/')[1] / 'context.json')
        assert identity['sourceSHA256'] == row['sourceSHA256']
        assert identity['exactCurrentComponentRoute']['qualified'] is True
        assert identity['originalOwnership']['sourceGraphVerified'] is True
        identities[uid] = identity
        for path, sha in context['neighbourTileHashes'].items():
            assert path not in tiles or tiles[path] == sha
            tiles[path] = sha
    forms = {}
    for name, sha in tiles.items():
        path = ROOT / '3d-viewer' / name
        assert digest(path.read_bytes()) == sha
        refs.append(path)
        for form in read(path)['buildings']:
            assert form['uid'] not in forms or forms[form['uid']] == form
            forms[form['uid']] = form
    for uid, row in rows.items():
        assert forms[uid] == row['source']['building']
    shapes = {uid: polygon(f) for uid, f in forms.items()}
    group = shapely.union_all([shapes[uid] for uid in rows])
    projections, meshes, hashes = {}, {}, {}
    for uid, row in rows.items():
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256']
        refs.append(asset)
        tri = decode_original_world_triangles(asset.read_bytes())
        assert len(tri) == row['native']['model']['triangles']
        meshes[uid] = tri
        hashes[uid] = row['sourceSHA256']
        projections[uid] = shapely.union_all(shapely.polygons(tri[:, :, [0, 2]]))
    combined = shapely.union_all(list(projections.values()))
    outside = []
    for uid, shape in shapes.items():
        if uid in rows:
            continue
        area = float(combined.intersection(shape).area)
        if area > 0:
            form = forms[uid]
            outside.append(dict(uid=uid, name=form.get('name'), buildingCSUID=form.get('buildingCSUID'),
                                parent=form.get('parent'), intersectionAreaM2=area,
                                outsideGroupTargetAreaM2=float(combined.difference(group).intersection(shape).area),
                                bySource={key:float(value.intersection(shape).area) for key,value in projections.items()}))
    sources = []
    for uid, row in rows.items():
        f = forms[uid]
        sources.append(dict(uid=uid, modelId=row['modelId'], buildingCSUID=f.get('buildingCSUID'),
                            objectId=f.get('objectId'), name=f.get('name'), parent=f.get('parent'),
                            osmRefs=f.get('osmRefs', []), originalFaces=len(meshes[uid]),
                            rawIdentityReasons=identities[uid]['reasons'],
                            maximumSourceExtentFromGroupM=float(shapely.distance(shapely.points(meshes[uid][:,:,[0,2]].reshape(-1,2)),group).max()),
                            combinedTargetCoverage=float(combined.intersection(shapes[uid]).area / shapes[uid].area)))
    result = dict(uids=sorted(rows), sourceSHA256ByUid=hashes, currentManifestSHA256=selected['manifestSHA256'],
                  completeOriginalFaces=sum(len(t) for t in meshes.values()), currentContextForms=len(forms),
                  sources=sources, outsideGroupIntersections=sorted(outside,key=lambda r:-r['intersectionAreaM2']),
                  groupTargetAreaM2=float(group.area), combinedProjectionAreaM2=float(combined.area),
                  outsideGroupTargetProjectionM2=float(combined.difference(group).area),
                  sourceGeometryChanges=0, sourcePoseChanges=0, identityApproved=False,
                  physicalAcceptance=False, installationApproved=False, newlyInstalled=0, publication=False,
                  aiGeometryModelling=False, scriptExternalAICalls=0,
                  qualification='Complete original Float64 projections and exact current metadata for an explicitly selected group. Shared names/OSM parents do not establish ownership. External forms remain external. Raw identity failures retained; no overlap, extent, support, terrain or publication limits waived.')
    save(out/'summary.json',result)
    module('source_family_spatial_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        args.batch,'complete-original-source-family-current-spatial-diagnostic',list(dict.fromkeys(refs)),result)
    print(dict(sources=len(rows),outsideForms=len(outside),faces=result['completeOriginalFaces']),flush=True)


if __name__ == '__main__':
    main()
