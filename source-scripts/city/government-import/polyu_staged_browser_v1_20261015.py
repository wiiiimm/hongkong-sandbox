"""Private unchanged-original PolyU browser acceptance; no public publication."""
from pathlib import Path
import os,shutil,subprocess,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-staged-browser-v1-20261015';DOC=BASE/BATCH;STAGE=HERE/'local'/BATCH;UID='landsd/305582:0'
def main():
 assert not DOC.exists()and not STAGE.exists()
 inp=BASE/'government-xl-polyu-current-foundation-v1-20261015';r=read(inp/'result.json');assert r['allFoundationChecksPassed']
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256'],q['path']
 claim=reservations.claim('polyu-private-browser-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();STAGE.mkdir();source=HERE/'local/government-xl-polyu-current-loader-validation-v1-20261015';cat=read(source/'catalogue.json');assert len(cat['models'])==1;entry=cat['models'][0];assert entry['uid']==UID and not entry['publicationApproved'];dest=STAGE/entry['asset'];dest.parent.mkdir();shutil.copyfile(source/entry['asset'],dest);assert digest(dest.read_bytes())==entry['sha256']
  save(STAGE/'catalogue.json',cat);save(STAGE/'source-forms.json',read(source/'source-forms.json'))
  candidate=read(BASE/'government-xl-polyu-refined-candidate-metadata-validator-v1-20261014/unchanged-validator-outcome.json')['metadataOnlyCandidate'];assert digest((ROOT/candidate['path']).read_bytes())==candidate['sha256'];patch=read(ROOT/candidate['path']);pub=module('polyu_unchanged_publisher',HERE.parent/'island-detail-integration/publish.py');parent=read(ROOT/'3d-viewer/city/data/terrain.json');manifest=read(ROOT/'3d-viewer/city/data/manifest.json');pub.validate_patch(patch,parent);pub.check_patch_overlap(patch,parent.get('patches',[])+[read(ROOT/'3d-viewer'/p['url'])for p in manifest['terrainPatches']]);save(DOC/'terrain-validation.json',dict(passed=True,candidate=candidate,publication=False))
  terrain=dict(source=candidate['path'],sha256=candidate['sha256'],destination='city/data/government-native-polyu-original-v1-20261015.json',resolution=patch['cell'],area='PolyU original campus podium')
  bounds=entry['worldBounds'];centre=[(a+b)/2 for a,b in zip(*bounds)];expanded=[[centre[i]+(p[i]-centre[i])*1.15 for i in range(3)]for p in bounds]
  config=dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[terrain],browserUids=[UID],failureTestUids=[UID],fitBox=True,captureBoundsByModel={UID:expanded},nativeSupportUidsByModel={UID:['landsd/305793:0']},retainedBuildingUidsByModel={UID:['landsd/114494:0','landsd/235076:0']})
  save(DOC/'browser-config.json',config);tool=HERE/'esplanade_joint_browser_v2_20261015.mjs';command=['node',str(tool),'staged',str((DOC/'browser-config.json').relative_to(ROOT))]
  with(DOC/'browser.log').open('w')as log:p=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
  save(DOC/'command.json',dict(command=command,exitCode=p.returncode,publication=False,visualAcceptance=False))
  for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256'],q['path']
  paths=[ROOT/q['path']for q in r['evidenceRefs']]+[inp/'result.json',Path(__file__),tool,HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/native_terrain_validation.py']+[p for p in STAGE.rglob('*')if p.is_file()]
  module('polyu_browser_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-private-browser-current-neighbours-v1',paths,dict(uids=[UID],browserExitCode=p.returncode,fullAcceptance=False,visualAcceptance=False,nativePublicationHoldRetained=True));assert p.returncode==0
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
