"""Fresh, fenced held-model continuation with early dependency routing and CPU proof."""
import json
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row
from dependency_preflight import from_catalogues

BATCH = 'workflow-optimisation-20261005'
BASE = ROOT / 'docs/astra-city/government-import/government-xl-remaining-20260923'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
LEASE = LOCAL / 'reservation.json'
PRIOR = BASE / 'sol-hold-resolution-20261004/result.json'


def ref(path):
    return {'path': str(Path(path).relative_to(ROOT)), 'sha256': digest(Path(path).read_bytes())}


def prepare():
    assert not (DOC / 'result.json').exists(), 'Completed evidence exists; reuse it.'
    assert not LEASE.exists(), 'Use the existing owned attempt, not another start.'
    previous = read(PRIOR)
    candidates = [r for r in previous['rows'] if not r['installed']]
    available = {}
    catalogue_refs = []
    def add_catalogue(path):
        path = Path(path)
        catalogue_refs.append(ref(path))
        cat = read(path)
        for model in cat['models']:
            available[model['uid']] = {'entry': {'rootTranslation': cat.get('rootTranslation'), **model},
                                      'path': str((path.parent / model['asset']).relative_to(ROOT))}
    for name in ('government-xl-remaining-20260923', 'government-xl-remaining-held-20260923',
                 'government-xl-source-revision-20260924', 'government-xl-source-http-retry-20260924'):
        path = HERE / 'local' / name / 'recovered/catalogue.json'
        if path.exists():
            add_catalogue(path)
    support_selection = BASE / 'beverly-hill-pair-terrain-diagnostic-20260928/support-selection.json.gz'
    for row in read(support_selection)['rows']:
        available[row['uid']] = {'entry': row['candidate']['entry'],
                                'path': str(Path(row['candidate']['path']).relative_to(ROOT))}
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = read(manifest_path)
    for url in manifest['officialModelCatalogues']:
        add_catalogue(ROOT / '3d-viewer' / url)
    # Prefer the staged exact source, without making it an installed candidate.
    citywalk_stage = HERE / 'accepted/government-xl-citywalk-source-20261004/catalogue.json'
    add_catalogue(citywalk_stage)
    pairs = [{'uid': r['uid'], 'supportUid': r['supportUid']} for r in
             read(BASE / 'sol-continuation-20261003/support-contact.json')['rows']]
    towers = [s['entry']['uid'] for s in available.values() if any(
        isinstance(d, dict) and d['uid'] == 'landsd/134332:0'
        for d in s['entry'].get('supportDependencies', []))]
    assert len(towers) == 5
    pairs += [{'uid': uid, 'supportUid': 'landsd/134332:0', 'inspectUnresolved': True} for uid in sorted(towers)]
    pairs += [{'uid': 'landsd/76364:0', 'supportUid': 'landsd/232025:0'}]
    uids = sorted({r['uid'] for r in candidates} | {p[k] for p in pairs for k in ('uid', 'supportUid')})
    assert set(uids) <= set(available), 'Source missing; no reacquisition authorised by this script.'
    for row in previous['rows']:
        assert available[row['uid']]['entry']['sha256'] == row['sourceSHA256'], 'Source revision changed'
    forms, tile_refs = {}, []
    for tile in manifest['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        found = [b for b in read(path)['buildings'] if b['uid'] in uids]
        if found:
            tile_refs.append(ref(path))
            forms.update({b['uid']: b for b in found})
        if len(forms) == len(uids):
            break
    assert set(forms) == set(uids), 'Current source form missing'
    claim = reservations.claim('codex-workflow-compute-' + str(uuid.uuid4()),
                               ['building:' + u for u in uids], batch=BATCH)
    assert claim['ok'], claim
    receipt = json.loads(json.dumps(claim['reservation'], default=str))
    save(LEASE, receipt)
    # Freeze the previous checker for full-output equivalence, not historical acceptance reuse.
    baseline_commit = '4bf9293b'
    script_path = 'source-scripts/city/government-import/support-interface.mjs'
    raw = subprocess.check_output(['git', 'show', baseline_commit + ':' + script_path], cwd=ROOT).decode()
    baseline = DOC / 'support-interface-baseline.mjs'
    # Relative imports remain portable beside the frozen diagnostic evidence.
    import os
    three = os.path.relpath(ROOT / '3d-viewer/vendor/three.module.js', baseline.parent)
    contact = os.path.relpath(HERE / 'support-contact.mjs', baseline.parent)
    baseline.parent.mkdir(parents=True, exist_ok=True)
    baseline.write_text(raw.replace('../../../3d-viewer/vendor/three.module.js', three)
                       .replace('./support-contact.mjs', contact))
    candidate_catalogue = DOC / 'candidate-catalogue.json'
    save(candidate_catalogue, {'models': [available[r['uid']]['entry'] for r in candidates]})
    preflight = from_catalogues(manifest_path, [candidate_catalogue])
    save(DOC / 'dependency-preflight.json', preflight)
    inputs = {'pairs': pairs, 'sources': {u: {**available[u], 'form': forms[u]} for u in uids},
              'baseline': ref(baseline), 'baselineCommit': baseline_commit,
              'baselineOriginalSHA256': digest(raw.encode()), 'tileRefs': tile_refs,
              'catalogueRefs': catalogue_refs, 'priorResult': ref(PRIOR), 'manifest': ref(manifest_path)}
    save(DOC / 'support-inputs.json', inputs)
    payload = {'uids': uids, 'priorResult': ref(PRIOR), 'inputs': ref(DOC / 'support-inputs.json'),
               'preflight': ref(DOC / 'dependency-preflight.json'),
               'scripts': [ref(HERE / p) for p in ('workflow-optimisation-20261005.py',
                   'workflow-support-check.mjs', 'triangle-point-index.mjs', 'support-interface.mjs',
                   'support-contact.mjs', 'dependency_preflight.py')]}
    stage = 'held-workflow-compute-v1'
    jid = jobs.enqueue(BATCH, stage, payload)
    job = jobs.claim(BATCH, receipt['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jid
    save(LOCAL / 'job.json', json.loads(json.dumps(job, default=str)))
    save(DOC / 'checkpoint.json', {'batch': BATCH, 'jobId': jid, 'humanStatus': 'in-process',
                                  'selectedHeld': len(candidates), 'resources': uids})
    return subprocess.call([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'),
        'run', '--lease-file', str(LEASE), '--', sys.executable, str(Path(__file__)), 'execute'], cwd=ROOT)


def execute():
    receipt, job = read(LEASE), read(LOCAL / 'job.json')
    assert reservations.owns(receipt) and jobs.heartbeat(job, lease_seconds=1800)
    try:
        payload = job['payload']
        for evidence in [payload['priorResult'], payload['inputs'], payload['preflight'], *payload['scripts']]:
            assert digest((ROOT / evidence['path']).read_bytes()) == evidence['sha256']
        inputs = read(DOC / 'support-inputs.json')
        for evidence in [inputs['manifest'], *inputs['tileRefs'], *inputs['catalogueRefs']]:
            assert digest((ROOT / evidence['path']).read_bytes()) == evidence['sha256']
        subprocess.run(['node', str(HERE / 'workflow-support-check.mjs'),
                        str(DOC / 'support-inputs.json'), str(DOC / 'support-checks.json')], cwd=ROOT, check=True)
        checks = read(DOC / 'support-checks.json')
        assert all(r['completeEvidenceEqual'] for r in checks['rows'])
        rows = read(PRIOR)['rows']
        by_uid = {r['uid']: r for r in checks['rows']}
        routed = {r['uid']: r for r in read(DOC / 'dependency-preflight.json')['rows']}
        for row in rows:
            if row['installed']:
                continue
            row['earlyDependencyPreflight'] = routed[row['uid']]
            if row['uid'] in by_uid:
                p = by_uid[row['uid']]['proof']
                row['freshSupportCheck'] = {'samples': p['samples'], 'strictContacts': p['strictContacts'],
                    'wallIntersections': p['wallIntersections'], 'unresolved': len(p['unresolved']),
                    'passed': p['passed'], 'completeBaselineEvidenceEqual': True,
                    'evidence': ref(DOC / 'support-checks.json')}
            row['workflowContinuation'] = 'Current source dependency metadata inspected; original support geometry checked where an exact pair exists. Prior terrain holds retained; no acceptance or geometry edits.'
        report = {'batch': BATCH, 'rows': rows, 'counts': {'installedInPilot': 1, 'heldUnknown': 9,
            'newlyInstalled': 0, 'heldAI': 0, 'heldHuman': 0, 'inProcess': 0},
            'remainingXLBatch': read(PRIOR)['remainingXLBatch'], 'priorResult': ref(PRIOR),
            'evidenceRefs': [ref(p) for p in sorted(DOC.glob('*')) if p.is_file() and p.name != 'checkpoint.json']
                + payload['scripts'], 'executor': 'Codex root; AI-assisted workflow/code development, no per-building AI modelling or architectural review',
            'scriptExternalAICalls': 0, 'modelGeometryChanges': 0, 'publication': False,
            'qualification': 'Nine held pilot sources routed; eleven exact source/support pairs tested, including installed controls. Full acceptance outputs remain identical. Workflow optimisation is not a new installation, source revision resolution, whole-landmark completion or physical-phone speedup.'}
        # Source and job ownership are fenced in the same completion transaction.
        with connect() as con:
            con.row_factory = dict_row
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            assert reservations._current(con, receipt)
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",
                               (Jsonb(report), job['id'], job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s', (job['id'],)).fetchone()[0] == report
        save(DOC / 'result.json', report)
        save(DOC / 'neon-sync.json', {'jobId': job['id'], 'exactResultMatch': True, 'sourceReservationFenced': True,
                                     'reviewStatesUnchanged': True, 'result': ref(DOC / 'result.json')})
        checkpoint = read(DOC / 'checkpoint.json')
        checkpoint.update(humanStatus='complete', inProcess=0, result=ref(DOC / 'result.json'))
        save(DOC / 'checkpoint.json', checkpoint)
        print(json.dumps(report['counts']), flush=True)
    except BaseException as error:
        jobs.finish(job, error=type(error).__name__ + ': ' + str(error), retry=False)
        raise


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'execute':
        execute()
    else:
        sys.exit(prepare())
