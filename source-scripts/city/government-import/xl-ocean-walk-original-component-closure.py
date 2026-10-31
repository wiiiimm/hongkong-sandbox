"""Trace Ocean Walk original components using its verified retained geographic scope. No acceptance."""
import importlib.util
import json
import subprocess
import sys
import uuid
import zipfile
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row, NATIVE_RUN
from installed_source_identity import installed_identity
from government_georef_cell_identity import geographic_cell
sys.path.insert(0, str(HERE.parent / 'enhancement-screening'))
from shape_prepare import canonical_bytes, entry, scan, acquire, _convert_one

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--batch', required=True)
parser.add_argument('--base', required=True)
parser.add_argument('--pair', action='append', required=True, help='Exact tower UID=original support UID; explicit diagnostic scope only')
parser.add_argument('--owned', action='store_true', help=argparse.SUPPRESS)
args = parser.parse_args()
assert args.batch.startswith('government-xl-') and Path(args.batch).name == args.batch
BATCH = args.batch
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH
BASE = ROOT / args.base
PAIRS = [tuple(pair.split('=')) for pair in args.pair]
assert all(len(pair) == 2 and all(uid.startswith('landsd/') and uid.endswith(':0') for uid in pair) for pair in PAIRS)
assert len(PAIRS) == len(set(PAIRS))



def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


def start():
    assert not DOC.exists(), 'Fresh exact-source closure only; completed evidence is immutable'
    scope = sorted({u for pair in PAIRS for u in pair})
    claim = reservations.claim('codex-xl-source-closure-' + str(uuid.uuid4()),
                               ['building:' + u for u in scope], batch=BATCH)
    assert claim['ok'], claim
    save(LOCAL / 'reservation.json', json.loads(json.dumps(claim['reservation'], default=str)))
    subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'), 'run',
                    '--lease-file', str(LOCAL / 'reservation.json'), '--', sys.executable,
                    __file__, *sys.argv[1:], '--owned'], cwd=ROOT, check=True)


def typed_match(model, form):
    try:
        geographic_cell(model['modelId'], form['buildingCSUID'], form['structureType'])
        return True
    except (ValueError, KeyError):
        return False


def diagnostic_entry(outcome, form):
    model = outcome['model']
    exact = [v for v in model['matching']['officialCandidates']
             if v['objectId'] == form['objectId'] and v['buildingCSUID'] == form['buildingCSUID']]
    assert len(exact) == 1 and typed_match(model, form)
    official = exact[0]
    # Exact component routing creates diagnostic metadata only. Keep every raw
    # ambiguous cached match and retain all identity/physical/publication gates.
    candidate = {**model['asset'], 'uid': form['uid'], 'objectId': form['objectId'],
        'buildingCSUID': form['buildingCSUID'], 'label': form.get('name') or model['modelId'],
        'modelId': model['modelId'], 'triangles': model['triangles'], 'worldBounds': model['worldBounds'],
        'sourceTile': outcome['sheet'], 'rootTranslation': [-834500, 0, 816500], 'priority': 'unreviewed',
        'recordedBaseHeight': form['baseHeightHKPD'], 'recordedTopHeight': form['topHeightHKPD'],
        'overlapOfSmallerFootprint': official['overlapOfSmallerFootprint'],
        'footprintCentroidDistanceMetres': official['footprintCentroidDistanceMetres'],
        'sourceIdentityReviewed': False, 'placementReviewed': False, 'publicationApproved': False}
    return candidate, 'exact-type-georef-object-csuid-diagnostic-only'


def owned():
    lease = read(LOCAL / 'reservation.json'); assert reservations.owns(lease)
    selected = {r['uid']: r for r in read(BASE / 'check-selection.json.gz')['rows']}
    rows = {u: selected[u] for u, _ in PAIRS}
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = read(manifest_path); forms = {}
    wanted = {u for pair in PAIRS for u in pair}
    for tile in manifest['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        for b in read(path)['buildings']:
            if b['uid'] in wanted:
                forms[b['uid']] = {'building': b, 'tile': tile['url'], 'tileSHA256': digest(path.read_bytes())}
    assert set(forms) == wanted
    for tower, support in PAIRS:
        if support in rows: continue
        primary = rows[tower]; key = primary['native']['cacheKey']
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            sha, data = con.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s', (key,)).fetchone()
        assert sha == primary['native']['resultSha']
        form = forms[support]['building']
        models = [m for m in data['models'] if typed_match(m, form)
                  and any(v['objectId'] == form['objectId'] and v['buildingCSUID'] == form['buildingCSUID']
                          for v in m.get('matching', {}).get('officialCandidates', []))]
        sheet = primary['native']['sheet']
        lookup_basis = 'exact-record-in-primary-stage'
        if not models:
            # Components often straddle sheets. Search the pinned inventory by
            # exact GeoRef, then require the same full ObjectID/CSUID match in
            # its immutable native stage; proximity never supplies an identity.
            with connect() as con:
                con.execute('SET TRANSACTION READ ONLY')
                profiles = con.execute('SELECT DISTINCT cache_key,sheet FROM astra_modelling.native_model_sizes '
                    'WHERE run_id=%s AND model_id LIKE %s',
                    (NATIVE_RUN, 'B' + form['buildingCSUID'][:10] + '%')).fetchall()
                outcomes = []
                for cache_key, candidate_sheet in profiles:
                    cached = con.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r '
                        'JOIN astra_modelling.native_stage_members m USING(cache_key) '
                        'WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, cache_key)).fetchone()
                    assert cached, 'Indexed support stage is absent from the pinned native run'
                    candidate_sha, candidate_data = cached
                    for model in candidate_data['models']:
                        if typed_match(model, form) and any(
                            v['objectId'] == form['objectId'] and v['buildingCSUID'] == form['buildingCSUID']
                            for v in model.get('matching', {}).get('officialCandidates', [])):
                            outcomes.append((cache_key, candidate_sha, candidate_sheet, model))
            assert len(outcomes) == 1, ('Missing or ambiguous indexed exact original support', support, len(outcomes))
            key, sha, sheet, model = outcomes[0]
            models = [model]
            lookup_basis = 'exact-object-csuid-georef-in-pinned-cross-sheet-index'
        assert len(models) == 1, ('Ambiguous exact original support record', support)
        native = {'cacheKey': key, 'resultSha': sha, 'sheet': sheet,
                  'uids': [support], 'model': models[0]}
        candidate, basis = diagnostic_entry(native, form)
        assert support == 'landsd/81743:0'
        previous = read(ROOT / 'docs/astra-city/government-import/government-xl-ocean-walk-complete-source-local-20261008/selection.json.gz')['rows'][0]
        assert previous['source'] == forms[support]
        assert candidate['sha256'] == previous['sourceSHA256']
        assert candidate['modelId'] == previous['modelId']
        assert candidate['buildingCSUID'] == previous['candidate']['entry']['buildingCSUID']
        assert candidate['recordedBaseHeight'] == previous['candidate']['entry']['recordedBaseHeight']
        assert candidate['recordedTopHeight'] == previous['candidate']['entry']['recordedTopHeight']
        candidate['footprintScope'] = support
        candidate['suppressesBuildingUids'] = []
        rows[support] = {'uid': support, 'source': forms[support], 'native': native,
                         'modelId': models[0]['modelId'], 'name': form.get('name'),
                         'triangles': models[0]['triangles'],
                         'sourceSHA256': models[0]['asset']['sha256'],
                         'candidate': {'entry': candidate}, 'sourceLookupBasis': basis,
                         'indexedLookupBasis': lookup_basis}
    cache = {}
    missing = {r['sourceSHA256'] for r in rows.values()}
    for folder in [HERE / 'local', ROOT / '3d-viewer/city/data/official-models']:
        for path in folder.rglob('*.glb.gz'):
            sha = path.name.removesuffix('.glb.gz')
            if sha in missing and digest(path.read_bytes()) == sha:
                cache[sha] = path; missing.remove(sha)
            if not missing: break
        if not missing: break
    recoveries = []
    for row in rows.values():
        sha = row['sourceSHA256']; destination = LOCAL / 'assets' / (sha + '.glb.gz')
        destination.parent.mkdir(parents=True, exist_ok=True)
        if sha in cache:
            raw = cache[sha].read_bytes(); method = 'verified-local-original'; transferred = 0
        else:
            sheet = row['native']['sheet']; folder = LOCAL / 'sheets' / sheet
            with connect() as con:
                con.execute('SET TRANSACTION READ ONLY')
                pinned = con.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1", (sheet,)).fetchone()[0]
            directory, _ = scan({'SHEETNO': sheet, 'Format_glTF': pinned['sourceURL'],
                                 'REVISIONDATE': pinned['revision']}, folder / 'directory')
            directory['models'] = [m for m in directory['models'] if m['modelId'] == row['modelId']]
            assert len(directory['models']) == 1
            receipt = acquire(directory, folder / 'directory/zip-directory.bin', folder / 'original')
            packed = folder / 'packed'; packed.mkdir(exist_ok=True)
            with zipfile.ZipFile(folder / 'original' / (sheet + '.zip')) as archive:
                model = row['native']['model']
                converted = _convert_one(archive, archive.getinfo(model['sourceEntry']), folder / 'decoded', packed, {}, {'modelId': row['modelId']})
                raw = canonical_bytes((packed / converted['asset']['asset']).read_bytes(), sha)
            transferred = receipt['newThisInvocationBytes']; method = 'exact-original-government-recovery'
        assert digest(raw) == sha and len(raw) == row['native']['model']['asset']['bytes']
        destination.write_bytes(raw); row['candidate']['path'] = str(destination.relative_to(ROOT))
        row['candidate']['entry']['asset'] = 'assets/' + destination.name
        row['source'] = forms[row['uid']]
        recoveries.append({'uid': row['uid'], 'sourceSHA256': sha, 'method': method,
                           'transferredBytes': transferred, 'sourcePreserved': True})
        print(json.dumps({'recovered': row['uid'], 'method': method, 'transferredBytes': transferred}), flush=True)
        assert reservations.owns(lease)
    ordered = [rows[u] for u in sorted(rows)]
    save(DOC / 'selection.json.gz', {'batch': BATCH, 'rows': ordered, 'manifestSHA256': digest(manifest_path.read_bytes())})
    save(DOC / 'recovery.json', {'rows': recoveries, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0, 'publication': False})
    contexts = []; context = module('closure_exact_context', 'xl-final-script-pass.py'); context.s.LOCAL = LOCAL
    identity = module('closure_identity', 'xl-remaining-direct.py')
    for row in ordered:
        triangles = context.s.glb_triangles(row); lo, hi = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
        neighbours = context.load_forms([lo[0] - 2, lo[2] - 2, hi[0] + 2, hi[2] + 2])
        proof = context.identity_context(row, triangles, neighbours)
        original_matches = row['native']['model']['matching']['viewerMatches']
        reuse=installed_identity(row,manifest)
        contexts.append({'acceptedIdentityReuse':reuse,'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'], 'identity': proof,
                         'boundedProjectionPassed': bool(identity.identity_clear(proof)),
                         'originalUniqueViewerMatch': len(original_matches) == 1 and original_matches[0]['uid'] == row['uid'],
                         'neighbourTileHashes': {tile: digest((ROOT / '3d-viewer' / tile).read_bytes()) for _, _, tile in neighbours}})
    save(DOC / 'context.json.gz', {'rows': contexts})
    save(DOC / 'support-inputs.json', {'sources': ordered, 'pairs': [{'uid': u, 'supportUid': s} for u, s in PAIRS]})
    subprocess.run(['node', str(HERE / 'ocean-walk-original-component-interfaces.mjs'), str(DOC.relative_to(ROOT)) + '/'], cwd=ROOT, check=True)
    interfaces = read(DOC / 'support-checks.json.gz')
    for path, sha in interfaces['inputHashes'].items(): assert digest((ROOT / path).read_bytes()) == sha
    ctx = {r['uid']: r for r in contexts}; outcomes = []
    for pair in interfaces['rows']:
        support = ctx[pair['supportUid']]; tower = ctx[pair['uid']]
        reasons = []
        interface = pair['interface']
        if interface is None:
            assert pair['loadFailure']['reason'] == 'runtime-source-footprint-fit'
            reasons.append('runtime-source-footprint-fit:' + pair['loadFailure']['uid'])
        elif not interface['passed']: reasons.append('original-support-interface-unresolved')
        if not support['originalUniqueViewerMatch'] and not support['acceptedIdentityReuse']: reasons.append('support-original-viewer-match-held')
        if not support['boundedProjectionPassed'] and not support['acceptedIdentityReuse']: reasons.append('support-bounded-source-projection-held')
        if (not tower['originalUniqueViewerMatch'] or not tower['boundedProjectionPassed']) and not tower['acceptedIdentityReuse']: reasons.append('tower-source-identity-held')
        reasons.append('support-terrain-foundation-runtime-publication-not-complete')
        outcomes.append({**{k: pair[k] for k in ('uid', 'supportUid', 'sourceSHA256', 'supportSHA256')},
                         'humanStatus': 'held-unknown', 'reasons': reasons,
                         'interfaceChecked': interface is not None, 'loadFailure': pair.get('loadFailure'),
                         'interfacePassed': interface['passed'] if interface else False,
                         'samples': interface['samples'] if interface else None,
                         'unresolvedSamples': len(interface['unresolved']) if interface else None,
                         'nextStep': 'Resolve the recorded exact source identity/support interface, then support terrain, full foundation, neighbours, runtime/browser and publication. No source edits or tolerance increases.',
                         'requiresAI': False, 'requiresHumanDecision': False})
    refs = [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p.read_bytes())}
            for p in sorted(DOC.iterdir()) if p.is_file()]
    refs.extend({'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in (HERE/'accepted_source_identity.py',HERE/'installed_source_identity.py'))
    payload = {'evidenceRefs': refs, 'runnerSHA256': digest(Path(__file__).read_bytes()), 'manifestSHA256': digest(manifest_path.read_bytes())}
    stage = 'ocean-walk-retained-original-component-closure-v1'; jobid = jobs.enqueue(BATCH, stage, payload)
    job = jobs.claim(BATCH, lease['owner'], [stage], lease_seconds=1800); assert job and job['id'] == jobid
    result = {**payload, 'batch': BATCH, 'jobId': jobid, 'rows': outcomes,
              'recoveredOriginalMeshes': len(rows), 'additionalSupportSources': len({support for _, support in PAIRS} - {tower for tower, _ in PAIRS}),
              'interfacesPassed': sum(r['interfacePassed'] for r in outcomes),
              'interfacesChecked': sum(r['interfaceChecked'] for r in outcomes),
              'runtimeRejectedPairs': sum(not r['interfaceChecked'] for r in outcomes), 'newlyInstalled': 0,
              'activeWorkers': 0, 'queuedFollowups': 0, 'modelGeometryChanges': 0,
              'scriptExternalAICalls': 0, 'publication': False,
              'qualification': 'Candidate-held exact identifiers locate a source for diagnostics only. Original viewer matching and bounded projection failures remain held; interface checks cannot waive identity or installation gates.'}
    with connect() as con:
        con.row_factory = dict_row; con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,)); assert reservations._current(con, lease)
        for row in rows.values():
            native = row['native']; actual = con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, native['cacheKey'])).fetchone()
            assert actual and actual['result_sha'] == native['resultSha']
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jobid, job['owner'], job['token'])).rowcount == 1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY'); assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s', (jobid,)).fetchone()[0] == result
    save(DOC / 'result.json', result); save(DOC / 'neon-sync.json', {'jobId': jobid, 'resultVerified': True})
    print(json.dumps({'jobId': jobid, 'neonVerified': True, 'interfacesPassed': result['interfacesPassed'], 'newlyInstalled': 0}), flush=True)


if __name__ == '__main__':
    owned() if args.owned else start()
