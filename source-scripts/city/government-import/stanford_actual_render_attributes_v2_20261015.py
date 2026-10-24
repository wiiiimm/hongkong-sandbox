"""Capture exact current loader arithmetic for one combined original hotel asset."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-stanford-actual-render-attributes-v2-20261015';DOC=BASE/BATCH
UID='landsd/335875:0'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();DOC.mkdir();bindingpath=BASE/'government-xl-unmapped-two-primary-evidence-v1-20261015/viewer-bindings.json';bound=next(r for r in read(bindingpath)['rows']if r['modelId']=='B365201779201063C0');b=next(x for x in bound['bindings']if x['viewerUID']==UID);form=b['viewerForm'];tile=ROOT/'3d-viewer/city/data/tiles'/ (form['tile']+'.json');assert form in read(tile)['buildings'];cataloguepath=HERE/'local/government-xl-unmapped-runtime-diagnostic-v1-20261015/candidates/catalogue.json';catalogue=read(cataloguepath);entry={**next(e for e in catalogue['models']if e['uid']==UID),'rootTranslation':catalogue['rootTranslation']};assert entry['rootTranslation']==[-834500,0,816500];source=next(s for s in read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows']if s['modelId']==bound['modelId']);asset=ROOT/source['asset']['path'];assert digest(asset.read_bytes())==entry['sha256']==bound['sourceSHA256'];manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath)
 save(DOC/'input.json.gz',{'currentManifest':ref(manifestpath),'currentCatalogueRefs':[ref(ROOT/'3d-viewer'/url)for url in manifest['officialModelCatalogues']],'evidenceRefs':[ref(bindingpath),ref(tile),ref(cataloguepath)],'rows':[{'uid':UID,'entry':entry,'building':form,'path':str(asset.relative_to(ROOT))}],'qualification':'Single diagnostic route for combined original hotel. Podium suppression and identity acceptance are not granted.'})
 tool=HERE/'stanford_actual_render_attributes_v1_20261015.mjs'
 with (DOC/'capture.log').open('w')as log:p=subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'command.json',{'exitCode':p.returncode});assert p.returncode==0
 output=read(DOC/'attributes.json.gz');assert output['startEndAllInputsVerified'];refs=[Path(__file__),tool]+[ROOT/p for p in output['inputHashes']]
 for p,h in output['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 module('freeze_stanford_attributes',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'single-original-hotel-complete-loader-attributes-v1',refs,{'uids':[UID],'completeFaces':10049,'fullAcceptance':False});print('Captured one complete original hotel, three runtime arithmetic representations',flush=True)
if __name__=='__main__':main()
