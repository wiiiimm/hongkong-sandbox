"""Measure complete original scope against exact current component groups.

A non-geometry source review, not an acceptance or publication route. Retains
individual failures and measures full same-parent groups without changing limits.
"""
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, connect, reservations, jobs, Jsonb, dict_row, NATIVE_RUN
from government_georef_cell_identity import geographic_cell

BATCH = 'government-xl-six-source-identity-review-20261008'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
CAPTURE = ROOT / 'docs/astra-city/government-import/government-xl-six-original-footprint-previews-20261008'
LOCAL = HERE / 'local' / BATCH
FINDINGS = {
 'landsd/138091:0': 'Complete long market hall with repeated curved roof sections; yellow target is the small corner component. Large blue same-parent hall outline follows the main structure.',
 'landsd/113733:0': 'Complete market hall with central elevated block; yellow target covers that block only. Blue same-parent open-sided structure covers the surrounding hall.',
 'landsd/75642:0': 'Complete L-shaped pier with long covered walkway and wider terminal deck. Yellow target covers a short roof segment only; no full pier footprint is present in the captured building forms.',
 'landsd/75643:0': 'Complete elongated open pier deck with lamps, supports and small shelters. Yellow target covers one small shelter; the deck extends far beyond both captured building forms.',
 'landsd/43101:0': 'Two tall structural frames with bridges and long members. Yellow target covers only part of one frame. The capture alone cannot establish full source identity or component ownership.',
 'landsd/99482:0': 'Lookout tower with broad surrounding platform and long elevated approach ramp. Yellow target describes part of the tower; the ramp and platform extend beyond that footprint.',
}


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def main():
    assert not (DOC / 'result.json').exists(), 'Completed evidence is immutable'
    lease = read(Path('/tmp/astra-six-source-review-20261008.json'))
    assert reservations.owns(lease)
    capture = read(CAPTURE / 'result.json'); frozen = read(CAPTURE / 'inputs.json')
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (capture['jobId'],)).fetchone() == ('complete', capture)
    refs = [ref(CAPTURE / 'result.json'), ref(Path(__file__))]
    for item in capture['evidenceRefs']:
        assert ref(ROOT / item['path']) == item
        refs.append(item)
    for path, sha in frozen['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
        refs.append({'path': path, 'sha256': sha})
    selection = read(ROOT / 'docs/astra-city/government-import/government-xl-held-component-recovery-20261008/physical-selection.json.gz')
    selected = {r['uid']: r for r in selection['rows']}
    spec = importlib.util.spec_from_file_location('six_scope_original_decoder', HERE / 'xl-second-pass.py')
    decoder = importlib.util.module_from_spec(spec); spec.loader.exec_module(decoder); decoder.LOCAL = LOCAL
    outcomes = []
    for model in frozen['models']:
        row = selected[model['uid']]; uid = row['uid']
        assert model['sourceSHA256'] == row['sourceSHA256']
        raw = (ROOT / model['assetPath']).read_bytes(); assert digest(raw) == model['sourceSHA256']
        path = LOCAL / 'assets' / (model['sourceSHA256'] + '.glb.gz'); path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, model['nativeCacheKey'])).fetchone() == (model['nativeResultSHA256'],)
        tri = decoder.glb_triangles(row); projection = shapely.union_all(shapely.polygons(tri[:, :, [0, 2]]))
        target = next(b for b in model['forms'] if b['uid'] == uid)
        group = [b for b in model['forms'] if b['uid'] == uid or (target.get('parent') and b.get('parent') == target['parent'])]
        shape = shapely.union_all([Polygon(b['rings'][0], b['rings'][1:]) for b in group])
        others = shapely.union_all([Polygon(b['rings'][0], b['rings'][1:]) for b in model['forms'] if b['uid'] not in {g['uid'] for g in group}])
        cell = geographic_cell(row['modelId'], target['buildingCSUID'], target['structureType'])
        measures = {'sourceProjectionAreaM2': float(projection.area), 'groupAreaM2': float(shape.area),
            'targetCoveredBySourceProjection': float(shape.intersection(projection).area / shape.area),
            'sourceExcessMaximumDistanceFromTargetM': float(shapely.distance(shapely.points(tri[:, :, [0, 2]].reshape(-1, 2)), shape).max()),
            'sourceExcessCoveredByUnrelatedFormsM2': float(projection.difference(shape).intersection(others).area),
            'targetCoversWholeGeoRefCell': shape.covers(cell), 'sourceProjectionCoversWholeGeoRefCell': projection.covers(cell)}
        reasons = []
        for key, low, high in [('targetCoveredBySourceProjection', .95, 1.000000001), ('sourceExcessMaximumDistanceFromTargetM', 0, 10), ('sourceExcessCoveredByUnrelatedFormsM2', 0, 1)]:
            if not low <= measures[key] <= high: reasons.append('whole-source-group-spatial-bound:' + key)
        if not measures['targetCoversWholeGeoRefCell']: reasons.append('group-does-not-cover-whole-georef-cell')
        if not measures['sourceProjectionCoversWholeGeoRefCell']: reasons.append('source-does-not-cover-whole-georef-cell')
        outcomes.append({'uid': uid, 'modelId': row['modelId'], 'sourceSHA256': row['sourceSHA256'],
            'finding': FINDINGS[uid], 'captureInspected': ref(CAPTURE / (uid.split('/')[1].replace(':', '-') + '.png')),
            'groupForms': group, 'measures': measures, 'remainingReasons': reasons,
            'candidateForOfficialGroupVerification': len(group) > 1 and not reasons,
            'identityAccepted': False, 'installationApproved': False,
            'nextAction': 'Verify exact official complete same-building group, then run a dedicated identity and full physical route.' if len(group) > 1 and not reasons else 'Retain fallback. Obtain authoritative whole-structure boundaries/component ownership before any complete-source route; do not crop, move or remodel the original.',
            'reviewType': 'AI source/component interpretation of prepared original captures plus local full-mesh measurements',
            'geometryEdits': 0})
        assert reservations.heartbeat(lease, ttl=1800)
        print(json.dumps({'uid': uid, 'groupUids': [b['uid'] for b in group], 'measures': measures, 'remainingReasons': reasons}), flush=True)
    save(DOC / 'review.json', {'rows': outcomes, 'authorization': 'keep working and do not stop. install / fix and install all the models you can. if some are truely blocked, note it in neon and flag the reason; do not stop for anything',
        'executor': 'Current Codex coordinator; model/effort and attributable token total not exposed by this evidence recorder',
        'reviewScope': 'Original source identity/component analysis only; no geometry generation, edits, acceptance or tolerance waivers.'})
    refs.append(ref(DOC / 'review.json')); refs = list({r['path']: r for r in refs}.values())
    stage = 'bounded-original-source-component-scope-review-v1'
    payload = {'captureJobId': capture['jobId'], 'uids': sorted(FINDINGS), 'evidenceRefs': refs}
    jid = jobs.enqueue(BATCH, stage, payload); job = jobs.claim(BATCH, lease['owner'], [stage], lease_seconds=1800); assert job and job['id'] == jid
    result = {**payload, 'batch': BATCH, 'jobId': jid, 'rows': outcomes,
        'newlyInstalled': 0, 'publication': False, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0,
        'sourceReviewUsedAI': True, 'installationApproved': False,
        'candidateUids': [r['uid'] for r in outcomes if r['candidateForOfficialGroupVerification']],
        'qualification': 'Review complete, not acceptance. Full original bytes and pose measured against current complete same-parent forms. Original singleton loader failures remain. Candidate groups need official ownership verification, fresh dedicated identity, physical, runtime and browser checks before publication.'}
    try:
        with connect() as con:
            con.row_factory = dict_row
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,)); assert reservations._current(con, lease)
            for item in refs: assert ref(ROOT / item['path']) == item
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
        save(DOC / 'result.json', result); save(DOC / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
        print(json.dumps({'jobId': jid, 'candidateUids': result['candidateUids'], 'neonVerified': True}), flush=True)
    except Exception:
        jobs.finish(jid, job['owner'], job['token'], error='Bounded source review recording failed; retain local evidence and inspect failure before retry.')
        raise


if __name__ == '__main__':
    main()
