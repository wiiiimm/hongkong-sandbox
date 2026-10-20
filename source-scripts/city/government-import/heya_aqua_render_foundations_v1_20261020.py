"""Complete Heya Tower2 foundations in actual renderer coordinate representations."""
from pathlib import Path
import subprocess
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-heya-aqua-render-foundations-v1-20261020';DOC=BASE/BATCH;SUP=BASE/'government-xl-heya-aqua-current-support-v3-20261020';GROUND=BASE/'government-xl-heya-aqua-current-ground-v1-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [SUP,GROUND]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in r['evidenceRefs']}
 def take(folder,p):
  assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 source=take(SUP,SUP/'support-inputs.json')['sources'];mp=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(mp)
 def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 cats=[ref(ROOT/'3d-viewer'/url) for url in manifest['officialModelCatalogues']];rows=[]
 for r in source:
  tile=ROOT/'3d-viewer'/r['source']['tile'];assert next(b for b in read(tile)['buildings'] if b['uid']==r['uid'])==r['source']['building'];refs.append(tile);rows.append(dict(uid=r['uid'],entry=r['candidate']['entry'],building=r['source']['building'],path=r['candidate']['path']))
 save(DOC/'input.json.gz',dict(rows=rows,currentManifest=ref(mp),currentCatalogueRefs=cats,evidenceRefs=[ref(p) for p in refs]))
 tool=HERE/'heya_aqua_actual_attributes_v1_20261020.mjs';subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 cap=read(DOC/'attributes.json.gz');assert len(cap['rows'])==2 and not cap['rejected'];runtime=take(GROUND,HERE/'local'/GROUND.name/'runtime-geometry.json.gz')['rows'][0];ground=np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3);final=module('heya_actual_foundation',HERE/'xl-final-script-pass.py');out=[]
 for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:
  tri={r['uid']:np.asarray(r[field]).reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)] for r in cap['rows']};b=next(r for r in source if r['uid']=='landsd/184287:0')['source']['building'];f=final.foundation_context(tri['landsd/184287:0'],np.concatenate([ground,tri['landsd/184285:0']]),Polygon(b['rings'][0],b['rings'][1:]));save(DOC/(mode+'-foundation.json'),f);item=dict(mode=mode,**{k:v for k,v in f.items() if k!='components'});out.append(item);print(item,flush=True)
 for p,h in cap['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 refs.extend([tool,HERE/'xl-final-script-pass.py']);result=dict(uids=[r['uid'] for r in source],rows=out,installationApproved=False,sourceGeometryChanges=0);save(DOC/'summary.json',result);module('heya_render_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-actual-renderer-tower-installed-podium-foundations',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
