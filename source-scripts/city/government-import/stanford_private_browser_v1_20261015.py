"""Private combined-source preview; staged suppression is not publication approval."""
from pathlib import Path
import subprocess,os,shutil
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-stanford-private-browser-v1-20261015';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=HERE/'local/government-xl-stanford-current-loader-validation-v1-20261015'
def main():
 assert not DOC.exists() and not LOCAL.exists();DOC.mkdir();LOCAL.mkdir()
 cat=read(PRIOR/'catalogue.json');assert len(cat['models'])==1;e=cat['models'][0]
 e.update(priority='landmark',suppressesBuildingUids=['landsd/305584:0'])
 dest=LOCAL/e['asset'];dest.parent.mkdir(parents=True);shutil.copyfile(PRIOR/e['asset'],dest);assert digest(dest.read_bytes())==e['sha256']
 forms=read(PRIOR/'source-forms.json');save(LOCAL/'catalogue.json',cat);save(LOCAL/'source-forms.json',[forms[e['uid']]['building']])
 terrain=LOCAL/'terrain.json';shutil.copyfile(PRIOR/'private-terrain.json',terrain)
 rel=lambda p:str(p.relative_to(ROOT))
 config={'stage':rel(LOCAL)+'/','doc':rel(DOC)+'/','catalogueURL':'city/data/official-models/'+BATCH+'/catalogue.json','terrain':[{'source':rel(terrain),'destination':'city/data/'+BATCH+'-terrain.json','sha256':digest(terrain.read_bytes()),'resolution':5,'area':'Private Grand Stanford candidate'}],'browserUids':[e['uid']],'failureTestUids':[e['uid']],'fitBox':True}
 save(LOCAL/'browser-config.json',config)
 tool=HERE/'primrose_assembly_acceptance_browser_v1_20261015.mjs';cmd=['node',str(tool),'staged',rel(LOCAL/'browser-config.json')]
 with (DOC/'browser.log').open('w') as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
 save(DOC/'command.json',{'command':cmd,'exitCode':p.returncode,'publication':False})
 refs=[Path(__file__),tool,*[p for p in LOCAL.rglob('*') if p.is_file()]]
 module('freeze_stanford_browser',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-combined-source-browser-v1',refs,{'uids':[e['uid']],'browserExitCode':p.returncode,'fullAcceptance':False,'installed':False,'qualification':'Unapproved combined-source preview with conditional podium suppression; identity review remains pending. No live catalogue writes.'})
 print({'exitCode':p.returncode},flush=True)
if __name__=='__main__':main()
