"""Rebind unchanged selected original sources to the exact current map; no approval transfer."""
import argparse
from copy import deepcopy
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--uid', action='append', required=True)
    parser.add_argument('--feature-scope-review', required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / args.batch
    assert not doc.exists()
    _, pins = authenticate(base / args.capture)
    path = base / args.capture / 'selection.json.gz'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    wanted = set(args.uid)
    assert 0 < len(wanted) == len(args.uid) <= 40
    rows = deepcopy([r for r in read(path)['rows'] if r['uid'] in wanted])
    assert {r['uid'] for r in rows} == wanted
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    manifestsha = digest(manifestpath.read_bytes())
    manifest = read(manifestpath)
    refs = [Path(__file__), base / args.capture / 'result.json', path, manifestpath]
    for url in manifest['officialModelCatalogues']:
        catalogue = ROOT / '3d-viewer' / url
        assert not wanted & {r['uid'] for r in read(catalogue)['models']}, 'Source is already installed'
        refs.append(catalogue)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for row in rows:
            asset = ROOT / row['candidate']['path']
            assert digest(asset.read_bytes()) == row['sourceSHA256'] == row['candidate']['entry']['sha256']
            refs.append(asset)
            tile = ROOT / '3d-viewer' / row['source']['tile']
            building = next(b for b in read(tile)['buildings'] if b['uid'] == row['uid'])
            assert building == row['source']['building'], 'Changed current source form requires fresh investigation'
            row['source']['tileSHA256'] = digest(tile.read_bytes())
            refs.append(tile)
            key = row['native']['cacheKey']
            found = db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s', (key,)).fetchone()
            assert found and found[0] == row['native']['resultSha']
            model = next(m for m in found[1]['models'] if m['modelId'] == row['modelId'])
            assert model == row['native']['model'] and model['asset']['sha256'] == row['sourceSHA256']
            entry = row['candidate']['entry']
            for field in ['sourceIdentityReviewed', 'identityReviewApproved', 'placementReviewed', 'publicationApproved']:
                assert not entry.get(field), 'Refuse to transfer prior source approval'
    scopefolder=base/args.feature_scope_review
    scope_receipt,scope_pins=authenticate(scopefolder)
    scopepath=scopefolder/'prepared-scope.json'
    assert digest(scopepath.read_bytes())==scope_pins[str(scopepath.relative_to(ROOT))]
    scope=read(scopepath)
    assert scope_receipt['sourceIdentityInterpretationApproved'] is True and len(rows)==1
    row=rows[0];entry=row['candidate']['entry'];building=row['source']['building']
    assert scope['uid']==row['uid'] and scope['sha256']==row['sourceSHA256'] and scope['modelId']==row['modelId'] and scope['worldBounds']==entry['worldBounds']
    current=dict(uid=building['uid'],objectId=building['objectId'],buildingCSUID=building['buildingCSUID'],parent=building.get('parent'),osmRefs=building.get('osmRefs'),rings=building['rings'],baseHeightHKPD=building.get('baseHeightHKPD'),topHeightHKPD=building.get('topHeightHKPD'))
    assert scope['form']==current and scope['identityReviewed'] is True
    reviewpath=ROOT/scope['sourceReview']['path']
    assert digest(reviewpath.read_bytes())==scope['sourceReview']['sha256']==scope_pins[str(reviewpath.relative_to(ROOT))]
    key='reviewed-original-feature:'+row['uid']
    data=ROOT/'3d-viewer/city/official-model-reviewed-original-feature-data.js'
    import json
    registry=json.loads(data.read_text().split('Object.freeze(',1)[1].rsplit(');',1)[0])
    assert registry[key]==scope and not entry.get('variantId') and not entry.get('suppressesBuildingUids') and not entry.get('footprintScope')
    entry['footprintScope']=key
    refs.extend([scopefolder/'result.json',scopepath,reviewpath,data,ROOT/'3d-viewer/city/official-model-reviewed-original-feature-footprint.js',ROOT/'3d-viewer/city/official-model-footprint-scopes.js'])
    assert digest(manifestpath.read_bytes()) == manifestsha
    save(doc / 'selection.json.gz', dict(rows=rows, manifestSHA256=manifestsha))
    result = dict(uids=sorted(wanted), sourceSHA256ByUid={r['uid']:r['sourceSHA256'] for r in rows}, currentManifestSHA256=manifestsha, installationApproved=False, publication=False, sourceGeometryChanges=0, scriptExternalAICalls=0, qualification='Exact unchanged source/form/native record rechecked against current catalogue and manifest. Only explicit exact-source identity extent review is reused for loader routing. No geometry capture, terrain, foundation, placement, runtime or browser approval transferred.')
    save(doc / 'summary.json', result)
    module('refresh_selection_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'current-unapproved-original-source-selection', refs, result)


if __name__ == '__main__':
    main()
