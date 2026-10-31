"""Measure the two original columns' joins without imposing welded topology."""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-greenfield-after-fung-yip-'
BATCH = P + 'two-original-columns-context-v1-20261025'
UID = 'landsd/258419:0'
FACES = list(range(9427, 9459))


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, name):
        if batch not in pins:
            _, pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        p = BASE / batch / name
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)

    source = next(r for r in take(P + 'seam-runtime-v2-20261025', 'selection.json.gz')['rows'] if r['uid'] == UID)
    attr = next(r for r in take(P + 'attributes-v1-20261025', 'attributes.json.gz')['rows'] if r['uid'] == UID)
    raw = (ROOT / source['candidate']['path']).read_bytes()
    assert digest(raw) == source['sourceSHA256'] == attr['sourceSHA256']
    refs.append(ROOT / source['candidate']['path'])
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    worlds = dict(original=decode_original_world_triangles(raw), **{
        mode: np.asarray(attr[key]).reshape(-1, 3)[ix]
        for mode, key in [('literal', 'completeLiteralWorldPosition'),
                          ('left', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
                          ('balanced', 'completeExplicitBalancedFloat32WorldPosition')]})
    views_batch = 'government-xl-greenfield-258419-after-fung-yip-32-wall-views-v2-20261025'
    views = take(views_batch, 'summary.json')
    assert views['displaySubsetOnly'] and views['displayedExactNegativeFaces'] == FACES
    assert len(views['regions']) == 1
    image = ROOT / views['regions'][0]['image']
    assert digest(image.read_bytes()) == views['regions'][0]['imageSHA256']
    refs.append(image)
    summaries = []
    clearance = 'government-xl-greenfield-258419-after-fung-yip-complete-ground-v2-20261025'
    for mode, t in worlds.items():
        assert len(t) == 10007
        cap = take(clearance, mode + '-cap-paths.json.gz')
        assert cap['sourceWorldSHA256'] == digest(t.astype('<f8').tobytes())
        bad = sorted(r['sourceFace'] for r in cap['proof']['paths'] if not r['hasExactSharedEdgeClearCapPath'])
        assert bad == FACES
        other = [i for i in range(len(t)) if i not in FACES]
        contacts = exact_finite_contacts(t, FACES, t, other)
        save(out / (mode + '-finite-joins.json.gz'), contacts)
        groups = []
        for ids in [FACES[:16], FACES[16:]]:
            positive = [r for r in contacts['contacts'] if r['sourceFaceA'] in ids and r['dimension'] > 0]
            groups.append(dict(sourceFaces=ids, bounds=[t[ids].min((0, 1)).tolist(), t[ids].max((0, 1)).tolist()], positiveSourceJoinPairs=len(positive), contactOtherSourceFaces=sorted({r['sourceFaceB'] for r in positive})))
        summaries.append(dict(mode=mode, sourceWorldSHA256=digest(t.astype('<f8').tobytes()), groups=groups, strictSharedEdgeCapPathPassed=False, completeOriginalFaces=10007))
    result = dict(uids=[UID], sourceSHA256=source['sourceSHA256'], rows=summaries,
                  actuallyInspectedImage=dict(path=str(image.relative_to(ROOT)), sha256=digest(image.read_bytes())),
                  sourceGeometryChanges=0, sourcePoseChanges=0, physicalAcceptance=False,
                  installationApproved=False, aiGeometryModelling=False,
                  qualification='ROOT opened the complete32-face two-angle diagnostic: these are the sides of two polygonal columns beneath original canopy geometry. Exact finite contacts with the rest of the immutable original are measured in all four worlds; they imply no engineering load-bearing approval. The missing shared-edge cap paths remain false. All85wall negatives, their existing highest-vertex checks, actual ground coverage and whole-source foundations remain separate evidence.')
    save(out / 'summary.json', result)
    refs += [HERE / 'exact_original_finite_triangle_contacts_20261010.py', HERE / 'exact_packed_world_geometry_20261009.py']
    module('greenfield_column_context', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'exact-two-original-column-source-join-diagnostic', refs, result)


if __name__ == '__main__':
    main()
