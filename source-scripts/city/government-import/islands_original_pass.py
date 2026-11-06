"""Explicit frozen Peng Chau/Cheung Chau/Tung Chung original-source batches.

Reuse the established regional preparation/recovery/validation implementation.
This is not a publisher and never grants installation or compression approval.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TARGETS = ROOT/'docs/astra-city/government-import/islands-peng-cheung-tung-20261106/targets.json.gz'
REGIONS = {'peng-chau': {'10.12'}, 'cheung-chau': {'10.13'}, 'tung-chung': {'10.1', '10.2'}}


def configure(region, offset, count):
    if region not in REGIONS or offset < 0 or not 1 <= count <= 1000:
        raise ValueError('Explicit region, nonnegative offset and 1..1000 sources required')
    data = json.loads(gzip.decompress(TARGETS.read_bytes()))
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    if hashlib.sha256(manifest.read_bytes()).hexdigest() != data['sourceManifestSha256']:
        raise ValueError('Source manifest changed; reconcile a new campaign, not stale targets')
    rows = [r for r in data['rows'] if r['sectionId'] in REGIONS[region]]
    chosen = rows[offset:offset+count]
    if len(chosen) != count or len({r['uid'] for r in chosen}) != count:
        raise ValueError('Incomplete or ambiguous explicit source selection')
    name = f'government-islands-{region}-{offset:04d}-{count}-20261106'
    spec = importlib.util.spec_from_file_location('islands_existing_regional_adapter', HERE/'southwest-lantau-pass.py')
    helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    helper.UIDS = tuple(r['uid'] for r in chosen)
    helper.BATCH = helper.xl.BATCH = name
    helper.LOCAL = helper.xl.LOCAL = HERE/'local'/name
    helper.DOC = helper.xl.DOC = ROOT/'docs/astra-city/government-import'/name
    helper.INVENTORY = TARGETS
    helper.xl.LIMIT = count
    return helper, data, chosen


def run(phase, region, offset, count):
    helper, campaign, selected = configure(region, offset, count)
    if phase == 'prepare':
        helper.prepare()
        # The reused source checks remain unchanged; bind the new geographic
        # selection rather than retaining the historical helper's area label.
        path = helper.LOCAL/'selection.json.gz'
        frozen = helper.xl.read(path)
        assert set(r['uid'] for r in frozen['rows']) == set(r['uid'] for r in selected)
        assert frozen['nativeRun'] == campaign['nativeRun']
        expected = {r['uid']: r for r in selected}
        for row in frozen['rows']:
            pin = expected[row['uid']]
            assert (row['native']['cacheKey'], row['modelId'], row['native']['sheet']) == (pin['cacheKey'], pin['modelId'], pin['sheet'])
        frozen.update(selectionPolicy=f'Explicit uninstalled original-government sources in {region}; no AI geometry modelling',
            campaignSHA256=helper.xl.h(TARGETS), sourceAdapterSHA256=helper.xl.h(Path(__file__)),
            reusedPreparationSHA256=helper.xl.h(HERE/'southwest-lantau-pass.py'))
        helper.xl.save(path, frozen); helper.xl.save(helper.DOC/'selection.json.gz', frozen)
    elif phase == 'recover':
        helper.xl.recover()
    elif phase == 'check-owned':
        helper.xl.check_owned()
    else:
        frozen = helper.xl.read(helper.LOCAL/'selection.json.gz')
        claim = helper.xl.reservations.claim('codex-islands-'+str(uuid.uuid4()),
            ['building:'+r['uid'] for r in frozen['rows']], batch=helper.BATCH, ttl=3600)
        if not claim['ok']:
            raise ValueError('Existing source owner; no takeover')
        receipt = helper.LOCAL/'reservation.json'
        helper.xl.save(receipt, json.loads(json.dumps(claim['reservation'], default=str)))
        subprocess.run([sys.executable, str(HERE.parent/'shared-modelling/reservations.py'), 'run',
            '--lease-file', str(receipt), '--', sys.executable, __file__, 'check-owned',
            '--region', region, '--offset', str(offset), '--count', str(count)], cwd=ROOT, check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['prepare', 'recover', 'check', 'check-owned'])
    parser.add_argument('--region', choices=REGIONS, required=True)
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--count', type=int, required=True)
    args = parser.parse_args()
    run(args.phase, args.region, args.offset, args.count)
