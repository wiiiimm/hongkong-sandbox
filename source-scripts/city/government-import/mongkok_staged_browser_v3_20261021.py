"""Private browser validation of the new stand with the real installed opposite stand."""
from pathlib import Path
import copy,os,subprocess,json,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mongkok-staged-browser-v3-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
NODE='/home/williamli/.nvm/versions/node/v24.18.0/bin/node'
def owned():
    lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)];pins={}
    def take(batch,p):
        _,ps=authenticate(BASE/batch);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/batch/'result.json',p]);return read(p)
    batch='government-xl-mongkok-loader-v1-20261021';catalogue=take(batch,HERE/'local'/batch/'catalogue.json');assert take(batch,BASE/batch/'summary.json')['checksPassed']==2
    entry=copy.deepcopy(next(e for e in catalogue['models']if e['uid']=='landsd/240332:0'));src=HERE/'local'/batch/entry['asset'];assert digest(src.read_bytes())==entry['sha256'];refs.append(src)
    entry.update(priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False);entry['asset']='assets/'+entry['sha256']+'.glb.gz';target=LOCAL/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(src.read_bytes())
    catalogue['models']=[entry];catalogue['counts']={'packedModels':1};save(LOCAL/'catalogue.json',catalogue);save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']))
    batch='government-xl-mongkok-inset-pair-runtime-v1-20261021';selection=take(batch,BASE/batch/'selection.json.gz');row=next(r for r in selection['rows']if r['uid']==entry['uid']);save(LOCAL/'source-forms.json',[row['source']['building']]);save(LOCAL/'validation-forms.json',{row['uid']:row['source']})
    c=take(batch,BASE/batch/'terrain-candidates.json')[0];p=ROOT/c['path'];assert digest(p.read_bytes())==c['sha256'];refs.append(p)
    terrain=[dict(source=c['path'],destination='city/data/government-native-mongkok-private-browser-v1-20261021.json',sha256=c['sha256'],resolution=read(p)['cell'],area='Private original stadium terrain check',replaces=c['replaces'])]
    tool=HERE/'mongkok_settled_camera_browser_v3_20261021.mjs';refs.append(tool)
    config=dict(stage=str(LOCAL.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=terrain,browserUids=[row['uid']],fitBox=True,captureDirectionByModel={row['uid']:[-.3,.7,-1]},additionalRetainedUids=['landsd/240527:0'],jointUids=['landsd/240332:0','landsd/240527:0'],nativeSupportUidsByModel={})
    for width in [1280,390]:
        assert reservations.owns(lease);cfg={**config,'viewportWidths':[width],'failureTestUids':[row['uid']]if width==390 else[],'doc':str((DOC/str(width)).relative_to(ROOT))+'/'};p=LOCAL/f'browser-config-{width}.json';save(p,cfg);DOC.mkdir(parents=True,exist_ok=True)
        with(DOC/f'browser-{width}.log').open('w')as log:proc=subprocess.run([NODE,str(tool),'staged',str(p.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1200)
        save(DOC/f'command-{width}.json',dict(exitCode=proc.returncode));assert proc.returncode==0
        assert read(DOC/str(width)/'staged-browser.json')['passed']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
    refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
    module('stadium_staged_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-original-and-retained-desktop-mobile-browser',list(dict.fromkeys(refs)),dict(uids=['landsd/240332:0','landsd/240527:0'],installationApproved=False,visualAcceptance=False,sourceGeometryChanges=0))
def main():
    if '--owned'in sys.argv:return owned()
    assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/240332:0','building:landsd/240527:0'],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
    try:subprocess.run([sys.executable,str(HERE/'harbourfront_reserved_runner_v1_20261021.py'),str(p),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
