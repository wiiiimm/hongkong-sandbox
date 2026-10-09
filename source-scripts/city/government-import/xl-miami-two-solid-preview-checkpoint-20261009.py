"""Freeze clean solid exports and explicit original-material/fallback assertions."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read,digest,connect
BATCH='government-xl-miami-two-solid-preview-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;STAGE=HERE/'accepted'/BATCH
UIDS={'landsd/202994:0','landsd/203433:0'}
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 base=DOC.parent/'government-xl-miami-two-original-staged-20261009';staged=read(base/'result.json');assert staged['jobId']=='57fb4bda504515abff5a99e66a6451e86a9ea233a6e016b0dd7f161305187ce2'
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(staged['jobId'],)).fetchone()==('complete',staged)
 for r in staged['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256'],r['path']
 inputs=read(DOC/'solid-preview-inputs.json');assert inputs['currentManifestSHA256']==digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())
 models=read(STAGE/'catalogue.json')['models'];prior=read(HERE/'accepted/government-xl-miami-two-original-staged-20261009/catalogue.json')['models'];assert {m['uid'] for m in models}==UIDS
 for m in models:
  old=next(o for o in prior if o['uid']==m['uid']);assert m['publicationApproved'] is True and old['publicationApproved'] is False
  assert {k:v for k,v in m.items() if k!='publicationApproved'}=={k:v for k,v in old.items() if k!='publicationApproved'}
  assert digest((STAGE/m['asset']).read_bytes())==m['sha256']
 module('solid_browser_validator',HERE/'integrate.py').browser_verified(DOC/'browser-solid-v3/staged-browser.json',UIDS)
 appearance=read(DOC/'appearance-check/staged-browser.json');assert appearance['passed'] and not appearance['errors'] and {v['uid'] for v in appearance['views']}==UIDS
 for v in appearance['views']:
  m=next(m for m in models if m['uid']==v['uid']);assert v['sourceSHA256']==m['sha256'] and v['sourceTriangles']==m['triangles'] and v['proceduralWindows'] is False and v['basicFallbackVertices']==0 and v['selectionClosed'] and v['active']
  assert v['materials'] and all(a['visible'] and not a['wireframe'] and a['opacity']==1 and not a['transparent'] for a in v['materials'])
  assert v['retained']['landsd/232089:0']=={'loaded':True,'detailedActive':False,'hidden':False}
 paths=[Path(__file__),base/'result.json']+[ROOT/r['path'] for r in staged['evidenceRefs']]+[p for p in STAGE.rglob('*') if p.is_file()]+[HERE/f for f in ['xl-miami-two-solid-preview-20261009.py','xl-miami-two-solid-browser-20261009.mjs','xl-miami-two-solid-appearance-20261009.mjs','xl-miami-two-original-live-install-20261009.py']]
 module('solid_preview_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-unchanged-original-solid-source-rendering-and-primary-basic-removal-v1',paths,{'uids':sorted(UIDS),'sourceStageJobId':staged['jobId'],'sourceSHA256s':{m['uid']:m['sha256'] for m in models},'currentManifestSHA256':inputs['currentManifestSHA256'],'stagedBrowserPassed':True,'solidOriginalAppearancePassed':True,'eightCleanDesktopMobileDayNightExportsOpened':True,'twoAdditionalMaterialSourceAndFallbackAssertionsPassed':True,'primaryBasicFallbackVertices':0,'sourceMaterialsOpaqueVisibleWireframeFalse':True,'selectionHighlightClosedThroughNormalUI':True,'retainedBasicPodiumVisible':True,'scriptFullAcceptancePassed':True,'sourceGeometryChanges':0,'remainingReason':'root-independent-clean-export-review-and-atomic-live-publication','nextStep':'Root runs the pinned atomic Miami live installer after independent review. Earlier yellow edges were selected-building highlighting, not source wireframe; review flag has no runtime source-material effect. No installed credit yet.'})
if __name__=='__main__':main()
