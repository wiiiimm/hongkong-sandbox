"""Fetch the exact official source record; no geometry edits or approval inference."""
import json
import uuid
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from run import ROOT, HERE, save, digest, reservations
from primrose_compound_foundation_v2_20261015 import module

UID = 'landsd/61216:0'
BATCH = 'government-xl-murray-house-primary-record-v1-20261021'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH

def main():
    assert not DOC.exists(), 'Preserve existing evidence; do not overwrite'
    claim = reservations.claim('murray-house-primary-' + str(uuid.uuid4()),
                               ['building:' + UID], batch=BATCH, ttl=1800)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        params = dict(f='json', where="BuildingCSUID='3965608830T20050430'",
                      outFields='*', returnGeometry='true', outSR='2326')
        url = ('https://portal.csdi.gov.hk/server/rest/services/common/'
               'landsd_rcd_1637211194312_35158/MapServer/0/query?' + urlencode(params))
        with urlopen(url, timeout=60) as response:
            raw = response.read()
        record = json.loads(raw)
        assert 'error' not in record, record.get('error')
        assert len(record.get('features', [])) == 1, 'Expected one exact CSUID record'
        assert reservations.owns(lease)
        DOC.mkdir(parents=True)
        (DOC / 'primary-response.json').write_bytes(raw)
        save(DOC / 'request.json', dict(url=url, responseSHA256=digest(raw)))
        module('stone_primary_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'exact-original-primary-record', [Path(__file__)],
            dict(uids=[UID], sourceCSUID='3965608830T20050430',
                 identityAccepted=False, primaryRecordCount=1,
                 remainingReason='source-extent-role-and-current-terrain-placement',
                 nextStep='Compare primary footprint with exact original component evidence; retain all installation gates.'))
        print(json.dumps(record['features'][0]['attributes']), flush=True)
    finally:
        assert reservations.release(lease)['ok']

if __name__ == '__main__':
    main()
