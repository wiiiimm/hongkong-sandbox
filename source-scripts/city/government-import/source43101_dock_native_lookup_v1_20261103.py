"""Nominate exact cached government Dock1A components for whole-source checks.

No downloaded bytes, footprint-only identity acceptance or geometry changes.
"""
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect, NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v2_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-source43101-dock-native-lookup-v1-20261103'
SELECT = 'government-xl-source43101-current-selection-v1-20261029'
UIDS = ['landsd/43101:0', 'landsd/316521:0', 'landsd/316522:0']


def owned():
    lease = read(HERE / 'local' / BATCH / 'reservation.json')
    assert reservations.owns(lease)
    _, pins = authenticate(BASE / SELECT)
    p = BASE / SELECT / 'selection.json.gz'
    assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
    selected = read(p)['rows'][0]
    assert selected['uid'] == UIDS[0]
    tile = ROOT / '3d-viewer' / selected['source']['tile']
    forms = {r['uid']: r for r in read(tile)['buildings'] if r['uid'] in UIDS}
    assert set(forms) == set(UIDS)
    assert forms[UIDS[0]] == selected['source']['building']
    with connect() as c:
        c.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        sheet = c.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s', (selected['native']['cacheKey'],)).fetchone()
        assert sheet and sheet[0] == '8-SW-11C'
        rows = c.execute('''SELECT i.sheet,i.cache_key,r.result_sha,model,match
            FROM astra_modelling.native_stage_inputs i
            JOIN astra_modelling.native_stage_results r USING(cache_key)
            JOIN astra_modelling.native_stage_members member USING(cache_key)
            CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') model
            CROSS JOIN LATERAL jsonb_array_elements(COALESCE(model->'matching'->'viewerMatches','[]'::jsonb)) match
            WHERE member.run_id=%s AND i.sheet=%s AND match->>'uid'=ANY(%s)
            ORDER BY i.cache_key,model->>'modelId' ''', (NATIVE_RUN, sheet[0], UIDS)).fetchall()
    grouped = {u: [] for u in UIDS}
    for sheet, cache, sha, model, match in rows:
        uid = match['uid']
        if match.get('buildingCSUID') != forms[uid].get('buildingCSUID'):
            continue
        grouped[uid].append(dict(sheet=sheet, cacheKey=cache, resultSHA256=sha, model=model, viewerMatch=match,
                                 sourceKey=cache + '/' + model['modelId']))
    out = BASE / BATCH
    result = dict(uids=UIDS, sourceSHA256=selected['sourceSHA256'], searchedNativeRun=NATIVE_RUN,
                  searchedSheets=['8-SW-11C'], currentTile=dict(path=str(tile.relative_to(ROOT)), sha256=digest(tile.read_bytes())),
                  rows=[dict(uid=u, currentViewerForm=forms[u], exactCachedNativeMatches=grouped[u]) for u in UIDS],
                  freshProviderHTTPQueried=False, originalSourceAcquisitionPerformed=False,
                  sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False,
                  identityAccepted=False, physicalAcceptance=False, installationApproved=False, publication=False,
                  qualification='Exact current-viewer UID/CSUID match nomination in the authenticated pinned native run and explicit source sheet only. Cached model metadata is not fresh provider identity approval or a downloaded/rendered actor. Missing matches do not establish government-wide absence. Use matching immutable originals to check both43101roots against complete current Dock1A interfaces; do not replace them with footprint proxies.')
    save(out / 'summary.json', result)
    assert reservations.owns(lease) and digest(tile.read_bytes()) == result['currentTile']['sha256']
    module('source43101_dock_lookup_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'exact-cached-current-dock1a-source-nomination', [Path(__file__), BASE / SELECT / 'result.json', p, tile], result)
    print({u: len(grouped[u]) for u in UIDS}, flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not (BASE / BATCH).exists() and not (HERE / 'local' / BATCH).exists()
        claim = reservations.claim('source43101-dock-lookup-' + str(uuid.uuid4()), ['building:' + u for u in UIDS] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], 'Exact source group reservation unavailable'
        execute_reserved(claim['reservation'], HERE / 'local' / BATCH / 'reservation.json', [sys.executable, __file__, '--owned'])
