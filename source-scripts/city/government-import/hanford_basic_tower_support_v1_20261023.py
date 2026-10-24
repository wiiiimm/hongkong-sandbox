"""Canonical actual-basic towers against Hanford original podium in all four worlds."""
from pathlib import Path
import subprocess
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-hanford-six-basic-towers-original-support-v1-20261023';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(name,path):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime='government-xl-next-repairs-hanford-plaza-276187-bounded-followthrough-v1-20261023-runtime'
    current='government-xl-next-repairs-hanford-plaza-276187-bounded-followthrough-v1-20261023'
    attributes='government-xl-next-repairs-hanford-plaza-276187-bounded-prephysical-v1-20261023-attributes'
    selection=take(runtime,base/runtime/'selection.json.gz');row=selection['rows'][0];assert row['uid']=='landsd/276187:0'
    attr=take(attributes,base/attributes/'attributes.json.gz')['rows'][0]
    metric=take(current,base/current/'summary.json');uids={r['uid']for r in metric['basicFlags']};assert uids=={'landsd/186759:0','landsd/194214:0','landsd/194240:0','landsd/194245:0','landsd/194256:0','landsd/194725:0'}
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifestpath.read_bytes())==selection['manifestSHA256'];manifest=read(manifestpath);refs.append(manifestpath)
    native=set();suppressed=set()
    for url in manifest['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;refs.append(path)
        for m in read(path)['models']:native.add(m['uid']);suppressed.update(m.get('suppressesBuildingUids',[]))
    assert not uids&(native|suppressed)
    tile=ROOT/'3d-viewer'/row['source']['tile'];forms=read(tile)['buildings'];refs.append(tile);tower_forms=[b for b in forms if b['uid']in uids];assert len(tower_forms)==6
    for b in tower_forms:assert b['parent']==row['source']['building']['parent'] and b['structureType']=='Tower'and not b.get('modelGeometry')
    out.mkdir();basicinput=out/'basic-inputs.json';basicpath=out/'basic-geometry.json'
    save(basicinput,dict(manifestSHA256=selection['manifestSHA256'],currentInputHashes={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs if p.is_file()},rows=[dict(building=b,tile=str(tile.relative_to(ROOT)))for b in tower_forms]))
    tool=HERE/'xl-one-peking-current-foreign-basic-tower-geometry-v1-20261010.mjs'
    with(out/'capture.log').open('w')as log:subprocess.run(['node',str(tool),str(basicinput.relative_to(ROOT)),str(basicpath.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    basics=read(basicpath)
    for p,h in basics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);literal=np.asarray(attr['completeLiteralWorldPosition']).reshape(-1,3);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
    original=literal.copy();tri=decode_original_world_triangles(asset.read_bytes());original[index.ravel()]=tri.reshape(-1,3);assert np.array_equal(original[index],tri)
    positions={'original':original,'literal':literal,'leftF32':np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3),'balancedF32':np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3)}
    rows=[]
    for b in basics['rows']:
        for mode,position in positions.items():rows.append(dict(uid=b['uid'],supportUid=row['uid'],sourceSHA256=row['sourceSHA256'],supportGeometry=dict(position=position.reshape(-1).tolist(),index=index.reshape(-1).tolist()),modes=[dict(mode=mode,geometry=dict(position=b['position'],index=b['index']))]))
    refs.extend([basicinput,basicpath,tool]);save(out/'mode-inputs.json.gz',dict(rows=rows,evidenceRefs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in dict.fromkeys(refs)]))
    checker=HERE/'original_four_world_current_basic_support_v1_20261023.mjs'
    with(out/'contacts.log').open('w')as log:subprocess.run(['node',str(checker),str(out.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    checks=read(out/'mode-checks.json.gz');assert len(checks['rows'])==24
    for p,h in checks['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    result=dict(uids=[row['uid']],basicTowerUids=sorted(uids),testedInterfaces=24,passedInterfaces=sum(r['proof']['passed']for r in checks['rows']),allCanonicalInterfacesPassed=all(r['proof']['passed']for r in checks['rows']),sameRecordedParentProved=True,sourceGeometryChanges=0,installationApproved=False,publication=False,qualification='Actual current basic tower meshes against all four complete unchanged original podium streams. Shared parent alone grants no support or identity approval. Raw ground-gap flags, original-source clearance, coastal nonregression and all other gates remain separate.')
    save(out/'summary.json',result);refs.append(checker);module('hanford_tower_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'four-world-current-basic-towers-on-original-podium-diagnostic',list(dict.fromkeys(refs)),result);print(result,flush=True)


if __name__=='__main__':main()
