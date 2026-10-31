"""Private four-original loader and neighbour checks; no installation approval."""
from pathlib import Path
import json,sys,uuid,subprocess,shutil
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-nobhill-group-four-world-v1-20261018';GROUND=BASE/'government-xl-nobhill-shelter-ground-trial-v1-20261018';TEMPLATE=BASE/'government-xl-nobhill98845-source-terrain-v2-20261018';BATCH='government-xl-nobhill-joint-validation-v2-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);pins={};refs=[Path(__file__)]
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,GROUND,TEMPLATE]:
   receipt=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(folder/'result.json')
   for e in receipt['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 def checked(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 rows=checked(CAP/'selection.json.gz')['rows'];selection=checked(GROUND/'selection.json.gz');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 catalogue=checked(HERE/'local'/TEMPLATE.name/'catalogue.json');catalogue['area']=BATCH;catalogue['models']=[];catalogue['counts']['packedModels']=len(rows);forms={}
 for row in rows:
  source=ROOT/row['candidate']['path'];assert digest(source.read_bytes())==row['sourceSHA256'];refs.append(source);dest=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);assert digest(dest.read_bytes())==row['sourceSHA256'];entry={**row['candidate']['entry'],'asset':'assets/'+dest.name,'placementReviewed':False,'publicationApproved':False};catalogue['models'].append(entry);row['candidate']={**row['candidate'],'entry':entry,'path':str(dest.relative_to(ROOT))};forms[row['uid']]=row['source']
 selection['rows']=rows;save(DOC/'selection.json.gz',selection);save(LOCAL/'catalogue.json',catalogue);save(LOCAL/'catalogue-index.json',dict(catalogues=['catalogue.json'],models=len(rows)));save(LOCAL/'source-forms.json',forms)
 candidates=checked(GROUND/'terrain-candidates.json');inputs=checked(GROUND/'neighbour-inputs.json.gz');uids=[r['uid']for r in rows];inputs['candidateIds']=uids
 for p in candidates:assert digest((ROOT/p['path']).read_bytes())==p['sha256'];refs.append(ROOT/p['path']);p['uids']=uids
 inputs['patches']=candidates;save(DOC/'terrain-candidates.json',candidates);save(DOC/'neighbour-inputs.json.gz',inputs)
 def rel(p):return str(p.relative_to(ROOT))
 commands=[['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')],['node',str(HERE.parent/'building-batch/validate_candidates_multi_retained.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],['node',str(HERE/'check-neighbours-multi-retained.mjs'),rel(DOC)+'/']];results=[]
 for args in commands:
  assert reservations.owns(lease);result=subprocess.run(args,cwd=ROOT);results.append(dict(command=args,returncode=result.returncode));assert result.returncode in (0,1);refs.append(Path(args[1]))
 save(DOC/'commands.json',dict(rows=results));assert reservations.owns(lease)
 for p in refs:
  key=str(p.relative_to(ROOT))
  if key in pins:assert digest(p.read_bytes())==pins[key]
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file() and p.name!='reservation.json');summary=dict(uids=uids,commands=results,physicalAccepted=False,installationApproved=False,qualification='Private staged four-model checks only. Source-specific support, complete actual-native bounds nomination, browser and publication remain separate.');out=module('nob_joint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'nobhill-four-originals-private-loader-neighbour-checks-v2',list(dict.fromkeys(refs)),summary);print(out['jobId'],flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists();inputs=read(GROUND/'neighbour-inputs.json.gz');uids={r['building']['uid']for r in inputs['rows']}|{r['uid']for r in read(CAP/'selection.json.gz')['rows']};keys={('building:'if u.startswith('landsd/')else'source-form:')+u for u in uids}|{'terrain:city/data/terrain.json'};claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
