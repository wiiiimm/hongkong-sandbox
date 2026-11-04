"""Heya fresh current unchanged owned identity and complete raw strict diagnosis.
Existing original-government-owned-georef-identity-v1 only; no physical credit.
Unexecuted draft. Exact current installed support entry/source bound independently.
"""
import argparse, importlib.util, json, uuid, subprocess, sys
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations, NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files as raw_verify_files
from government_owned_identity import verify_files, POLICY
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from terrain_source_preflight import preflight, SourceSheetIndex

def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--uid', required=True)
    parser.add_argument('--input', required=True)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--owned',action='store_true',help=argparse.SUPPRESS)
    args = parser.parse_args()
    assert args.uid == 'landsd/184286:0'
    assert args.batch == 'government-xl-heya-aqua-184286-current-owned-identity-v1-20261011'
    assert args.input == 'docs/astra-city/government-import/government-xl-georef-numerical-recovery-sequence-20261008-184286-0/selection.json.gz'
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    assert args.uid.startswith('landsd/') and args.uid.endswith(':0')
    input_path = (ROOT / args.input).resolve()
    assert input_path.is_relative_to(ROOT) and input_path.is_file()
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    assert not doc.exists(), 'Never replace a frozen diagnostic attempt'
    lease_path=local/'reservation.json'
    if not args.owned:
        assert not local.exists(), 'Fresh supervised input batch only'
        claim = reservations.claim('current-original-identity-diagnostic-' + str(uuid.uuid4()),
                                   ['building:' + args.uid,'building:landsd/184285:0'], batch=args.batch, ttl=3600)
        assert claim['ok'],claim
        save(lease_path,json.loads(json.dumps(claim['reservation'],default=str)))
        status=subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(lease_path),'--ttl','3600','--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT).returncode
        assert status==0,status
        return
    lease=read(lease_path)
    assert reservations.owns(lease)
    try:
        manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
        manifest_raw = manifest_path.read_bytes()
        manifest = json.loads(manifest_raw)
        assert digest(manifest_raw) == '947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
        catalogue_paths = [ROOT/'3d-viewer'/u for u in manifest['officialModelCatalogues']]
        catalogue_pins = [ref(p) for p in catalogue_paths]
        all_entries = [(p, m) for p in catalogue_paths for m in read(p)['models']]
        assert len(all_entries) == len({m['uid'] for _,m in all_entries})
        support = [(p,m) for p,m in all_entries if m['uid']=='landsd/184285:0']
        assert len(support)==1
        support_catalogue,support_entry=support[0]
        assert (support_entry['buildingCSUID'],support_entry['modelId'],support_entry['sha256']) == ('3394422191P20151008','B339442219102063C0','46add0484e7cedd20b7de12c9843a2cba8bb419f5824dde27fb9b41fb8efa1b2')
        support_asset=support_catalogue.parent/support_entry['asset']
        assert digest(support_asset.read_bytes())==support_entry['sha256']
        matches = [row for row in read(input_path)['rows'] if row['uid'] == args.uid]
        assert len(matches) == 1
        row = dict(matches[0])
        assert (row['modelId'],row['sourceSHA256'],row['triangles'])==('B339682218601063C0','f9c73a61b679ebc18df1741c01c7e98463a4269928a38b882e3a41d268646155',17910)
        installed = {model['uid'] for url in manifest['officialModelCatalogues']
                     for model in read(ROOT / '3d-viewer' / url)['models']}
        assert args.uid not in installed
        source_path = ROOT / row['candidate']['path']
        source_raw = source_path.read_bytes()
        assert digest(source_raw) == row['sourceSHA256']
        triangles = decode_original_world_triangles(source_raw)
        assert len(triangles) == row['triangles'] and np.isfinite(triangles).all()
        low, high = triangles.min(axis=(0, 1)), triangles.max(axis=(0, 1))
        final = module('diagnostic_complete_current_forms', 'xl-final-script-pass.py')
        forms = final.load_forms([low[0]-2, low[2]-2, high[0]+2, high[2]+2])
        own = [item for item in forms if item[0]['uid'] == args.uid]
        assert len(own) == 1
        form, _, tile = own[0]
        assert form['buildingCSUID'] == row['source']['building']['buildingCSUID']
        row['source'] = dict(building=form, tile=tile,
                             tileSHA256=digest((ROOT/'3d-viewer'/tile).read_bytes()))
        context = dict(uid=args.uid, sourceSHA256=row['sourceSHA256'],
                       identity=final.identity_context(row, triangles, forms),
                       neighbourTileHashes={t: digest((ROOT/'3d-viewer'/t).read_bytes())
                                            for _, _, t in forms})
        with connect() as connection:
            connection.execute('SET TRANSACTION READ ONLY')
            native = connection.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',
                                        (NATIVE_RUN, row['native']['cacheKey'])).fetchone()
            assert native == (row['native']['resultSha'],)
            source_rows=read(ROOT/'docs/astra-city/government-import/government-xl-georef-sparkle-heya-original-supports-20261008/support-inputs.json')['sources']
            source_rows=[r for r in source_rows if r['uid'] in (args.uid,'landsd/184285:0')]
            assert len(source_rows)==2 and len({r['uid'] for r in source_rows})==2
            native_rows=connection.execute("SELECT r.cache_key,m,i.sheet,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_members membership USING(cache_key), LATERAL jsonb_array_elements(r.result->'models')m WHERE membership.run_id=%s AND m->>'modelId' IN ('B339682218601063C0','B339442219102063C0') ORDER BY m->>'modelId'",(NATIVE_RUN,)).fetchall()
            assert len(native_rows)==2 and len({(k,m['modelId']) for k,m,_,_ in native_rows})==2
            for r in source_rows:
                matches=[(k,m,s,h) for k,m,s,h in native_rows if m['modelId']==r['modelId']]
                assert len(matches)==1
                k,m,sheet,h=matches[0]
                assert (k,h,m,sheet)==(r['native']['cacheKey'],r['native']['resultSha'],r['native']['model'],r['native']['sheet'])
        save(doc/'complete-two-native-source-memberships.json',dict(nativeRun=NATIVE_RUN,rows=[dict(cacheKey=k,model=m,sheet=s,resultSHA256=h)for k,m,s,h in native_rows],sourceInputs=ref(ROOT/'docs/astra-city/government-import/government-xl-georef-sparkle-heya-original-supports-20261008/support-inputs.json')))
        raw_identity = raw_verify_files(row, context, local/'raw-full-cell-identity')
        identity = verify_files(row, context, local/'original-source-identity')
        assert identity['policy']==POLICY and identity['uid']==args.uid
        save(doc/'raw-full-cell-identity.json', raw_identity)
        save(doc/'installed-support-entry.json',dict(catalogue=ref(support_catalogue),asset=ref(support_asset),entry=support_entry))
        save(doc/'all-current-catalogues.json',dict(rows=catalogue_pins,manifestSHA256=digest(manifest_raw)))
        index_path = ROOT/'source-scripts/city/landmark-acquisition/index.json'
        routing = preflight(row, context, SourceSheetIndex(read(index_path)))
        routing.update(legacyProjectionIdentity=routing['identity'], identity=identity,
                       canStartTerrainWork=False, uid=args.uid, currentForms=len(forms))
        assert manifest_path.read_bytes() == manifest_raw and reservations.owns(lease)
        for pin in catalogue_pins: assert ref(ROOT/pin['path'])==pin
        assert digest(support_asset.read_bytes())==support_entry['sha256']
        save(doc/'selection.json.gz', dict(rows=[row], manifestSHA256=digest(manifest_raw)))
        save(doc/'context.json.gz', dict(rows=[context]))
        save(doc/'complete-current-forms.json.gz', dict(rows=[b for b, _, _ in forms]))
        save(doc/'identity.json', identity)
        save(doc/'indexed-diagnostic.json', routing)
        (doc/'captured-manifest.json').write_bytes(manifest_raw)
        freeze = module('diagnostic_immutable_neon_receipt', 'xl-popcorn-source-investigations-checkpoints-20261009.py')
        inputs = [Path(__file__), input_path, source_path, index_path,
                  HERE/'exact_original_georef_cell_identity_20261009.py',
                  HERE/'government_owned_identity.py', HERE/'original_source_ownership.py', HERE/'georef_projection_coverage.py', HERE/'xl-second-pass.py',
                  support_asset, *catalogue_paths, ROOT/'docs/astra-city/government-import/government-xl-georef-sparkle-heya-original-supports-20261008/support-inputs.json',
                  HERE/'exact_packed_world_geometry_20261009.py',
                  HERE/'xl-final-script-pass.py', HERE/'terrain_source_preflight.py']
        inputs += [p for p in local.rglob('*') if p.is_file()]
        inputs += [ROOT/'3d-viewer'/t for _, _, t in forms]
        result = freeze.freeze(args.batch, 'heya-current-unchanged-owned-identity-no-physical-credit-v1', inputs,
            dict(uids=[args.uid], sourceSHA256=row['sourceSHA256'],
                 manifestSHA256=digest(manifest_raw), completeOriginalFaces=len(triangles),
                 completeCurrentForms=len(forms), rawIdentityPassed=raw_identity['passed'],
                 rawIdentityReasons=raw_identity['reasons'], rawFullCellIdentityPassed=raw_identity['passed'],
                 ownedIdentityReasons=identity['reasons'], identityAccepted=identity['passed'], physicalAccepted=False,
                 scriptFullAcceptancePassed=False, canStartTerrainWork=False,
                 currentHeldReason='source-envelope-identity-unresolved' if not identity['passed'] else 'independent-complete-physical-checks-required',
                 nextStep='Run fresh actual source/support four-world capture, ordinary no-terrain physical diagnosis, then exact genuine ground/interface and58 terminal visual account. No historical runtime proof transfers across changed viewer modules.',
                 qualification='The unchanged existing owned GeoRef identity policy is replayed independently of the retained raw strict cell proof. Positive owned identity grants no physical, source-support, native reapproval, terrain, collision, component role or installation credit. Exact current installed podium entry/source is context only. Rendering must be newly captured against actual current production modules.'))
        print(json.dumps(dict(uid=args.uid, rawIdentityPassed=raw_identity['passed'],
                              reasons=identity['reasons'], jobId=result['jobId'],
                              publication=False)), flush=True)
    finally:
        # The existing supervisor owns release; never remove a lease while its
        # numerical child is still active. It records release on every outcome.
        pass

if __name__ == '__main__':
    main()
