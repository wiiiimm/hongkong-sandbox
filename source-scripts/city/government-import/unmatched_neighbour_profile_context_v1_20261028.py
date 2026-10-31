"""Inspect missing exact joins without treating a GeoRef prefix as identity."""
import argparse
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--lookup', required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT/'docs/astra-city/government-import'
    doc, prior = base/a.batch, base/a.lookup
    assert not doc.exists()
    _, pins = authenticate(prior)
    path = prior/'lookup.json'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    lookup = read(path)
    wanted = {r['uid']: r for r in lookup['rows'] if not r['matches']}
    assert wanted
    found = {u: [] for u in wanted}
    with connect() as db:
        db.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        for record in lookup['checkedNativeRecords']:
            sha, data = db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s', (record['cacheKey'],)).fetchone()
            assert sha == record['resultSHA256']
            for model in data['models']:
                for uid, row in wanted.items():
                    prefix = row['source']['building']['buildingCSUID'][:10]
                    if model['modelId'][1:11] == prefix:
                        found[uid].append(dict(sheet=record['sheet'], cacheKey=record['cacheKey'],
                            resultSHA256=sha, model=model))
    result = dict(uids=sorted(wanted), searchedSheets=lookup['searchedSheets'],
        rows=[dict(uid=u, currentSource=wanted[u]['source'], prefixCandidates=found[u],
            interpretation='Source preparation/identity review required; prefix is not approval' if found[u] else 'No prefix candidate in the explicitly inspected pinned BUILDING records; not government-wide absence') for u in sorted(wanted)],
        identityAccepted=False, installationApproved=False, sourceGeometryChanges=0,
        qualification='Only exact immutable source-record context. Candidate-less source components retain their complete original hold reasons, asset bytes, matching and extents. No UID reassignment, model recovery, corruption/permanent rejection, footprint waiver, geometry edit or installation credit.')
    save(doc/'summary.json', result)
    module('unmatched_neighbour_prefix_context_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'missing-neighbour-exact-source-profile-context', [Path(__file__), prior/'result.json', path], result)
    print({u: [r['model']['modelId'] for r in found[u]] for u in sorted(wanted)}, flush=True)


if __name__ == '__main__':
    main()
