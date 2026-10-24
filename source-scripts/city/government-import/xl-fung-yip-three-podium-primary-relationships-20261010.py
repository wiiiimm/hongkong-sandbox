"""Exact primary relationships for three distinct touching source podiums."""
import importlib.util
import json
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations

BATCH = 'government-xl-fung-yip-three-podium-primary-relationships-20261010'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
UIDS = ['landsd/79883:0', 'landsd/12728:0', 'landsd/79882:0']
INPUTS = [DOC.parent / 'government-xl-terrain-recovery-fung-yip-original-pair-current-recovery-v2-20261010/selection.json.gz',
          DOC.parent / 'government-xl-terrain-recovery-fung-yip-foreign-original-recovery-v1-20261010/selection.json.gz']


def main():
    assert not DOC.exists()
    claim = reservations.claim('fung-yip-primary-relationships-' + str(uuid.uuid4()),
        ['building:' + uid for uid in UIDS], batch=BATCH, ttl=1800)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        DOC.mkdir(parents=True)
        rows = [row for path in INPUTS for row in read(path)['rows'] if row['uid'] in UIDS]
        assert len(rows) == 3 and {r['uid'] for r in rows} == set(UIDS)
        csuids = [next(r['source']['building']['buildingCSUID'] for r in rows if r['uid'] == uid) for uid in UIDS]
        spec = importlib.util.spec_from_file_location('fung_yip_exact_primary_capture', HERE / 'xl-man-fuk-man-oi-primary-relations-20261010.py')
        primary = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(primary)
        primary.DOC = DOC
        before = (ROOT / '3d-viewer/city/data/manifest.json').read_bytes()
        where = 'BuildingCSUID IN (' + ','.join("'" + uid + "'" for uid in csuids) + ')'
        features = primary.query(0, where, 'exact-current-primary', True)
        assert len(features) == 3 and {f['attributes']['BuildingCSUID'] for f in features} == set(csuids)
        relations = primary.query(1002, where, 'exact-current-structure-relations')
        structure_ids = sorted({f['attributes']['BuildingStructureID'] for f in relations})
        structures = primary.query(1003, 'BuildingStructureID IN (' + ','.join(map(str, structure_ids)) + ')', 'exact-current-structures') if structure_ids else []
        # Record direct provider roles exactly; do not synthesize relations from
        # shared names/parents or positive original surface contacts.
        save(DOC / 'diagnostic.json', dict(uids=UIDS, exactSourceRows=rows, csuids=csuids,
            primary=features, relations=relations, structures=structures,
            capturedManifestSHA256=digest(before), identityAccepted=False, structuralSupportAccepted=False,
            physicalAccepted=False, installationApproved=False, sourceGeometryChanges=0,
            qualification='Exact current primary stable identities and explicit government structure relationships only. Three distinct touching original source actors remain distinct; contacts and current labels imply no shared ownership, actor suppression or support/collision exemption.'))
        assert (ROOT / '3d-viewer/city/data/manifest.json').read_bytes() == before
        spec = importlib.util.spec_from_file_location('fung_yip_primary_fence', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
        fence = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fence)
        result = fence.freeze(BATCH, 'three-exact-podium-primary-relationship-diagnosis-v1',
            [Path(__file__), HERE / 'xl-man-fuk-man-oi-primary-relations-20261010.py'] + INPUTS,
            dict(uids=UIDS, manifestSHA256=digest(before), primaryRecords=len(features), explicitRelationships=len(relations),
                 identityAccepted=False, physicalAccepted=False,
                 nextStep='Compare exact named provider structure/permit roles with complete original intersections; preserve all separate foreign actors and physical gates.',
                 qualification='Authoritative relationship research only; no acceptance or geometry changes.'))
        print(json.dumps(dict(jobId=result['jobId'], csuids=csuids, relations=relations, structures=structures)), flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':main()
