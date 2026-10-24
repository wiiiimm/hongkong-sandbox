"""Private podium/shelter close-up with all four unchanged originals present."""
from pathlib import Path
import os,subprocess,shutil,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import BASE,SOURCE,PODIUM,module
BATCH='government-xl-primrose-private-podium-browser-v2-20261015';DOC=BASE/BATCH;STAGE=HERE/'local'/BATCH
TERRAIN=BASE/'government-xl-primrose-private-terrain-floor-v5-20261015'
def main():
 assert not DOC.exists()and not STAGE.exists();refs={}
 for folder in [SOURCE,TERRAIN,BASE/'government-xl-primrose-podium-role-review-v2-20261015']:
  r=read(folder/'result.json')
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for q in r['evidenceRefs']:
   assert q['path']not in refs or refs[q['path']]==q['sha256'];refs[q['path']]=q['sha256']
  refs[str((folder/'result.json').relative_to(ROOT))]=digest((folder/'result.json').read_bytes())
 for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(SOURCE/'selection.json.gz')['rows'];podium=next(r for r in rows if r['uid']==PODIUM)
 claim=reservations.claim('primrose-private-browser-'+str(uuid.uuid4()),['building:'+r['uid']for r in rows],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();STAGE.mkdir();entries=[]
  for row in sorted(rows,key=lambda r:r['uid']!=PODIUM):
   e=dict(row['candidate']['entry']);e.update(priority='landmark',proceduralWindows=False,placementReviewed=False,publicationApproved=False,suppressesBuildingUids=[])
   if row['uid']!=PODIUM:e['supportDependencies']=[dict(uid=PODIUM,state='candidate',csuid=podium['source']['building']['buildingCSUID'],sha256=podium['sourceSHA256'])]
   dest=STAGE/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],dest);assert digest(dest.read_bytes())==row['sourceSHA256'];entries.append(e)
  cat=dict(schemaVersion=1,kind='staged-official-model-catalogue',area='Private Primrose original assembly',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],coordinatePolicy='Unchanged source geometry and original placement',counts=dict(packedModels=4),models=entries)
  save(STAGE/'catalogue.json',cat);save(STAGE/'source-forms.json',[r['source']['building']for r in rows])
  candidate=read(TERRAIN/'terrain-candidates.json')[0];dest=STAGE/Path(candidate['path']).name;shutil.copyfile(ROOT/candidate['path'],dest);assert digest(dest.read_bytes())==candidate['sha256']
  bounds=podium['native']['model']['worldBounds'];lo,hi=bounds;centre=[(a+b)/2 for a,b in zip(lo,hi)];expanded=[[c-(b-a)*.7 for a,b,c in zip(lo,hi,centre)],[c+(b-a)*.7 for a,b,c in zip(lo,hi,centre)]]
  config=dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[dict(source=str(dest.relative_to(ROOT)),destination='city/data/'+BATCH+'-terrain.json',sha256=candidate['sha256'],resolution=read(dest)['cell'],area=cat['area'])],browserUids=[PODIUM],failureTestUids=[PODIUM],jointUids=[e['uid']for e in entries],fitBox=True,captureBoundsByModel={PODIUM:expanded})
  shelter=next(b for b in read(ROOT/'3d-viewer/city/data/tiles/-2_-5.json')['buildings']if b['uid']=='landsd/74566:0');ring=shelter['rings'][0];config['focusPoint']=[(min(p[0]for p in ring)+max(p[0]for p in ring))/2,shelter['topHeightHKPD'],(min(p[1]for p in ring)+max(p[1]for p in ring))/2]
  save(STAGE/'browser-config.json',config);tool=HERE/'primrose_shelter_focus_browser_v1_20261015.mjs';command=['node',str(tool),'staged',str((STAGE/'browser-config.json').relative_to(ROOT))]
  with (DOC/'browser.log').open('w')as log:p=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
  save(DOC/'command.json',dict(command=command,exitCode=p.returncode,publication=False))
  for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h,p
  paths=[ROOT/p for p in refs]+[Path(__file__),tool,HERE/'primrose_compound_foundation_v2_20261015.py']+[p for p in STAGE.rglob('*')if p.is_file()]
  module('preview_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-four-original-podium-shelter-browser-context-v1',paths,dict(uids=[r['uid']for r in rows],browserExitCode=read(DOC/'command.json')['exitCode'],fullAcceptance=False,qualification='Unapproved private preview, current BASIC shelter retained. Screenshots require inspection. No publication, model edits or suppression.'))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
