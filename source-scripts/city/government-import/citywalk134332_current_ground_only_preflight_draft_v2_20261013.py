"""Draft read-only ground-capture preparation; never claims reservations or imports renderer."""
import argparse,json,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,digest,connect
import citywalk134332_surviving_native_supervised_draft_v1_20261013 as W
P=ROOT/'docs/astra-city/government-import/government-xl-citywalk134332-current-ground-only-proposal-v2-20261013'
JOB='ca2a6024037ef04c57b0f6ffbf9220f2abd27f824b554595c2d4db7be516a67e'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def inputs(a):
 plan=read(P/'ground-capture-plan.json');assert a.expected_manifest==plan['expectedManifest'];assert plan['expectedNativeCount']==6650
 for e in plan['evidenceRefs']:assert ref(ROOT/e['path'])==e
 npz=ROOT/plan['providerOriginalNPZ']['path'];assert ref(npz)==plan['providerOriginalNPZ']
 with np.load(npz,allow_pickle=False)as saved:
  original=saved[plan['providerOriginalNPZKey']];assert original.shape==(41277,3,3)and np.isfinite(original).all();assert digest(original.astype('<f8').tobytes())==plan['providerOriginalWorldSHA256']=='e4f766dcd25463e7bbef605068852b893059df268eff9cc3b5f73d2b1b3cdb21';assert [original.min(axis=(0,1)).tolist(),original.max(axis=(0,1)).tolist()]==plan['providerOriginalFaceBounds']
 result=read(W.Q.D/'result.json');assert result['jobId']==JOB
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 before=W.inputs(a);assert before==read(W.LOCAL/'protected-state-before.json');assert len(before['uids'])==19 and before['observedProtectedReviewRecords']==1704
 attrs=read(ROOT/plan['capture']['path']);assert attrs['startEndAllInputsVerified']
 for p,h in attrs['inputHashes'].items():assert ref(ROOT/p)['sha256']==h
 group=read(W.GROUP);tile=read(ROOT/'3d-viewer/city/data/tiles/-3_-5.json');current={f['uid']:f for f in tile['buildings']};assert all(current[f['uid']]==f for f in group['completeGroupForms']);assert len(group['completeGroupForms'])==13
 assert group['sourceSHA256']==plan['sourceSHA256']and group['worldTrianglesSHA256']=='e4f766dcd25463e7bbef605068852b893059df268eff9cc3b5f73d2b1b3cdb21'
 components=read(W.Q.COMP)['components'];ids=[i for c in components for i in c['sourceFaceIndices']];assert len(components)==193 and sorted(ids)==list(range(41277))
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');patches=[p for p in manifest['terrainPatches']if p['url']=='city/data/government-native-134332-0.json'];assert len(patches)==1
 live=ref(ROOT/'3d-viewer'/patches[0]['url']);assert live['sha256']=='1d21dc85feb6870c9bdfb1e3b2e8949dff9062a493a87b2bce762c1e827bc8f4'
 return dict(readOnlyPreflightPassed=True,noWorker=True,currentManifest=before['currentManifest'],currentNativeCount=6650,contextUIDs=19,protectedReviewRows=1704,completedContactJob=JOB,all2497LiteralRefsVerified=len(result['evidenceRefs'])==2497,identity13FormsExact=True,providerOriginalWorldTupleExact=True,completeSourceFaces=41277,completeOriginalBodies=193,currentTerrain=live,historicalProposedTerrainFoundationIsNotCurrent=True,identityContextReusableNotNewAcceptance=True,currentFoundationMissing=True,currentRuntimeMissing=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-manifest',required=True);a=p.parse_args();print(json.dumps(inputs(a),sort_keys=True))
if __name__=='__main__':main()
