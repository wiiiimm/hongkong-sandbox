"""DRAFT source-only immutable original Youth Square diagnostic; no acceptance/review edits."""
from pathlib import Path
import importlib.util
import json
from run import ROOT, HERE, read, save, digest, connect
BATCH = 'government-xl-youth-square173512-original-body-extent-podium-contacts-v1-20261011'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
METHOD = ROOT / 'docs/astra-city/government-import/government-xl-youth-square173512-original-source-method-v1-20261011/METHOD.md'
PROTECTED = ['landsd/173512:0', 'landsd/139415:0']
def ref(p):
    return dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes()))
def state():
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id', (PROTECTED,)).fetchall()
def main():
    before = state()
    assert not (DOC / 'result.json').exists()
    d = read(DOC / 'diagnostic.json.gz')
    assert d['uid'] == PROTECTED[0] and d['podiumUid'] == PROTECTED[1]
    assert d['completeFaces'] == {PROTECTED[0]: 13100, PROTECTED[1]: 22}
    assert d['completeTowerPodiumPairDomain'] == 13100 * 22
    assert len(d['all286HistoricalGroupFarFaces']) == 286
    assert d['sourceOnly'] and d['historicalInputsOnly']
    assert not any(d[k] for k in ['currentAcceptance', 'identityAccepted', 'installationApproved', 'sourceGeometryChanges', 'terrainGeometryChanges', 'structuralRootCredit'])
    for uid, count in d['completeFaces'].items():
        c = d['originalCensuses'][uid]
        faces = [f for fs in c['sharedEdgeConnectedComponents'] for f in fs] + c['exactNonrenderingOriginalFaces']
        assert len(faces) == count and set(faces) == set(range(count))
        assert ref(ROOT / d['sources'][uid]['path']) == d['sources'][uid]
    for e in d['evidenceRefs']:
        assert ref(ROOT / e['path']) == e
    spec = importlib.util.spec_from_file_location('reviewed_source_freezer', HERE / 'parkview_block17_freeze_current_source_evidence_20261011.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    paths = {p for p in DOC.rglob('*') if p.is_file()}
    paths.add(METHOD)
    m.local_imports(HERE / 'youth_square173512_original_body_extent_podium_contacts_v1_20261011.py', paths)
    m.local_imports(Path(__file__), paths)
    m.declared_refs(d, paths)
    summary = dict(completeFaces=d['completeFaces'], genuineBodies={uid: len(c['sharedEdgeConnectedComponents']) for uid, c in d['originalCensuses'].items()}, exactZeros={uid: c['exactNonrenderingOriginalFaces'] for uid, c in d['originalCensuses'].items()}, farFaces=286, exactFiniteContacts=len(d['allFiniteTowerPodiumContacts']), allBodyObligations=len(d['allBodyObligations']), identitySupportUnqualified=True)
    note = d['qualification'] + ' Primary plan registration is a next method, not a completed finding.'
    (DOC / 'REVIEW.md').write_text('# Youth Square unchanged original source diagnostic\n\n' + note + '\n\n' + json.dumps(summary) + '\n')
    save(DOC / 'review.json', dict(uids=PROTECTED, sourceOnly=True, summary=summary, finding=note, currentAcceptance=False, installationApproved=False, evidenceRefs=[ref(p) for p in sorted(paths)]))
    paths.update([DOC / 'REVIEW.md', DOC / 'review.json'])
    m.F.freeze(BATCH, 'youth-square-original-body-extent-podium-contacts-no-acceptance', sorted(paths), dict(uids=PROTECTED, sourceOnly=True, currentAcceptance=False, installationApproved=False, governmentGeometryChanges=0, terrainGeometryChanges=0, modelReviewWrites=0, pointerWrites=0, qualification=note))
    assert state() == before
    result = read(DOC / 'result.json')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (result['jobId'],)).fetchone() == ('complete', result)
    for e in result['evidenceRefs']:
        assert ref(ROOT / e['path']) == e
    print(json.dumps(dict(jobId=result['jobId'], protectedReviewsUnchanged=True, allEvidenceRefsVerified=len(result['evidenceRefs']), sourceOnly=True)), flush=True)
if __name__ == '__main__':
    main()
