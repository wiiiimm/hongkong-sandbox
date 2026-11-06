"""Nominate fresh direct-check positives for unchanged original browser review.

Exact Neon results and current inputs are replayed. This prepares private files;
the existing worker still repeats metrics, browser and guarded installation gates.
"""
import argparse
import copy
from pathlib import Path
from islands_direct_stage import ROOT, HERE, read, save, sha, rel, policy
from run import connect


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--direct-check', required=True)
    a = p.parse_args()
    assert all(b.startswith('government-islands-') and '/' not in b for b in (a.batch, a.direct_check))
    base = ROOT / 'docs/astra-city/government-import'
    source_doc, doc = base / a.direct_check, base / a.batch
    source_stage, stage = HERE / 'accepted' / a.direct_check, HERE / 'accepted' / a.batch
    assert not doc.exists() and not stage.exists()
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    selection = read(source_doc / 'selection.json.gz')
    assert selection['manifestSHA256'] == sha(manifest_path)
    result_path = source_doc / 'results.json.gz'
    report, sync = read(result_path), read(source_doc / 'neon-sync.json')
    assert sync['exactResultMatch'] and report['modelReviewWrites'] == 0
    evidence = {'path': rel(result_path), 'sha256': sha(result_path)}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        state, stored = db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (sync['jobId'],)).fetchone()
        assert state == 'complete' and stored['evidence'] == evidence
        assert {k:v for k,v in stored.items() if k not in ('jobId', 'evidence')} == report
    metrics = read(source_doc / 'metrics.json')
    pins = {}
    def pin(path):
        key, digest = rel(path), sha(path)
        assert key not in pins or pins[key] == digest
        pins[key] = digest
    for path, digest in {**report['inputHashes'], **metrics['inputHashes']}.items():
        assert sha(ROOT / path) == digest, path
        pin(ROOT / path)
    for name in ('selection.json.gz', 'results.json.gz', 'neon-sync.json', 'metrics.json', 'validation.json', 'dependency-preflight.json'):
        pin(source_doc / name)
    rows = {r['uid']:r for r in selection['rows']}
    chosen = []
    for outcome in report['rows']:
        if outcome['reasons']:
            continue
        row = rows[outcome['uid']]
        assert outcome['sourceSHA256'] == row['candidate']['entry']['sha256']
        assert not policy.reasons({'state':'runtime-validated-awaiting-acceptance', 'sourceSHA256':outcome['sourceSHA256'], 'identityProof':row.get('identityProof')}, outcome['metrics'], metrics['profiles']['mobile'])
        assert outcome['validation']['outcome'] == 'runtime-accepted-placement-unreviewed'
        assert not outcome['validation']['concerns']
        chosen.append(copy.deepcopy(row))
    assert 0 < len(chosen) <= 40
    uids = sorted(r['uid'] for r in chosen)
    installed = {m['uid'] for url in read(manifest_path)['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models']}
    assert not installed.intersection(uids)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        states = dict(db.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC', (uids,)))
    assert not any(s in ('held', 'source-unavailable', 'identity-unresolved', 'installed-verified') for s in states.values())
    identity_path = ROOT / selection['identityEvidencePath']
    identities = {r['uid']:r for r in read(identity_path)['rows']}
    pin(identity_path)
    catalogue = read(source_stage / 'catalogue.json')
    by_model = {m['uid']:m for m in catalogue['models']}
    models = []
    for row in chosen:
        uid = row['uid']
        entry = copy.deepcopy(by_model[uid])
        assert not entry.get('supportDependencies') and not entry.get('retainedBasicSupportDependencies')
        assert all(entry[k] is False for k in ('publicationApproved', 'placementReviewed', 'sourceIdentityReviewed', 'identityReviewApproved'))
        if row.get('identityProof'):
            assert identities[uid]['passed'] and identities[uid]['proof'] == row['identityProof']
        asset = source_stage / entry['asset']
        assert sha(asset) == entry['sha256']
        pin(asset)
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert sha(tile) == row['source']['tileSHA256']
        pin(tile)
        target = stage / entry['asset']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(asset.read_bytes())
        models.append(entry)
    catalogue.update(area='Island unchanged current-terrain direct originals', models=models, counts={'packedModels':len(models)})
    save(stage / 'catalogue.json', catalogue)
    save(stage / 'catalogue-index.json', {'models':len(models), 'catalogues':['catalogue.json']})
    save(stage / 'source-forms.json', [{**r['source']['building'], 'tile':Path(r['source']['tile']).stem} for r in chosen])
    save(doc / 'selection.json.gz', {'batch':a.batch, 'manifestSHA256':sha(manifest_path), 'rows':chosen, 'nominationOnly':True})
    destination = f'city/data/official-models/{a.batch}/catalogue.json'
    save(stage / 'plan.json', {'areas':[{'area':catalogue['area'], 'catalogue':rel(stage / 'catalogue.json'), 'destination':destination, 'terrain':[]}], 'topLevelTerrainPatches':[]})
    save(stage / 'browser-config.json', {'stage':rel(stage)+'/', 'doc':rel(doc)+'/', 'catalogueURL':destination, 'terrain':[], 'fitBox':True, 'browserUids':uids, 'failureTestUids':uids, 'visibilitySupplementUids':[], 'captureDirectionByModel':{u:[.2,4,.2] for u in uids}, 'viewQualification':'High oblique original-source views; no every-facade/as-built claim.'})
    pin(Path(__file__))
    pin(manifest_path)
    save(doc / 'stage.json', {'batch':a.batch, 'uids':uids, 'sources':len(uids), 'inputHashes':pins, 'identityEvidencePath':rel(identity_path), 'catalogueSHA256':sha(stage / 'catalogue.json'), 'planSHA256':sha(stage / 'plan.json'), 'sourceGeometryChanges':0, 'terrainChanges':0, 'publication':False})
    print({'nominated':len(uids), 'uids':uids, 'installed':0}, flush=True)


if __name__ == '__main__':
    main()
