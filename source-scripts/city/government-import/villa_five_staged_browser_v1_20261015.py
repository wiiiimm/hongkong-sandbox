"""Private runtime evidence for five unchanged Villa originals; no approval/publication."""
from pathlib import Path
import os, subprocess, importlib.util, uuid, urllib.request
from run import ROOT,HERE,read,save,digest,connect,reservations
BATCH='government-xl-villa-five-staged-browser-v1-20261015'
BASE=ROOT/'docs/astra-city/government-import'; DOC=BASE/BATCH
INPUT=BASE/'government-xl-villa-five-current-physical-v4-20261015'
STAGE=HERE/'local'/INPUT.name

def main():
 assert not DOC.exists()
 receipt=read(INPUT/'result.json')
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']: assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 for p in ['city/app.js','city/building-geometry.js','city/procedural-footprint-corrections.js','city/data/manifest.json']:
  assert urllib.request.urlopen('http://127.0.0.1:4176/'+p).read()==(ROOT/'3d-viewer'/p).read_bytes(),p
 catalogue=read(STAGE/'catalogue.json'); models=catalogue['models'];uids=[m['uid'] for m in models]
 assert set(uids)=={'landsd/89917:0','landsd/58497:0','landsd/63823:0','landsd/121309:0','landsd/148052:0'}
 uids=['landsd/89917:0']+[u for u in uids if u!='landsd/89917:0']
 bounds=[[min(m['worldBounds'][0][i] for m in models) for i in range(3)],[max(m['worldBounds'][1][i] for m in models) for i in range(3)]]
 centre=[(a+b)/2 for a,b in zip(*bounds)];mobile=[[centre[i]+(v-centre[i])*1.3 for i,v in enumerate(p)]for p in bounds]
 terrain=HERE/'local/government-xl-villa-five-float32-bounded-terrain-gap-infill-proposal-v1-20261010/government-native-89917-0.json'
 assert digest(terrain.read_bytes())=='7b0e4c7feb05b1f6e76756d72877f5c157e532bd5288be679ccea386062adff6'
 claim=reservations.claim('villa-staged-browser-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir()
  config=dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',browserUids=uids,jointUids=uids,failureTestUids=['landsd/89917:0'],fitBox=True,captureBoundsByModel={u:bounds for u in uids},captureBoundsByViewport={'390':{u:mobile for u in uids}},terrain=[dict(source=str(terrain.relative_to(ROOT)),destination='city/data/government-native-villa-private-browser-v1-20261015.json',sha256=digest(terrain.read_bytes()),area='Villa original-source private terrain',resolution=5)])
  save(DOC/'browser-config.json',config)
  tool=HERE/'primrose_assembly_acceptance_browser_v1_20261015.mjs';command=['node',str(tool),'staged',str((DOC/'browser-config.json').relative_to(ROOT))]
  with (DOC/'browser.log').open('w') as log:p=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
  save(DOC/'command.json',dict(command=command,exitCode=p.returncode,publication=False,visualAcceptance=False))
  for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
  paths=[ROOT/r['path']for r in receipt['evidenceRefs']]+[INPUT/'result.json',Path(__file__),tool,terrain]
  spec=importlib.util.spec_from_file_location('checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.freeze(BATCH,'private-five-original-runtime-browser-v1',paths,dict(uids=uids,browserExitCode=p.returncode,fullAcceptance=False,visualAcceptance=False,qualification='Private runtime evidence only; source functional and placed collision acceptance remain required. No live publication.'))
  assert p.returncode==0
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
