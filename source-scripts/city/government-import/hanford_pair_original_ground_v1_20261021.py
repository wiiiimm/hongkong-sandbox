"""Compare both immutable Hanford sources against their authenticated government terrain."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-hanford-pair-original-ground-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
    assert not DOC.exists();refs=[Path(__file__)]
    def take(name,path):
        _,pins=authenticate(BASE/name);assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.extend([BASE/name/'result.json',path]);return read(path)
    cap='government-xl-hanford-pair-runtime-v1-20261021';selection=take(cap,BASE/cap/'selection.json.gz');rows=selection['rows'];runtime=take(cap,HERE/'local'/cap/'runtime-geometry.json.gz');geometries={r['uid']:r for r in runtime['rows']}
    old='government-xl-hanford-plaza-terrain-continuation-v4-20261005';recovery=take(old,BASE/old/'source-recovery.json');assert recovery['sheet']=='6-SW-11A';paths=[]
    for e in recovery['terrainFiles']:
        p=HERE/'local'/old/'sheets/6-SW-11A/terrain'/e['name'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
        if p.suffix=='.gltf':paths.append(p)
    new='government-xl-hanford-support-recovery-v2-20261021';_,pins=authenticate(BASE/new);r=take(new,BASE/new/'recovery.json');assert r['sheet']=='6-SW-11B'
    for e in r['source']['entries']:
        if not e['name'].startswith('TERRAIN'):continue
        p=HERE/'local'/new/'sheets/6-SW-11B/terrain'/e['name'];assert digest(p.read_bytes())==e['sha256']==pins[str(p.relative_to(ROOT))];refs.append(p)
        if p.suffix=='.gltf':paths.append(p)
    assert len(paths)==2
    decoder=module('hanford_original_terrain',HERE/'xl-second-pass.py');decoder.LOCAL=LOCAL
    terrain=np.concatenate([decoder.terrain_triangles(p)for p in paths]);lo=np.min([r['native']['model']['worldBounds'][0]for r in rows],axis=0);hi=np.max([r['native']['model']['worldBounds'][1]for r in rows],axis=0)
    terrain=terrain[(terrain[:,:,0].max(1)>=lo[0]-10)&(terrain[:,:,0].min(1)<=hi[0]+10)&(terrain[:,:,2].max(1)>=lo[2]-10)&(terrain[:,:,2].min(1)<=hi[2]+10)]
    final=module('hanford_foundations',HERE/'xl-final-script-pass.py');results=[]
    for row in rows:
        g=geometries[row['uid']];assert g['sourceSHA256']==row['sourceSHA256'];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];b=row['source']['building'];poly=Polygon(b['rings'][0],b['rings'][1:])
        results.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],originalTerrainFoundation=final.foundation_context(tri,terrain,poly),currentTerrainFoundation=final.foundation_context(tri,np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3),poly)))
    save(LOCAL/'original-terrain.json.gz',dict(triangles=terrain.tolist(),sourcePaths=[str(p.relative_to(ROOT))for p in paths]));refs.extend([LOCAL/'original-terrain.json.gz',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py'])
    save(DOC/'summary.json',dict(rows=results,terrainTriangles=len(terrain),installationApproved=False))
    module('hanford_ground_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-original-government-versus-current-ground',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],rows=results,installationApproved=False))
    print([(r['uid'],r['originalTerrainFoundation']['fullyBuriedTriangles'],r['currentTerrainFoundation']['fullyBuriedTriangles'])for r in results],flush=True)

if __name__=='__main__':main()
