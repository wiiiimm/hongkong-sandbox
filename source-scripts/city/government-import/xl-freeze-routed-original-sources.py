"""Freeze exact restored XL components for a fresh full-cell terrain continuation."""
import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, reservations, NATIVE_RUN
from component_type_resolution import resolve
from terrain_source_preflight import SourceSheetIndex, preflight


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def owned(a, doc, local):
    lease = read(local / 'reservation.json'); assert reservations.owns(lease)
    prior = ROOT / 'docs/astra-city/government-import/government-xl-held-component-recovery-20261008'
    selected = read(prior / 'selection.json.gz')
    historical = {r['uid']: r for r in selected['rows']}
    assert set(a.uid) <= set(historical)
    records = [read(prior / f) for f in ['routing.json', 'government-recovery.json', 'current-checks.json']]
    available = {r['uid']: r for r in records[1]['rows'] if r['state'] == 'exact-source-ready'}
    assert set(a.uid) <= set(available)
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_sha = digest(manifest_path.read_bytes()); manifest = read(manifest_path)
    live = {m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models']}
    assert not set(a.uid) & live
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        for record in records:
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (record['jobId'],)).fetchone() == ('complete', record)
        assert not con.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=ANY(%s)', (a.uid,)).fetchall(), 'Existing review requires explicit continuation'
        for uid in a.uid:
            n = historical[uid]['native']
            assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, n['cacheKey'])).fetchone() == (n['resultSha'],)
    prefixes = {historical[u]['modelId'][1:11] for u in a.uid}
    sources = []
    for tile in manifest['tiles']:
        path = ROOT / '3d-viewer' / tile['url']; raw = path.read_bytes()
        sources.extend({'building': b, 'tile': tile['url'], 'tileSHA256': digest(raw)}
                       for b in json.loads(raw)['buildings'] if str(b.get('buildingCSUID') or '')[:10] in prefixes)
    spec = importlib.util.spec_from_file_location('routed_fresh_context', HERE / 'xl-final-script-pass.py')
    final = importlib.util.module_from_spec(spec); spec.loader.exec_module(final); final.s.LOCAL = local
    index_path = ROOT / 'source-scripts/city/landmark-acquisition/index.json'; index = SourceSheetIndex(read(index_path))
    rows = []; contexts = []; routes = []
    for uid in a.uid:
        assert reservations.owns(lease)
        old = historical[uid]; route = resolve(old['native']['model'], sources)
        assert route['qualified'] and route['uid'] == uid, route
        assert old['routing']['official'] == route['official']
        raw = (ROOT / available[uid]['asset']['path']).read_bytes()
        assert digest(raw) == old['sourceSHA256'] == available[uid]['asset']['sha256']
        target = local / 'assets' / (old['sourceSHA256'] + '.glb.gz'); target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
        source = route['source']; b = source['building']; entry = old['candidate']['entry']
        assert (entry['objectId'], entry['buildingCSUID'], entry['recordedBaseHeight'], entry['recordedTopHeight']) == (b['objectId'], b['buildingCSUID'], b['baseHeightHKPD'], b['topHeightHKPD'])
        row = {**old, 'source': source, 'name': b.get('name') or old['modelId'], 'currentReview': None, 'routing': route,
               'candidate': {'entry': entry, 'path': str(target.relative_to(ROOT))}}
        triangles = final.s.glb_triangles(row); lo, hi = triangles.min(axis=(0,1)), triangles.max(axis=(0,1))
        neighbours = final.load_forms([lo[0]-2, lo[2]-2, hi[0]+2, hi[2]+2])
        context = {'uid': uid, 'sourceSHA256': row['sourceSHA256'], 'identity': final.identity_context(row, triangles, neighbours),
                   'neighbourTileHashes': {tile: digest((ROOT / '3d-viewer' / tile).read_bytes()) for _,_,tile in neighbours}}
        rows.append(row); contexts.append(context); routes.append(preflight(row, context, index))
        print(json.dumps({'uid': uid, 'name': row['name'], 'rawMatchingPreserved': True, 'frozen': len(rows)}), flush=True)
    assert digest(manifest_path.read_bytes()) == manifest_sha
    for context in contexts:
        for tile, sha in context['neighbourTileHashes'].items(): assert digest((ROOT / '3d-viewer' / tile).read_bytes()) == sha
    save(doc / 'check-selection.json.gz', {'batch': a.batch, 'rows': rows, 'nativeRun': NATIVE_RUN, 'manifestSHA256': manifest_sha,
           'qualification': 'Fresh exact routed original source freeze, not identity/physical approval or installation credit.'})
    save(doc / 'context.json.gz', {'rows': contexts})
    save(doc / 'preflight.json', {'rows': routes, 'priorEvidence': [ref(prior / f) for f in ['selection.json.gz', 'routing.json', 'government-recovery.json', 'current-checks.json']],
           'runner': ref(Path(__file__)), 'routingPolicy': ref(HERE / 'component_type_resolution.py'),
           'originalBytesAndMatchingPreserved': True, 'newlyInstalled': 0, 'publication': False,
           'modelGeometryChanges': 0, 'scriptExternalAICalls': 0})


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--uid', action='append', required=True); p.add_argument('--batch', required=True); p.add_argument('--owned', action='store_true'); a = p.parse_args()
    assert Path(a.batch).name == a.batch and a.batch.startswith('government-xl-')
    assert 1 <= len(a.uid) <= 100 and len(a.uid) == len(set(a.uid))
    doc = ROOT / 'docs/astra-city/government-import' / a.batch; local = HERE / 'local' / a.batch
    if a.owned: return owned(a, doc, local)
    assert not doc.exists(), 'Fresh immutable inputs only'
    claim = reservations.claim('codex-xl-routed-freeze-' + str(uuid.uuid4()), ['building:' + u for u in a.uid], batch=a.batch); assert claim['ok'], claim
    save(local / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run', '--lease-file', str(local / 'reservation.json'), '--', sys.executable, __file__, *sys.argv[1:], '--owned'], cwd=ROOT, check=True)

if __name__ == '__main__': main()
