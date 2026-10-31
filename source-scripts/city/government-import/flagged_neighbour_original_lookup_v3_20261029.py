"""Reusable exact UID/CSUID lookup for retained BASIC regression obligations.

Read-only acquisition nomination. Missing matches apply only to explicitly
searched pinned sheets, never to the whole government's source inventory.
"""
import argparse
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ['batch', 'capture', 'scope', 'form-checks']:
        parser.add_argument('--'+arg, required=True)
    parser.add_argument('--extra-uid', action='append', default=[])
    parser.add_argument('--extra-sheet', action='append', default=[], help='Explicit adjoining pinned sheets to search; not identity approval')
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT/'docs/astra-city/government-import'
    doc = base/args.batch
    assert not doc.exists()
    refs, pins, receipts = [Path(__file__)], {}, {}
    for name in [args.capture, args.scope, args.form_checks]:
        directory = base/name
        receipt, bound = authenticate(directory)
        receipts[name] = receipt
        refs.append(directory/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(base/args.capture/'selection.json.gz')['rows']
    forms = take(base/args.scope/'form-obligations.json.gz')
    report = receipts[args.form_checks]
    assert ('flagged' in report) != ('basicFlags' in report), 'Require one explicit regression flag schema'
    flags = report['flagged'] if 'flagged' in report else report['basicFlags']
    wanted = sorted({r['uid'] for r in flags} | set(args.extra_uid))
    by_uid = {r['uid']: r for r in forms}
    assert set(wanted) <= set(by_uid)
    assert all(sheet and '/' not in sheet and len(sheet) <= 30 for sheet in args.extra_sheet)
    cache_keys = sorted({r['native']['cacheKey'] for r in selection})
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        indexed = db.execute('SELECT i.cache_key,i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=ANY(%s)', (cache_keys,)).fetchall()
    native_sheets = {key: (sheet, sha) for key, sheet, sha in indexed}
    assert set(native_sheets) == set(cache_keys)
    for r in selection:
        sheet, sha = native_sheets[r['native']['cacheKey']]
        assert sha == r['native']['resultSha']
        assert not r['candidate']['entry'].get('sourceTile') or r['candidate']['entry']['sourceTile'] == sheet
    sheets = sorted({sheet for sheet, _ in native_sheets.values()} | set(args.extra_sheet))
    current_sources = {}
    for uid in wanted:
        form = by_uid[uid]
        path = ROOT/'3d-viewer/city/data/tiles'/(form['tile']+'.json')
        assert [r for r in read(path)['buildings'] if r['uid'] == uid] == [form]
        refs.append(path)
        current_sources[uid] = dict(building=form, tile=str(path.relative_to(ROOT/'3d-viewer')), tileSHA256=digest(path.read_bytes()))
    matches = {uid: [] for uid in wanted}
    records = []
    with connect() as db:
        db.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        native = db.execute('''SELECT i.sheet,i.cache_key,r.result_sha,r.result
            FROM astra_modelling.native_stage_inputs i
            JOIN astra_modelling.native_stage_results r USING(cache_key)
            JOIN astra_modelling.native_stage_members m USING(cache_key)
            WHERE m.run_id=%s AND i.sheet=ANY(%s) ORDER BY i.sheet,i.cache_key''', (NATIVE_RUN, sheets)).fetchall()
        assert {r[0] for r in native} == set(sheets)
        for sheet, cache, sha, result in native:
            records.append(dict(sheet=sheet, cacheKey=cache, resultSHA256=sha))
            for model in result['models']:
                for match in model.get('matching', {}).get('viewerMatches', []):
                    uid = match['uid']
                    if uid in matches and match.get('buildingCSUID') == by_uid[uid].get('buildingCSUID'):
                        matches[uid].append(dict(sheet=sheet, nativeCacheKey=cache, nativeResultSHA256=sha,
                            sourceKey=cache+'/'+model['modelId'], model=model))
    summary = dict(uids=wanted, searchedSheets=sheets, nativeRun=NATIVE_RUN,
        rows=[dict(uid=uid, source=current_sources[uid], matches=matches[uid]) for uid in wanted],
        checkedNativeRecords=records, uniqueExactMatches=sum(len(v) == 1 for v in matches.values()),
        noExactMatches=[u for u in wanted if not matches[u]], multipleExactMatches=[u for u in wanted if len(matches[u]) > 1],
        installationApproved=False, identityAccepted=False, sourceGeometryChanges=0,
        qualification='Exact current UID/CSUID metadata nomination on the explicitly searched pinned project source sheets. All missing/ambiguous units retained. Original assets are not acquired by this command; no terrain/source acceptance or installation credit. A missing sheet-local match is not government-wide absence.')
    save(doc/'lookup.json', summary)
    module('flagged_neighbour_original_lookup_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        args.batch, 'exact-current-flagged-neighbour-original-unit-lookup', list(dict.fromkeys(refs)), summary)
    print(dict(requested=len(wanted), sheets=sheets, unique=summary['uniqueExactMatches'],
               missing=summary['noExactMatches'], ambiguous=summary['multipleExactMatches']), flush=True)


if __name__ == '__main__':
    main()
