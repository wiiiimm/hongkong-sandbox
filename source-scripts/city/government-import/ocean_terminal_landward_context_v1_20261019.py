"""Fresh identity and exact original landward overlap views; no approval."""
from pathlib import Path
import subprocess,numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ocean-terminal-landward-context-v1-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-ocean-terminal-private-ground-v2-20261018';VIEWS=BASE/'government-xl-ocean-terminal-source-views-v1-20261019';CONTEXT=BASE/'government-xl-next-five-original-identity-v1-20261018/205767:0'
def main():
 assert not DOC.exists();receipt=read(VIEWS/'result.json');refs=[Path(__file__),VIEWS/'result.json'];pins={e['path']:e['sha256']for e in receipt['evidenceRefs']}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 row=read(CAP/'selection.json.gz')['rows'][0];proof=verify_files(row,read(CONTEXT/'context.json'),LOCAL/'205767:0');save(DOC/'identity.json',proof)
 assert proof['sourceSHA256']==row['sourceSHA256'] and proof['exactWholeCellCoverage']['covered'] and proof['originalOwnership']['sourceGraphVerified']
 refs.extend([CONTEXT/'context.json',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py'])
 raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];t=decode_original_world_triangles(raw);assert digest(np.asarray(t,dtype='<f8').tobytes())==proof['worldTrianglesSHA256'];polys=shapely.polygons(t[:,:,[0,2]]);valid=shapely.area(polys)>1e-10
 final=module('ocean_landward_forms',HERE/'xl-final-script-pass.py');forms=final.load_forms([490,-970,940,-745]);refs.append(HERE/'xl-final-script-pass.py');out=[];models=[]
 expected=proof['originalOwnership']['fullProjection']['intersectingForms'];foreign=[r for r in expected if not r['sameParent'] and not r['sharedOsmReference']];assert {r['uid']for r in foreign}=={'landsd/215934:0','landsd/231469:0','landsd/234188:0'}
 for e in foreign:
  form,polygon,tile=next(r for r in forms if r[0]['uid']==e['uid']);refs.append(ROOT/'3d-viewer'/tile)
  ids=np.flatnonzero(valid & shapely.intersects(polys,polygon));assert len(ids)==e['sourceFaceCount'],(e['uid'],len(ids),e['sourceFaceCount'])
  area=float(shapely.union_all(shapely.intersection(polys[valid],polygon)).area);assert abs(area-e['intersectionAreaM2'])<1e-7
  selected=t[ids];lo=selected.min((0,1));hi=selected.max((0,1));out.append(dict(uid=e['uid'],name=e['name'],sourceFaceIds=ids.tolist(),triangles=selected.tolist(),intersectionAreaM2=area,sourceBounds=[lo.tolist(),hi.tolist()],form=form))
  frame=[(lo-[4,3,4]).tolist(),(hi+[4,3,4]).tolist()]
  for suffix,direction in [('front',[1,.65,1]),('reverse',[-1,.65,-1])]:
   models.append(dict(uid='review/'+e['uid'].split('/')[1].replace(':','-')+'-'+suffix,label=e['name'],assetPath=row['candidate']['path'],sourceSHA256=row['sourceSHA256'],worldBounds=row['candidate']['entry']['worldBounds'],triangles=row['triangles'],forms=[form],reviewFrame=frame,viewDirection=direction,highlightFaces=selected.tolist()))
 save(DOC/'overlaps.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],rows=out,rawIdentityReasons=proof['reasons'],installationApproved=False))
 tool=HERE/'ocean_terminal_overlap_views_v1_20261019.mjs';refs.append(tool);refs.extend(p for p in LOCAL.rglob('*') if p.is_file());refs=list(dict.fromkeys(refs));hashes={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
 save(DOC/'input.json',dict(models=models,inputHashes=hashes));subprocess.run(['node',str(tool),'--inputs',str((DOC/'input.json').relative_to(ROOT)),'--out',str(DOC.relative_to(ROOT))],cwd=ROOT,check=True)
 report=read(DOC/'render.json');assert len(report['views'])==6 and not report['errors']
 for p,h in {**hashes,**report['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('ocean_landward_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'ocean-terminal-fresh-identity-and-landward-overlaps',list(dict.fromkeys(refs)),dict(uids=[row['uid']],overlaps=[dict(uid=r['uid'],faces=len(r['sourceFaceIds']),areaM2=r['intersectionAreaM2'])for r in out],rawIdentityReasons=proof['reasons'],installationApproved=False))
if __name__=='__main__':main()
