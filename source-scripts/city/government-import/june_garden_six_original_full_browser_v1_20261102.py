"""Private full six-original/69-retained desktop/mobile day-night checks; no publish.

The existing source metadata contract, unchanged source bytes and complete
reservation scope remain mandatory. Every deliberately failed peer must keep
the complete BASIC group; retry must activate the entire group atomically.
"""
import argparse, copy, json, os, shutil, socket, subprocess, sys, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from original_coordinated_retained_contract_v1_20261027 import verify_metadata

BASE = ROOT/'docs/astra-city/government-import'
RUNTIME = 'government-xl-tower3-june-garden-six-originals-current-v1-20261102-runtime'
PATCH = 'government-xl-tower3-227380-retained-chain-validated-v4-20261102'
SCOPE = 'government-xl-tower3-227380-chain-current-checks-v1-20261102-scope'
PRIMARY, SMALL = 'landsd/227380:0', 'landsd/264492:0'
TOWERS = ['landsd/264489:0','landsd/264491:0','landsd/264493:0','landsd/264495:0']
PORT = 4197


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',required=True); p.add_argument('--resources-plan',required=True)
    p.add_argument('--owned',action='store_true'); a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    doc, local = BASE/a.batch, HERE/'local'/a.batch
    pp = (ROOT/a.resources_plan).resolve(); assert pp.is_relative_to(BASE)
    resources = sorted(set(read(pp)['resources'])|{f'server:127.0.0.1:{PORT}'})
    lp = local/'reservation.json'
    if not a.owned:
        assert not doc.exists() and not local.exists()
        c = reservations.claim('june-garden-private-atomic-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=3600)
        assert c['ok'], c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease = read(lp); assert reservations.owns(lease) and set(lease['resources']) == set(resources)
    assert not doc.exists(); refs, pins = [Path(__file__),pp], {}
    def take(batch,path):
        if batch not in pins:
            receipt,pins[batch] = authenticate(BASE/batch); refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    selection = take(RUNTIME,BASE/RUNTIME/'selection.json.gz')
    rows = {r['uid']:r for r in selection['rows']}; ids = sorted([PRIMARY,SMALL,*TOWERS])
    assert set(rows) == set(ids)
    sources = {u:rows[u]['sourceSHA256'] for u in ids}
    original = {u:copy.deepcopy(rows[u]['candidate']['entry']) for u in ids}
    # Recover required provenance omitted by legacy unapproved packers.
    # Same guarded native-input/result join as the existing generic preview.
    provenance = {}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for uid in ids:
            native = rows[uid]['native']
            values = db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s',(native['cacheKey'],)).fetchall()
            assert len(values) == 1 and values[0][1] == native['resultSha']
            sheet = values[0][0]; assert isinstance(sheet,str) and sheet
            if 'sourceTile' in original[uid]: assert original[uid]['sourceTile'] == sheet
            original[uid]['sourceTile'] = sheet
            provenance[uid] = dict(sourceTile=sheet,cacheKey=native['cacheKey'],resultSHA256=native['resultSha'],sourceSHA256=sources[uid],geometryChanges=0)
    doc.mkdir(); save(doc/'source-tile-provenance.json',provenance)
    save(doc/'complete-unapproved-source-entries.json',original)
    refs.extend([doc/'source-tile-provenance.json',doc/'complete-unapproved-source-entries.json'])
    supports = dict.fromkeys(TOWERS,PRIMARY); models = []
    for uid in ids:
        row = rows[uid]; asset = ROOT/row['candidate']['path']; raw = asset.read_bytes()
        assert digest(raw) == sources[uid] == original[uid]['sha256']
        assert len(raw) == original[uid]['bytes']; refs.append(asset)
        model = copy.deepcopy(original[uid]); assert not model.get('supportDependencies')
        assert not model.get('publicationApproved') and not model.get('placementReviewed')
        model.update(asset='assets/'+sources[uid]+'.glb.gz',priority='landmark',
                     proceduralWindows=False,activationGroup=ids,
                     publicationApproved=False,placementReviewed=False)
        if uid in supports:
            model['supportDependencies'] = [dict(uid=PRIMARY,state='installed',
                buildingCSUID=original[PRIMARY]['buildingCSUID'],sha256=sources[PRIMARY])]
        target = local/model['asset']; target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(raw); models.append(model)
    assert verify_metadata(models,sources,supports,original,{PRIMARY:None,SMALL:None})
    catalogue = dict(schemaVersion=1,kind='staged-official-model-catalogue',
        crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',
        datasetId='landsd_rcd_1742809441342_98380',area='Private June Garden original diagnostic',
        coordinatePolicy='Unchanged native source nodes/float bits; one city translation, no terrain draping or vertical multiplier',
        counts=dict(packedModels=len(models)),rootTranslation=[-834500,0,816500],models=models)
    save(local/'catalogue.json',catalogue)
    save(local/'source-forms.json',[rows[u]['source']['building'] for u in ids])
    manifestpath = ROOT/'3d-viewer/city/data/manifest.json'; before = digest(manifestpath.read_bytes())
    assert before == selection['manifestSHA256']; refs.append(manifestpath); manifest = read(manifestpath)
    current = set()
    for url in manifest['officialModelCatalogues']:
        path = ROOT/'3d-viewer'/url; refs.append(path)
        for entry in read(path)['models']:
            assert entry['uid'] not in current; current.add(entry['uid'])
    assert len(current) == 7095 and not current&set(ids)
    proposal,pins[PATCH] = authenticate(BASE/PATCH); refs.append(BASE/PATCH/'result.json')
    assert proposal['status'] == 'private-three-member-chain-surface-validator-passed'
    assert proposal['allEffectiveMembersRequired'] is True and len(proposal['members']) == 3
    terrain = []
    for member in proposal['members']:
        candidate = ROOT/member['candidate']['path']; data = take(PATCH,candidate)
        assert digest(candidate.read_bytes()) == member['candidate']['sha256']
        old = ROOT/'3d-viewer'/member['replaces']['url']; refs.append(old)
        assert digest(old.read_bytes()) == member['replaces']['sha256']
        assert sum(r['url'] == member['replaces']['url'] for r in manifest['terrainPatches']) == 1
        terrain.append(dict(source=str(candidate.relative_to(ROOT)),sha256=member['candidate']['sha256'],
            destination='city/data/private-june-garden-atomic-'+member['member']+'.json',
            resolution=data['cell'],area='Private June Garden original diagnostic',replaces=member['replaces']))
    scope = take(SCOPE,BASE/SCOPE/'scope.json')
    assert {'building:'+u for u in scope['touchingNativeUids']} <= set(resources)
    config = dict(diagnosticOnly=True,publication=False,stage=str(local.relative_to(ROOT))+'/',
        catalogueURL='city/data/official-models/'+a.batch+'/catalogue.json',
        viewerURL=f'http://127.0.0.1:{PORT}/city.html',terrain=terrain,availabilityOverlays=[],
        viewportWidths=[1280,390],nativeSupportUidsByModel={u:[PRIMARY] for u in TOWERS},
        atomicCaptureDirectionByViewport={1280:[-1,1.8,-1],390:[-1,2.6,-1]})
    configpath = local/'config.json'; save(configpath,config)
    refs.extend([configpath,local/'catalogue.json',local/'source-forms.json',
                 HERE/'original_coordinated_retained_contract_v1_20261027.py'])
    # Exercise the exact production parser before launching a browser/server.
    parser_code = "import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';import {prepareModelCatalogue} from './3d-viewer/city/official-model-assets.js';const data=JSON.parse(await readFile(process.argv[1],'utf8'));const models=prepareModelCatalogue(data,process.argv[2]);assert.equal(models.length,6);console.log('Production catalogue parser: six unchanged originals accepted');"
    subprocess.run(['node','--input-type=module','-e',parser_code,str(local/'catalogue.json'),
        f'http://127.0.0.1:{PORT}/'+config['catalogueURL']],cwd=ROOT,check=True)
    tool = HERE/'ronsdale_three_live_browser_v16_20261027.mjs'; refs.append(tool)
    config.update(doc=str(doc.relative_to(ROOT))+'/',additionalRetainedUids=sorted(scope['touchingNativeUids']),
        failureTestUids=[],catalogueReplacements=[],fitBox=True,
        captureDirectionByModel={u:[-1,2.6,-1] for u in ids})
    assert len(config['additionalRetainedUids']) == 69
    save(configpath,config)
    for name in ['app.js','official-models.js','streaming.js','model-group-lifecycle.js',
                 'model-activation-groups.js','model-support.js','official-model-assets.js',
                 'tile-cache.js','model-variants.js','model-byte-cache.js']:
        refs.append(ROOT/'3d-viewer/city'/name)
    bound = {str(path.relative_to(ROOT)):digest(path.read_bytes()) for path in refs}
    # Reserve and use only our own diagnostic server; never stop an existing one.
    with socket.socket() as probe: probe.bind(('127.0.0.1',PORT))
    server = None
    with (doc/'server.log').open('w') as serverlog, (doc/'browser.log').open('w') as browserlog:
        try:
            server = subprocess.Popen([sys.executable,'-m','http.server',str(PORT),
                '--bind','127.0.0.1','--directory',str(ROOT/'3d-viewer')],stdout=serverlog,stderr=subprocess.STDOUT)
            import time, urllib.request
            for attempt in range(50):
                assert server.poll() is None, 'Own diagnostic server failed'
                try:
                    with urllib.request.urlopen(config['viewerURL'],timeout=1) as response: assert response.status == 200
                    break
                except OSError: time.sleep(.1)
            else: raise RuntimeError('Own diagnostic server did not become ready')
            subprocess.run(['node',str(tool),'staged',str(configpath.relative_to(ROOT))],
                cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},stdout=browserlog,
                stderr=subprocess.STDOUT,check=True,timeout=7200)
        finally:
            if server is not None:
                server.terminate()
                try: server.wait(timeout=10)
                except subprocess.TimeoutExpired: server.kill(); server.wait(timeout=10)
    report = read(doc/'staged-browser.json')
    assert report['passed'] and not report['errors']
    views = report['retainedNativeOwnViews']
    assert len(views) == 276
    assert {(v['uid'],v['time'],v['width']) for v in views} == {(u,t,w) for u in scope['touchingNativeUids'] for t in ['15:00','22:00'] for w in [1280,390]}
    assert all(v['active'] and v['visible'] and v['fallbackFaces'] == 0 for v in views)
    for path, sha in bound.items(): assert digest((ROOT/path).read_bytes()) == sha
    assert reservations.owns(lease) and digest(manifestpath.read_bytes()) == before
    refs.extend([doc/'staged-browser.json',doc/'browser.log',doc/'server.log'])
    refs.extend(doc.rglob('*.png'))
    summary = dict(uids=ids,sourceSHA256ByUid=sources,retainedNativeActors=69,passed=True,
        originalGovernmentGeometryChanges=0,sourcePoseChanges=0,productionChanges=0,
        newlyInstalled=0,physicalAcceptance=False,visualAcceptance=False,
        installationApproved=False,publication=False,qualification=__doc__)
    save(doc/'summary.json',summary)
    module('june_garden_full_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'private-six-original-69-retained-full-browser-diagnostic',refs,summary)


if __name__ == '__main__': main()
