"""Freeze the strict direct-import subset of an explicit island campaign.

No terrain/model edits, approval writes or publication. Existing failed cases are
retained for the source-terrain continuation; current guards are replayed.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from run import connect
from dependency_preflight import from_catalogues


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


policy = module('islands_direct_policy', HERE/'acceptance-policy.py')


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    return str(Path(path).resolve().relative_to(ROOT))


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True)+'\n').encode()
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == '.gz' else raw)


def prepare(region, suffix):
    assert region in ('peng-chau', 'cheung-chau')
    campaign = ROOT/'docs/astra-city/government-import/islands-peng-cheung-tung-20261106'
    selection = read(campaign/'targets.json.gz')
    manifest_path = ROOT/'3d-viewer/city/data/manifest.json'
    assert sha(manifest_path) == selection['sourceManifestSha256']
    chunks = [(0, 1000), (1000, 425)] if region == 'peng-chau' else [(0, 1000), (1000, 1000), (2000, 1000), (3000, 420)]
    batch = f'government-islands-{region}-direct-{suffix}'
    doc = ROOT/'docs/astra-city/government-import'/batch
    stage = HERE/'accepted'/batch
    assert not doc.exists() and not stage.exists(), 'Fresh immutable stage required'
    pins = {rel(campaign/'targets.json.gz'): sha(campaign/'targets.json.gz')}
    rows = []
    deferred = []
    for offset, count in chunks:
        source_doc = ROOT/'docs/astra-city/government-import'/f'government-islands-{region}-{offset:04d}-{count}-20261106'
        for filename in ('check-selection.json.gz', 'results.json.gz', 'metrics.json', 'neon-sync.json'):
            p = source_doc/filename
            pins[rel(p)] = sha(p)
        report = read(source_doc/'results.json.gz')
        assert read(source_doc/'neon-sync.json')['exactResultMatch']
        selected = {r['uid']: r for r in read(source_doc/'check-selection.json.gz')['rows']}
        metrics = read(source_doc/'metrics.json')
        for path, digest in metrics['inputHashes'].items():
            assert sha(ROOT/path) == digest, path
            assert path not in pins or pins[path] == digest
            pins[path] = digest
        for outcome in report['rows']:
            if outcome['reasons']:
                deferred.append({'uid': outcome['uid'], 'reasons': outcome['reasons'], 'next': 'source-terrain-and-identity-continuation'})
                continue
            row = selected[outcome['uid']]
            assert not policy.reasons({'state': 'runtime-validated-awaiting-acceptance', 'sourceSHA256': outcome['sourceSHA256']}, outcome['metrics'], metrics['profiles']['mobile'])
            assert not outcome['validation']['concerns']
            assert outcome['validation']['outcome'] == 'runtime-accepted-placement-unreviewed'
            assert sha(ROOT/row['candidate']['path']) == outcome['sourceSHA256']
            assert sha(ROOT/'3d-viewer'/row['source']['tile']) == row['source']['tileSHA256']
            rows.append(row)
    assert rows and len({r['uid'] for r in rows}) == len(rows)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        reviews = dict(db.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC', ([r['uid'] for r in rows],)))
        keys = list({r['native']['cacheKey'] for r in rows})
        native = dict(db.execute('SELECT cache_key,result_sha FROM astra_modelling.native_stage_results WHERE cache_key=ANY(%s)', (keys,)))
    landmarks = {c['uid'] for r in read(ROOT/'docs/astra-city/landmark-registry/inventory-candidates.json')['rows'] for c in r['candidates']}
    accepted = []
    for row in rows:
        reasons = []
        if reviews.get(row['uid']) in ('held', 'source-unavailable', 'identity-unresolved', 'installed-verified'):
            reasons.append('existing-review-requires-explicit-resolution')
        if row['uid'] in landmarks:
            reasons.append('landmark-component-scope')
        assert native[row['native']['cacheKey']] == row['native']['resultSha']
        if reasons:
            deferred.append({'uid': row['uid'], 'reasons': reasons})
        else:
            accepted.append(row)
    assert accepted
    stage.mkdir(parents=True)
    catalogue = read(HERE.parent/'kai-tak-port/staged/catalogue.json')
    catalogue = {k: v for k, v in catalogue.items() if k not in ('models', 'counts', 'area')}
    catalogue.update(area=f'{region} strict original government ports', models=[], counts={'packedModels': len(accepted)})
    for row in accepted:
        entry = copy.deepcopy(row['candidate']['entry'])
        assert not entry.get('supportDependencies') and not entry.get('retainedBasicSupportDependencies')
        entry.update(priority='detail', proceduralWindows=False, publicationApproved=False,
                     placementReviewed=False, sourceIdentityReviewed=False, identityReviewApproved=False)
        path = stage/entry['asset']
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/row['candidate']['path'], path)
        assert sha(path) == entry['sha256']
        catalogue['models'].append(entry)
    save(stage/'catalogue.json', catalogue)
    deps = from_catalogues(manifest_path, [stage/'catalogue.json'])
    save(doc/'dependency-preflight.json', deps)
    assert not deps['requiresAssemblyInvestigation'], 'Resolve dependency migration before admission'
    save(doc/'selection.json.gz', {'batch': batch, 'manifestSHA256': sha(manifest_path), 'rows': accepted, 'inputHashes': pins})
    save(stage/'catalogue-index.json', {'models': len(accepted), 'catalogues': ['catalogue.json']})
    save(stage/'source-forms.json', [{**r['source']['building'], 'tile': Path(r['source']['tile']).stem} for r in accepted])
    destination = f'city/data/official-models/{batch}/catalogue.json'
    save(stage/'plan.json', {'areas': [{'area': catalogue['area'], 'catalogue': rel(stage/'catalogue.json'), 'destination': destination, 'terrain': []}], 'topLevelTerrainPatches': []})
    save(stage/'browser-config.json', {'stage': rel(stage)+'/', 'doc': rel(doc)+'/', 'catalogueURL': destination,
         'terrain': [], 'fitBox': True, 'browserUids': [r['uid'] for r in accepted], 'failureTestUids': [r['uid'] for r in accepted]})
    save(doc/'stage.json', {'batch': batch, 'region': region, 'sources': len(accepted), 'uids': [r['uid'] for r in accepted],
         'inputHashes': pins, 'deferred': deferred, 'sourceGeometryChanges': 0, 'terrainChanges': 0, 'publication': False,
         'catalogueSHA256': sha(stage/'catalogue.json'), 'planSHA256': sha(stage/'plan.json')})
    print(json.dumps({'batch': batch, 'sources': len(accepted), 'deferred': len(deferred), 'publication': False}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--region', choices=('peng-chau', 'cheung-chau'), required=True)
    parser.add_argument('--suffix', required=True)
    args = parser.parse_args()
    prepare(args.region, args.suffix)
