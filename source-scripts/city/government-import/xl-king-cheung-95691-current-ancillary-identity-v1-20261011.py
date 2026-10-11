"""Unmocked current104-face typed identity replay; no physical/import approval."""
import importlib.util, json, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from king_cheung_current_ancillary_identity_20261011 import verify_files, RAW, PROPOSAL, UID
BATCH = 'government-xl-king-cheung-95691-current-ancillary-identity-v1-20261011'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH; LOCAL = HERE / 'local' / BATCH
def main():
    assert not DOC.exists()
    claim = reservations.claim('king-cheung-ancillary-identity-' + str(uuid.uuid4()), ['building:' + UID], batch=BATCH, ttl=3600)
    assert claim['ok']; lease = claim['reservation']
    try:
        row = read(RAW / 'selection.json.gz')['rows'][0]; context = read(RAW / 'context.json.gz')['rows'][0]
        manifest = ROOT / '3d-viewer/city/data/manifest.json'; before = manifest.read_bytes()
        catalogues = [(ROOT / '3d-viewer' / url, digest((ROOT / '3d-viewer' / url).read_bytes())) for url in json.loads(before)['officialModelCatalogues']]
        identity = verify_files(row, context, LOCAL / 'original-identity')
        assert identity['passed'] and identity['reasons'] == [] and not identity['physicalAccepted'] and not identity['installationApproved']
        save(DOC / 'identity.json', identity); save(DOC / 'selection.json.gz', dict(rows=[row], manifestSHA256=digest(before)))
        save(DOC / 'context.json.gz', dict(rows=[context])); (DOC / 'captured-manifest.json').write_bytes(before)
        refs = [Path(__file__), HERE / 'king_cheung_current_ancillary_identity_20261011.py',
                HERE / 'test_king_cheung_current_ancillary_identity_20261011.py', HERE / 'king_cheung_complete_ancillary_proposal_20261011.py',
                HERE / 'exact_original_georef_cell_identity_20261009.py', HERE / 'exact_packed_world_geometry_20261009.py',
                HERE / 'xl-final-script-pass.py', PROPOSAL / 'result.json', PROPOSAL / 'diagnostic.json.gz',
                RAW / 'selection.json.gz', RAW / 'context.json.gz', RAW / 'identity.json', manifest, ROOT / row['candidate']['path']]
        refs += [ROOT / pin['path'] for pin in read(PROPOSAL / 'result.json')['evidenceRefs']]
        refs += [path for path, _ in catalogues] + [ROOT / '3d-viewer' / tile for tile in context['neighbourTileHashes']]
        refs += [p for p in LOCAL.rglob('*') if p.is_file()] + [DOC / 'identity.json', DOC / 'selection.json.gz', DOC / 'context.json.gz', DOC / 'captured-manifest.json']
        assert reservations.owns(lease) and manifest.read_bytes() == before
        for path, sha in catalogues: assert digest(path.read_bytes()) == sha
        s = importlib.util.spec_from_file_location('king_typed_identity_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
        m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
        r = m.freeze(BATCH, 'current-bound104-original-ancillary-canopy-identity-only-no-ground-or-installation-credit', refs,
             dict(uids=[UID], identityAccepted=True, scriptFullAcceptancePassed=False, physicalAccepted=False, sourceGeometryChanges=0,
                  rawExtentReasonsRetained=identity['rawAncillaryExtentReasonsRetained'], canopyPost43StillIsolated=True, newlyInstalled=0))
        print(json.dumps(dict(jobId=r['jobId'], identityAccepted=True, physicalAccepted=False)), flush=True)
    finally: assert reservations.release(lease)['ok']
if __name__ == '__main__': main()
