"""Qualify both unchanged towers against the installed original podium and ground."""
from pathlib import Path
import subprocess,sys,json,uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-remaining-forty-assembly-support-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CAP=BASE/'government-xl-remaining-forty-assembly-runtime-v1-20261021'
PAIRS={'landsd/256702:0':'landsd/233771:0','landsd/278234:0':'landsd/277890:0','landsd/314698:0':'landsd/277890:0','landsd/278458:0':'landsd/277890:0','landsd/137130:0':'landsd/23296:0','landsd/198440:0':'landsd/259604:0','landsd/339808:0':'landsd/290878:0','landsd/255531:0':'landsd/258737:0'}
UIDS=list(PAIRS)
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();receipt,pins=authenticate(CAP);refs=[Path(__file__),CAP/'result.json']
 def consume(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 selected=consume(CAP/'selection.json.gz');rows=selected['rows'];runtime=consume(HERE/'local'/CAP.name/'runtime-geometry.json.gz');metrics=consume(CAP/'metrics.json');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
 for r in rows:
  p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p)
 save(DOC/'selection.json.gz',selected);save(DOC/'support-inputs.json',dict(pairs=[dict(uid=u,supportUid=PAIRS[u])for u in UIDS],sources=rows))
 tool=HERE/'original-support-closure-interfaces.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True);checks=read(DOC/'support-checks.json.gz')
 geometry={r['uid']:r for r in runtime['rows']};world={u:np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]for u,g in geometry.items()};final=module('parkview13_14_foundations',HERE/'xl-final-script-pass.py');out=[]
 for u in UIDS:
  POD=PAIRS[u]
  b=next(r['source']['building']for r in rows if r['uid']==u);ground=np.asarray(geometry[u]['drawnGroundGeometry']).reshape(-1,3,3)
  f=final.foundation_context(world[u],np.concatenate([ground,world[POD]]),Polygon(b['rings'][0],b['rings'][1:]));interface=next(r['interface']for r in checks['rows']if r['uid']==u)
  result=dict(uid=u,supportUid=POD,foundation=f,interfaceSummary={k:interface[k]for k in ['passed','samples','strictContacts','wallIntersections']},unresolved=len(interface['unresolved']));out.append(result);print(result,flush=True);assert reservations.owns(lease)
 save(DOC/'summary.json',dict(rows=out,installationApproved=False))
 for p,h in {**metrics['inputHashes'],**checks['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([HERE/'xl-final-script-pass.py']);module('parkview_pair_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'eight-original-tower-support-foundations',list(dict.fromkeys(refs)),dict(uids=UIDS,rows=out,installationApproved=False))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in sorted(set(UIDS)|set(PAIRS.values()))],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE/'harbourfront_reserved_runner_v1_20261021.py'),str(path),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
