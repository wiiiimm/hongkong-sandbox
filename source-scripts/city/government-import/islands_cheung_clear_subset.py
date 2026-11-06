"""Stage a bounded Cheung Chau original subset from completed scripted checks.

Historical checks nominate only. The direct worker repeats current strict source,
identity/contact/runtime and staged/live browser gates before guarded publication.
"""
import argparse
from pathlib import Path
from islands_direct_stage import ROOT, HERE, read, save, sha, rel
from run import connect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--limit', type=int, default=50)
    args = parser.parse_args()
    assert args.batch.startswith('government-islands-cheung-chau-') and '/' not in args.batch
    assert 1 <= args.limit <= 50
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    stage = HERE / 'accepted' / args.batch
    assert not doc.exists() and not stage.exists()
    pins, eligible = {}, {}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for shard in range(4):
            base = ROOT / f'docs/astra-city/government-import/government-islands-cheung-chau-resume-20261106-v2-check-{shard}'
            sync = read(base / 'neon-sync.json')
            assert sync['exactResultMatch'] and sync['reviewWrites'] == 0
            report_path = base / 'results.json.gz'
            evidence = {'path': rel(report_path), 'sha256': sha(report_path)}
            assert db.execute('SELECT result->\'evidence\' FROM astra_modelling.jobs WHERE id=%s AND status=\'complete\'',
                              (sync['jobId'],)).fetchone()[0] == evidence
            selected = {r['uid']: r for r in read(base / 'check-selection.json.gz')['rows']}
            for row in read(report_path)['rows']:
                if row['reasons'] or row.get('validation', {}).get('concerns'):
                    continue
                assert row['uid'] in selected
                assert row['sourceSHA256'] == selected[row['uid']]['candidate']['entry']['sha256']
                assert row['uid'] not in eligible
                eligible[row['uid']] = selected[row['uid']]
            for path in (report_path, base / 'check-selection.json.gz', base / 'neon-sync.json'):
                pins[rel(path)] = sha(path)
        states = dict(db.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC',
                                 (list(eligible),))) if eligible else {}
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = read(manifest_path); pins[rel(manifest_path)] = sha(manifest_path)
    installed = {m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models']}
    rejected = {u: s for u, s in states.items() if s in ('held', 'source-unavailable', 'identity-unresolved', 'installed-verified') and u not in installed}
    chosen = [eligible[u] for u in sorted(eligible) if u not in installed and u not in rejected][:args.limit]
    assert chosen, 'No uninstalled script-clear sources; retain negatives and continue source/terrain investigation'
    catalogue = {k: v for k, v in read(HERE.parent / 'kai-tak-port/staged/catalogue.json').items() if k not in ('area', 'models', 'counts')}
    models = []
    for row in chosen:
        entry = dict(row['candidate']['entry'])
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert sha(tile) == row['source']['tileSHA256']
        source = Path(row['candidate']['path'])
        if not source.is_absolute(): source = ROOT / source
        assert source.resolve().is_relative_to(ROOT) and sha(source) == entry['sha256']
        pins[rel(source)] = sha(source); pins[rel(tile)] = sha(tile)
        entry.update(priority='detail', proceduralWindows=False, placementReviewed=False,
                     sourceIdentityReviewed=False, identityReviewApproved=False, publicationApproved=False)
        target = stage / entry['asset']; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes()); models.append(entry)
    catalogue.update(area='Cheung Chau unchanged government originals', models=models, counts={'packedModels': len(models)})
    save(stage / 'catalogue.json', catalogue); save(stage / 'catalogue-index.json', {'models': len(models), 'catalogues': ['catalogue.json']})
    save(stage / 'source-forms.json', [{**r['source']['building'], 'tile': Path(r['source']['tile']).stem} for r in chosen])
    save(doc / 'selection.json.gz', {'rows': chosen, 'batch': args.batch, 'manifestSHA256': sha(manifest_path), 'nominationOnly': True})
    destination = f'city/data/official-models/{args.batch}/catalogue.json'
    save(stage / 'plan.json', {'areas': [{'area': catalogue['area'], 'catalogue': rel(stage / 'catalogue.json'),
         'destination': destination, 'terrain': []}], 'topLevelTerrainPatches': []})
    uids = [r['uid'] for r in chosen]
    save(stage / 'browser-config.json', {'stage': rel(stage) + '/', 'doc': rel(doc) + '/', 'catalogueURL': destination,
         'terrain': [], 'fitBox': True, 'browserUids': uids, 'failureTestUids': uids, 'visibilitySupplementUids': [],
         'captureDirectionByModel': {u: [.2, 4, .2] for u in uids},
         'viewQualification': 'High oblique views retain dense neighbours; no every-facade or as-built claim.'})
    pins[rel(Path(__file__))] = sha(Path(__file__))
    save(doc / 'stage.json', {'batch': args.batch, 'uids': uids, 'sources': len(uids), 'inputHashes': pins,
         'catalogueSHA256': sha(stage / 'catalogue.json'), 'planSHA256': sha(stage / 'plan.json'),
         'historicalMetricsAreNominationsOnly': True, 'sourceGeometryChanges': 0, 'terrainChanges': 0, 'publication': False})
    save(doc / 'nomination-summary.json', {'clearOriginals': len(eligible), 'alreadyInstalled': len(set(eligible) & installed),
         'existingReviewExclusions': rejected, 'selected': uids, 'publication': False})
    print({'stagedOriginals': len(uids), 'clearNominationPool': len(eligible), 'installed': 0}, flush=True)


if __name__ == '__main__':
    main()
