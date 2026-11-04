"""Verify the qualified private original pair through the production browser."""
from pathlib import Path
import os,subprocess,importlib.util,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
BATCH='government-xl-esplanade-joint-staged-browser-v1-20261015'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
INPUT=BASE/'government-xl-esplanade-joint-private-stage-v1-20261015'
STAGE=HERE/'accepted'/INPUT.name

def main():
 assert not DOC.exists()
 receipt=read(INPUT/'result.json')
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 save(INPUT/'ROOT-VERIFIED.json',dict(jobId=receipt['jobId'],neonResultExact=True,everyEvidenceHashVerified=True,publication=False))
 uids=['landsd/268828:0','landsd/309385:0']
 claim=reservations.claim('esplanade-staged-browser-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();config=read(STAGE/'browser-config.json');config['doc']=str(DOC.relative_to(ROOT))+'/'
  # Enlarge the mobile framing box while retaining the complete source bounds.
  mobile={}
  for uid,b in config['captureBoundsByModel'].items():
   c=[(x+y)/2 for x,y in zip(*b)];mobile[uid]=[[c[i]+(p[i]-c[i])*1.3 for i in range(3)]for p in b]
  config['captureBoundsByViewport']={'390':mobile}
  save(DOC/'browser-config.json',config)
  tool=HERE/'esplanade_joint_browser_v2_20261015.mjs'
  command=['node',str(tool),'staged',str((DOC/'browser-config.json').relative_to(ROOT))]
  with (DOC/'browser.log').open('w')as log:p=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
  save(DOC/'command.json',dict(command=command,exitCode=p.returncode,publication=False,visualAcceptance=False))
  for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
  paths=[ROOT/r['path']for r in receipt['evidenceRefs']]+[INPUT/'result.json',Path(__file__),tool]
  spec=importlib.util.spec_from_file_location('checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.freeze(BATCH,'qualified-private-original-pair-browser-v1',paths,dict(uids=uids,browserExitCode=p.returncode,fullAcceptance=False,visualAcceptance=False,qualification='Approved private stage; screenshots require root inspection; no live publication.'))
  assert p.returncode==0
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
