"""One Peking complete-record projection diagnostic; preserve every raw failure.

This read-only scene audit never approves a source or starts terrain work. Unlike
the ordinary acceptance preflight, a failed identity check is a durable outcome.
"""
import argparse, importlib.util, json, uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations, NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files
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
    args = parser.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    assert args.uid.startswith('landsd/') and args.uid.endswith(':0')
    input_path = (ROOT / args.input).resolve()
    assert input_path.is_relative_to(ROOT) and input_path.is_file()
    doc = ROOT / 'docs/astra-city/government-import' / args.batch
    local = HERE / 'local' / args.batch
    assert not doc.exists(), 'Never replace a frozen diagnostic attempt'
    claim = reservations.claim('current-original-identity-diagnostic-' + str(uuid.uuid4()),
                               ['building:' + args.uid], batch=args.batch, ttl=3600)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
        manifest_raw = manifest_path.read_bytes()
        manifest = json.loads(manifest_raw)
        matches = [row for row in read(input_path)['rows'] if row['uid'] == args.uid]
        assert len(matches) == 1
        row = dict(matches[0])
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
        import shapely
        final.projection = lambda faces: shapely.union_all(shapely.polygons(np.asarray(faces)[:, :, [0, 2]]))
        assert args.uid == 'landsd/233985:0', 'Named source diagnostic only'
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
        identity = verify_files(row, context, local/'original-source-identity')
        index_path = ROOT/'source-scripts/city/landmark-acquisition/index.json'
        routing = preflight(row, context, SourceSheetIndex(read(index_path)))
        routing.update(legacyProjectionIdentity=routing['identity'], identity=identity,
                       canStartTerrainWork=False, uid=args.uid, currentForms=len(forms))
        assert manifest_path.read_bytes() == manifest_raw and reservations.owns(lease)
        save(doc/'selection.json.gz', dict(rows=[row], manifestSHA256=digest(manifest_raw)))
        save(doc/'context.json.gz', dict(rows=[context]))
        save(doc/'complete-current-forms.json.gz', dict(rows=[b for b, _, _ in forms]))
        save(doc/'identity.json', identity)
        save(doc/'indexed-diagnostic.json', routing)
        (doc/'captured-manifest.json').write_bytes(manifest_raw)
        freeze = module('diagnostic_immutable_neon_receipt', 'xl-popcorn-source-investigations-checkpoints-20261009.py')
        inputs = [Path(__file__), input_path, source_path, index_path,
                  HERE/'exact_original_georef_cell_identity_20261009.py',
                  HERE/'exact_packed_world_geometry_20261009.py',
                  HERE/'xl-final-script-pass.py', HERE/'terrain_source_preflight.py']
        inputs += [p for p in local.rglob('*') if p.is_file()]
        inputs += [ROOT/'3d-viewer'/t for _, _, t in forms]
        result = freeze.freeze(args.batch, 'complete-current-original-identity-diagnostic-v1', inputs,
            dict(uids=[args.uid], sourceSHA256=row['sourceSHA256'],
                 manifestSHA256=digest(manifest_raw), completeOriginalFaces=len(triangles),
                 completeCurrentForms=len(forms), rawIdentityPassed=identity['passed'],
                 rawIdentityReasons=identity['reasons'], identityAccepted=False,
                 scriptFullAcceptancePassed=False, canStartTerrainWork=False,
                 currentHeldReason='source-envelope-identity-unresolved' if not identity['passed'] else 'independent-complete-physical-checks-required',
                 nextStep='Review the complete source envelope and named related actors; preserve all raw identity reasons and complete independent physical/runtime gates.',
                 qualification='Diagnostic only. Raw passes or failures grant no installation, permanent rejection, skip credit, related-actor collision exemption or terrain acceptance.'))
        print(json.dumps(dict(uid=args.uid, rawIdentityPassed=identity['passed'],
                              reasons=identity['reasons'], jobId=result['jobId'],
                              publication=False)), flush=True)
    finally:
        assert reservations.release(lease)['ok']

if __name__ == '__main__':
    main()
