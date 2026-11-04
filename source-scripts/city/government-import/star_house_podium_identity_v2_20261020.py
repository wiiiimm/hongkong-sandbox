"""Current exact identity evidence for Star House's original supporting podium."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-star-house-podium-identity-v2-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PRIOR=BASE/'government-xl-star-parkview-support-v1-20261020';UID='landsd/231484:0'
assert not DOC.exists();r=read(PRIOR/'result.json')
with connect() as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
pins={e['path']:e['sha256'] for e in r['evidenceRefs']};sel=PRIOR/'selection.json.gz';assert digest(sel.read_bytes())==pins[str(sel.relative_to(ROOT))];row=next(x for x in read(sel)['rows'] if x['uid']==UID);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];tile=ROOT/'3d-viewer'/row['source']['tile'];assert next(b for b in read(tile)['buildings'] if b['uid']==UID)==row['source']['building']
historicalTileSHA256=row['source']['tileSHA256'];row['source']['tileSHA256']=digest(tile.read_bytes());save(DOC/'current-tile-binding.json',dict(uid=UID,historicalTileSHA256=historicalTileSHA256,currentTileSHA256=row['source']['tileSHA256'],exactBuildingRecordUnchanged=True))
tri=decode_original_world_triangles(asset.read_bytes());lo,hi=tri.min((0,1)),tri.max((0,1));final=module('star_podium_identity_context',HERE/'xl-final-script-pass.py');near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);tiles={t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in near};context=dict(sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,near),neighbourTileHashes=tiles);save(DOC/'context.json',context);proof=verify_files(row,context,LOCAL);save(DOC/'identity.json',proof)
refs=[Path(__file__),PRIOR/'result.json',sel,asset,tile,HERE/'xl-final-script-pass.py',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']
for t,h in tiles.items():p=ROOT/'3d-viewer'/t;assert digest(p.read_bytes())==h;refs.append(p)
summary=dict(uids=[UID],passed=proof['passed'],reasons=proof['reasons'],sourceSHA256=row['sourceSHA256'],installationApproved=False,modelGeometryChanges=0)
module('star_podium_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-current-podium-identity',list(dict.fromkeys(refs)),summary);print(summary,flush=True)
