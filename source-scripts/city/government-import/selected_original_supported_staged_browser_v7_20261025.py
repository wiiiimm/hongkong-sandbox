"""V7: retain V6 guards with the existing OSM source-form lease namespace."""
import argparse
import math
import copy
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'patch', 'review']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--support', action='append', default=[], help='sourceUid,supportUid')
    parser.add_argument('--retain-basic', action='append', default=[])
    parser.add_argument('--retain-native',action='append',default=[])
    parser.add_argument('--installed-support-update',action='store_true')
    parser.add_argument('--owned', action='store_true')
    parser.add_argument('--capture-direction',nargs=3,type=float,required=True)
    parser.add_argument('--source-camera',action='append',default=[],help='uid,dx,dy,dz; inspection camera only')
    parser.add_argument('--retained-camera',action='append',default=[],help='uid,dx,dy,dz; inspection camera only')
    parser.add_argument('--camera-nomination',action='append',default=[])
    args = parser.parse_args()
    assert all(math.isfinite(v)for v in args.capture_direction)and args.capture_direction[1]>0
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / args.batch, HERE / 'local' / args.batch
    leasepath = local / 'reservation.json'
    refs, receipts, pins = [Path(__file__)], {}, {}
    for name in [args.runtime, args.patch, args.review,*args.camera_nomination]:
        receipt, bound = authenticate(base / name)
        receipts[name] = receipt
        refs.append(base / name / 'result.json')
        for key, sha in bound.items():
            assert key not in pins or pins[key] == sha
            pins[key] = sha
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selection = take(base / args.runtime / 'selection.json.gz')
    rows = selection['rows']
    uids = [r['uid'] for r in rows]
    assert len(uids) == len(set(uids)) and len(uids) <= 40
    supports = dict(pair.split(',') for pair in args.support)
    assert set(supports) <= set(uids) and set(supports.values()) <= set(uids)
    review = take(base / args.review / 'ROOT-PHYSICAL-REVIEW.json')
    assert review['sourceSpecificPhysicalInterpretationAccepted']
    assert review['sourceSHA256ByUid'] == {r['uid']: r['sourceSHA256'] for r in rows}
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.append(manifest)
    if not args.owned:
        assert not doc.exists() and not local.exists()
        resources=review['leaseResources']
        assert {('building:' if uid.startswith('landsd/') else 'source-form:')+uid for uid in uids+args.retain_basic+args.retain_native} <= set(resources)
        claim = reservations.claim(args.batch + '-' + str(uuid.uuid4()), resources, batch=args.batch, ttl=3600)
        assert claim['ok'], claim
        lease = claim['reservation']
        save(leasepath, json.loads(json.dumps(lease, default=str)))
        try:
            subprocess.run([sys.executable, str(HERE / 'harbourfront_reserved_runner_v1_20261021.py'), str(leasepath), sys.executable, __file__, *sys.argv[1:], '--owned'], cwd=ROOT, check=True)
        finally:
            if reservations.owns(lease):
                assert reservations.release(lease)['ok']
        return
    lease = read(leasepath)
    assert reservations.owns(lease) and not doc.exists()
    assert set(review['leaseResources']) <= set(lease['resources'])
    assert set(args.retain_native)==set(review['retainedNativeUids'])
    assert supports==review['supportByUid']
    entries = []
    for row in rows:
        uid = row['uid']
        source = row['source']
        tile = ROOT / '3d-viewer' / source['tile']
        assert next(b for b in read(tile)['buildings'] if b['uid'] == uid) == source['building']
        refs.append(tile)
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            native = db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s', (row['native']['cacheKey'],)).fetchone()
        assert native and native[1] == row['native']['resultSha']
        entry = copy.deepcopy(row['candidate']['entry'])
        if uid in supports:
            support = next(r for r in rows if r['uid'] == supports[uid])
            entry['supportDependencies'] = [dict(uid=support['uid'], state='installed', buildingCSUID=support['source']['building']['buildingCSUID'], sha256=support['sourceSHA256'])]
        entry.update(sourceTile=native[0], priority='landmark', proceduralWindows=False, publicationApproved=False, placementReviewed=False)
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256']
        refs.append(asset)
        entry['asset'] = 'assets/' + row['sourceSHA256'] + '.glb.gz'
        destination = local / entry['asset']
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(asset.read_bytes())
        entries.append(entry)
    save(local / 'catalogue.json', dict(schemaVersion=1, kind='staged-official-model-catalogue', datasetId='landsd_rcd_1742809441342_98380', crs='EPSG:2326', verticalDatum='Hong Kong Principal Datum', rootTranslation=[-834500, 0, 816500], models=entries, counts=dict(packedModels=len(entries))))
    save(local / 'catalogue-index.json', dict(models=len(entries), catalogues=['catalogue.json']))
    save(local / 'source-forms.json', [r['source']['building'] for r in rows])
    save(local / 'validation-forms.json', {r['uid']: r['source'] for r in rows})
    candidate = receipts[args.patch]['candidate']
    terrainpath = ROOT / candidate['path']
    assert digest(terrainpath.read_bytes()) == candidate['sha256']
    refs.append(terrainpath)
    terrain = [dict(source=candidate['path'], destination='city/data/' + args.batch + '-terrain.json', sha256=candidate['sha256'], resolution=read(terrainpath)['cell'], area='Private original-source diagnostic')]
    if candidate.get('replaces'):
        replacement=candidate['replaces']
        replaced_path=ROOT/'3d-viewer'/replacement['url']
        assert digest(replaced_path.read_bytes())==replacement['sha256']
        assert set(replacement['retainedUids'])<=set(args.retain_native)
        refs.append(replaced_path)
        terrain[0]['replaces']=replacement
    catalogue_replacements=[]
    if args.installed_support_update:
        update=review['installedSupportUpdate']
        assert update['ownerUid'] in args.retain_native and update['changedFields']==['supportDependencies']
        current=ROOT/'3d-viewer'/update['url'];afterpath=ROOT/update['source']
        assert digest(current.read_bytes())==update['beforeSHA256'] and digest(afterpath.read_bytes())==update['sha256']
        before,after=read(current),read(afterpath)
        assert [m for m in before['models'] if m['uid']==update['ownerUid']]==[update['beforeEntry']]
        assert [m for m in after['models'] if m['uid']==update['ownerUid']]==[update['afterEntry']]
        expected=copy.deepcopy(before)
        changed=next(m for m in expected['models'] if m['uid']==update['ownerUid'])
        changed['supportDependencies']=update['afterEntry']['supportDependencies']
        assert expected==after
        assert {k:v for k,v in update['beforeEntry'].items()if k!='supportDependencies'}=={k:v for k,v in update['afterEntry'].items()if k!='supportDependencies'}
        for dep in changed['supportDependencies']:
            parent=next(r for r in rows if r['uid']==dep['uid'])
            assert dep['state']=='installed' and dep['sha256']==parent['sourceSHA256'] and dep['buildingCSUID']==parent['source']['building']['buildingCSUID']
        refs.extend([current,afterpath])
        catalogue_replacements.append(update)
    else:
        assert not review.get('installedSupportUpdate'),'Exact reviewed support replacement must be staged'
    tool = HERE / 'ronsdale_three_live_browser_v10_20261024.mjs'
    refs.append(tool)
    directions={uid:args.capture_direction for uid in uids}
    for name in args.camera_nomination:
        nomination=take(base/name/'summary.json');assert len(nomination['uids'])==1 and nomination['uids'][0]in uids;uid=nomination['uids'][0]
        assert nomination['sourceSHA256']==next(r['sourceSHA256']for r in rows if r['uid']==uid)and nomination['currentManifestSHA256']==selection['manifestSHA256']and not nomination['visualAcceptance']and not nomination['installationApproved']
        directions[uid]=nomination['cameraDirection']
    retained_directions={}
    for values,allowed,target in [(args.source_camera,set(uids),directions),(args.retained_camera,set(args.retain_native),retained_directions)]:
        seen=set()
        for text in values:
            parts=text.split(',');assert len(parts)==4;uid=parts[0];vector=list(map(float,parts[1:]))
            assert uid in allowed and uid not in seen and all(math.isfinite(v)for v in vector)and vector[1]>0
            seen.add(uid);target[uid]=vector
    config = dict(retainedNativeOwnViews=True,dependencyFallbackRetainedUids=[u['ownerUid']for u in catalogue_replacements],retainedCaptureDirectionByModel=retained_directions,additionalRetainedUids=args.retain_native,catalogueReplacements=catalogue_replacements,stage=str(local.relative_to(ROOT)) + '/', catalogueURL='city/data/official-models/' + args.batch + '/catalogue.json', terrain=terrain, browserUids=uids, fitBox=True, captureDirectionByModel=directions, retainedBuildingUids=args.retain_basic, jointUids=uids, nativeSupportUidsByModel={uid: [support] for uid, support in supports.items()})
    preflightpath = local / 'preflight-config.json'
    save(preflightpath, dict(**config, doc=str(doc.relative_to(ROOT)) + '/'))
    subprocess.run(['node', str(tool), 'preflight', str(preflightpath.relative_to(ROOT))], cwd=ROOT, check=True)
    for width in [1280, 390]:
        assert reservations.owns(lease)
        path = local / f'browser-config-{width}.json'
        save(path, dict(**config, viewportWidths=[width], failureTestUids=uids if width == 390 else [], doc=str((doc / str(width)).relative_to(ROOT)) + '/'))
        doc.mkdir(parents=True, exist_ok=True)
        with (doc / f'browser-{width}.log').open('w') as log:
            proc = subprocess.run(['node', str(tool), 'staged', str(path.relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, env={**os.environ, 'CHROME_PATH': '/opt/google/chrome/chrome'}, timeout=1200)
        save(doc / f'command-{width}.json', dict(exitCode=proc.returncode))
        assert proc.returncode == 0 and read(doc / str(width) / 'staged-browser.json')['passed']
    for path in set(refs):
        key = str(path.relative_to(ROOT))
        if key in pins:
            assert digest(path.read_bytes()) == pins[key]
    assert reservations.owns(lease)
    refs.extend(path for path in local.rglob('*') if path.is_file() and path.name != 'reservation.json')
    result = dict(uids=uids,retainedNativeUids=args.retain_native,installedSupportUpdateStaged=bool(catalogue_replacements),installationApproved=False, visualAcceptance=False, sourceGeometryChanges=0, scriptExternalAICalls=0)
    module('selected_browser_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'selected-private-original-desktop-mobile-browser', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
