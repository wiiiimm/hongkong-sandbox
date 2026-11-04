"""Current source identity checks for eight unchanged Mount Sterling originals."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mount-sterling-eight-identity-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;REC=BASE/'government-xl-mount-sterling-nine-original-recovery-v1-20261020'
def main():
    assert not DOC.exists();receipt=read(REC/'result.json')
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']};p=REC/'recovery.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];rows=[r for r in read(p)['rows'] if r['modelId']!='B323332207601063C0'];refs=[Path(__file__),REC/'result.json',p]
    manifest=ROOT/'3d-viewer/city/data/manifest.json';manifestsha=digest(manifest.read_bytes());refs.append(manifest);tile=ROOT/'3d-viewer/city/data/tiles/-2_-3.json';forms={b['uid']:b for b in read(tile)['buildings']};refs.append(tile)
    final=module('mount_sterling_identity',HERE/'xl-final-script-pass.py');summary=[]
    for r in rows:
        asset=ROOT/r['assetPath'];assert digest(asset.read_bytes())==r['sourceSHA256']==pins[r['assetPath']];refs.append(asset)
        row=dict(r,triangles=r['native']['model']['triangles'],source=dict(building=forms[r['uid']],tile='city/data/tiles/-2_-3.json',tileSHA256=digest(tile.read_bytes())),candidate=dict(path=r['assetPath']))
        tri=decode_original_world_triangles(asset.read_bytes());lo,hi=tri.min((0,1)),tri.max((0,1));near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);tiles={t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in near};context=dict(sourceSHA256=r['sourceSHA256'],identity=final.identity_context(row,tri,near),neighbourTileHashes=tiles);key=r['uid'].split('/')[1];save(DOC/key/'context.json',context);proof=verify_files(row,context,LOCAL/key);save(DOC/key/'identity.json',proof);refs.extend(ROOT/'3d-viewer'/t for t in tiles);item=dict(uid=r['uid'],passed=proof['passed'],reasons=proof['reasons']);summary.append(item);print(item,flush=True)
    assert digest(manifest.read_bytes())==manifestsha
    refs.extend(p for p in LOCAL.rglob('*') if p.is_file());refs.extend([HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py']);save(DOC/'summary.json',dict(rows=summary,installationApproved=False))
    module('mount_sterling_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'eight-current-original-identity-checks',list(dict.fromkeys(refs)),dict(uids=[r['uid'] for r in rows],rows=summary,installationApproved=False))
if __name__=='__main__':main()
