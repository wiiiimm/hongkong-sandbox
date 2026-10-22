"""Retain the complete installed Sung Fung terrain while inserting the original source repair."""
import subprocess,numpy as np,shapely,traceback
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from float32_coverage import approve_roundoff
BASE=ROOT/'docs/astra-city/government-import';PLAN=BASE/'government-xl-sung-fung-retained-region-plan-v1-20261022';BATCH='government-xl-sung-fung-retained-native-candidate-v1-20261022'
def main():
 doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists()
 receipt,pins=authenticate(PLAN);path=PLAN/'summary.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];plan=read(path);assert plan['uids']==['landsd/79098:0']and plan['retainedPatchCount']==1 and plan['allFlatNative']
 parent=plan['retainedPatches'][0];oldpath=ROOT/'3d-viewer'/parent['url'];assert digest(oldpath.read_bytes())==parent['sha256'];old=read(oldpath);assert parent['extent']==plan['regionalParentExtent'],'Single parent must contain the full repair region'
 inset=plan['privateInset'];assert digest((ROOT/inset['path']).read_bytes())==inset['sha256'];refs=[Path(__file__),PLAN/'result.json',path,oldpath,ROOT/inset['path']]
 mp=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(mp.read_bytes());refs.append(mp)
 doc.mkdir();local.mkdir();out=local/'candidate-terrain.json';lineage=local/'lineage.json.gz'
 ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 save(doc/'input.json',dict(parent=ref(oldpath),inset=dict(path=inset['path'],sha256=inset['sha256']),refs=[ref(p)for p in refs],uids=plan['uids'],bounds=parent['extent'],cut=inset['bounds'],lineage=str(lineage.relative_to(ROOT))))
 tool=HERE/'selected_retained_native_inset_v1.mjs';subprocess.run(['node',str(tool),str((doc/'input.json').relative_to(ROOT)),str(out.relative_to(ROOT))],cwd=ROOT,check=True)
 evidence=read(lineage)
 for p,h in evidence['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 candidate=read(out);root=read(ROOT/'3d-viewer/city/data/terrain.json');builder=module('retained_inset_builder',HERE/'resolve_pass_indexed_parent_clipping_v2.py');error=None
 try:
  save(doc/'numerical-coverage.json',approve_roundoff(candidate,parent['extent']))
  proof=module('retained_inset_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');proof.DOC=doc;proof.overlap_proof(candidate,[oldpath,ROOT/inset['path'],lineage,tool,Path(__file__)])
  builder.validate_patch(candidate,root)
  assert evidence['outputFaces']<=evidence['originalFaces']+25000,'Incremental terrain runtime budget exceeded'
 except Exception as exc:error=dict(errorType=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());save(doc/'failure.json',error)
 save(out,candidate);assert digest(mp.read_bytes())==msha
 descriptor=dict(path=str(out.relative_to(ROOT)),sha256=digest(out.read_bytes()),replaces=dict(url=parent['url'],sha256=parent['sha256'],retainedUids=parent['retainedUids']))
 save(doc/'scope.json',dict(uids=plan['uids'],cells=candidate['coarseCells'],bounds=plan['regionalParentExtent']))
 result=dict(uids=plan['uids'],status='private-terrain-validator-passed'if error is None else'retained-inset-investigation',candidate=descriptor,retainedUids=parent['retainedUids'],newlyInstalled=0,installationApproved=False,publication=False,sourceGeometryChanges=0,scriptExternalAICalls=0,wholeOriginalTerrainRetainedOutsideInset=True,minimumNewInsetHeight=evidence['minimumInsetHeight'],error=error)
 save(doc/'summary.json',result);refs.extend([tool,lineage,out,ROOT/'3d-viewer/city/data/terrain.json',HERE/'resolve_pass_indexed_parent_clipping_v2.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py',HERE/'float32_coverage.py'])
 module('retained_inset_candidate_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'retained-native-source-inset-candidate',refs,result)
 print(dict(status=result['status'],error=error,outputFaces=evidence['outputFaces']),flush=True)
if __name__=='__main__':main()
