"""Search every pinned native stage for the unresolved exact component identity."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, NATIVE_RUN
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
SRC = BASE / 'government-xl-china-ferry-neighbour-sources-v1-20261020'
BATCH = 'government-xl-china-ferry-81118-global-source-search-v1-20261020'
DOC = BASE / BATCH
assert not DOC.exists()
receipt = read(SRC / 'result.json')
assert receipt['missing'] == ['landsd/81118:0']
with connect() as db:
    db.execute('SET TRANSACTION READ ONLY')
    assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                      (receipt['jobId'],)).fetchone() == ('complete', receipt)
    count = db.execute(
        'SELECT count(DISTINCT cache_key) FROM astra_modelling.native_stage_members WHERE run_id=%s',
        (NATIVE_RUN,)).fetchone()[0]
    matches = db.execute("""
        SELECT DISTINCT r.cache_key,r.result_sha,i.sheet,r.result
        FROM astra_modelling.native_stage_results r
        JOIN astra_modelling.native_stage_inputs i USING(cache_key)
        JOIN astra_modelling.native_stage_members m USING(cache_key)
        WHERE m.run_id=%s AND EXISTS (
          SELECT 1 FROM jsonb_array_elements(r.result->'models') model
          WHERE model->>'modelId' LIKE %s OR EXISTS (
            SELECT 1 FROM jsonb_array_elements(
              COALESCE(model->'matching'->'officialCandidates','[]'::jsonb)) candidate
            WHERE candidate->>'objectId'=%s OR candidate->>'buildingCSUID'=%s))
        ORDER BY r.cache_key
    """, (NATIVE_RUN, 'B3532217937%', '81118', '3532217937T20071228')).fetchall()
rows = []
for key, sha, sheet, result in matches:
    save(DOC / ('registry-' + key + '.json.gz'),
         dict(cacheKey=key, resultSHA256=sha, sheet=sheet, result=result))
    for model in result['models']:
        candidates = model.get('matching', {}).get('officialCandidates', [])
        exact = [c for c in candidates if c.get('objectId') == 81118
                 or c.get('buildingCSUID') == '3532217937T20071228']
        if exact or model['modelId'].startswith('B3532217937'):
            rows.append(dict(nativeStageKey=key, nativeStageSHA256=sha,
                             sheet=sheet, model=model, exactCandidates=exact))
summary = dict(
    uids=['landsd/81118:0'], nativeRun=NATIVE_RUN, nativeStageMembers=count,
    matches=len(rows), installationApproved=False, permanentRejection=False,
    qualification='Exact object ID, exact CSUID or encoded source-coordinate prefix across the pinned native run; absence does not prove provider unavailability.')
save(DOC / 'nominations.json', dict(rows=rows, **summary))
module('china_missing_freeze',
       HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
           BATCH, 'exact-component-all-native-stage-source-search',
           [Path(__file__), SRC / 'result.json'], summary)
print(summary, flush=True)
