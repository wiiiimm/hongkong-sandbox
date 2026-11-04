"""Private original-source terrain candidate; no geometry edits or publication."""
from pathlib import Path
import json,subprocess,sys,uuid,traceback
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tower6803-pair-terrain-candidate-v2-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-tower6803-current-capture-v1-20261020';UIDS=['landsd/6803:0','landsd/15047:0']
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists()
 r=read(CAP/'result.json');pins={e['path']:e['sha256'] for e in r['evidenceRefs']}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 sel=CAP/'selection.json.gz';assert digest(sel.read_bytes())==pins[str(sel.relative_to(ROOT))]
 rows=read(sel)['rows'];assert sorted(r['uid'] for r in rows)==sorted(UIDS)
 refs=[Path(__file__),CAP/'result.json',sel,HERE/'original_pair_terrain_diagnostic.py']
 mp=ROOT/'3d-viewer/city/data/manifest.json';parent=ROOT/'3d-viewer/city/data/terrain.json';fences={p:digest(p.read_bytes()) for p in [mp,parent]};refs.extend(fences)
 for row in rows:
  p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256'];refs.append(p)
  target=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes());assert digest(target.read_bytes())==row['sourceSHA256']
  tile=ROOT/'3d-viewer'/row['source']['tile'];assert next(b for b in read(tile)['buildings'] if b['uid']==row['uid'])==row['source']['building'];refs.append(tile)
 save(DOC/'selection.json.gz',dict(rows=rows))
 error=None
 try:module('tower6803_pair_terrain_builder',HERE/'original_pair_terrain_diagnostic.py').build(rows,DOC,LOCAL)
 except Exception as e:
  error=dict(type=type(e).__name__,message=str(e),traceback=traceback.format_exc());save(DOC/'failure.json',error)
 assert reservations.owns(lease)
 for p,h in fences.items():assert digest(p.read_bytes())==h
 for p in [HERE/'xl-second-pass.py',HERE/'xl-indexed-terrain-continuation.py',HERE/'native_patch_resolution.py']:refs.append(p)
 refs.extend(p for p in LOCAL.rglob('*') if p.is_file() and p.name!='reservation.json')
 t=read(DOC/'terrain.json') if (DOC/'terrain.json').exists() else None
 if t:refs.extend(ROOT/e['path'] for e in t['sourceFiles'])
 result=module('tower6803_pair_candidate_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-pair-private-terrain-construction',list(dict.fromkeys(refs)),dict(uids=UIDS,constructionPassed=error is None,error=error,candidate=t,installationApproved=False,modelGeometryChanges=0,nextStep='Complete current affected-actor and physical/runtime checks; construction alone is not acceptance.'))
 print(dict(jobId=result['jobId'],constructionPassed=error is None,error=error),flush=True)
def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
