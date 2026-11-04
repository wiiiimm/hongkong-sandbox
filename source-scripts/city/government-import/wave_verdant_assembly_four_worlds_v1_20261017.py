"""Complete eight-original compound support/foundation replay on actual V4 terrain."""
from pathlib import Path
import subprocess,numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave-verdant-assembly-four-worlds-v1-20261017';DOC=BASE/BATCH
NAMES=['government-xl-wave-four-world-paths-v1-20261017','government-xl-wave-verdant-four-world-paths-v1-20261017','government-xl-wave-verdant-block2-render-attributes-v1-20261017','government-xl-wave-verdant-multicore-ground-capture-v4-20261017']
PODIUMS=['landsd/301560:0','landsd/304885:0'];UIDS=['landsd/275510:0','landsd/275511:0','landsd/301560:0','landsd/301558:0','landsd/301562:0','landsd/195000:0','landsd/194520:0','landsd/304885:0']
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 worlds=read(BASE/NAMES[0]/'worlds.json.gz');verdant=read(BASE/NAMES[1]/'worlds.json.gz');attrs=read(BASE/NAMES[2]/'attributes.json.gz')['rows'];assert len(attrs)==1;attr=attrs[0]
 sources={r['uid']:r for r in read(BASE/'government-xl-wave-all-original-support-distance-v1-20261017/support-inputs.json')['sources']};sources.update({r['uid']:r for r in read(BASE/'government-xl-wave-verdant-podium-support-v1-20261017/support-inputs.json')['sources']});sources.update({r['uid']:r for r in read(BASE/'government-xl-wave-verdant-block2-original-recovery-v1-20261017/selection.json.gz')['rows']})
 keys={'literal':'completeLiteralWorldPosition','left':'completeExplicitLeftAssociatedFloat32WorldPosition','balanced':'completeExplicitBalancedFloat32WorldPosition'}
 row=sources['landsd/194520:0'];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];original=decode_original_world_triangles(raw);ground=np.array(read(BASE/NAMES[3]/'after-ground.json.gz')['completeRelevantDrawnTriplets']).reshape(-1,3,3);final=module('wave_verdant_joint_foundation',HERE/'xl-final-script-pass.py');summary=[]
 for mode in ['original','literal','left','balanced']:
  w={u:np.array(t)for u,t in {**worlds[mode],**verdant[mode]}.items()};w['landsd/194520:0']=original if mode=='original'else np.array(attr[keys[mode]]).reshape(-1,3)[np.array(attr['completeOriginalIndex']).reshape(-1,3)]
  assert set(UIDS)<=set(w);support=np.concatenate([ground]+[w[u]for u in PODIUMS]);rows=[]
  for u in UIDS:
   assert len(w[u])==sources[u]['native']['model']['triangles']
   if u not in PODIUMS:rows.append(dict(uid=u,position=w[u].reshape(-1).tolist(),index=list(range(len(w[u])*3))))
  d=DOC/mode;save(d/'input.json.gz',dict(rows=rows,podium=support.tolist()));tool=HERE/'wave_retained_basic_support_v1_20261017.mjs';subprocess.run(['node',str(tool),str(d.relative_to(ROOT))],cwd=ROOT,check=True);proof=read(d/'support.json.gz');byuid={r['uid']:r['proof']for r in proof['rows']}
  for p,h in proof['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
  for uid in UIDS:
   b=sources[uid]['source']['building'];f=final.foundation_context(w[uid],ground if uid in PODIUMS else support,Polygon(b['rings'][0],b['rings'][1:]));strict=f['completeTerrainTriangles']==f['triangles']and f['fullyBuriedAreaFraction']==0;interface=byuid.get(uid);r=dict(uid=uid,mode=mode,faces=len(w[uid]),strictFoundationAccepted=strict,buried=f['fullyBuriedTriangles'],upwardBuried=f['fullyBuriedUpwardTriangles'],supportPassed=None if interface is None else interface['passed'],samples=None if interface is None else interface['samples'],strictContacts=None if interface is None else interface['strictContacts'],unresolved=None if interface is None else len(interface['unresolved']));summary.append(r);save(d/(uid.split('/')[1]+'-foundation.json'),dict(sourceSHA256=sources[uid]['sourceSHA256'],foundation=f));print(r,flush=True)
 save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False,qualification='All eight proposed unchanged originals and all faces, four coordinate modes, actual V4 drawn terrain and both original podiums. Retained BASIC actors and browser/runtime checks remain separate. Canonical support failures retained.'));out=module('joint_assembly_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'eight-original-four-world-compound-placement-v1',list(set(refs)),dict(uids=UIDS,summary=summary,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
