"""Rebind three cached Elegant Garden originals and run existing identity checks.

No geometry edits, support/identity waiver, rendering or installation. Each phase
owns an independent lease; completed child evidence is never restarted here.
"""
import json
import subprocess
import sys
import uuid
from run import ROOT, HERE, read, save, reservations
from primrose_compound_foundation_v2_20261015 import module

PREFIX = 'government-xl-elegant-garden-'
BATCH = PREFIX + 'three-original-current-sequence-v1-20261027'
INVENTORY = 'government-xl-after-ocean-four-current-inventory-v1-20261027'
UIDS = ['landsd/173532:0', 'landsd/173768:0', 'landsd/236170:0']


def main():
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / BATCH, HERE / 'local' / BATCH
    assert not doc.exists() and not local.exists(), 'Preserve existing sequence evidence'
    doc.mkdir()
    local.mkdir(parents=True)
    block2 = PREFIX + 'block2-current-selection-v1-20261027'
    pair = PREFIX + 'block1-podium-current-selection-v1-20261027'
    combined = PREFIX + 'three-original-current-selection-v1-20261027'
    identity = PREFIX + 'three-original-current-identity-v1-20261027'
    context = PREFIX + 'three-original-record-context-v1-20261027'
    merge = str(HERE / 'merge_current_original_selections_v1_20261024.py')

    def selection(batch, captures, uids):
        return [sys.executable, merge, '--batch', batch, '--inventory', INVENTORY,
                *[arg for capture in captures for arg in ['--capture', capture]],
                *[arg for uid in uids for arg in ['--uid', uid]]]

    steps = [
        (block2, selection(block2, ['government-xl-remaining-178-v3-current-scene-v1-20261023-chunk-04-selection'], [UIDS[0]])),
        (pair, selection(pair, ['government-xl-coverage-assembly-closure-20261007-173768-0'], UIDS[1:])),
        (combined, selection(combined, [block2, pair], UIDS)),
        (identity, [sys.executable, str(HERE / 'selected_original_identity_v2.py'), '--batch', identity, '--capture', combined]),
        (context, [sys.executable, str(HERE / 'original_assembly_identity_context_v1_20261024.py'),
                   '--batch', context, '--capture', combined, '--identity', identity,
                   *[arg for uid in UIDS for arg in ['--uid', uid]]]),
    ]
    completed, refs = [], [__file__]
    for batch, command in steps:
        assert not (base / batch).exists()
        claimed = reservations.claim('elegant-original-phase-' + str(uuid.uuid4()),
                                     ['building:' + uid for uid in UIDS], batch=batch, ttl=3600)
        assert claimed['ok'], 'Another owner holds a source; no takeover'
        lease = claimed['reservation']
        lease_path = local / (batch + '-lease.json')
        save(lease_path, json.loads(json.dumps(lease, default=str)))
        print('Starting ' + batch, flush=True)
        try:
            log_path = local / (batch + '.log')
            with log_path.open('w') as log:
                result = subprocess.run([sys.executable, str(HERE / 'observed_reserved_runner_v1_20261027.py'),
                                         str(lease_path), *command], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        finally:
            if reservations.owns(lease):
                assert reservations.release(lease)['ok']
        if result.returncode != 0:
            save(doc / 'progress.json', dict(uids=UIDS, completed=completed, failedBatch=batch,
                 exitCode=result.returncode, installationApproved=False, publication=False,
                 permanentRejection=False, log=str(log_path.relative_to(ROOT))))
            raise RuntimeError('Phase failed; preserve completed evidence and inspect ' + batch)
        assert (base / batch / 'result.json').exists()
        completed.append(batch)
        save(doc / 'progress.json', dict(uids=UIDS, completed=completed, installationApproved=False,
                                       publication=False, permanentRejection=False))
        print('Completed ' + batch, flush=True)
    from pathlib import Path
    refs = [Path(__file__), *[base / batch / 'result.json' for batch in completed]]
    summary = dict(uids=UIDS, completed=completed, sourceGeometryChanges=0, sourcePoseChanges=0,
                   installationApproved=False, publication=False, physicalAcceptance=False,
                   identityAccepted=False, qualification='Fresh exact source/inventory rebind, then unchanged '
                   'complete identity and assembly-context diagnostics. Raw individual failures retained. '
                   'Prior support evidence is historical; no placement/identity/publication approval transfers.')
    save(doc / 'summary.json', summary)
    module('elegant_current_sequence_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'three-current-original-selection-and-identity-diagnostics', refs, summary)


if __name__ == '__main__':
    main()
