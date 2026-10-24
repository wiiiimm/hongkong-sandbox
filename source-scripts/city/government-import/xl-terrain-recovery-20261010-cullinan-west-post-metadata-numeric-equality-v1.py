"""Exact post-metadata current capture equality; no acceptance or native credit."""
import importlib.util,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-terrain-recovery-cullinan-west-three-complete-original-current-probe-';BATCH='xl-terrain-recovery-20261010-cullinan-west-post-metadata-numeric-equality-v1';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();folders=[BASE/(PREFIX+f'v{i}-20261010')for i in [1,2]];captures=[HERE/'local'/p.name/'runtime-geometry.json.gz'for p in folders];data=list(map(read,captures));selections=[read(p/'selection.json.gz')for p in folders];refs=[ref(Path(__file__)),ref(BASE/'government-xl-all-installed-dependency-metadata-applied-v1-20261010/result.json')];rows=[]
 for folder,cap in zip(folders,captures):
  result=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
  assert ref(cap)in result['evidenceRefs'];refs.extend(ref(p)for p in [folder/'result.json',folder/'selection.json.gz',cap])
 for old,new,oldrow,newrow in zip(data[0]['rows'],data[1]['rows'],selections[0]['rows'],selections[1]['rows']):
  assert old['uid']==new['uid']==oldrow['uid']==newrow['uid'];assert oldrow['sourceSHA256']==newrow['sourceSHA256'];assert oldrow['source']['building']==newrow['source']['building'];assert oldrow['candidate']['entry']==newrow['candidate']['entry'],'No role/pose/dependency changes for scoped actors'
  hashes={}
  for key in ['position','index','drawnGroundGeometry']:
   a,b=np.asarray(old[key]),np.asarray(new[key]);assert a.shape==b.shape and np.array_equal(a,b);hashes[key]=dict(shape=list(a.shape),literalNumericSHA256=digest(a.tobytes()),exactEquality=True)
  asset=ROOT/newrow['candidate']['path'];assert digest(asset.read_bytes())==newrow['sourceSHA256'];refs.append(ref(asset));rows.append(dict(uid=new['uid'],sourceSHA256=newrow['sourceSHA256'],completeLiteralGeometryAndGround=hashes))
 current=folders[1];receipt=read(current/'result.json')
 for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 result=dict(uids=[r['uid']for r in rows],rows=rows,completeSourceLiteralIndexAndGroundBitIdentical=True,oldNumericalProofMayBeReusedOnlyWithIndependentlyVerifiedCompleteBindings=True,metadataMutationNotSourceGeometryChange=True,currentCapture=ref(current/'result.json'),allCurrentCaptureRefsFreshlyReplayed=True,rawNativeAndSourceNegativesPreserved=True,nativeReacceptance=False,fullAcceptance=False,newlyInstalled=0,evidenceRefs=refs)
 save(DOC/'diagnostic.json.gz',result);s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'exact-post-metadata-current-source-literal-ground-numeric-equality-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],allScopedNumericalInputsBitIdentical=True,nativeReacceptance=False,fullAcceptance=False,newlyInstalled=0))
 print('All three scoped original/literal/ground numeric inputs bit-identical; no acceptance',flush=True)
if __name__=='__main__':main()
