"""Recover exact nominated originals through existing leased acquisition/packing.

No identity approval, geometry editing, screening or optimisation is performed.
"""
import argparse
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import sys
import uuid
from run import ROOT, HERE, read, save, digest, reservations, connect, NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
sys.path.insert(0, str(HERE.parent/'enhancement-screening'))
import shape_prepare


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--lookup', required=True)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT/'docs/astra-city/government-import'
    doc, local = base/args.batch, HERE/'local'/args.batch
    lease_path = local/'reservation.json'
    lookup_dir = base/args.lookup
    _, pins = authenticate(lookup_dir)
    lookup_path = lookup_dir/'lookup.json'
    assert digest(lookup_path.read_bytes()) == pins[str(lookup_path.relative_to(ROOT))]
    lookup = read(lookup_path)
    nominated = [r for r in lookup['rows'] if len(r['matches']) == 1 and r['matches'][0]['model'].get('candidate')]
    assert nominated and len(nominated) <= 20
    if not args.owned:
        assert not doc.exists() and not local.exists()
        resources = ['building:'+r['uid'] for r in nominated]
        resources += ['native-model:'+r['matches'][0]['sourceKey'] for r in nominated]
        claim = reservations.claim('nominated-original-recovery-'+str(uuid.uuid4()), sorted(resources), batch=args.batch, ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'], lease_path, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(lease_path)
    assert reservations.owns(lease) and not doc.exists()
    assert shutil.disk_usage(ROOT).free >= 3*1024**3
    refs = [Path(__file__), lookup_dir/'result.json', lookup_path, Path(shape_prepare.__file__)]
    sources, native, wanted = {}, [], {}
    for row in nominated:
        match = row['matches'][0]
        model, form = match['model'], row['source']['building']
        entry = model['candidate']
        for a,b in [('uid','uid'),('objectId','objectId'),('buildingCSUID','buildingCSUID'),('recordedBaseHeight','baseHeightHKPD'),('recordedTopHeight','topHeightHKPD')]:
            assert entry[a] == form[b]
        assert entry['sha256'] == model['asset']['sha256'] and entry['bytes'] <= 2*1024**2
        assert entry['publicationApproved'] is False and entry['placementReviewed'] is False
        path = ROOT/'3d-viewer'/row['source']['tile']
        assert digest(path.read_bytes()) == row['source']['tileSHA256']
        assert [r for r in read(path)['buildings'] if r['uid'] == row['uid']] == [form]
        refs.append(path)
        sources[row['uid']] = row['source']
        native.append(dict(sheet=match['sheet'], cacheKey=match['nativeCacheKey'], resultSha=match['nativeResultSHA256'], model=model))
        wanted[entry['sha256']] = entry['bytes']
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for record in lookup['checkedNativeRecords']:
            assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s', (record['cacheKey'],)).fetchone() == (record['resultSHA256'],)
    cache = local/'recovered/assets'
    cache.mkdir(parents=True)
    seeded = {}
    files = subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','*.glb.gz','source-scripts/city','3d-viewer/city/data'], cwd=ROOT, text=True).splitlines()
    for name in files:
        path = ROOT/name
        sha = path.name.removesuffix('.glb.gz')
        if sha in wanted and sha not in seeded:
            raw = path.read_bytes()
            if digest(raw) == sha and len(raw) == wanted[sha]:
                (cache/path.name).write_bytes(raw)
                seeded[sha] = name
                refs.append(path)
    inputs = local/'recovery-inputs.json.gz'
    save(inputs, dict(nativeRun=NATIVE_RUN, rows=sorted(sources), sources=sources, native=native))
    prepared = shape_prepare.prepare(inputs, local/'recovered', allow_source=True, workers=2,
        env_file=ROOT/'.env.modelling', reservation_receipt=lease)
    rows = []
    for row in nominated:
        match = row['matches'][0]
        model = match['model']; entry = deepcopy(model['candidate'])
        asset = cache/(entry['sha256']+'.glb.gz')
        assert digest(asset.read_bytes()) == entry['sha256'] and asset.stat().st_size == entry['bytes']
        entry['rootTranslation'] = [-834500,0,816500]
        entry['proceduralWindows'] = False
        rows.append(dict(uid=row['uid'], source=row['source'], modelId=model['modelId'], triangles=model['triangles'],
            native=dict(cacheKey=match['nativeCacheKey'],resultSha=match['nativeResultSHA256'],model=model),
            candidate=dict(path=str(asset.relative_to(ROOT)),entry=entry), originalGeometryOnly=True,sourceSHA256=entry['sha256']))
    assert not prepared['errors']
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    refs += [manifest, inputs]
    save(doc/'selection.json.gz',dict(rows=rows,manifestSHA256=digest(manifest.read_bytes())))
    out = dict(uids=sorted(sources), recoveredCount=len(rows), exactLocalSources=len(seeded),
        notNominated=[r['uid'] for r in lookup['rows'] if r not in nominated],
        methods=prepared['methods'], errors=prepared['errors'], missing=[],
        recoveredPackedBytes=sum(r['candidate']['entry']['bytes'] for r in rows),
        installationApproved=False, identityAccepted=False, physicalAccepted=False,sourceGeometryChanges=0,
        qualification='Exact nominated UID/CSUID sources, verified local bytes preferred and existing guarded government acquisition for missing bytes. Unchanged original assets/pose only. Unmatched/ambiguous/unpacked nominations remain explicit; no source identity, support, runtime, browser or installation approval.')
    save(doc/'summary.json',out)
    refs += [p for p in (local/'recovered').rglob('*') if p.is_file() and p.suffix != '.zip']
    assert reservations.owns(lease)
    module('nominated_original_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        args.batch,'nominated-exact-original-neighbour-recovery-and-unapproved-selection',list(dict.fromkeys(refs)),out)
    print(dict(recovered=len(rows),exactLocalSources=len(seeded),errors=prepared['errors']),flush=True)


if __name__ == '__main__':
    main()
