"""Consolidate exact original identity evidence; does not approve placement."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-park-avenue239350-identity-roster-v1-20261018'

def folder(name):
    return BASE / ('government-xl-park-avenue239350-' + name + '-20261018')

def main():
    doc = BASE / BATCH
    assert not doc.exists()
    names = ['current-identity-runtime-v3','companion-identity-runtime-v1','base-neighbour-identity-runtime-v1','identity-review-v1']
    pins, refs = {}, [Path(__file__)]
    with connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        for name in names:
            path = folder(name) / 'result.json'
            result = read(path)
            assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (result['jobId'],)).fetchone() == ('complete', result)
            refs.append(path)
            for item in result['evidenceRefs']:
                assert item['path'] not in pins or pins[item['path']] == item['sha256']
                pins[item['path']] = item['sha256']
    for path, sha in pins.items():
        assert digest((ROOT / path).read_bytes()) == sha, path
    rows = [row for name in names[:3] for row in read(folder(name) / 'selection.json.gz')['rows']]
    assert len(rows) == len({row['uid'] for row in rows}) == 6
    roster = []
    for row in rows:
        uid = row['uid']
        short = uid.split('/')[1]
        if uid=='landsd/239350:0':
            path=folder('identity-review-v1')/(short+'-review.json');proof=read(path)
            assert proof['identityOnlyApproved'] and proof['identityReviewApproved']
        else:
            name='companion-identity-runtime-v1' if uid in ['landsd/240161:0','landsd/227455:0'] else 'base-neighbour-identity-runtime-v1'
            path=folder(name)/(short+'-identity.json');proof=read(path)['proof']
            assert proof['passed'] and not proof['reasons']
        entry = row['candidate']['entry']
        sha = entry['sha256']
        assert proof['uid'] == uid and proof['sourceSHA256'] == row['sourceSHA256'] == sha
        assert digest((ROOT / row['candidate']['path']).read_bytes()) == sha
        assert path.relative_to(ROOT).as_posix() in pins
        source_key = row['native']['cacheKey'] + '/' + row['modelId']
        assert row.get('sourceKey', source_key) == source_key
        roster.append(dict(uid=uid, sourceKey=source_key, modelId=row['modelId'],
                           sourceSHA256=sha, buildingCSUID=entry['buildingCSUID'],
                           identityAccepted=True, identityEvidence=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())),
                           rawReasonsRetained=proof.get('rawReasonsRetained', proof.get('reasons', []))))
    save(doc / 'roster.json', dict(models=roster, identityAccepted=True, placementReviewed=False,
                                 publicationApproved=False, aiGeometryModelling=False))
    result = module('identity_roster_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'park-avenue-six-original-identity-roster-v1', [*refs, *[ROOT / path for path in pins]],
        dict(uids=[row['uid'] for row in rows], identityAccepted=True, fullAcceptance=False))
    print(result['jobId'], flush=True)

if __name__ == '__main__':
    main()
