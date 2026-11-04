"""Preserve a source-bound current-input obstruction without calling it corruption.

No permanent-invalid claim, installed/skip credit, geometry edit or tolerance change.
"""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';UID='landsd/30031:0';SHA='19a98fa6709619ab7ec32664025d15c084f458b4890f4b5db85d1fd36035b587';BATCH='government-xl-beverly30031-current-source-disposition-v1-20261028'
def main():
 p=argparse.ArgumentParser();p.add_argument('--lease',required=True);a=p.parse_args();lease=read(Path(a.lease));assert reservations.owns(lease)and 'building:'+UID in lease['resources'];out=BASE/BATCH;assert not out.exists();pins={};refs=[Path(__file__)]
 def take(batch,name='summary.json'):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 nomination=take('government-xl-beverly30031-prepared-neighbours-v1-20261028');assert nomination['uid']==UID and nomination['indexedSourceSHA256']==SHA
 assert nomination['completePreparedSheetModelCount']==51 and nomination['lowerOriginalCandidates']==0
 candidates={r['candidateUid']:r for r in nomination['nearbyOriginalCandidates']};assert set(candidates)=={'landsd/29943:0','landsd/80888:0'}
 current=take('government-xl-after-qe-beverly30031-ground-contact-followup-v2-20261026');assert current['sourceSHA256']==SHA and current['rawAcceptanceReasons']==['ground-contact-unresolved'] and current['lowRimChecks']==480 and .1<current['minimumLowGapM']<=current['maximumLowGapM']<1
 assert len(current['wholeFourWorldFoundations'])==4 and all(r['triangles']==r['completeTerrainTriangles']==10434 and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in current['wholeFourWorldFoundations'])
 native=take('government-xl-after-qe-beverly30031-native-contacts-v1-20261026')['rows'];assert len(native)==1;native=native[0]
 assert native['uid']==UID and native['sourceSHA256']==SHA and native['nativeUid']=='landsd/29943:0' and native['nativeSHA256']==candidates['landsd/29943:0']['model']['candidate']['sha256']
 assert len(native['modes'])==4 and all(r['finiteContactPairs']==r['positiveSurfaceContactPairs']==r['areaContactPairs']==0 for r in native['modes'])
 old='government-xl-beverly-garden-nine-bounded-source-path-review-v1-20261011';review_receipt=read(BASE/old/'result.json');authenticate(BASE/old);refs.append(BASE/old/'result.json')
 assert review_receipt['sourceSHA256s']=={UID:SHA,'landsd/80888:0':candidates['landsd/80888:0']['model']['candidate']['sha256']}
 assert review_receipt['completeFiniteOriginal80888ContactCount']==0 and review_receipt['completeSourceFaces']==10434 and review_receipt['completeSupportFaces']==1019
 review=take(old,'review.json');assert not review['existingFailurePreserved']['datumCorrectionSupported'];assert review['outcome']==review_receipt['outcome']
 # Verify actual immutable packages, not just their names in old receipts.
 for sha in review_receipt['sourceSHA256s'].values():
  paths=[ROOT/r['path']for r in review_receipt['evidenceRefs']if r['sha256']==sha and r['path'].endswith('.glb.gz')];assert paths
  path=next(p for p in paths if p.exists());assert digest(path.read_bytes())==sha;refs.append(path)
 result=dict(uids=[UID],uid=UID,sourceKey=nomination['sourceKey'],sourceSHA256=SHA,sourceGeometryChanges=0,sourcePoseChanges=0,state='held-for-authoritative-ground-or-support-source',humanStatus='held-unknown',needsHumanDecision=False,needsAIProcessing=None,knownScriptedRecoveryEstablished=False,currentRevisionInstallationBlocked=True,permanentRejection=False,corruptionEstablished=False,installationApproved=False,retainCurrentModel=True,doNotRepeatUnchangedChecks=True,minimumLowGapM=current['minimumLowGapM'],maximumLowGapM=current['maximumLowGapM'],lowRimChecks=480,completePreparedSheetModelsScanned=51,nearbyOriginalContactsNegative=sorted(candidates),reason='No demonstrated fixed-placement source-to-authentic-ground root; all480rim checks remain0.2266–0.571m above tested ground. Both nearby originals have complete negative finite-contact results. No authoritative datum/plinth correction is established.',nextStep='Retain fallback. Reopen only for new authoritative finished-grade/HKPD or original support evidence, or changed official model/terrain revision; require fresh current-map acceptance. No routine worker queued for unchanged bytes.',revisitTriggers=review['nextCausalMethod']['requirements'],unsupportedActions=review['nextCausalMethod']['unsupportedActions'],qualification='Current-input obstruction, not proof of permanent invalidity or unavailability of all future surveys. Historical positive browser/identity/foundation checks do not resolve the negative ground root, and no historical scene acceptance is transferred. No model-review state, installed/skip credit, source placement, geometry or threshold is changed.')
 save(out/'decision.json',result);assert reservations.owns(lease);module('beverly_source_disposition_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-revision-ground-support-obstruction-disposition',refs,result)
if __name__=='__main__':main()
