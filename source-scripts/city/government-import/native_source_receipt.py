"""Verify legacy native cache membership or a separately fenced fresh revision.

Fresh revisions never inherit the old native source SHA or rewrite its run.
"""
from pathlib import Path
from run import ROOT, read, digest, NATIVE_RUN


def values(result, names):
    assert result is not None, 'Required source receipt is missing'
    return tuple(result[name] for name in names) if isinstance(result, dict) else tuple(result)


def verify(con, row):
    native = row['native']; ref = native.get('revisionAcquisition')
    if ref is None:
        actual = con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r '
            'JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',
            (NATIVE_RUN, native['cacheKey'])).fetchone()
        assert values(actual, ('result_sha',)) == (native['resultSha'],), 'Legacy native result differs'
        return
    assert set(ref) == {'path', 'sha256', 'jobId'} and 'cacheKey' not in native and 'resultSha' not in native
    path = (ROOT / ref['path']).resolve()
    assert path.parent.parent == ROOT / 'docs/astra-city/government-import' and path.name == 'result.json'
    assert digest(path.read_bytes()) == ref['sha256'], 'Revision receipt file changed'
    receipt = read(path)
    actual = con.execute('SELECT stage,status,result FROM astra_modelling.jobs WHERE id=%s', (ref['jobId'],)).fetchone()
    assert values(actual, ('stage', 'status', 'result')) == (
        'explicit-current-government-revision-acquisition-v1', 'complete', receipt), 'Revision job is not the exact completed receipt'
    assert receipt['jobId'] == ref['jobId'] and not receipt['publication'] and receipt['newlyInstalled'] == 0
    for evidence in receipt['evidenceRefs']:
        source = (ROOT / evidence['path']).resolve(); assert source.is_relative_to(ROOT)
        assert digest(source.read_bytes()) == evidence['sha256'], 'Pinned revision evidence changed'
    matches = [r for r in receipt['rows'] if r['uid'] == row['uid']]
    assert len(matches) == 1, 'Revision source identity is ambiguous'
    expected = matches[0]
    assert expected['source'] == row['source'] and expected['modelId'] == row['modelId']
    assert expected['sourceSHA256'] == row['sourceSHA256'] == native['model']['asset']['sha256']
    assert expected['model'] == native['model'], 'Revision model metadata changed'
    assert expected['priorModelId'] != expected['modelId'] and expected['priorSourceSHA256'] != expected['sourceSHA256']
    for asset in [ROOT / expected['assetPath'], ROOT / row['candidate']['path']]:
        asset = asset.resolve(); assert asset.is_relative_to(ROOT)
        assert digest(asset.read_bytes()) == expected['sourceSHA256'], 'Original revision asset changed'
