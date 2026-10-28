"""Bind required catalogue source sheets to exact existing Neon stage results.

No database writes and no source geometry or acceptance changes. Several model
rows may legitimately share a single native-stage cache key.
"""


def source_sheet_bindings(db, rows):
    assert rows and len({r['uid'] for r in rows}) == len(rows)
    keys = {r['native']['cacheKey'] for r in rows}
    records = db.execute(
        'SELECT i.cache_key,i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i '
        'JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key = ANY(%s)',
        (sorted(keys),)).fetchall()
    current = {key: (sheet, sha) for key, sheet, sha in records}
    assert set(current) == keys and len(current) == len(records), 'Missing/duplicate native stage binding'
    bindings = {}
    for row in rows:
        native, entry = row['native'], row['candidate']['entry']
        sheet, result_sha = current[native['cacheKey']]
        assert result_sha == native['resultSha'], 'Native stage result changed'
        assert isinstance(sheet, str) and sheet, 'Native source sheet missing'
        assert entry['uid'] == native['model']['candidate']['uid'] == row['uid']
        assert native['model']['modelId'] == row['modelId'] == entry['modelId']
        assert native['model']['asset']['sha256'] == entry['sha256'] == row['sourceSHA256']
        assert entry.get('sourceTile') in (None, sheet), 'Existing source sheet conflicts with exact stage'
        bindings[row['uid']] = dict(uid=row['uid'], cacheKey=native['cacheKey'], resultSHA256=result_sha,
                                    sourceSHA256=row['sourceSHA256'], sourceTile=sheet,
                                    priorSourceTile=entry.get('sourceTile'), geometryChanges=0)
    return bindings
