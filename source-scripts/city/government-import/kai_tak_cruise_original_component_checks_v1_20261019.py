"""Complete recovered rooftop meshes against terminal and terrain; no approval."""
import subprocess,numpy as np
from pathlib import Path
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-kai-tak-cruise-original-component-checks-v1-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-kai-tak-cruise-component-recovery-v1-20261019';CAP=BASE/'government-xl-kai-tak-cruise-expanded-parent-v3-20261019'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [SRC,CAP]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 rows=read(SRC/'selection.json.gz')['rows'];wanted={r['uid']for r in rows};forms={}
 for name in ['2_-1','2_-2']:
  path=ROOT/('3d-viewer/city/data/tiles/'+name+'.json');refs.append(path)
  for b in read(path)['buildings']:
   if b['uid']in wanted:assert b['uid']not in forms;forms[b['uid']]=dict(building=b,tile=str(path.relative_to(ROOT/'3d-viewer')),tileSHA256=digest(path.read_bytes()))
 assert set(forms)==wanted
 g=read(HERE/'local'/CAP.name/'runtime-geometry.json.gz')['rows'][0];podium=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);allground=np.concatenate([ground,podium]);final=module('kai_original_components',HERE/'xl-final-script-pass.py');runtime=[];summary=[]
 for row in rows:
  uid=row['uid'];row['source']=forms[uid];assert row['source']['building']['buildingCSUID']==row['native']['model']['candidate']['buildingCSUID'];tri=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());assert len(tri)==row['triangles'];lo,hi=tri.min((0,1)),tri.max((0,1));near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);context=dict(sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,near));identity=verify_files(row,context,LOCAL/uid.split('/')[1]);save(DOC/(uid.split('/')[1]+'-identity.json'),identity);b=forms[uid]['building'];f=final.foundation_context(tri,allground,Polygon(b['rings'][0],b['rings'][1:]));save(DOC/(uid.split('/')[1]+'-foundation.json'),f);runtime.append(dict(uid=uid,position=tri.reshape(-1).tolist(),index=list(range(len(tri)*3))));summary.append(dict(uid=uid,triangles=len(tri),identityPassed=identity['passed'],identityReasons=identity['reasons'],foundation={k:v for k,v in f.items()if k!='components'}));refs.extend(ROOT/'3d-viewer'/tile for _,_,tile in near);print(summary[-1],flush=True)
 save(DOC/'input.json.gz',dict(rows=runtime,podium=podium.tolist()));tool=HERE/'wave_retained_basic_support_v1_20261017.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);support=read(DOC/'support.json.gz')
 for row in summary:
  p=next(r['proof']for r in support['rows']if r['uid']==row['uid']);row.update(supportPassed=p['passed'],strictContacts=p['strictContacts'],unresolved=len(p['unresolved']));print({k:v for k,v in row.items()if k!='foundation'},flush=True)
 save(DOC/'selection.json.gz',dict(rows=rows));save(DOC/'summary.json',dict(rows=summary,installationApproved=False))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in support['inputHashes']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file());refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_original_georef_cell_identity_20261009.py'])
 module('kai_component_checks_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-cruise-original-component-identity-foundation-support',list(dict.fromkeys(refs)),dict(uids=sorted(wanted),rows=summary,installationApproved=False))
if __name__=='__main__':main()
