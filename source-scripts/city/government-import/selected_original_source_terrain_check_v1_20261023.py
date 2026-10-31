"""Check explicit originals against authenticated same-cache original terrain bytes."""
import argparse
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','terrain-check','capture']:p.add_argument('--'+key,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert not out.exists()
    refs=[Path(__file__)]
    def bound(name,filename):
        _,pins=authenticate(base/name);path=base/name/filename
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
        refs.extend([base/name/'result.json',path]);return read(path),pins
    donor,pins=bound(a.terrain_check,'summary.json')
    selected,_=bound(a.capture,'selection.json.gz')
    assert 0<len(selected['rows'])<=8
    decoder=module('selected_source_terrain_decoder',HERE/'xl-second-pass.py')
    final=module('selected_source_terrain_foundation',HERE/'xl-final-script-pass.py')
    rows=[]
    for row in selected['rows']:
        native=row['native']
        donors=[r for r in donor['rows']if r.get('status')=='original-terrain-checked'and r.get('nativeResultSHA256')==native['resultSha']]
        assert donors and len({tuple(r['sourceTerrainPaths'])for r in donors})==1
        paths=donors[0]['sourceTerrainPaths'];ground=[]
        for name in paths:
            path=ROOT/name;assert digest(path.read_bytes())==pins[name];refs.append(path)
            gltf=read(path)
            for buffer in gltf.get('buffers',[]):
                member=path.parent/buffer['uri'];assert digest(member.read_bytes())==pins[str(member.relative_to(ROOT))];refs.append(member)
            ground.append(decoder.terrain_triangles(path))
        raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(ROOT/row['candidate']['path'])
        tri=decode_original_world_triangles(raw);assert len(tri)==row['triangles']
        terrain=np.concatenate(ground);lo,hi=tri.min((0,1)),tri.max((0,1));terrain=terrain[(terrain[:,:,0].max(1)>=lo[0]-10)&(terrain[:,:,0].min(1)<=hi[0]+10)&(terrain[:,:,2].max(1)>=lo[2]-10)&(terrain[:,:,2].min(1)<=hi[2]+10)]
        form=row['source']['building'];foundation=final.foundation_context(tri,terrain,Polygon(form['rings'][0],form['rings'][1:]))
        rows.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],status='original-terrain-checked',nativeResultSHA256=native['resultSha'],sourceTerrainPaths=paths,originalTerrainFoundation=foundation,installationApproved=False))
    result=dict(uids=[r['uid']for r in rows],rows=rows,sourceGeometryChanges=0,installationApproved=False,qualification='Fresh whole-source foundation diagnostics using exact same native-result terrain glTF/buffer hashes. No old terrain/source approval transfer; target support and current scene remain unaccepted.')
    save(out/'summary.json',result)
    refs.extend(HERE/n for n in ['xl-second-pass.py','xl-final-script-pass.py','exact_packed_world_geometry_20261009.py'])
    module('selected_source_terrain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'fresh-explicit-original-source-terrain-check',list(dict.fromkeys(refs)),result)
    print([dict(uid=r['uid'],buried=r['originalTerrainFoundation']['fullyBuriedTriangles'],minimumGapM=r['originalTerrainFoundation']['minimumGapM'])for r in rows],flush=True)


if __name__=='__main__':main()
