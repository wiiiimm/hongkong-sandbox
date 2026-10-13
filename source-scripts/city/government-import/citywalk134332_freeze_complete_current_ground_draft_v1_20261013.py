"""Draft immutable ground-only diagnostic receipt; no physical qualification."""
import argparse,json,importlib.util,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,connect
import citywalk134332_current_ground_only_supervised_draft_v1_20261013 as W
Q=W.Q
def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-manifest',required=True);a=p.parse_args();before=read(W.LOCAL/'protected-state-before.json');W.fence(a,before);d=read(W.D/'complete-current-drawn-ground.json.gz')
 assert d['sourceOnly']and not d['currentAcceptance']and not d['physicalAccepted']and not d['installationApproved'];assert d['sourceGeometryChanges']==d['terrainGeometryChanges']==0 and d['completeSourceFaces']==41277 and d['completeOriginalBodies']==193 and d['startEndInputsVerified'];assert d['savedModelCapture']==read(Q.P/'ground-capture-plan.json')['capture'];assert d['completeAllSlopesZeroProjectionAndTouchingFacetsRetained'];assert d['originalGroundBufferEqualsLiteralAtIdentityMatrix']and d['signedZeroByteDifferencesPreserved']and d['noOriginalLiteralByteHashEqualityClaim']
 names={'actualLiteral','explicitLeftF32','explicitBalancedF32'};assert set(d['completeRegionalGroundWorlds'])==names and {b['name']for b in d['groundWorldBindings']}==names
 n=d['completeRegionalGroundFaces'];assert n>0 and sum(len(m['selectedOriginalFaceIDs'])for m in d['groundMeshOrigins'])==n
 for m in d['groundMeshOrigins']:assert m['bufferLiteralEquality']['numericCoordinateEquality'];assert all(0<=i<m['completeIndexedFaces']for i in m['selectedOriginalFaceIDs']);assert len(m['selectedOriginalFaceIDs'])==len(set(m['selectedOriginalFaceIDs']))
 for b in d['groundWorldBindings']:
  arr=np.asarray(d['completeRegionalGroundWorlds'][b['name']],dtype='<f8');assert arr.shape==(n*9,)and np.isfinite(arr).all()and b['faces']==n;assert Q.digest(arr.tobytes())==b['worldTrianglesSHA256']
 for m in d['nativeHeightIndexAccounting']:assert len(m['heightIndexedOriginalFaces'])+len(m['heightExcludedOriginalFaces'])==m['sourceFaces'];assert sorted(m['heightIndexedOriginalFaces']+m['heightExcludedOriginalFaces'])==list(range(m['sourceFaces']))and m['allExcludedFacesRemainDrawn']
 for p,h in d['inputHashes'].items():assert Q.ref(ROOT/p)['sha256']==h
 spec=importlib.util.spec_from_file_location('ground_source_freezer',HERE/'parkview_block17_freeze_current_source_evidence_20261011.py');F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F);paths=set();F.local_imports(Path(__file__),paths);F.local_imports(Path(W.__file__),paths)
 for folder in [W.D,W.P,Q.P]:paths.update(p for p in folder.rglob('*')if p.is_file())
 paths.update([W.LOCAL/'protected-state-before.json',W.LOCAL/'immutable-lease-at-start.json']);F.declared_refs(before,paths);F.declared_refs(d,paths);F.declared_refs(read(Q.P/'ground-capture-plan.json'),paths);F.declared_refs(read(Q.P/'actual13-tests-readonly-preflight-closure-validation-v1.json'),paths);paths.update(ROOT/p for p in d['inputHashes']);assert W.LEASE not in paths;W.fence(a,before)
 result=F.F.freeze(W.BATCH,'complete-current-citywalk-drawn-ground-only-no-acceptance',sorted(paths),dict(uids=[Q.W.Q.UID],sourceOnly=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0,terrainGeometryChanges=0,completeSourceFaces=41277,completeOriginalBodies=193,currentNativeCount=6650,currentManifest=before['currentState']['currentManifest'],completeCurrentGround=Q.ref(W.D/'complete-current-drawn-ground.json.gz'),completeRegionalGroundFaces=n,noModelLoadOrSourceDecodeOrContactReplay=True,ordinaryFiniteNotYetComputed=True))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert Q.ref(ROOT/e['path'])==e
 W.fence(a,before);print(json.dumps(dict(jobId=result['jobId'],resultSHA256=Q.ref(W.D/'result.json')['sha256'],allRefs=len(result['evidenceRefs']),groundFaces=n,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
