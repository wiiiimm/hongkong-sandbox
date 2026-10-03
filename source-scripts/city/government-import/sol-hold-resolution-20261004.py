"""Fresh fenced continuation; never overwrite the completed 3 October checkpoint."""
import json
import shutil
import sys
import uuid
from run import ROOT, HERE, read, save, digest, reservations, jobs
import importlib.util

spec = importlib.util.spec_from_file_location('previous_continuation', HERE / 'sol-continuation-20261003.py')
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
PREVIOUS = c.DOC
BATCH = 'sol-hold-resolution-20261004'
c.DOC = c.BASE / BATCH
c.LOCAL = HERE / 'local' / BATCH
c.LEASE = c.LOCAL / 'reservation.json'
UIDS = ['landsd/91827:0', 'landsd/104302:0', 'landsd/134332:0', 'landsd/273839:0']


def start():
    assert not (c.DOC / 'checkpoint.json').exists(), 'Use the existing attempt, not a new start.'
    claim = reservations.claim('codex-hold-resolution-' + str(uuid.uuid4()),
        ['building:' + u for u in UIDS + ['landsd/305615:0', 'landsd/175935:0']], batch=BATCH)
    assert claim['ok'], claim
    receipt = json.loads(json.dumps(claim['reservation'], default=str)); save(c.LEASE, receipt)
    payload = {'priorResult': c.ref(PREVIOUS / 'result.json'), 'uids': UIDS,
        'viewerManifest': c.ref(ROOT / '3d-viewer/city/data/manifest.json'),
        'scope': 'Installed terrain preservation and exact source contact investigation; no geometry edits.'}
    stage = 'source-interface-compute-v1'
    jid = jobs.enqueue(BATCH, stage, payload)
    job = jobs.claim(BATCH, receipt['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jid
    save(c.LOCAL / 'job.json', json.loads(json.dumps(job, default=str)))
    save(c.DOC / 'checkpoint.json', {**payload, 'batch': BATCH, 'jobId': jid,
        'humanStatus': 'in-process', 'scriptExternalAICalls': 0})
    # Only copy immutable input reports; derived output belongs to this new attempt.
    save(c.DOC / 'citywalk-terrain-options.json', read(PREVIOUS / 'citywalk-terrain-options.json'))
    print({'jobId': jid, 'inProcess': len(UIDS)}, flush=True)


def citywalk():
    c.citywalk_checks()
    try:
        c.citywalk_protect()
    except AssertionError as error:
        save(c.DOC / 'initial-preservation-error.json', {'fringeM': .01, 'failedGuard': str(error)})
        raise


def protect():
    c.owns()
    mask = c.module('hold_resolution_mask', 'xl-shared-neighbour-mask-eval.py')
    doc = c.DOC / 'citywalk'
    result = read(doc / 'result.json')
    native = read(doc / 'native-neighbour-checks.json')
    blocked = sorted({u for r in read(doc / 'neighbour-checks.json')['patches']
                      for u in r['blockedBy']} - set(native['resolved']))
    variants = read(c.DOC / 'preservation-attempts.json') if (c.DOC / 'preservation-attempts.json').exists() else []
    for fringe in (.01,):
        c.owns()
        mask.LOCAL = c.LOCAL / ('citywalk-preserve-' + str(fringe))
        mask.SOURCE = mask.LOCAL / 'input.json'
        save(mask.SOURCE, {'rows': [{'uid': 'landsd/134332:0', 'site': 'citywalk',
            'candidatePatch': {'path': result['patchPath'], 'sha256': result['patchSHA256']},
            'sharedFootprintUids': [{'uid': u} for u in blocked]}]})
        # Copy the input context: the evaluator writes audited evidence beside it.
        context = c.DOC / ('citywalk-preserve-' + str(fringe))
        shutil.copytree(doc, context, dirs_exist_ok=True)
        mask.DIAGNOSTIC_DIRS = {'citywalk': context}
        mask.SOURCE_ASSET_DIRS = {'citywalk': c.LOCAL / 'citywalk-checks/candidates'}
        mask.OUTPUT = c.DOC / ('citywalk-preserve-' + str(fringe) + '.json')
        mask.BOUNDARY_FRINGE = fringe
        try:
            mask.run()
        except AssertionError as error:
            variants.append({'fringeM': fringe, 'failedGuard': str(error)})
            save(c.DOC / 'preservation-attempts.json', variants)
            print(variants[-1], flush=True)
            continue
        row = read(mask.OUTPUT)['rows'][0]
        folder = mask.LOCAL / 'citywalk'
        foundation = c.module('hold_foundation', 'xl-phase-one-foundation.py')
        foundation.UID = 'landsd/134332:0'; foundation.LOCAL = c.LOCAL / 'citywalk-checks'
        foundation.DOC = folder; foundation.SELECTION = doc / 'selection.json.gz'
        foundation.OUTPUT = context / 'foundation.json'
        save(folder / 'result.json', {**result, 'patchPath': row['candidatePatch']['path'],
                                      'patchSHA256': row['candidatePatch']['sha256']})
        foundation.run()
        variants.append({'fringeM': fringe, 'result': c.ref(mask.OUTPUT),
                         'foundation': c.ref(foundation.OUTPUT)})
        save(c.DOC / 'preservation-attempts.json', variants)
        break


def sync():
    receipt = c.owns()
    installed = read(c.DOC / 'ocean-pride/installed-acceptance.json')
    assert installed['publication'] and installed['uids'] == ['landsd/273839:0']
    rows = read(PREVIOUS / 'result.json')['rows']
    contacts = {r['uid']: r for r in read(c.DOC / 'contact-faces.json.gz')['rows']}
    for row in rows:
        if row['uid'] == 'landsd/273839:0':
            row.update(humanStatus='installed', detailedHold=None, installed=True,
                installationApproved=True, nextActionType=None, nextWork=None,
                observation='Installed unchanged original source after full current terrain foundation and exact original wall/podium interface proof: 74 strict rim contacts plus two vertical wall intersections. Existing podium 175935 is a required native loading/visibility dependency. Desktop/mobile day/night, picking, collision, fallback/retry and staged/live support visibility pass.',
                installedProof=c.ref(c.DOC / 'ocean-pride/installed-acceptance.json'))
        elif row['uid'] == 'landsd/134332:0':
            row.update(detailedHold='terrain-resolved-existing-tower-native-support-conflict',
                observation='Citywalk terrain resolved: exact installed neighbour facets retained, original source TIN restored under 100 failing face projections and only coplanar duplicate terrain clipped. Full 41,277-face drawn-terrain foundation has zero buried faces, clearance -0.491423m, runtime and all 292 neighbour forms pass. Staged desktop/mobile day/night/fallback checks pass for Citywalk and retained Citywalk 2 / Ocean Pride. Publisher prevented installation because five Vision City towers still depend on surveyed Citywalk fallback. Exact original native interface checks leave 294 unresolved rim samples across the five towers, with support above their rims by 0.378–1.378m. No Citywalk model, terrain or dependency metadata published.',
                nextWork='Reuse the passing terrain and browser evidence. Investigate the 294 pinned native support failures against original tower/podium faces and source revision metadata; do not enlarge embedding tolerance or migrate fallback dependencies without complete proof. Repeat current dependency/terrain/browser checks under fresh ownership only after that support conflict resolves.',
                publicationAttempt=c.ref(c.DOC/'citywalk-contact-rescue/publication-attempt.json'))
        elif row['uid'] == 'landsd/104302:0':
            row.update(observation='All 619 failing low-rim points are located on exact original 3D source triangles, including vertical edges. The source wall/podium interface rule resolves none; 605/1,224 original contacts remain. This does not have Ocean Pride\'s embedded-wall explanation.',
                       nextWork='Resolve authoritative support/interface coverage for the source-connected upper assembly; missing intersections and high gaps remain explicit. Do not apply the embedded-wall rule to unsupported spans.')
        if row['uid'] in contacts:
            row['interfaceDiagnostic'] = {'passed': contacts[row['uid']]['interfaceProof']['passed'],
                'strictContacts': contacts[row['uid']]['interfaceProof']['strictContacts'],
                'wallIntersections': contacts[row['uid']]['interfaceProof']['wallIntersections'],
                'evidence': c.ref(c.DOC / 'contact-faces.json.gz')}
    paths = [p for p in c.DOC.rglob('*') if p.is_file() and p.name not in
             ('result.json','neon-sync.json','ledger-sync.json','failed-publication-ledger-sync.json','checkpoint.json','README.md')]
    paths += [HERE / n for n in ('sol-hold-resolution-20261004.py','ocean-pride-source-interface-20261004.py',
        'sol-contact-faces-20261004.mjs','rendered_patch_sampler.py','support-interface.mjs',
        'support-contact.mjs','acceptance-metrics.mjs','xl-shared-neighbour-mask-eval.py',
        'check-native-neighbours.mjs','citywalk-local-contact-rescue-20261004.py',
        'citywalk-source-install-20261004.py','citywalk-tower-dependencies-20261004.mjs')]
    report = {'batch':BATCH,'priorResult':c.ref(PREVIOUS/'result.json'),'rows':rows,
        'counts':{'inspected':4,'newlyInstalled':1,'installedInPilot':1,'heldUnknown':9,'heldAI':0,'heldHuman':0,'inProcess':0},
        'remainingXLBatch':{'sourceForms':352,'installed':39,'held':313},
        'evidenceRefs':[c.ref(p) for p in sorted(set(paths))],
        'scriptExternalAICalls':0,'aiGeometryGeneration':False,'modelGeometryChanges':0,
        'viewerManifest':c.ref(ROOT/'3d-viewer/city/data/manifest.json'),
        'executor':'Codex root; AI used for code/non-modelling work only',
        'qualification':'Four priority forms investigated; six other pilot holds inherit their unchanged prior checkpoint. One source form installed, not whole-landmark completion. Citywalk source/terrain browser checks passed but its installed tower dependency migration remains blocked. Derived acquisition/diagnostic caches remain local-only; installed/staged assets and exact evidence are portable in Git.'}
    save(c.DOC/'result.json',report)
    snapshot = read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')['snapshotId']
    with c.connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        sources=dict(con.execute('SELECT uid,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(snapshot,UIDS)).fetchall())
    by_uid={r['uid']:r for r in rows}
    assert all(by_uid[u]['sourceSHA256']==sha for u,sha in sources.items())
    held=[u for u in sources if not by_uid[u]['installed']]
    if held:
        ledger=c.module('hold_resolution_ledger','../model-review-ledger/ledger.py')
        effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable',
            'job_id':read(c.LOCAL/'job.json')['id'],'issue':'HKS-203','output_ref':str((c.DOC/'result.json').relative_to(ROOT))}
        recorded=ledger.record_many(snapshot,c.LEASE,[(u,'held',c.DOC/'result.json',by_uid[u]['observation'],None) for u in held],
            effort=effort,request_id=BATCH+'-held-'+snapshot+'-'+digest((c.DOC/'result.json').read_bytes())[:16])
        save(c.DOC/'ledger-sync.json',{'snapshotId':snapshot,'heldRows':recorded})
    attempt=read(c.DOC/'citywalk-contact-rescue/publication-attempt.json')
    if attempt.get('snapshotId') and attempt['snapshotId']!=snapshot:
        ledger=c.module('failed_attempt_ledger','../model-review-ledger/ledger.py')
        effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable',
            'job_id':read(c.LOCAL/'job.json')['id'],'issue':'HKS-203','output_ref':str((c.DOC/'result.json').relative_to(ROOT))}
        recorded=ledger.record_many(attempt['snapshotId'],c.LEASE,[('landsd/134332:0','held',c.DOC/'result.json',by_uid['landsd/134332:0']['observation'],None)],effort=effort,request_id=BATCH+'-failed-publication-'+attempt['snapshotId']+'-'+digest((c.DOC/'result.json').read_bytes())[:16])
        save(c.DOC/'failed-publication-ledger-sync.json',{'snapshotId':attempt['snapshotId'],'rows':recorded,'currentPointerUnchanged':True})
    job=read(c.LOCAL/'job.json')
    with c.connect() as con:
        con.row_factory=c.dict_row
        con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
        assert reservations._current(con,receipt)
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(c.Jsonb(report),job['id'],job['owner'],job['token'])).rowcount==1
    with c.connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(job['id'],)).fetchone()[0]==report
    save(c.DOC/'neon-sync.json',{'jobId':job['id'],'resultVerified':True,'result':c.ref(c.DOC/'result.json')})
    assert reservations.release(receipt)['ok']
    checkpoint=read(c.DOC/'checkpoint.json');checkpoint.update(humanStatus='complete',result=c.ref(c.DOC/'result.json'),neonSync=c.ref(c.DOC/'neon-sync.json'),inProcess=0)
    save(c.DOC/'checkpoint.json',checkpoint)
    print({'newlyInstalled':1,'pilotHeld':9,'xlInstalled':39,'xlHeld':313,'inProcess':0},flush=True)


if __name__ == '__main__':
    {'start': start, 'citywalk': citywalk, 'protect': protect, 'sync': sync}[sys.argv[1]]()
