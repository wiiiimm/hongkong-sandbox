"""Freeze a complete original source-specific ancillary identity PROPOSAL only."""
import importlib.util, json
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from king_cheung_complete_ancillary_proposal_20261011 import proposal
BASE = ROOT / 'docs/astra-city/government-import'
RAW = BASE / 'government-xl-king-cheung-95691-current-original-identity-v1-20261011'
SOURCE = BASE / 'government-xl-king-cheung-95691-complete-original-extra-context-v1-20261011'
LOW = BASE / 'government-xl-king-cheung-95691-complete-low-parts-contacts-v1-20261011'
PRIMARY = BASE / 'government-xl-king-cheung-95691-primary-relations-v1-20261011'
EXPORT = BASE / 'government-xl-king-cheung-95691-primary-actual-pdf-source-context-exports-v2-20261011'
OWNER = BASE / 'government-xl-king-cheung-95691-ha-owner-bfa-plan-photo-packet-v1-20261011'
BATCH = 'government-xl-king-cheung-95691-complete-ancillary-proposal-v1-20261011'
DOC = BASE / BATCH
def main():
    assert not DOC.exists()
    receipts = [p / 'result.json' for p in [RAW, SOURCE, LOW, PRIMARY, EXPORT, OWNER]]
    refs = [Path(__file__), HERE / 'king_cheung_complete_ancillary_proposal_20261011.py',
            HERE / 'test_king_cheung_complete_ancillary_proposal_20261011.py',
            HERE / 'exact_packed_world_geometry_20261009.py']
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for p in receipts:
            r = read(p); assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (r['jobId'],)).fetchone() == ('complete', r)
            refs.append(p)
            for pin in r['evidenceRefs']:
                q = ROOT / pin['path']; assert digest(q.read_bytes()) == pin['sha256']; refs.append(q)
    row = read(RAW / 'selection.json.gz')['rows'][0]
    asset = ROOT / row['candidate']['path']; assert digest(asset.read_bytes()) == row['sourceSHA256']
    manifest = ROOT / '3d-viewer/city/data/manifest.json'; before = manifest.read_bytes()
    assert before == (RAW / 'captured-manifest.json').read_bytes()
    context = read(RAW / 'context.json.gz')['rows'][0]
    for tile, sha in context['neighbourTileHashes'].items(): assert digest((ROOT / '3d-viewer' / tile).read_bytes()) == sha
    output = proposal(read(RAW / 'identity.json'), row, decode_original_world_triangles(asset.read_bytes()),
                      read(RAW / 'complete-current-forms.json.gz')['rows'], read(PRIMARY / 'exact-current-one-primary.json'),
                      read(SOURCE / 'diagnostic.json.gz')['completeTopology'], read(LOW / 'diagnostic.json.gz'))
    output['architecturalInterpretationPrimaryRefs'] = [dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())) for p in
        [OWNER / 'raw/owner-estate-CLW.jpg', OWNER / 'raw/owner-barrier-free-access-en.pdf', EXPORT / 'exports.json', EXPORT / 'explicit-utf8-owner-record.json']]
    save(DOC / 'diagnostic.json.gz', output)
    refs += [asset, manifest, RAW / 'identity.json', RAW / 'selection.json.gz', RAW / 'context.json.gz', RAW / 'complete-current-forms.json.gz',
             PRIMARY / 'exact-current-one-primary.json', SOURCE / 'diagnostic.json.gz', LOW / 'diagnostic.json.gz', DOC / 'diagnostic.json.gz']
    assert manifest.read_bytes() == before
    for tile, sha in context['neighbourTileHashes'].items(): assert digest((ROOT / '3d-viewer' / tile).read_bytes()) == sha
    s = importlib.util.spec_from_file_location('king_ancillary_proposal_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    r = m.freeze(BATCH, 'complete104-original-faces-ancillary-identity-proposal-no-identity-ground-or-installation-credit', refs,
                 dict(uids=output['uids'], completeFaces=18742, proposedAncillaryFaces=104, ordinaryExtentFaces=18638,
                      proposalSpatialGuardsSatisfied=output['proposalSpatialGuardsSatisfied'], sourceOnly=True, identityAccepted=False, currentAcceptance=False, newlyInstalled=0))
    print(json.dumps(dict(jobId=r['jobId'], checks=output['fullSourceSpatialChecks'], identityAccepted=False)), flush=True)
if __name__ == '__main__': main()
