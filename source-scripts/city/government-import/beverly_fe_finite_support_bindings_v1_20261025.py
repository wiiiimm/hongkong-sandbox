"""Bind each exact F/E original to its unchanged surveyed BASIC podium; no acceptance."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, jobs
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-beverly-fe-finite-support-bindings-v1-20261025'

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
    runtime = 'government-xl-beverly-fe-after-k-runtime-v1-20261025'
    selection = take(runtime, 'selection.json.gz')
    sources = {row['uid']: row for row in selection['rows']}
    finite = take('government-xl-beverly-fe-after-k-finite-evidence-v1-20261025', 'summary.json')
    assert finite['verifiedFinitePaths'] == 448 and finite['strictCanonicalSupportPassed'] is False
    assert set(finite['uids']) == set(sources)
    payloads = take('government-xl-beverly-fe-after-k-four-world-basic-v1-20261025', 'mode-inputs.json.gz')['rows']
    basic = take('government-xl-beverly-fe-after-k-basic-contacts-v1-20261025', 'checks.json.gz')['rows']
    summary = dict(uids=sorted(sources), sourceSHA256ByUid={u:r['sourceSHA256'] for u,r in sources.items()},
                   rows=finite['rows'], identicalWorldContinuousContext=finite['identicalWorldContinuousContext'],
                   separateFiniteSupportEvidence=True, completeFourWorldCanonicalRetainedBasicSupport=False,
                   completeFourWorldFiniteRetainedBasicSupport=True, physicalAcceptance=False,
                   installationApproved=False, publication=False, sourceGeometryChanges=0)
    save(out / 'summary.json', summary)
    support_ref = dict(path=str((out/'summary.json').relative_to(ROOT)), sha256=digest((out/'summary.json').read_bytes()))
    bindings = []
    for uid, row in sources.items():
        checked = next(r for r in basic if r['uid'] == uid)
        payload = next(r for r in payloads if r['uid'] == uid)
        form = checked['supportForm']
        assert checked['sourceSHA256'] == payload['sourceSHA256'] == row['sourceSHA256']
        assert checked['basicIsCurrentFinalSupport'] and checked['canonicalContactPassed'] is False
        assert checked['supportUid'] == payload['supportUid'] == form['uid'] == 'landsd/233218:0'
        assert form['parent'] == row['source']['building']['parent'] and form['heightSource'] == 'landsd'
        bindings.append(dict(uid=uid, supportUid=form['uid'], supportCSUID=form['buildingCSUID'],
                             dependencyMode='retained-current-basic-podium', currentBasicForm=form,
                             currentBasicFormSHA256=digest(jobs.encode(form).encode()),
                             completeIndexedBasicGeometrySHA256=digest(jobs.encode(payload['supportGeometry']).encode()),
                             supportEvidence=support_ref, sourceSHA256=row['sourceSHA256'],
                             mustRemainBasicAndUnsuppressed=True, futureReplacementRequiresDependentRevalidation=True))
    save(out/'support-bindings.json', bindings)
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    module('beverly_fe_finite_support_bindings_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-original-finite-basic-support-lifetime-bindings', refs, summary)
if __name__ == '__main__':
    main()
