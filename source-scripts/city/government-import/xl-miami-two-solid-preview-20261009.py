"""Show the reviewed solid originals in a separate non-publishing browser stage."""
import importlib.util,shutil,subprocess,sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
BASE=module('miami_reviewed_stage',HERE/'xl-miami-two-stage-checkpoint-20261009.py')
BATCH='government-xl-miami-two-solid-preview-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
STAGE=HERE/'accepted'/BATCH
def main():
 assert not DOC.exists() and not STAGE.exists(),'Fresh non-publishing preview required'
 proof=BASE.recheck();catalogue=read(BASE.STAGE/'catalogue.json')
 for m in catalogue['models']:
  assert m['publicationApproved'] is False;m['publicationApproved']=True
  p=STAGE/m['asset'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(BASE.STAGE/m['asset'],p);assert digest(p.read_bytes())==m['sha256']
 save(STAGE/'catalogue.json',catalogue);shutil.copyfile(BASE.STAGE/'source-forms.json',STAGE/'source-forms.json');shutil.copyfile(BASE.STAGE/'catalogue-index.json',STAGE/'catalogue-index.json')
 old=read(BASE.STAGE/'plan.json');terrain=dict(old['topLevelTerrainPatches'][0]);p=STAGE/Path(terrain['source']).name;shutil.copyfile(ROOT/terrain['source'],p);terrain['source']=str(p.relative_to(ROOT));destination='city/data/official-models/'+BATCH+'/catalogue.json'
 save(STAGE/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':str((STAGE/'catalogue.json').relative_to(ROOT)),'destination':destination}],'topLevelTerrainPatches':[terrain]})
 config=read(BASE.STAGE/'browser-config-v2.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[terrain]);save(STAGE/'browser-config.json',config)
 save(DOC/'solid-preview-inputs.json',{'sourceStageJobId':'57fb4bda504515abff5a99e66a6451e86a9ea233a6e016b0dd7f161305187ce2','physicalReplay':proof,'soleCatalogueFieldChange':'publicationApproved:false→true','currentManifestSHA256':proof['currentManifestSHA256'],'publication':False,'sourceGeometryChanges':0})
 subprocess.run(['node',str(HERE/'xl-miami-two-staged-browser-20261009.mjs'),'staged',str((STAGE/'browser-config.json').relative_to(ROOT))],cwd=ROOT,check=True)
 report=module('miami_solid_browser_validator',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',set(BASE.UIDS));assert BASE.recheck()==proof
 for v in report['views']:
  if 'time' in v:assert v['fullyFramed'] and abs(v['ground']-v['groundSampler'])<=.004 and v['retained']['landsd/232089:0']=={'loaded':True,'detailedActive':False,'hidden':False}
 print({'solidOriginalBrowserPassed':True,'publication':False},flush=True)
if __name__=='__main__':main()
