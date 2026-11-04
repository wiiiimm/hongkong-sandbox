"""Rebind immutable original/native contact streams to the current post-school inventory."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from polyu_lee_shau_kee_original_catalogue_scope_v1_20261025 import SOURCES,RETAINED,verify_native_scope
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-polyu-lee-shau-kee-current-native-rebind-v1-20261025'
OLD='government-xl-after-tvb-next-three-with-companions-native-contacts-v1-20261025'
INV='government-xl-after-school-current-inventory-v1-20261025'
SCOPE='government-xl-polyu-lee-shau-kee-current-scope-v2-20261025'


def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(n,file):
  if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  p=BASE/n/file;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 native=take(OLD,'summary.json');original=take(OLD,'native-input.json.gz');attrs={r['uid']:r for r in take(OLD,'native-attributes.json.gz')['rows']}
 inventory=take(INV,'complete-bounds.json.gz');bounds={r['uid']:r for r in inventory['rows']};scope=take(SCOPE,'summary.json')
 manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());assert pins[INV][str(manifest.relative_to(ROOT))]==msha==scope['currentManifestSHA256'];refs.append(manifest)
 current={}
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:
   current[e['uid']]=e
   if e['uid']in RETAINED:
    r=next(r for r in original['rows']if r['uid']==e['uid']);assert r['entry']==e and r['path']==str((p.parent/e['asset']).relative_to(ROOT));asset=p.parent/e['asset'];assert digest(asset.read_bytes())==e['sha256']==RETAINED[e['uid']];refs.extend([p,asset])
    assert bounds[e['uid']]['sourceSHA256']==e['sha256']
    assert bounds[e['uid']]['completeFourWorldBounds'][1:]==[attrs[e['uid']][k]for k in ['completeLiteralWorldBounds','completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds','completeExplicitBalancedFloat32ModelMatrixWorldBounds']]
 for p,h in pins[OLD].items():
  if p.startswith('3d-viewer/')and p.endswith('.js'):assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 # Contact kernels depend on the immutable source streams, not changed terrain.
 # Current ground/coverage proofs are separately required by the ROOT review.
 assert verify_native_scope(scope,native,current)
 for p,h in pins[OLD].items():
  if p.startswith('docs/astra-city/government-import/'+OLD+'/')and p.endswith('.json.gz'):
   assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 save(out/'summary.json',native)
 proof=dict(uids=sorted(SOURCES),currentManifestSHA256=msha,archivedContactManifest=original['currentManifest'],nativeFourStreamBoundsReboundToCurrentInventory=True,currentNativeActors=len(current),allRetainedEntriesAndAssetBytesExactlyUnchanged=True,allConsumedRendererModulesExactlyUnchanged=True,archivedRawContactMetricsRetained=True,terrainApprovalTransferred=False,installationApproved=False,publication=False,sourceGeometryChanges=0)
 save(out/'current-context-binding.json',proof);refs.append(out/'summary.json')
 module('polyu_current_native_rebind_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-source-bound-original-native-contact-context-rebinding',refs,proof)


if __name__=='__main__':main()
