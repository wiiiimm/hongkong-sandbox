"""Prove historical exact pair geometry contexts still match the current capture.

Source, ground, entry and renderer equality only; raw negatives stay failures.
"""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BATCH = 'government-xl-nam-cheong-current-exact-context-reuse-v1-20261023'
OLD = 'government-xl-nam-cheong-fu-yun-joint-current-v1-20261023-runtime'
NEW = 'government-xl-nam-cheong-fu-yun-after-island-current-v1-20261023-runtime'
ATTR = 'government-xl-nam-cheong-fu-yun-joint-attributes-v1-20261023'
GRADE = 'government-xl-nam-cheong-wall-grade-path-v2-20261023'


def main():
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / BATCH
    assert not doc.exists()
    refs, pins = [Path(__file__)], {}
    for name in [OLD, NEW, ATTR, GRADE]:
        _, pins[name] = authenticate(base / name)
        refs.append(base / name / 'result.json')
    def take(name, path):
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    oldselection = take(OLD, base / OLD / 'selection.json.gz')
    newselection = take(NEW, base / NEW / 'selection.json.gz')
    selections = [{r['uid']: r for r in s['rows']} for s in [oldselection, newselection]]
    geometries = [{r['uid']: r for r in take(n, HERE / 'local' / n / 'runtime-geometry.json.gz')['rows']} for n in [OLD, NEW]]
    attrs = take(ATTR, base / ATTR / 'attributes.json.gz')
    assert attrs['startEndAllInputsVerified']
    attributes = {r['uid']: r for r in attrs['rows']}
    wanted = {'landsd/268867:0', 'landsd/270874:0'}
    assert all(set(rows) == wanted for rows in selections + geometries)
    assert set(attributes) == wanted
    for filename in ['official-models.js', 'official-model-assets.js', 'geo.js']:
        path = ROOT / '3d-viewer/city' / filename
        key = str(path.relative_to(ROOT))
        assert digest(path.read_bytes()) == pins[OLD][key] == pins[NEW][key]
        refs.append(path)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == newselection['manifestSHA256']
    refs.append(manifest)
    rows = []
    for uid in sorted(wanted):
        a, b = [s[uid] for s in selections]
        assert a['sourceSHA256'] == b['sourceSHA256'] == attributes[uid]['sourceSHA256']
        assert a['source'] == b['source']
        assert a['candidate']['entry'] == b['candidate']['entry']
        asset = ROOT / b['candidate']['path']
        assert digest(asset.read_bytes()) == b['sourceSHA256']
        refs.append(asset)
        bound = {}
        for key in ['position', 'index', 'drawnGroundGeometry']:
            old, new = [np.asarray(g[uid][key]) for g in geometries]
            assert old.shape == new.shape and np.array_equal(old, new)
            bound[key] = dict(shape=list(new.shape), canonicalArraySHA256=digest(new.astype('<f8').tobytes()))
        rows.append(dict(uid=uid, sourceSHA256=b['sourceSHA256'], exactArrays=bound,
                         candidateEntryAndFormUnchanged=True))
    grade = take(GRADE, base / GRADE / 'summary.json')
    assert grade['rawClearanceFailurePreserved'] and not grade['physicalAccepted']
    summary = dict(uids=sorted(wanted), rows=rows, currentManifestSHA256=newselection['manifestSHA256'],
                   reusableHistoricalAttributeBatch=ATTR, exactFiniteGradeContextBatch=GRADE,
                   rawClearanceFailures=grade['rawClearanceFailures'], historicalAcceptanceTransferred=False,
                   physicalAccepted=False, currentRegionalChecksStillRequired=True,
                   qualification='Exact source arrays, drawn ground, source entry/form and production renderer modules match. Reuse unchanged exact geometry measurements only; no new wall role, root, support, foreign contact, current neighbour, visual, publication or installation approval.')
    save(doc / 'summary.json', summary)
    module('nam_context_reuse_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'exact-original-current-geometry-context-equality', refs, summary)


if __name__ == '__main__':
    main()
