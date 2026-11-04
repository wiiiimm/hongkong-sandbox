"""Fresh exact source identity and outlying-face views; no installation approval."""
from pathlib import Path
import subprocess,numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-kai-tak-cruise-extent-views-v1-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-next-five-current-terrain-v1-20261018';VIEWS=BASE/'government-xl-remaining-three-source-views-v2-20261019';UID='landsd/263423:0'
def main():
 assert not DOC.exists();r=read(VIEWS/'result.json');refs=[Path(__file__),VIEWS/'result.json'];pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 row=next(r for r in read(CAP/'selection.json.gz')['rows']if r['uid']==UID);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];t=decode_original_world_triangles(raw);assert len(t)==45925
 final=module('kai_identity_forms',HERE/'xl-final-script-pass.py');lo,hi=t.min((0,1)),t.max((0,1));forms=final.load_forms([lo[0]-20,lo[2]-20,hi[0]+20,hi[2]+20])
 context=dict(sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,t,forms),neighbourTileHashes={tile:digest((ROOT/'3d-viewer'/tile).read_bytes())for _,_,tile in forms});save(DOC/'context.json',context)
 proof=verify_files(row,context,LOCAL/'263423:0');save(DOC/'identity.json',proof);assert proof['sourceSHA256']==row['sourceSHA256']and proof['originalOwnership']['sourceGraphVerified']and proof['exactWholeCellCoverage']['covered']
 poly=Polygon(row['source']['building']['rings'][0],row['source']['building']['rings'][1:]);xz=t[:,:,[0,2]];dist=np.asarray(shapely.distance(shapely.points(xz.reshape(-1,2)),poly)).reshape(-1,3);far=np.flatnonzero(dist.max(1)>10);selected=t[far];assert len(far)>0
 save(DOC/'extent.json',dict(uid=UID,sourceSHA256=row['sourceSHA256'],wholeWorldSHA256=digest(np.asarray(t,dtype='<f8').tobytes()),faceIds=far.tolist(),triangles=selected.tolist(),maximumDistanceM=float(dist.max()),rawIdentityReasons=proof['reasons'],installationApproved=False))
 a,b=selected.min((0,1)),selected.max((0,1));frame=[(a-[6,6,6]).tolist(),(b+[6,6,6]).tolist()];models=[]
 for name,viewframe,direction in [('whole',None,[.7,.6,1]),('extent-front',frame,[.7,.4,1]),('extent-reverse',frame,[-.7,.4,-1])]:models.append(dict(uid='review/'+name,label='Kai Tak Cruise Terminal',assetPath=row['candidate']['path'],sourceSHA256=row['sourceSHA256'],worldBounds=row['candidate']['entry']['worldBounds'],triangles=row['triangles'],forms=[row['source']['building']],reviewFrame=viewframe,viewDirection=direction,highlightFaces=selected.tolist()))
 tool=HERE/'kai_tak_cruise_extent_views_v1_20261019.mjs';refs.extend([tool,HERE/'xl-final-script-pass.py',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']);refs.extend(ROOT/'3d-viewer'/tile for _,_,tile in forms);refs.extend(p for p in LOCAL.rglob('*')if p.is_file());refs=list(dict.fromkeys(refs));hashes={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
 save(DOC/'input.json',dict(models=models,inputHashes=hashes));subprocess.run(['node',str(tool),'--inputs',str((DOC/'input.json').relative_to(ROOT)),'--out',str(DOC.relative_to(ROOT))],cwd=ROOT,check=True)
 report=read(DOC/'render.json');assert len(report['views'])==3 and not report['errors'];assert len({v['image']['path']for v in report['views']})==3
 for v in report['views']:assert digest((ROOT/v['image']['path']).read_bytes())==v['image']['sha256']
 for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('kai_extent_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-cruise-exact-source-extent-views',list(dict.fromkeys(refs)),dict(uids=[UID],extentFaces=len(far),maximumDistanceM=float(dist.max()),rawIdentityReasons=proof['reasons'],installationApproved=False))
if __name__=='__main__':main()
