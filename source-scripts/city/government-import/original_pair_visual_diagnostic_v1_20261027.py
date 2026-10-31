"""Capture complete, colour-coded original components; no appearance approval."""
import argparse
import subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','main']:parser.add_argument('--'+key,required=True)
    a=parser.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and not out.exists()
    _,pins=authenticate(base/a.runtime);selection_path=base/a.runtime/'selection.json.gz'
    assert digest(selection_path.read_bytes())==pins[str(selection_path.relative_to(ROOT))]
    selection=read(selection_path);assert 1<len(selection['rows'])<=8
    refs=[Path(__file__),base/a.runtime/'result.json',selection_path,HERE/'exact_packed_world_geometry_20261009.py']
    models={};forms=[];hashes={}
    for row in selection['rows']:
        path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==row['sourceSHA256'];refs.append(path)
        tri=decode_original_world_triangles(path.read_bytes());assert len(tri)==row['triangles']
        models[row['uid']]=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],assetPath=str(path.relative_to(ROOT)),
              triangles=len(tri),worldBounds=[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()])
        tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];refs.append(tile)
        assert next(f for f in read(tile)['buildings'] if f['uid']==row['uid'])==row['source']['building']
        forms.append(row['source']['building']);hashes[str(path.relative_to(ROOT))]=row['sourceSHA256'];hashes[str(tile.relative_to(ROOT))]=digest(tile.read_bytes())
    assert a.main in models
    model=dict(**models[a.main],forms=forms,failedSamples=[],originalComponents=[m for uid,m in models.items() if uid!=a.main])
    tool=HERE/'render-original-component-evidence-v2-20261027.mjs';refs.append(tool)
    hashes[str(tool.relative_to(ROOT))]=digest(tool.read_bytes())
    inputs=out/'inputs.json';save(inputs,dict(title='Ocean Centre · original components · diagnostic colours',models=[model],inputHashes=hashes));refs.append(inputs)
    with(out/'worker.log').open('w') as log:
        subprocess.run(['node',str(tool),'--inputs',str(inputs.relative_to(ROOT)),'--out',str((out/'views').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    report=read(out/'views/render.json');assert not report['errors'] and len(report['views'])==1
    for name,sha in report['inputHashes'].items():assert digest((ROOT/name).read_bytes())==sha;refs.append(ROOT/name)
    for view in report['views']:
        path=ROOT/view['image']['path'];assert digest(path.read_bytes())==view['image']['sha256'];refs.append(path)
    assert all(not v['installationApproved'] and not v['architectureReview'] for v in report['views'])
    result=dict(uids=list(models),views=report['views'],sourceGeometryChanges=0,physicalAcceptance=False,
                architectureReview=False,installationApproved=False,publication=False,
                qualification='Whole unchanged original pair in diagnostic material colours and current source footprints. No terrain, textures or runtime deployment shown. Capture completion alone grants no visual/source/support/installation approval.')
    save(out/'summary.json',result);refs.append(out/'views/render.json')
    module('pair_visual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-pair-coloured-geometry-visual-diagnostic',list(dict.fromkeys(refs)),result)
    print(dict(views=len(report['views']),image=report['views'][0]['image']['path']),flush=True)


if __name__=='__main__':main()
