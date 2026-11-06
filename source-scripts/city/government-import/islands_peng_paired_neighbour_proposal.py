"""Test a complete original neighbour pair on a retained authentic TIN proposal.

The former BASIC neighbour is replaced only if its original passes the same fresh
source/contact/runtime/browser gates. Terrain arrays are copied exactly; this is
not a neighbour exemption, approval, geometry edit or publication operation.
"""
import copy
import argparse
import json
import subprocess
import sys
import uuid
from pathlib import Path
from islands_direct_stage import ROOT, HERE, read, save, sha, rel, module
from run import connect, reservations

BATCH = 'government-islands-peng-chau-paired-neighbour-20261106-v1'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    local = HERE / 'local' / BATCH
    lease = local / 'proposal-reservation.json'
    if not args.owned:
        assert not local.exists()
        claim = reservations.claim('codex-islands-pair-'+str(uuid.uuid4()), ['building:landsd/190119:0','building:landsd/297799:0','terrain:city/data/terrain.json'], batch=BATCH, ttl=3600)
        assert claim['ok'], 'Existing owner; no takeover'
        save(lease, json.loads(json.dumps(claim['reservation'], default=str)))
        subprocess.run([sys.executable,HERE.parent/'shared-modelling/reservations.py','run','--lease-file',lease,'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
        return
    assert reservations.owns(read(lease))
    base = ROOT / 'docs/astra-city/government-import'
    doc, stage = base / BATCH, HERE / 'accepted' / BATCH
    assert not doc.exists() and not stage.exists()
    prior = base / 'government-islands-peng-chau-disjoint-terrain-20261106-v1'
    uids = ['landsd/190119:0', 'landsd/297799:0']
    pins, refs = {}, []
    def pin(path):
        key, digest = rel(path), sha(path)
        assert key not in pins or pins[key] == digest
        pins[key] = digest
    runtime = prior / 'runtime-current/results.json.gz'
    identity = base / 'government-islands-peng-chau-identity-20261106-v1/identities.json.gz'
    context = base / 'government-islands-peng-chau-context-20261106-v1/context.json.gz'
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for path in (runtime, identity, context):
            sync = read(path.parent / 'neon-sync.json')
            expected = {'path':rel(path), 'sha256':sha(path)}
            assert sync['exactResultMatch']
            assert db.execute("SELECT result->'evidence' FROM astra_modelling.jobs WHERE id=%s AND status='complete'", (sync['jobId'],)).fetchone()[0] == expected
            pin(path); pin(path.parent / 'neon-sync.json')
            refs.append({**expected, 'jobId':sync['jobId']})
        states = dict(db.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC', (uids,)))
    assert not any(s in ('held','source-unavailable','identity-unresolved','installed-verified') for s in states.values())
    old_neighbours = read(prior / 'runtime-current/neighbour-checks.final.json')
    old_patch = next(p for p in old_neighbours['patches'] if p['uids'] == [uids[0]])
    assert old_patch['blockedBy'] == [uids[1]]
    pin(prior / 'runtime-current/neighbour-checks.final.json')
    source_path = base / 'government-islands-peng-chau-source-terrain-20261106/check-selection.json.gz'
    by_uid = {r['uid']:r for r in read(source_path)['rows']}
    contexts = {r['uid']:r for r in read(context)['rows']}
    identities = {r['uid']:r for r in read(identity)['rows']}
    rows = []
    for uid in uids:
        row = copy.deepcopy(by_uid[uid]); c = contexts[uid]
        assert c['sourceSHA256'] == row['candidate']['entry']['sha256']
        if c['diagnosticReasons']:
            assert set(c['diagnosticReasons']) == {'strict-identity-fit'} and identities[uid]['passed']
            assert identities[uid]['context']['sourceSHA256'] == c['sourceSHA256']
            row['identityProof'] = identities[uid]['proof']
        rows.append(row)
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = read(manifest_path)
    installed = {m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models']}
    assert not installed.intersection(uids)
    parent_path = ROOT / '3d-viewer/city/data/terrain.json'
    old = module('paired_existing_terrain', HERE / 'tai-o-terrain-pass.py')
    parent = read(parent_path)
    terrain = read(ROOT / old_patch['path'])
    assert sha(ROOT / old_patch['path']) == old_patch['sha256']
    assert terrain['meta']['parentSha256'] == sha(parent_path)
    for p in manifest['terrainPatches']:
        path = ROOT / '3d-viewer' / p['url']; pin(path)
        assert not old.terrain_helpers.overlap(terrain['coarseCells'], read(path)['coarseCells'])
    for native in terrain['meta']['source']['nativeSources']:
        for p in native['sourceFiles']:
            assert sha(ROOT / p['path']) == p['sha256']; pin(ROOT / p['path'])
    pin(ROOT / old_patch['path']); pin(source_path); pin(parent_path); pin(manifest_path); pin(Path(__file__))
    proposed = copy.deepcopy(terrain)
    proposed['id'] = BATCH.removeprefix('government-')
    proposed['meta']['targetUids'] = uids
    assert {k:v for k,v in proposed.items() if k not in ('id','meta')} == {k:v for k,v in terrain.items() if k not in ('id','meta')}
    assert {k:v for k,v in proposed['meta'].items() if k != 'targetUids'} == {k:v for k,v in terrain['meta'].items() if k != 'targetUids'}
    old.resolve.validate_patch(proposed, parent)
    patch_path = stage / 'terrain' / (proposed['id'] + '.json'); save(patch_path, proposed); pin(patch_path)
    patch = {**old_patch, 'path':rel(patch_path), 'sha256':sha(patch_path), 'uids':uids}
    catalogue = read(HERE.parent / 'kai-tak-port/staged/catalogue.json')
    catalogue = {k:v for k,v in catalogue.items() if k not in ('area','models','counts')}
    models = []
    for row in rows:
        entry = copy.deepcopy(row['candidate']['entry'])
        assert not entry.get('supportDependencies') and not entry.get('retainedBasicSupportDependencies')
        entry.update(priority='detail', proceduralWindows=False, publicationApproved=False, placementReviewed=False, identityReviewApproved=False, sourceIdentityReviewed=False)
        source = ROOT / row['candidate']['path']; assert sha(source) == entry['sha256']; pin(source)
        target = stage / entry['asset']; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(source.read_bytes())
        models.append(entry)
    catalogue.update(area='Peng Chau unchanged original neighbour pair', models=models, counts={'packedModels':len(models)})
    save(stage / 'catalogue.json', catalogue); save(stage / 'catalogue-index.json', {'models':len(models),'catalogues':['catalogue.json']})
    save(doc / 'selection.json.gz', {'batch':BATCH, 'manifestSHA256':sha(manifest_path),'rows':rows})
    save(doc / 'terrain-candidates.json', [{'path':patch['path'],'sha256':patch['sha256']}])
    save(stage / 'plan.json', {'areas':[{'area':catalogue['area'],'catalogue':rel(stage / 'catalogue.json'),'destination':f'city/data/official-models/{BATCH}/catalogue.json','terrain':[]}], 'topLevelTerrainPatches':[{'source':patch['path'],'sha256':patch['sha256'],'destination':'city/data/'+proposed['id']+'.json','resolution':proposed['cell'],'area':catalogue['area']}]})
    affected = []
    from shapely.geometry import Polygon, box
    domain = box(*patch['bounds'])
    for tile in manifest['tiles']:
        path = ROOT / '3d-viewer' / tile['url']; pin(path)
        for b in read(path)['buildings']:
            if b.get('rings') and Polygon(b['rings'][0],b['rings'][1:]).intersects(domain):
                affected.append({'building':b,'patchIndexes':[0],'existingNative':b['uid'] in installed})
    save(doc / 'neighbour-inputs.json.gz', {'rows':affected,'candidateIds':uids,'patches':[patch],'inputHashes':pins})
    save(doc / 'identity-evidence.json.gz', {'rows':[identities[u] for u in uids if u in identities],'sourceEvidence':refs,'publication':False})
    save(doc / 'proposal.json', {'uids':uids,'terrainArraysExactlyUnchanged':True,'sourceGeometryChanges':0,'newlyInstalled':0,'publication':False,'qualification':'Fresh complete pair source/contact, all affected BASIC/native regressions and browser/publisher gates remain mandatory.'})
    save(doc / 'rebind.json', {'currentManifestSHA256':sha(manifest_path),'sourceGeometryChanges':0,'terrainGeometryChanges':0,'terrainMetadataOnlyChanges':['id','meta.targetUids'],'retainedTerrainSHA256':old_patch['sha256'],'publication':False})
    assert reservations.owns(read(lease))
    print({'privateOriginals':len(rows),'affectedForms':len(affected),'publication':False}, flush=True)


if __name__ == '__main__':
    main()
