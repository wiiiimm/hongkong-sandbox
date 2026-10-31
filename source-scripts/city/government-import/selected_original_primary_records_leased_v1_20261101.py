"""Run the existing bounded primary-record fetch under exact source leases."""
import argparse
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--capture', required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.capture])
    base = ROOT / 'docs/astra-city/government-import'
    _, pins = authenticate(base / a.capture)
    selected = base / a.capture / 'selection.json.gz'
    assert digest(selected.read_bytes()) == pins[str(selected.relative_to(ROOT))]
    rows = read(selected)['rows']
    assert 0 < len(rows) <= 40 and len({r['uid'] for r in rows}) == len(rows)
    assert not (base / a.batch).exists()
    local = HERE / 'local' / a.batch
    assert not local.exists()
    resources = sorted('building:' + r['uid'] for r in rows)
    claim = reservations.claim('primary-records-' + str(uuid.uuid4()), resources,
                               batch=a.batch, ttl=3600)
    assert claim['ok'], claim
    return execute_reserved(claim['reservation'], local / 'reservation.json',
        [sys.executable, str(HERE / 'selected_original_primary_records_v1_20261025.py'),
         '--batch', a.batch, '--capture', a.capture])


if __name__ == '__main__':
    main()
