"""Freeze twenty-three explicit XL continuation sources; no acceptance or publication."""
import importlib.util
import json
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect
sys.path.insert(0, str(HERE.parent / 'enhancement-screening'))
from shape_prepare import entry
from terrain_source_preflight import SourceSheetIndex, preflight

BATCH = 'government-xl-extended-23-inputs-20261005'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH
UIDS = [f'landsd/{i}:0' for i in [227948,186864,289787,232526,244683,232896,231645,226296,72296,234188,229881,81743,273672,193086,292155,177604,258562,311743,84014,280350,98845,235076,258411]]
BASE = ROOT / 'docs/astra-city/government-import/government-xl-remaining-20260923'


def run():
    assert not DOC.exists(), 'Immutable inputs already exist'
    claim = reservations.claim('codex-xl-independent-inputs-' + str(uuid.uuid4()),
                               ['building:' + u for u in UIDS], batch=BATCH)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        macro = read(BASE / 'selection.json.gz'); by_uid = {r['uid']: r for r in macro['rows']}
        manifest_path = ROOT / '3d-viewer/city/data/manifest.json'; manifest = read(manifest_path)
        installed = {m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models']}
        assert not set(UIDS) & installed
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            reviews = dict(con.execute("SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC", (UIDS,)))
        assert not reviews, 'Existing review requires explicit resolution'
        forms = {}
        for tile in manifest['tiles']:
            path = ROOT / '3d-viewer' / tile['url']
            for b in read(path)['buildings']:
                if b['uid'] in UIDS: forms[b['uid']] = {'building': b, 'tile': tile['url'], 'tileSHA256': digest(path.read_bytes())}
        assert set(forms) == set(UIDS)
        wanted = {by_uid[u]['sourceSHA256'] for u in UIDS}; assets = {}
        for path in (HERE / 'local').rglob('*.glb.gz'):
            sha = path.name.removesuffix('.glb.gz')
            if sha in wanted and digest(path.read_bytes()) == sha:
                assets[sha] = path; wanted.remove(sha)
            if not wanted: break
        assert not wanted, 'Original source assets must be recovered before freezing'
        spec = importlib.util.spec_from_file_location('independent_source_context', HERE / 'xl-final-script-pass.py')
        context = importlib.util.module_from_spec(spec); spec.loader.exec_module(context); context.s.LOCAL = LOCAL
        index = SourceSheetIndex(read(ROOT / 'source-scripts/city/landmark-acquisition/index.json'))
        rows, contexts, routes = [], [], []
        for uid in UIDS:
            old = by_uid[uid]; source = forms[uid]; sha = old['sourceSHA256']; path = LOCAL / 'assets' / (sha + '.glb.gz')
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(assets[sha].read_bytes())
            candidate = entry(old['native'], source['building']); candidate['asset'] = 'assets/' + path.name
            row = {**old, 'source': source, 'currentReview': None, 'candidate': {'entry': candidate, 'path': str(path.relative_to(ROOT))}}
            triangles = context.s.glb_triangles(row); lo, hi = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
            neighbours = context.load_forms([lo[0] - 2, lo[2] - 2, hi[0] + 2, hi[2] + 2])
            evidence = {'uid': uid, 'sourceSHA256': sha, 'identity': context.identity_context(row, triangles, neighbours),
                        'neighbourTileHashes': {tile: digest((ROOT / '3d-viewer' / tile).read_bytes()) for _, _, tile in neighbours}}
            route = preflight(row, evidence, index)
            rows.append(row); contexts.append(evidence); routes.append(route)
            print(json.dumps({'uid': uid, 'name': old['name'], 'indexedSheets': [s['sheet'] for s in route['indexedSheets']], 'identityPassed': route['canStartTerrainWork']}), flush=True)
        assert reservations.owns(lease)
        save(DOC / 'check-selection.json.gz', {**macro, 'batch': BATCH, 'rows': rows, 'manifestSHA256': digest(manifest_path.read_bytes()),
                                               'qualification': 'Explicit twenty-three-case input freeze; all cases retained including failed identity preflight. No acceptance or status credit.'})
        save(DOC / 'context.json.gz', {'rows': contexts})
        save(DOC / 'preflight.json', {'rows': routes, 'originalSelectionSHA256': digest((BASE / 'selection.json.gz').read_bytes()),
                                     'modelGeometryChanges': 0, 'scriptExternalAICalls': 0, 'publication': False})
    finally:
        reservations.release(lease)


if __name__ == '__main__': run()
