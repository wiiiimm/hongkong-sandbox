"""Build fresh full-source identity inputs from a fenced original revision receipt.

No old native cache is relabelled, and identity never grants installation credit.
"""
import argparse, importlib.util, json, subprocess, sys, uuid
from pathlib import Path
from revision_sheet_identity import source_sheet
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row
from government_georef_cell_identity import verify_files
sys.path.insert(0, str(HERE.parent / 'enhancement-screening'))
from shape_prepare import entry


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result); return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True); p.add_argument('--batch', required=True)
    p.add_argument('--owned', action='store_true'); a = p.parse_args()
    assert a.batch.startswith('government-xl-') and Path(a.batch).name == a.batch
    doc = ROOT / 'docs/astra-city/government-import' / a.batch
    local = HERE / 'local' / a.batch; lease = local / 'reservation.json'
    source = (ROOT / a.source).resolve(); assert source.parent == doc.parent
    acquired = read(source / 'result.json'); uids = acquired['uids']
    assert acquired['acquired'] == len(uids) and not acquired['errors'] and not acquired['publication']
    if not a.owned:
        assert not doc.exists(), 'Fresh identity inputs required'
        claim = reservations.claim('codex-xl-revision-identity-' + str(uuid.uuid4()),
            ['building:' + u for u in uids], batch=a.batch); assert claim['ok'], claim
        save(lease, json.loads(json.dumps(claim['reservation'], default=str)))
        subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'),
            'run', '--lease-file', str(lease), '--', sys.executable, __file__,
            *sys.argv[1:], '--owned'], cwd=ROOT, check=True); return
    receipt = read(lease); assert reservations.owns(receipt)
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                           (acquired['jobId'],)).fetchone() == ('complete', acquired)
        assert not con.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=ANY(%s)', (uids,)).fetchall()
    for ref in acquired['evidenceRefs']: assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    decoder = module('revision_original_decoder', 'xl-second-pass.py'); decoder.LOCAL = local
    final = module('revision_full_identity', 'xl-final-script-pass.py')
    rows = []; contexts = []; decisions = []
    source_ref = {'path': str((source / 'result.json').relative_to(ROOT)),
                  'sha256': digest((source / 'result.json').read_bytes()), 'jobId': acquired['jobId']}
    for original in acquired['rows']:
        model = original['model']; uid = original['uid']; sha = original['sourceSHA256']
        raw = (ROOT / original['assetPath']).read_bytes(); assert digest(raw) == sha
        dest = local / 'assets' / (sha + '.glb.gz'); dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(raw)
        assert digest((ROOT / '3d-viewer' / original['source']['tile']).read_bytes()) == original['source']['tileSHA256']
        # Fresh receipt type deliberately has no legacy cacheKey/resultSha.
        native = {'sheet': source_sheet(model, read(source / 'revisions.json')),
                  'model': model, 'revisionAcquisition': source_ref}
        row = {'uid': uid, 'name': original['source']['building']['name'], 'modelId': original['modelId'],
            'sourceSHA256': sha, 'triangles': model['triangles'], 'source': original['source'],
            'native': native, 'currentReview': None,
            'candidate': {'path': str(dest.relative_to(ROOT)), 'entry': entry(native, original['source']['building'])}}
        triangles = decoder.glb_triangles(row); low = triangles.min(axis=(0, 1)); high = triangles.max(axis=(0, 1))
        forms = final.load_forms([low[0]-2, low[2]-2, high[0]+2, high[2]+2])
        context = {'uid': uid, 'sourceSHA256': sha,
                   'identity': final.identity_context(row, triangles, forms),
                   'neighbourTileHashes': {tile: digest((ROOT / '3d-viewer' / tile).read_bytes()) for _, _, tile in forms}}
        positive = verify_files(row, context, local / ('identity-' + uid.split('/')[1].replace(':', '-')))
        rows.append(row); contexts.append(context); decisions.append(positive)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    save(doc / 'check-selection.json.gz', {'batch': a.batch, 'rows': rows,
         'manifestSHA256': digest(manifest.read_bytes()), 'sourceRevisionReceipt': source_ref})
    save(doc / 'context.json.gz', {'rows': contexts})
    save(doc / 'identity.json', {'rows': decisions, 'publication': False})
    paths = [source / 'result.json', Path(__file__), doc / 'check-selection.json.gz',
             doc / 'context.json.gz', doc / 'identity.json', HERE / 'government_georef_cell_identity.py',
             HERE / 'original_source_ownership.py', HERE / 'xl-second-pass.py', HERE / 'xl-final-script-pass.py']
    refs = [{'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())} for path in paths]
    payload = {'uids': uids, 'evidenceRefs': refs}; stage = 'explicit-current-government-revision-full-identity-v1'
    jid = jobs.enqueue(a.batch, stage, payload); job = jobs.claim(a.batch, receipt['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jid
    result = {**payload, 'batch': a.batch, 'jobId': jid,
        'rows': [{'uid': d['uid'], 'sourceSHA256': d['sourceSHA256'], 'passed': d['passed'], 'reasons': d['reasons']} for d in decisions],
        'identityPassed': sum(d['passed'] for d in decisions), 'publication': False,
        'newlyInstalled': 0, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
        'requiresAI': False, 'requiresHumanDecision': False,
        'qualification': 'Fresh whole original government geometry, full geographic cell and current footprint identity only. Full physical/browser/publication remains pending; old native run unchanged.'}
    with connect() as con:
        con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,)); con.row_factory = dict_row
        assert reservations._current(con, receipt)
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY'); assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
    save(doc / 'result.json', result); save(doc / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
    print(json.dumps({'identityPassed': result['identityPassed'], 'rows': result['rows'], 'jobId': jid, 'newlyInstalled': 0}), flush=True)


if __name__ == '__main__': main()
