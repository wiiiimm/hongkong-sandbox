"""Current exact original identity and nearby form context for Plaza Ascot."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-identity-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-next-twenty-current-terrain-v2-20261020';UID='landsd/258411:0'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={e['path']:e['sha256']for e in r['evidenceRefs']};p=SRC/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);row=next(r for r in read(p)['rows']if r['uid']==UID)
 tile=ROOT/'3d-viewer'/row['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==UID)==row['source']['building'];refs.append(tile)
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';manifestsha=digest(manifest.read_bytes());refs.append(manifest)
 final=module('ascot_identity',HERE/'xl-final-script-pass.py');tri=decode_original_world_triangles(asset.read_bytes());lo,hi=tri.min((0,1)),tri.max((0,1));near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);tiles={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in near}
 context=dict(sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,near),neighbourTileHashes=tiles);save(DOC/'context.json',context);proof=verify_files(row,context,LOCAL);save(DOC/'identity.json',proof)
 refs.extend(ROOT/'3d-viewer'/t for t in tiles);assert digest(manifest.read_bytes())==manifestsha
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file());refs.extend([HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
 summary=dict(uids=[UID],passed=proof['passed'],reasons=proof['reasons'],installationApproved=False);save(DOC/'summary.json',summary)
 module('ascot_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-current-original-source-identity',list(dict.fromkeys(refs)),summary);print(summary,flush=True)
if __name__=='__main__':main()
