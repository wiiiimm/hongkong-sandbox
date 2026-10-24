"""Private three-original assembly capture; no publication or geometry edits."""
from pathlib import Path
import os, subprocess, shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-opus-original-group-browser-v1-20261017'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=HERE/'local/government-xl-opus-original-group-v1-20261017'
def main():
 assert not DOC.exists() and not LOCAL.exists()
 pins={};refs=[Path(__file__)]
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for name in ['original-group-v1-20261017','source-support-review-v1-20261017','current-native-scope-v2-20261017']:
   p=BASE/('government-xl-opus-'+name)/'result.json';r=read(p)
   assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for q in r['evidenceRefs']:
    assert q['path'] not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 DOC.mkdir();LOCAL.mkdir();rel=lambda p:str(p.relative_to(ROOT));cat=read(PRIOR/'catalogue.json');forms=read(PRIOR/'source-forms.json')
 for e in cat['models']:
  e['proceduralWindows']=False
  e['supportDependencies']=[] if e['uid']=='landsd/248432:0' else [dict(uid='landsd/248432:0',state='candidate',csuid='3599414486P20120215',sha256='413249980adc12dffbe589ec5db87a66075682c71e134b0e21a74d228d85f72e')]
  dest=LOCAL/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(PRIOR/e['asset'],dest);assert digest(dest.read_bytes())==e['sha256']
 save(LOCAL/'catalogue.json',cat);save(LOCAL/'source-forms.json',[forms[e['uid']]['building'] for e in cat['models']])
 tr=read(BASE/'government-xl-opus-original-group-v1-20261017/terrain-candidates.json')[0];assert digest((ROOT/tr['path']).read_bytes())==tr['sha256']
 uids=[e['uid'] for e in cat['models']];bounds=[[min(e['worldBounds'][0][i] for e in cat['models']) for i in range(3)],[max(e['worldBounds'][1][i] for e in cat['models']) for i in range(3)]]
 config=dict(stage=rel(LOCAL)+'/',doc=rel(DOC)+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[dict(source=tr['path'],destination='city/data/'+BATCH+'-terrain.json',sha256=tr['sha256'],resolution=5,area='Private Opus original terrain')],browserUids=uids,failureTestUids=['landsd/248432:0'],dependentFailureUidsByModel={'landsd/248432:0':['landsd/322573:0','landsd/319559:0']},nativeSupportUidsByModel={u:[] for u in uids},jointUids=uids,fitBox=True,captureDirectionByModel={u:[.75,.6,-.65] for u in uids},captureBoundsByModel={u:bounds for u in uids})
 save(LOCAL/'browser-config.json',config);tool=HERE/'pool_dependency_assembly_browser_v1_20261017.mjs';cmd=['node',str(tool),'staged',rel(LOCAL/'browser-config.json')]
 with (DOC/'browser.log').open('w') as log:out=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
 save(DOC/'command.json',dict(command=cmd,exitCode=out.returncode,publication=False,diagnosticOnly=True))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 refs += [ROOT/'3d-viewer/city/official-models.js',tool,*[p for p in LOCAL.rglob('*') if p.is_file()]]
 r=module('fu_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-three-original-opus-assembly-browser-diagnostic-v1',list(dict.fromkeys(refs)),dict(uids=uids,browserExitCode=out.returncode,fullAcceptance=False,newlyInstalled=0))
 print(dict(jobId=r['jobId'],exitCode=out.returncode),flush=True)
if __name__=='__main__':main()
