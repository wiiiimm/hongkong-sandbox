"""Freeze exact original tower sources for explicit component closure checks.

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
    sources = []
    with connect() as con:
        con.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        for tower, podium in pairs:
            form = forms[tower]['building']
            lower = forms[podium]['building']
            assert form['structureType'] == 'Tower' and lower['structureType'] == 'Podium'
            assert form.get('parent') and form['parent'] == lower.get('parent')
            assert set(form.get('osmRefs', [])) & set(lower.get('osmRefs', []))
            profiles = con.execute('SELECT DISTINCT cache_key,sheet FROM astra_modelling.native_model_sizes '
                'WHERE run_id=%s AND model_id LIKE %s',
                (NATIVE_RUN, 'B' + form['buildingCSUID'][:10] + '%')).fetchall()
            matches = []
            for key, sheet in profiles:
                cached = con.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r '
                    'JOIN astra_modelling.native_stage_members m USING(cache_key) '
                    'WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, key)).fetchone()
                assert cached, 'Missing pinned native stage'
                sha, data = cached
                for model in data['models']:
                    official = [v for v in model.get('matching', {}).get('officialCandidates', [])
                        if v['objectId'] == form['objectId'] and v['buildingCSUID'] == form['buildingCSUID']]
                    if len(official) == 1 and model['modelId'][1:11] == form['buildingCSUID'][:10]:
                        matches.append({'cacheKey': key, 'resultSha': sha, 'sheet': sheet,
                            'uids': [tower], 'model': model})
            assert len(matches) == 1, ('Missing or ambiguous exact original tower', tower, len(matches))
            native = matches[0]
            viewer = native['model']['matching']['viewerMatches']
            assert len(viewer) == 1 and viewer[0]['uid'] == tower, 'Original viewer match held'
            assert viewer[0]['objectId'] == form['objectId']
            assert viewer[0]['buildingCSUID'] == form['buildingCSUID']
            candidate = entry(native, form)
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
    save(doc / 'inputs.json', {'batch': args.batch, 'pairs': [dict(uid=u, supportUid=s) for u, s in pairs],
        'nativeRun': NATIVE_RUN, 'sourceRefs': refs,
        'publication': False, 'newlyInstalled': 0, 'modelGeometryChanges': 0,
        'qualification': 'Exact pinned tower lookup for original support diagnostics. The closure runner '
            'must reserve both components, acquire exact bytes and verify all native results. No identity approval.'})
    print({'batch': args.batch, 'pairs': len(pairs), 'towerSources': len(sources), 'publication': False})


if __name__ == '__main__':
    main()
