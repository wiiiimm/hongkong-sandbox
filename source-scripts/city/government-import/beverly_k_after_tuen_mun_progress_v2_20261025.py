"""Checkpoint exact Beverly K finite support evidence without installation credit."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-beverly-k-after-tuen-mun-progress-v2-20261025'
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];completed=[]
 for folder in sorted(BASE.glob('government-xl-beverly-k-after-tuen-mun-*-20261025')):
  if folder.name==BATCH or not(folder/'result.json').is_file():continue
  result,_=authenticate(folder);completed.append(dict(batch=folder.name,jobId=result['jobId']));refs.append(folder/'result.json')
 prior=BASE/'government-xl-beverly-k-after-tuen-mun-progress-v1-20261025'/'remaining-work.json';refs.append(prior);result=read(prior)
 support=BASE/'government-xl-beverly-k-after-tuen-mun-finite-basic-evidence-v1-20261025'/'summary.json';refs.append(support);proof=read(support)
 assert proof['completeFourWorldFiniteRetainedBasicSupport']is True and proof['completeFourWorldCanonicalRetainedBasicSupport']is False and proof['physicalSupportAccepted']is False
 manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest);assert digest(manifest.read_bytes())==result['currentManifestSHA256']
 result.update(completed=completed,checkpointVersion=2,separateFiniteBasicEvidence=dict(path=str(support.relative_to(ROOT)),sha256=digest(support.read_bytes())),remainingWork=[
  'Private-basic-browser-v1 desktop/mobile day/night source and retained-J exports all actually inspected; P233218 remains visible BASIC and mobile failed-download fallback passed. These private checks grant no live installation credit.',
  'Bind bounded source-specific physical/identity interpretation preserving canonical strict support false, all105 K/J contacts and7 roof-area contacts; finite path evidence is not automatic source/publication approval. Native J publicationApproved:false remains unchanged.',
  'Prepare a separate guarded finite-support admission path that replays exact four-world evidence and checks current BASIC lifetime, complete4form leases and full retained-native evidence. Do not set canonical support true or weaken the existing canonical publisher.',
  'After private qualification, commit/push before installation; guarded install then actually inspect fresh live exports, record full old6954assets/521inventory/globalBASIC/native/manifest readback, refresh inventories and commit/push. No geometry modelling or optimisation.'
 ])
 result['evidence'].update(finiteUndersideTargetsPerMode=10,finiteUndersidePathsVerifiedPerMode=10,finiteModeCount=4,embeddingM=.34999847412109375,canonicalContactPassed=False,horizontalNativeContactPairAreaSumM2=.005276418214587686,contactPairAreaIsUnion=False,foreignBlockAPositivePairs=0)
 browser=BASE/'government-xl-beverly-k-after-tuen-mun-private-basic-browser-v1-20261025';_,pins=authenticate(browser);images=[]
 for width in [390,1280]:
  report=browser/str(width)/'staged-browser.json';refs.append(report);r=read(report);assert r['passed']and not r['errors']
  views=[v for v in r['views']if 'time'in v];assert len(views)==2
  for v in views:assert v['retained']['landsd/233218:0']==dict(loaded=True,detailedActive=False,hidden=False,base=41.4,height=34.5,baseSource='landsd')
  if width==390:assert any(v.get('phase')=='failed-download'and v.get('fallbackRetained')for v in r['views'])
  paths=sorted((browser/str(width)).glob('*.png'));assert len(paths)==4
  for image in paths:
   key=str(image.relative_to(ROOT));assert digest(image.read_bytes())==pins[key];refs.append(image);images.append(dict(path=key,sha256=pins[key]))
 result.update(privateImagesActuallyViewedByRoot=images,privateViewDecision='Source K and retained J facades/roofs/base interfaces readable in all8 private exports. Original grey/darknight materials and existing BASIC illuminated windows remain; no new static visible defect observed. Raw canonical failure and native publication hold preserved. Not live-image or publication approval.',privateBrowserDiagnosticsPassed=True)
 save(out/'remaining-work.json',result)
 module('beverly_k_finite_progress_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'beverly-k-separate-finite-support-evidence-and-actionable-holds',list(dict.fromkeys(refs)),result)
 print(dict(completed=len(completed),newlyInstalled=0,state=result['state']),flush=True)
if __name__=='__main__':main()
