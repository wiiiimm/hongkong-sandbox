"""Run current exact identity checks on the recovered immutable support asset."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-hanford-support-identity-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
    assert not DOC.exists()
    source=BASE/'government-xl-hanford-support-recovery-v2-20261021';_,pins=authenticate(source)
    p=source/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
    row=read(p)['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==pins[str(asset.relative_to(ROOT))]
    tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes())
    tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==row['triangles']
    final=module('hanford_identity_context',HERE/'xl-final-script-pass.py');lo,hi=tri.min((0,1)),tri.max((0,1));near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
    tiles={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in near}
    context=dict(sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,near),neighbourTileHashes=tiles)
    proof=verify_files(row,context,LOCAL);save(DOC/'context.json',context);save(DOC/'identity.json',proof)
    save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=mh))
    refs=[Path(__file__),source/'result.json',p,asset,tile,manifest,HERE/'xl-final-script-pass.py',HERE/'exact_original_georef_cell_identity_20261009.py']
    for t,h in tiles.items():
        p=ROOT/'3d-viewer'/t;assert digest(p.read_bytes())==h;refs.append(p)
    assert digest(manifest.read_bytes())==mh
    refs.extend(p for p in LOCAL.rglob('*')if p.is_file())
    result=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],identityPassed=proof['passed'],reasons=proof['reasons'],sourceGeometryChanges=0,installationApproved=False)
    module('hanford_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'recovered-original-current-identity',refs,result)
    print(result,flush=True)

if __name__=='__main__':main()
