"""Bounded exact-original support tests for four remaining XL sources."""
from pathlib import Path
import subprocess,copy
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-star-parkview-support-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PAIRS={'landsd/33396:0':'landsd/231484:0','landsd/256113:0':'landsd/254491:0','landsd/255917:0':'landsd/254491:0','landsd/255646:0':'landsd/254491:0'}
assert not DOC.exists();refs=[Path(__file__)];pins={};prior=BASE/'government-xl-next-twenty-current-terrain-v2-20261020';receipt=read(prior/'result.json')
with connect() as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
oldpins={e['path']:e['sha256'] for e in receipt['evidenceRefs']};sel=prior/'selection.json.gz';assert digest(sel.read_bytes())==oldpins[str(sel.relative_to(ROOT))];refs.extend([prior/'result.json',sel]);rows=[copy.deepcopy(r) for r in read(sel)['rows'] if r['uid'] in PAIRS];assert len(rows)==4
star=BASE/'government-xl-terrain-recovery-star-house-original-pair-preflight-v1-20261010/selection.json.gz';starrow=next(r for r in read(star)['rows'] if r['uid']=='landsd/231484:0');refs.append(star)
with connect() as c:
 c.execute('SET TRANSACTION READ ONLY')
 assert c.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(starrow['native']['cacheKey'],)).fetchone()==(starrow['native']['resultSha'],)
rows.append(copy.deepcopy(starrow));manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);pins[str(manifestpath.relative_to(ROOT))]=digest(manifestpath.read_bytes());matches=[]
for url in manifest['officialModelCatalogues']:
 p=ROOT/'3d-viewer'/url;cat=read(p)
 for e in cat['models']:
  if e['uid']=='landsd/254491:0':matches.append((e,p));refs.append(p)
assert len(matches)==1;e,p=matches[0];asset=p.parent/e['asset'];assert digest(asset.read_bytes())==e['sha256'];final=module('star_park_context',HERE/'xl-final-script-pass.py');lo,hi=e['worldBounds'];forms=final.load_forms([lo[0],lo[2],hi[0],hi[2]]);found=[(b,t) for b,_,t in forms if b['uid']==e['uid']];assert len(found)==1;b,t=found[0]
pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
with connect() as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(pointer['snapshotId'],e['uid'])).fetchone()==('installed-verified',e['sha256'])
rows.append(dict(uid=e['uid'],sourceSHA256=e['sha256'],triangles=e['triangles'],candidate=dict(entry=copy.deepcopy(e),path=str(asset.relative_to(ROOT))),source=dict(building=b,tile=t)))
for r in rows:
 if 'native' in r:r['triangles']=r['native']['model']['triangles']
 asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
 tile=ROOT/'3d-viewer'/r['source']['tile'];assert next(b for b in read(tile)['buildings'] if b['uid']==r['uid'])==r['source']['building'];refs.append(tile)
 dest=LOCAL/r['candidate']['entry']['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(asset.read_bytes());r['candidate']['path']=str(dest.relative_to(ROOT));refs.append(dest)
save(DOC/'support-inputs.json',dict(pairs=[dict(uid=u,supportUid=v) for u,v in PAIRS.items()],sources=rows));save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=pins[str(manifestpath.relative_to(ROOT))]))
subprocess.run(['node',str(HERE/'original-support-closure-interfaces.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
subprocess.run(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
metrics=read(DOC/'metrics.json');assert all(not r.get('error') for r in metrics['rows']);geometry={r['uid']:r for r in read(LOCAL/'runtime-geometry.json.gz')['rows']};world={u:np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)] for u,g in geometry.items()};out=[];checks=read(DOC/'support-checks.json.gz')
for u,v in PAIRS.items():
 b=next(r['source']['building'] for r in rows if r['uid']==u);ground=np.asarray(geometry[u]['drawnGroundGeometry']).reshape(-1,3,3);f=final.foundation_context(world[u],np.concatenate([ground,world[v]]),Polygon(b['rings'][0],b['rings'][1:]));interface=next(r['interface'] for r in checks['rows'] if r['uid']==u);out.append(dict(uid=u,supportUid=v,foundation=f,interfaceSummary={k:interface[k] for k in ['passed','samples','strictContacts','wallIntersections']},unresolved=len(interface['unresolved'])));print(out[-1],flush=True)
save(DOC/'summary.json',dict(rows=out,installationApproved=False))
for p,h in {**pins,**metrics['inputHashes'],**checks['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
refs.extend([HERE/'xl-final-script-pass.py',LOCAL/'runtime-geometry.json.gz'])
module('star_park_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-original-current-support-foundations',list(dict.fromkeys(refs)),dict(uids=list(PAIRS),rows=out,installationApproved=False))
