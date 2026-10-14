"""Private unchanged-source browser preview, without publication/placement approval."""
from pathlib import Path
import os,subprocess,shutil,importlib.util,uuid
from run import ROOT,HERE,read,save,digest,reservations
BATCH='government-xl-esplanade-private-browser-v3-20261015';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;STAGE=HERE/'local'/BATCH;PHYSICAL=BASE/'government-xl-esplanade-pair-current-physical-v3-20261015';INPUT=HERE/'local'/PHYSICAL.name

def main():
 assert not DOC.exists()and not STAGE.exists();receipt=read(PHYSICAL/'result.json');refs=[ROOT/r['path']for r in receipt['evidenceRefs']]
 for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 rows=read(PHYSICAL/'selection.json.gz')['rows'];claim=reservations.claim('esplanade-private-browser-'+str(uuid.uuid4()),['building:'+r['uid']for r in rows],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();STAGE.mkdir();catalogue=read(INPUT/'catalogue.json');catalogue['models'].sort(key=lambda e:e['uid']!='landsd/309385:0')
  for entry in catalogue['models']:
   entry.update(priority='landmark',proceduralWindows=False,placementReviewed=False,publicationApproved=False)
   if entry['uid']=='landsd/268828:0':entry['supportDependencies']=[dict(uid='landsd/309385:0',state='candidate',csuid='1484527460P20191115',sha256='ab5f78c1349cfb01db2d60bb36af0122ec8d374abaa5c8b63eaac63f58cd097c')]
   source=INPUT/entry['asset'];dest=STAGE/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);assert digest(dest.read_bytes())==entry['sha256']
  save(STAGE/'catalogue.json',catalogue);save(STAGE/'source-forms.json',[r['source']['building']for r in rows]);patch=read(PHYSICAL/'terrain-candidates.json')[0];dest=STAGE/Path(patch['path']).name;shutil.copyfile(ROOT/patch['path'],dest);assert digest(dest.read_bytes())==patch['sha256']
  config=dict(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[dict(source=str(dest.relative_to(ROOT)),destination='city/data/'+BATCH+'-terrain.json',sha256=patch['sha256'],resolution=read(dest)['cell'],area='Private Esplanade source preview')],browserUids=[r['uid']for r in rows],failureTestUids=['landsd/309385:0'],jointUids=['landsd/309385:0','landsd/268828:0'],fitBox=True,captureBoundsByModel={r['uid']:r['native']['model']['worldBounds']for r in rows})
  bounds=[r['native']['model']['worldBounds']for r in rows];lo=[min(b[0][i]for b in bounds)for i in range(3)];hi=[max(b[1][i]for b in bounds)for i in range(3)];centre=[(a+b)/2 for a,b in zip(lo,hi)];expanded=[[c-(b-a)*.75 for a,b,c in zip(lo,hi,centre)],[c+(b-a)*.75 for a,b,c in zip(lo,hi,centre)]];config['captureBoundsByModel']={r['uid']:expanded for r in rows}
  save(STAGE/'browser-config.json',config);tool=HERE/'esplanade_joint_browser_v2_20261015.mjs';command=['node',str(tool),'staged',str((STAGE/'browser-config.json').relative_to(ROOT))]
  with (DOC/'browser.log').open('w')as log:p=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
  save(DOC/'command.json',dict(command=command,exitCode=p.returncode,installationApproved=False,publication=False,failureRetryTestRequested=True))
  for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
  refs.extend([Path(__file__),tool,PHYSICAL/'result.json']);refs.extend(p for p in STAGE.rglob('*')if p.is_file())
  spec=importlib.util.spec_from_file_location('esplanade_preview_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'private-original-pair-browser-diagnostic-v1',refs,dict(uids=[r['uid']for r in rows],browserExitCode=p.returncode,physicalAccepted=False,fullAcceptance=False,qualification='Private routed catalogue and terrain only; no live changes, no placement/publication approval, podium failed-download/retry test included, screenshots require root inspection.'));print('Browser exit:',p.returncode,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
