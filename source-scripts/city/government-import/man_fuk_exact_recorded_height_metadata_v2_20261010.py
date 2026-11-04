"""Continue only the complete, previously proved exact metadata correction.

The unchanged old repair is replayed against the fresh current form and source.
An already corrected entry must exactly equal that entire replayed entry.
"""
import copy
from run import ROOT, read, digest
from man_fuk_exact_recorded_height_metadata_20261010 import repair as original_repair

PRIOR = ROOT / 'docs/astra-city/government-import/government-xl-man-fuk-complete-retained-original-physical-v5-20261010/exact-recorded-height-metadata.json'
PRIOR_SHA = 'cdf0d7deb8d5f44b9b92032ea54d43d1951322a4005b53fecbb7286e55cd840a'


def repair(entry, building, source_bytes):
    assert digest(PRIOR.read_bytes()) == PRIOR_SHA, 'Prior exact correction evidence changed'
    prior = read(PRIOR)
    assert prior['sourceFormBytesUnchanged'] and prior['sourceGeometryChanges'] == 0
    assert len(prior['rows']) == 1
    original = prior['rows'][0]
    corrected, replay = original_repair(original['originalEntry'], building, source_bytes)
    assert replay == original, 'Prior exact correction differs from current replay'
    assert entry == corrected == original['correctedEntry'], 'Complete corrected entry differs'
    out = copy.deepcopy(entry)
    proof = dict(contract='man-fuk-already-proved-exact-metadata-continuation-v2',
        uid=entry['uid'], sourceSHA256=entry['sha256'],
        priorExactCorrectionEvidence=dict(path=str(PRIOR.relative_to(ROOT)), sha256=PRIOR_SHA),
        completePriorExactCorrectionReplayed=replay,
        completeCurrentEntryExactlyEqualsPriorCorrection=True,
        changedFields=[], originalEntry=copy.deepcopy(entry), correctedEntry=copy.deepcopy(out),
        geometryBytesChanged=False, placementChanged=False,
        loaderSourceEqualityWaived=False, physicalAccepted=False,
        qualification='Replay the previously byte-pinned one-ULP correction against the fresh authoritative form and original source. Require the entire already corrected entry to equal the replay exactly; change no field and waive no source, loader, geometry, support or physical gate.')
    return out, proof
