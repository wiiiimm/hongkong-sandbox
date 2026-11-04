"""Extra retained-own-view audit after the full original installed readback."""
import os
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_retained_own_views_contract_v1_20261025 import verify


def main():
 base=ROOT/'docs/astra-city/government-import';cfgpath=(ROOT/os.environ['ORIGINAL_INSTALL_CONFIG']).resolve();assert cfgpath.is_relative_to(base);cfg=read(cfgpath)
 installed=base/(cfg['prefix']+'-original-installed-v1-'+cfg['date']);receipt,pins=authenticate(installed)
 full=base/(cfg['prefix']+'-installed-root-readback-v4-'+cfg['date']);full_receipt,_=authenticate(full)
 assert full_receipt['passed'] and full_receipt['installedJobId']==receipt['jobId']and full_receipt['previousAssetsVerified']==cfg['currentNativeActors']and full_receipt['completeFixedXLRowsCompared']==521
 out=base/(cfg['prefix']+'-installed-native-root-readback-v1-'+cfg['date']);assert not out.exists()
 refs=[Path(__file__),HERE/'original_retained_own_views_contract_v1_20261025.py',cfgpath,installed/'result.json',full/'result.json']
 def take(path):
  key=str(path.relative_to(ROOT));assert digest(path.read_bytes())==pins[key];refs.append(path);return read(path)
 physical=take(base/cfg['physical']/'ROOT-PHYSICAL-REVIEW.json');expected=physical['retainedNativeEntries'];assert set(expected)==set(cfg['retainedNativeUids'])
 inspection=read(installed/'ROOT-LIVE-EXPORT-INSPECTION.json');assert inspection['reviewer']=='ROOT'and inspection['visualAcceptance'];refs.append(installed/'ROOT-LIVE-EXPORT-INSPECTION.json')
 images=inspection['retainedImagesActuallyViewed'];assert len(images)==4*len(expected) and len({i['path']for i in images})==len(images)
 views=[];exports=[]
 for width in [390,1280]:
  folder=installed/('viewport-'+str(width));report=take(folder/'live-browser.json');assert report['passed']and not report['errors']
  for v in report['retainedNativeOwnViews']:
   path=folder/v['file'];key=str(path.relative_to(ROOT));sha=digest(path.read_bytes());assert sha==pins[key]
   matches=[i for i in images if i['path']==key and i['sha256']==sha and (i['uid'],i['width'],i['time'])==(v['uid'],v['width'],v['time'])];assert len(matches)==1
   refs.append(path);exports.append(dict(path=key,sha256=sha));views.append(v)
 assert verify(views,expected)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';m=take(manifest);found={}
 for url in m['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url
  for entry in read(path)['models']:
   if entry['uid']in expected:
    assert entry==expected[entry['uid']];asset=path.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];refs.extend([path,asset]);found[entry['uid']]=entry
 assert found==expected
 history=take(installed/'historical-input-context.json');binding=next(q for q in history['mutableCurrentByteSnapshots']if q['originalPath']=='3d-viewer/city/data/manifest.json')
 oldpath=ROOT/binding['savedHistoricalBytes']['path'];assert digest(oldpath.read_bytes())==binding['originalSHA256'];refs.append(oldpath);old=read(oldpath)
 assert {k:v for k,v in m.items()if k not in ['officialModelCatalogues','terrainPatches']}=={k:v for k,v in old.items()if k not in ['officialModelCatalogues','terrainPatches']}
 assert m['officialModelCatalogues'][:-1]==old['officialModelCatalogues']and m['terrainPatches'][:-1]==old['terrainPatches']
 result=dict(uids=list(cfg['sources']),passed=True,installedJobId=receipt['jobId'],snapshotId=receipt['snapshotId'],fullXLCurrentCounts=receipt['fullXLCurrentCounts'],retainedNativeEntries=expected,retainedLiveExportsActuallyViewed=exports,allOtherManifestFieldsUnchanged=True,oldCatalogueOrderPreserved=True,nativeMetadataChanges=0,sourceGeometryChanges=0,aiGeometryModelling=False)
 save(out/'ROOT-NATIVE-READBACK.json',result)
 module('native_addition_installed_readback_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name,'installed-original-additive-retained-own-views-and-manifest-readback',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
