"""Diagnose an immutable terrain-distant installed source and unchanged original support."""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, connect, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from retained_native_template_v3_20261023 import exact_rendered_face_multiset


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'owner', 'uid', 'support', 'patch', 'inventory', 'neighbours']:
        p.add_argument('--' + k, required=True)
    p.add_argument('--lease', required=True)
    a = p.parse_args()
    lease = read(Path(a.lease)); assert reservations.owns(lease) and {'building:'+a.uid,'building:'+a.support,'building:'+a.owner} <= set(lease['resources'])
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / a.batch
    assert not doc.exists()
    refs, pins, receipts = [Path(__file__)], {}, {}
    for batch in [a.patch, a.inventory, a.neighbours]:
        receipt, bound = authenticate(base / batch)
        receipts[batch] = receipt
        for key, sha in bound.items():
            assert key not in pins or pins[key] == sha, "Conflicting authenticated input revisions"
            pins[key] = sha
        refs.append(base / batch / 'result.json')

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    inventory = {r['uid']: r for r in take(base / a.inventory / 'complete-bounds.json.gz')['rows']}
    proposal=receipts[a.patch]
    assert proposal['status']=='private-three-member-chain-surface-validator-passed'and proposal['allEffectiveMembersRequired']is True and len(proposal['members'])==3
    beforeparts=[];afterparts=[];oldboxes=[];newboxes=[]
    root=take(ROOT/'3d-viewer/city/data/terrain.json')
    builder=module('unchanged_coordinated_extent',HERE/'resolve-pass-indexed-parent-clipping.py')
    for member in proposal['members']:
        oldpath=ROOT/'3d-viewer'/member['replaces']['url'];assert digest(oldpath.read_bytes())==member['replaces']['sha256'];refs.append(oldpath);old=read(oldpath)
        candidate=take(ROOT/member['candidate']['path'])
        for patch,parts,boxes in [(old,beforeparts,oldboxes),(candidate,afterparts,newboxes)]:
            m=patch['nativeMesh'];parts.append(np.asarray(m['position'],dtype='float32').astype('float64').reshape(-1,3)[np.asarray(m['index']).reshape(-1,3)]);boxes.append(shapely.box(*builder.extent(patch['coarseCells'],root)))
    before=np.concatenate(beforeparts);after=np.concatenate(afterparts)
    changedRootMask=shapely.union_all(oldboxes).symmetric_difference(shapely.union_all(newboxes))
    refs.append(HERE/'resolve-pass-indexed-parent-clipping.py')
    report = take(base / a.neighbours / 'summary.json')
    raw = next(r for r in report['nativeRows'] if r['uid'] == a.uid)
    assert raw['passed'] is False and raw['terrain']['maximumBurialIncrease'] == 0
    assert raw['terrain']['minimumGapBefore'] == raw['terrain']['minimumGapAfter']
    assert raw['terrain']['newlyWhollyBuried'] == raw['terrain']['newlyUpwardWhollyBuried'] == 0
    manifest = take(ROOT / '3d-viewer/city/data/manifest.json')
    entries = {}
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        for entry in read(path)['models']:
            if entry['uid'] in [a.uid, a.support]:
                assert entry['uid'] not in entries
                entries[entry['uid']] = (entry, path)
    assert set(entries) == {a.uid, a.support}
    support_raw = next(r for r in report['nativeRows'] if r['uid'] == a.support)
    assert support_raw['passed'] is True
    assert support_raw['terrain']['newlyWhollyBuried'] == support_raw['terrain']['newlyUpwardWhollyBuried'] == 0
    assert support_raw['terrain']['maximumBurialIncrease'] == 0
    assert a.support in raw['support']['pinnedNativeUids'] and raw['terrain']['minimumGapAfter'] > 2
    pointerpath = ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
    pointersha = digest(pointerpath.read_bytes()); pointer = read(pointerpath); refs.append(pointerpath)
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        for uid in [a.uid,a.support]:
            assert con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(pointer['snapshotId'],uid)).fetchone() == ('installed-verified',entries[uid][0]['sha256'])
    rows = []
    for uid in [a.uid, a.support]:
        entry, catalogue = entries[uid]
        assert inventory[uid]['sourceSHA256'] == entry['sha256']
        asset = catalogue.parent / entry['asset']
        assert digest(asset.read_bytes()) == entry['sha256']
        refs.append(asset)
        bounds = np.asarray(inventory[uid]['completeFourWorldBounds'])
        low, high = bounds[:, 0].min(0), bounds[:, 1].max(0)
        assert not shapely.box(low[0],low[2],high[0],high[2]).intersects(changedRootMask), 'Root coarse masking changed under complete native/source bounds'
        def relevant(triangles):
            return triangles[np.all(triangles[:, :, [0, 2]].max(1) >= low[[0, 2]], axis=1) &
                             np.all(triangles[:, :, [0, 2]].min(1) <= high[[0, 2]], axis=1)]
        old_faces, new_faces = relevant(before), relevant(after)
        assert len(old_faces) and len(new_faces)
        box = shapely.box(low[0],low[2],high[0],high[2])
        assert box.difference(shapely.union_all(oldboxes)).is_empty and box.difference(shapely.union_all(newboxes)).is_empty, 'Complete source bounds must stay inside effective native chain mask'
        proof = dict(uid=uid, sourceSHA256=entry['sha256'], completeFourWorldBounds=bounds.tolist(), completeIntersectingTerrainFacesBefore=len(old_faces), completeIntersectingTerrainFacesAfter=len(new_faces), rootCoarseMaskUnchangedAcrossCompleteBounds=True, currentInstalledReviewSnapshot=pointer['snapshotId'], sourceGeometryAndPoseUnchanged=True)
        if uid == a.uid:
            before_max, after_max = float(old_faces[:,:,1].max()), float(new_faces[:,:,1].max())
            assert before_max < low[1]-2 and after_max < low[1]-2, 'Source must remain conservatively terrain-distant under complete four-world bounds'
            proof.update(beforeCompleteFacetMaximumHeight=before_max, afterCompleteFacetMaximumHeight=after_max, sourceMinimumHeight=float(low[1]), minimumConservativeClearanceM=float(low[1]-max(before_max,after_max)), terrainRelevantBefore=False,terrainRelevantAfter=False)
        else:
            proof['currentFullNativeRegressionPassed'] = True
            proof['rawNativeRegression'] = support_raw
        rows.append(proof)
    assert reservations.owns(lease) and digest(pointerpath.read_bytes()) == pointersha
    result = dict(uids=[a.owner], nativeUid=a.uid, supportUid=a.support, rows=rows,
                  rawNativeRegression=raw, terrainDistantSourceContextProved=True, proposalTerrainNonRegressionProved=False,
                  existingNativeReaccepted=False, rawSupportPolicyPassed=False,
                  sourceGeometryChanges=0, installationApproved=False,
                  qualification='Complete four-world source bounds remain strictly more than2m above every intersecting before/after terrain facet, using conservative full-facet maxima. Original source/support assets, source pose, current installed Neon reviews and unchanged root mask are bound. Current full native regression passes for the original support. Raw pre-existing source rim-fraction failure remains false and is not reapproved. This is an alternative diagnostic context, NOT exact terrain equivalence, full nonregression, physical or publication approval.')
    save(doc / 'summary.json', result)
    refs.append(HERE / 'retained_native_template_v3_20261023.py')
    module('unchanged_native_context_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'terrain-distant-current-installed-original-support-context-diagnostic', refs, result)
    print(dict(rows=rows, rawSupportPolicyPassed=False), flush=True)


if __name__ == '__main__':
    main()
