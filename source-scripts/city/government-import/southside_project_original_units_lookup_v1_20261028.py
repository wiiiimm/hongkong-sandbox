"""Readonly exact current UID/CSUID source lookup for the podium project forms."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-southside-project-original-units-lookup-v1-20261028'
DOC = BASE / BATCH
GROUND = BASE / 'government-xl-la-marina-southside-original-terrain-v1-20261028'
SUPPORT = BASE / 'government-xl-southside-basic-podium-support-diagnostic-v1-20261028'
REGRESSION = BASE / 'government-xl-southside-six-partition-basic-regressions-v1-20261028'


def main():
    assert not DOC.exists()
    refs, pins = [Path(__file__)], {}
    for batch in [GROUND, SUPPORT, REGRESSION]:
        _, bound = authenticate(batch)
        refs.append(batch / 'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    support = take(SUPPORT / 'summary.json')
    wanted = {r['uid'] for r in support['rows'] if r['podiumProjectionCoverageM2'] > 0} | {'landsd/315025:0'}
    assert len(wanted) == 17
    forms = {r['building']['uid']: r['building'] for r in take(REGRESSION / 'neighbour-inputs.json.gz')['rows']}
    assert wanted <= set(forms)
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = take(manifestpath)
    tiles = {t['id']: t for t in manifest['tiles']}
    sources = {}
    for uid in sorted(wanted):
        form = forms[uid]
        path = ROOT / '3d-viewer' / tiles[form['tile']]['url']
        assert next(f for f in take(path)['buildings'] if f['uid'] == uid) == form
        sources[uid] = dict(building=form, tile=tiles[form['tile']]['url'], tileSHA256=digest(path.read_bytes()))
    inputs = take(GROUND / 'source-inputs.json')['inputs']
    rows = {uid: [] for uid in wanted}
    records = []
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for sheet, record in inputs.items():
            sha, native = db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s', (record['cacheKey'],)).fetchone()
            assert sha == record['resultSHA256']
            records.append(dict(sheet=sheet, cacheKey=record['cacheKey'], resultSHA256=sha))
            for model in native['models']:
                for match in model.get('matching', {}).get('viewerMatches', []):
                    uid = match['uid']
                    if uid in wanted and match.get('buildingCSUID') == forms[uid].get('buildingCSUID'):
                        rows[uid].append(dict(sheet=sheet, nativeCacheKey=record['cacheKey'], nativeResultSHA256=sha,
                                              sourceKey=record['cacheKey'] + '/' + model['modelId'], model=model))
    result = dict(uids=sorted(wanted), rows=[dict(uid=uid, source=sources[uid], matches=rows[uid]) for uid in sorted(wanted)],
                  checkedNativeRecords=records, uniqueExactMatches=sum(len(v) == 1 for v in rows.values()),
                  noExactMatches=[u for u in sorted(wanted) if not rows[u]],
                  multipleExactMatches=[u for u in sorted(wanted) if len(rows[u]) > 1],
                  installationApproved=False, identityAccepted=False, sourceGeometryChanges=0,
                  qualification='Readonly native source metadata for the 16 flagged BASIC forms with positive podium projection plus the podium itself. Exact current UID/CSUID matching only; all absent/ambiguous cases preserved. This nominates acquisition candidates, not architectural identity, ownership, placement, support or installation acceptance. Four outside-podium flags remain separate terrain obligations.')
    save(DOC / 'lookup.json', result)
    module('southside_project_original_units_lookup_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-current-project-original-unit-lookup-across-pinned-sheets', list(dict.fromkeys(refs)), result)
    print(dict(forms=len(wanted), unique=result['uniqueExactMatches'], missing=result['noExactMatches'], multiple=result['multipleExactMatches']), flush=True)


if __name__ == '__main__':
    main()
