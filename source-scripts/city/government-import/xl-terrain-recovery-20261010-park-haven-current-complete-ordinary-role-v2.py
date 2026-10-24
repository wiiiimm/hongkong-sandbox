"""Add independently complete current native whole-bounds inventory to v1."""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-terrain-recovery-park-haven-current-complete-ordinary-role-v2-20261010';DOC=BASE/BATCH
s=importlib.util.spec_from_file_location('park_full_ordinary_v1',HERE/'xl-terrain-recovery-20261010-park-haven-current-complete-ordinary-role-v1.py');prior=importlib.util.module_from_spec(s);s.loader.exec_module(prior)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def recheck():
 result=prior.recheck();bounds=result['terrainProposal'][0]['bounds'];manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start==result['currentManifest'];whole=[];touching=[]
 for url in read(manifest)['officialModelCatalogues']:
  catalogue=ROOT/'3d-viewer'/url
  for model in read(catalogue)['models']:
   b=np.asarray(model['worldBounds'],float);assert b.shape==(2,3) and np.isfinite(b).all() and np.all(b[0]<=b[1]);row=dict(uid=model['uid'],sourceSHA256=model['sha256'],catalogue=ref(catalogue),completeOriginalWorldBounds=b.tolist());whole.append(row)
   if b[0,0]<=bounds[2] and b[1,0]>=bounds[0] and b[0,2]<=bounds[3] and b[1,2]>=bounds[1]:touching.append(row)
 assert len({r['uid'] for r in whole})==len(whole) and [r['uid'] for r in touching]==['landsd/246270:0'] and result['completeCurrentRetainedNativeChecks']['blocked']==result['completeCurrentRetainedNativeChecks']['resolved']==[r['uid'] for r in touching]
 assert ref(manifest)==start;result.update(contract='park-haven-complete-current-ordinary-original-support-v2',completeCurrentNativeWholeBoundsInventory=whole,completeCurrentNativeWholeBoundsTouchingProposal=touching);result['evidenceRefs']=sorted({r['path']:r for r in result['evidenceRefs']+[ref(Path(__file__)),ref(Path(prior.__file__))]}.values(),key=lambda r:r['path']);return result
def main():
 assert not DOC.exists();result=recheck();save(DOC/'typed-role.json.gz',result);f=prior.module('freeze_park_native_scope','xl-popcorn-source-investigations-checkpoints-20261009.py');f.freeze(BATCH,'complete-current-original-ordinary-support-plus-whole-native-scope-v2',[ROOT/x['path'] for x in result['evidenceRefs']],dict(uids=result['uids'],currentTypedPhysicalAccepted=True,reasons=[],sourceGeometryChanges=0,terrainProposalGeometryChanged=True,completeOriginalFaces=11173,completeOriginalComponents=554,completeCurrentNativeScope=['landsd/246270:0'],typedRole=ref(DOC/'typed-role.json.gz'),browserRequired=True,publication=False,newlyInstalled=0));print(dict(passed=True,faces=11173,parts=554,foreign=24),flush=True)
if __name__=='__main__':main()
