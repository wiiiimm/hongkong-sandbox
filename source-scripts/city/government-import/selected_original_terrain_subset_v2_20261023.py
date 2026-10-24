"""Bind one historical government TIN record to an exact unchanged current source.

Only immutable terrain paths and original diagnostics are reused; no current-scene
placement approval transfers from the older batch.
"""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','terrain','capture','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-') and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    prior=take(a.terrain,base/a.terrain/'summary.json')
    terrain=next(r for r in prior['rows']if r['uid']==a.uid)
    selection=take(a.capture,base/a.capture/'selection.json.gz')
    source=next(r for r in selection['rows']if r['uid']==a.uid)
    assert terrain['sourceSHA256']==source['sourceSHA256'] and terrain['status'] in ['original-terrain-checked','fresh-terrain-checked']
    assert terrain['nativeResultSHA256']==source['native']['resultSha']
    terrain={**terrain,'historicalDiagnosticStatus':terrain['status'],'status':'original-terrain-checked'}
    for filename in terrain['sourceTerrainPaths']:
        path=ROOT/filename;gltf=take(a.terrain,path)
        for b in gltf.get('buffers',[]):
            member=path.parent/b['uri'];assert member.resolve().is_relative_to(ROOT)
            assert digest(member.read_bytes())==pins[a.terrain][str(member.relative_to(ROOT))];refs.append(member)
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    result=dict(uids=[a.uid],rows=[terrain],historicalOriginalTerrainDiagnosticOnly=True,currentManifestSHA256=selection['manifestSHA256'],installationApproved=False,sourceGeometryChanges=0,publication=False)
    save(out/'summary.json',result)
    module('selected_terrain_subset_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-source-historical-terrain-subset-current-binding',refs,result)


if __name__=='__main__':main()
