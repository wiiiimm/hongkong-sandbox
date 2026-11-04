"""Refresh original Parkview13/14 and existing podium runtime measurements under a renewable lease."""
import json
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

UIDS = ['landsd/253980:0', 'landsd/255260:0', 'landsd/254491:0']
BATCH = 'government-xl-parkview-13-14-current-runtime-v1-20261021'
BASE = ROOT / 'docs/astra-city/government-import'
DOC = BASE / BATCH
LOCAL = HERE / 'local' / BATCH
SOURCE = BASE / 'government-xl-parkview-14-companion-projection-v2-20261021'

def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease)
    receipt,pins=authenticate(SOURCE)
    selection_path=SOURCE/'projection.json.gz'
    assert digest(selection_path.read_bytes())==pins[str(selection_path.relative_to(ROOT))]
    companion=read(selection_path)['companion']
    prior=BASE/'government-xl-next-twenty-current-terrain-v6-20261021'
    _,priorpins=authenticate(prior);oldselection=prior/'selection.json.gz'
    assert digest(oldselection.read_bytes())==priorpins[str(oldselection.relative_to(ROOT))]
    first=next(r for r in read(oldselection)['rows']if r['uid']==UIDS[0])
    tile=ROOT/'3d-viewer'/first['source']['tile'];forms={b['uid']:b for b in read(tile)['buildings']}
    assert set(UIDS)<=set(forms)
    manifest_data=read(ROOT/'3d-viewer/city/data/manifest.json')
    installed=[(m,cat['rootTranslation'])for url in manifest_data['officialModelCatalogues']for cat in [read(ROOT/'3d-viewer'/url)]for m in cat['models']if m['uid']==UIDS[2]]
    assert len(installed)==1;podium,translation=installed[0]
    podium_asset=ROOT/'3d-viewer/city/data/official-models/government-xxl-parkview-20260913/assets'/ (podium['sha256']+'.glb.gz')
    sources=[ROOT/first['candidate']['path'],ROOT/companion['assetPath'],podium_asset]
    entries=[first['candidate']['entry'],{**companion['candidate'],'rootTranslation':translation},{**podium,'rootTranslation':translation}]
    rows=[]
    for uid,asset,entry in zip(UIDS,sources,entries):
        assert entry['uid']==uid and digest(asset.read_bytes())==entry['sha256']
        target=LOCAL/'assets'/(entry['sha256']+'.glb.gz');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(asset.read_bytes())
        entry={**entry,'asset':'assets/'+target.name,'proceduralWindows':False}
        rows.append(dict(uid=uid,sourceSHA256=entry['sha256'],modelId=entry['modelId'],triangles=entry['triangles'],candidate=dict(path=str(target.relative_to(ROOT)),entry=entry),source=dict(building=forms[uid],tile=first['source']['tile'],tileSHA256=digest(tile.read_bytes()))))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_hash = digest(manifest.read_bytes())
    save(DOC / 'selection.json.gz', dict(rows=rows, manifestSHA256=manifest_hash))
    capture = HERE / 'acceptance-metrics-multi-retained.mjs'
    command = ['node', str(capture), '--selection', str((DOC / 'selection.json.gz').relative_to(ROOT)),
               '--candidates', str(LOCAL.relative_to(ROOT)),
               '--out', str((DOC / 'metrics.json').relative_to(ROOT)),
               '--geometry-out', str((LOCAL / 'runtime-geometry.json.gz').relative_to(ROOT))]
    save(DOC / 'command.json', command)
    with (DOC / 'worker.log').open('w') as log:
        subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    report = read(DOC / 'metrics.json')
    assert len(report['rows']) == 3 and all(not r.get('error') for r in report['rows']), report['rows']
    refs = [Path(__file__), SOURCE / 'result.json', selection_path, prior/'result.json', oldselection, *sources, capture,
            LOCAL / 'runtime-geometry.json.gz']
    for path, expected in report['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == expected, path
        refs.append(ROOT / path)
    assert digest(manifest.read_bytes()) == manifest_hash and reservations.owns(lease)
    module('murray_runtime_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'original-current-runtime-measurement', refs,
        dict(uids=UIDS, currentManifestSHA256=manifest_hash, runtime=report['rows'], installationApproved=False,
             nextStep='Assess current tower and podium ground contacts against the saved assembly interface; retain all installation checks.'))
    print(json.dumps(report['rows']), flush=True)

def main():
    if '--owned' in sys.argv:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim(BATCH + '-' + str(uuid.uuid4()), ['building:' + uid for uid in UIDS], batch=BATCH, ttl=3600)
    assert claim['ok'], claim
    lease = claim['reservation']
    save(LOCAL / 'reservation.json', json.loads(json.dumps(lease, default=str)))
    try:
        subprocess.run([sys.executable, str(HERE / 'harbourfront_reserved_runner_v1_20261021.py'),
                        str(LOCAL / 'reservation.json'), sys.executable, __file__, '--owned'], cwd=ROOT, check=True)
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']

if __name__ == '__main__':
    main()
