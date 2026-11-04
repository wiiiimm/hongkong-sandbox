"""Diagnose complete compound wall warnings against verified strict support roots.

No admission or publication flags are changed. Failed raw clearance stays failed.
"""
from pathlib import Path
import argparse
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_face_attachment_minimax_v2_20261024 import attachment_paths

BASE = ROOT / 'docs/astra-city/government-import'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'support-checks', 'strict-paths', 'compound', 'uid']:
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    for name in [a.batch, a.runtime, a.support_checks, a.strict_paths, a.compound]:
        assert name.startswith('government-xl-') and '/' not in name
    out = BASE / a.batch
    assert not out.exists()
    pins, refs = {}, [Path(__file__)]

    def take(batch, name, local=False):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        path = (HERE / 'local' if local else BASE) / batch / name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(a.runtime, 'selection.json.gz')
    strict = take(a.support_checks, 'summary.json')
    compound = take(a.compound, 'summary.json')
    path_summary = take(a.strict_paths, 'summary.json')
    assert strict['supportedUid'] == compound['supportedUid'] == a.uid
    assert compound['supportUid'] == strict['installedSupportUid']
    assert strict['sourceSHA256ByUid'] == path_summary['sourceSHA256ByUid']
    assert compound['sourceSHA256'] == strict['sourceSHA256ByUid'][a.uid]
    native_uid = strict['installedSupportUid']
    assert compound['supportSHA256'] == strict['sourceSHA256ByUid'][native_uid]
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == strict['currentManifestSHA256'] == path_summary['currentManifestSHA256']
    refs.append(manifest)
    source = next(r for r in selection['rows'] if r['uid'] == a.uid)
    asset = ROOT / source['candidate']['path']
    assert digest(asset.read_bytes()) == compound['sourceSHA256']
    refs.append(asset)
    matches = []
    for url in read(manifest)['officialModelCatalogues']:
        cat = ROOT / '3d-viewer' / url
        for entry in read(cat)['models']:
            if entry['uid'] == native_uid:
                matches.append(entry)
                native_asset = cat.parent / entry['asset']
                assert digest(native_asset.read_bytes()) == entry['sha256']
                refs.extend([cat, native_asset])
    assert matches == [strict['installedNativeEntry']]
    runtime = take(a.runtime, 'runtime-geometry.json.gz', local=True)
    g = next(r for r in runtime['rows'] if r['uid'] == a.uid)
    actual_ground = np.asarray(g['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    summaries = []
    for mode, compound_mode in [('original', 'original'), ('literal', 'literal'), ('leftF32', 'left'), ('balancedF32', 'balanced')]:
        inp = take(a.support_checks, mode + '/input.json.gz')
        child = inp['rows'][0]
        assert child['uid'] == a.uid
        tri = np.asarray(child['position'], dtype='<f8').reshape(-1, 3)[np.asarray(child['index']).reshape(-1, 3)]
        podium = np.asarray(inp['podium'], dtype='<f8')
        paths = take(a.strict_paths, mode + '.json.gz')
        low = take(a.compound, compound_mode + '.json.gz')
        caps = take(a.compound, compound_mode + '-cap-paths.json.gz')
        assert digest(tri.tobytes()) == paths['sourceWorldSHA256'] == low['sourceWorldSHA256'] == caps['sourceWorldSHA256']
        assert digest(podium.tobytes()) == paths['supportWorldSHA256'] == caps['supportWorldSHA256']
        ground = np.concatenate([actual_ground, podium])
        assert digest(ground.tobytes()) == low['groundSHA256'] == caps['compoundGroundSHA256']
        assert digest(actual_ground.tobytes()) == caps['actualGroundSHA256']
        assert low['completeSourceFaces'] == len(tri)
        expected = next(r for r in compound['rows'] if r['mode'] == compound_mode)
        assert expected['exactAffectedFaces'] == [r['sourceFace'] for r in low['rows']]
        targets, excluded = [], []
        for row in low['rows']:
            face = row['sourceFace']
            assert np.array_equal(tri[face], np.asarray(row['vertices']))
            if row['absoluteNormalYRatio'] is None or row['absoluteNormalYRatio'] >= .25:
                excluded.append(face)
                continue
            targets.append(dict(witness=dict(position=tri[face].mean(0).tolist(), sourceFace=face), incidentFaces=[face]))
        rows = attachment_paths(tri, dict(targets=targets, proof=dict(contacts=[])), [], strict_anchors=paths['canonicalStrictRoots'])
        save(out / (mode + '.json.gz'), dict(mode=mode, sourceWorldSHA256=paths['sourceWorldSHA256'], supportWorldSHA256=paths['supportWorldSHA256'], rows=rows, rawClearanceRows=low['rows'], rawCapProof=caps['proof'], excludedNonWallFaces=excluded, supportApproved=False, physicalAcceptance=False))
        summary = dict(mode=mode, affectedFaces=len(low['rows']), wallTargets=len(rows), excludedNonWallFaces=excluded, finitePaths=sum(r['hasUnrestrictedFiniteAttachment'] for r in rows), disconnectedFaces=[r['witness']['sourceFace'] for r in rows if not r['hasUnrestrictedFiniteAttachment']], endpointOvershootFaces=[r['witness']['sourceFace'] for r in rows if r.get('riseAboveEndpointsM', 0) > 0], rawCompoundCapPathsPassed=expected['compoundCapPathsPassed'], physicalAcceptance=False)
        summaries.append(summary)
        print(summary, flush=True)
    result = dict(uids=[a.uid, native_uid], sourceSHA256ByUid=strict['sourceSHA256ByUid'], currentManifestSHA256=selection['manifestSHA256'], rows=summaries, sourceGeometryChanges=0, sourcePoseChanges=0, supportApproved=False, physicalAcceptance=False, installationApproved=False, qualification='Diagnostic shared-original-edge routes from each exact negative wall centroid to authenticated strict rim anchors. All raw compound negatives, non-wall warnings and failed cap proofs are preserved. Paths do not grant source-role, support or publication approval.')
    save(out / 'summary.json', result)
    refs.extend(HERE / name for name in ['original_face_attachment_minimax_v2_20261024.py', 'pool_incident_wall_contacts_v1_20261017.py'])
    module('compound_wall_root_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'installed-compound-wall-strict-root-diagnostic', refs, result)


if __name__ == '__main__':
    main()
