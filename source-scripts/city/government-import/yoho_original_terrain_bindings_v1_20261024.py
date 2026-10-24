"""Bind previously acquired exact government terrain to the unchanged Yoho podium.
Historical terrain inputs only; no old physical approval is transferred.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-next-repairs-yoho-podium-original-terrain-bindings-v1-20261024'
OLD='xl-terrain-recovery-20261012-yoho-untouched-sheets-parent-mask-failures-v1'
CURRENT='government-xl-next-repairs-yoho-two-current-runtime-v1-20261024'
UID='landsd/231756:0'

def main():
    out=BASE/BATCH;assert not out.exists();old,pins=authenticate(BASE/OLD);_,current=authenticate(BASE/CURRENT)
    assert UID in old['uids'];selection=BASE/CURRENT/'selection.json.gz';assert digest(selection.read_bytes())==current[str(selection.relative_to(ROOT))]
    row=next(r for r in read(selection)['rows']if r['uid']==UID);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
    historical=[r for r in old['evidenceRefs']if r['sha256']==row['sourceSHA256']and r['path'].endswith('.glb.gz')];assert historical
    refs=[Path(__file__),BASE/OLD/'result.json',BASE/CURRENT/'result.json',selection,asset]
    for ref in historical:
        path=ROOT/ref['path'];assert digest(path.read_bytes())==ref['sha256'];refs.append(path)
    paths=sorted(path for path in pins if path.endswith('.gltf')and'/terrain/TERRAIN'in path);assert len(paths)==2
    for name in paths:
        path=ROOT/name;assert digest(path.read_bytes())==pins[name];refs.append(path)
        for buffer in read(path).get('buffers',[]):
            member=path.parent/buffer['uri'];assert digest(member.read_bytes())==pins[str(member.relative_to(ROOT))];refs.append(member)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==read(selection)['manifestSHA256'];refs.append(manifest)
    result=dict(uids=[UID],rows=[dict(uid=UID,sourceSHA256=row['sourceSHA256'],sourceTerrainPaths=paths)],currentManifestSHA256=digest(manifest.read_bytes()),historicalTerrainReceipt=old['jobId'],sourceGeometryChanges=0,installationApproved=False,qualification='Exact historical government terrain metadata/buffers and unchanged podium source bytes only. This is neither a fresh government revision search nor current physical acceptance. Any private inset must capture current rendered parent and pass all current source/neighbour/terrain/runtime/browser guards.')
    save(out/'summary.json',result);module('yoho_terrain_binding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-government-terrain-input-bindings',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
