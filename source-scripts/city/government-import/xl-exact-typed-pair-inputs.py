"""Freeze qualified explicit component pairs; retain per-pair lookup exceptions.

Read-only pinned native inventory and current viewer forms; no acquired geometry,
identity approval, publication, or installation credit. Missing/ambiguous joins
reject rather than fabricating native viewer matches.
"""
import argparse
import sys
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, NATIVE_RUN

sys.path.insert(0, str(HERE.parent / 'enhancement-screening'))
from shape_prepare import entry
from component_type_resolution import resolve


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--pair', action='append', required=True)
    args = parser.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    pairs = [tuple(p.split('=')) for p in args.pair]
    assert all(len(p) == 2 and p[0] != p[1] and all(
        u.startswith('landsd/') and u.endswith(':0') for u in p) for p in pairs)
    assert len(pairs) == len(set(pairs))
    wanted = {u for p in pairs for u in p}
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    assert not doc.exists(), 'Fresh frozen inputs only'
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = read(manifest_path)
    forms = {}
    for tile in manifest['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        for building in read(path)['buildings']:
            if building['uid'] in wanted:
                assert building['uid'] not in forms, 'Duplicate current source form'
                forms[building['uid']] = {'building': building, 'tile': tile['url'],
                    'tileSHA256': digest(path.read_bytes())}
    assert set(forms) == wanted, 'Missing exact current source component'
    sources, qualified, held, profile_cache, stage_cache, tower_cache = [], [], [], {}, {}, {}
    with connect() as con:
        con.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        for tower, podium in pairs:
            form = forms[tower]['building']
            lower = forms[podium]['building']
            assert form['structureType'] == 'Tower' and lower['structureType'] == 'Podium'
            assert form.get('parent') and form['parent'] == lower.get('parent')
            assert set(form.get('osmRefs', [])) & set(lower.get('osmRefs', []))
            if tower in tower_cache:
                qualified.append((tower, podium))
                continue
            georef = form['buildingCSUID'][:10]
            if georef not in profile_cache:
                profile_cache[georef] = con.execute('SELECT DISTINCT cache_key,sheet FROM astra_modelling.native_model_sizes '
                    'WHERE run_id=%s AND model_id LIKE %s', (NATIVE_RUN, 'B' + georef + '%')).fetchall()
            profiles = profile_cache[georef]
            matches = []
            for key, sheet in profiles:
                if key not in stage_cache:
                    stage_cache[key] = con.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r '
                        'JOIN astra_modelling.native_stage_members m USING(cache_key) '
                        'WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, key)).fetchone()
                cached = stage_cache[key]
                assert cached, 'Missing pinned native stage'
                sha, data = cached
                for model in data['models']:
                    official = [v for v in model.get('matching', {}).get('officialCandidates', [])
                        if v['objectId'] == form['objectId'] and v['buildingCSUID'] == form['buildingCSUID']]
                    routing = resolve(model, list(forms.values()))
                    if len(official) == 1 and routing['qualified'] and routing['uid'] == tower:
                        matches.append({'cacheKey': key, 'resultSha': sha, 'sheet': sheet,
                            'uids': [tower], 'model': model, 'routing': routing})
            if len(matches) != 1:
                held.append({'uid': tower, 'supportUid': podium, 'reason': 'missing-or-ambiguous-exact-original-tower', 'exactMatches': len(matches)})
                print(held[-1], flush=True)
                continue
            native = matches[0]
            model = native['model']
            official = native['routing']['official']
            candidate = {**model['asset'], 'uid': tower, 'label': form.get('name') or model['modelId'],
                'objectId': form['objectId'], 'buildingCSUID': form['buildingCSUID'],
                'modelId': model['modelId'], 'triangles': model['triangles'], 'worldBounds': model['worldBounds'],
                'sourceTile': native['sheet'], 'rootTranslation': [-834500, 0, 816500],
                'recordedBaseHeight': form['baseHeightHKPD'], 'recordedTopHeight': form['topHeightHKPD'],
                'priority': 'unreviewed', 'sourceIdentityReviewed': False, 'placementReviewed': False,
                'publicationApproved': False, 'overlapOfSmallerFootprint': official['overlapOfSmallerFootprint'],
                'footprintCentroidDistanceMetres': official['footprintCentroidDistanceMetres']}
            qualified.append((tower, podium))
            tower_cache[tower] = native
            review = con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews '
                'WHERE uid=%s ORDER BY updated_at DESC LIMIT 1', (tower,)).fetchone()
            sources.append({'uid': tower, 'source': forms[tower], 'native': native,
                'modelId': native['model']['modelId'], 'name': form.get('name'),
                'triangles': native['model']['triangles'],
                'sourceSHA256': native['model']['asset']['sha256'],
                'candidate': {'entry': candidate},
                'currentReview': None if review is None else {
                    'state': review[0], 'sourceSHA256': review[1]}})
    refs = [{'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}
        for path in [manifest_path, Path(__file__)]]
    save(doc / 'check-selection.json.gz', {'rows': sources, 'manifestSHA256': digest(manifest_path.read_bytes())})
    save(doc / 'inputs.json', {'batch': args.batch, 'pairs': [dict(uid=u, supportUid=s) for u, s in qualified],
        'requestedPairs': [dict(uid=u, supportUid=s) for u, s in pairs], 'lookupExceptions': held,
        'nativeRun': NATIVE_RUN, 'sourceRefs': refs + [{'path': str((HERE / 'component_type_resolution.py').relative_to(ROOT)), 'sha256': digest((HERE / 'component_type_resolution.py').read_bytes())}],
        'publication': False, 'newlyInstalled': 0, 'modelGeometryChanges': 0,
        'qualification': 'Exact pinned tower lookup for original support diagnostics. The closure runner '
            'must reserve both components, acquire exact bytes and verify all native results. Component type resolves source metadata only; raw cached viewer ambiguity is preserved. No identity approval.'})
    print({'batch': args.batch, 'requestedPairs': len(pairs), 'qualifiedPairs': len(qualified), 'lookupExceptions': len(held), 'towerSources': len(sources), 'publication': False})


if __name__ == '__main__':
    main()
