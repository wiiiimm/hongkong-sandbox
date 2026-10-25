"""Save current Beverly K evidence and explicit remaining work; no approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-beverly-k-after-tuen-mun-progress-v1-20261025'

def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];completed=[]
 for folder in sorted(BASE.glob('government-xl-beverly-k-after-tuen-mun-*-20261025')):
  if not(folder/'result.json').is_file():continue
  result,_=authenticate(folder);completed.append(dict(batch=folder.name,jobId=result['jobId']));refs.append(folder/'result.json')
 assert len(completed)==12
 def summary(name):return read(BASE/name/'summary.json')
 identity=read(BASE/'government-xl-beverly-k-after-tuen-mun-identity-v1-20261025/255543:0/identity.json');assert identity['passed']and not identity['reasons']
 foundation=summary('government-xl-beverly-k-after-tuen-mun-foundations-v1-20261025');assert foundation['establishedFoundationPolicyPassed']and all(r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in foundation['rows'])
 continuous=summary('government-xl-beverly-k-after-tuen-mun-continuous-v1-20261025');assert continuous['rows'][0]['wholeSourceFaces']==10130 and continuous['rows'][0]['wholeSourceUncoveredFaces']==0
 contacts=summary('government-xl-beverly-k-after-tuen-mun-full-native-contacts-v1-20261025');assert len(contacts['rows'])==1 and contacts['rows'][0]['nativeUid']=='landsd/255939:0'
 basic=summary('government-xl-beverly-k-after-tuen-mun-basic-contacts-v2-20261025');assert not basic['canonicalContactPassed']and basic['strictContacts']==0 and basic['samples']==126 and basic['unresolved']==10
 manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest)
 result=dict(uids=['landsd/255543:0'],sourceSHA256=identity['sourceSHA256'],currentManifestSHA256=digest(manifest.read_bytes()),completed=completed,
  installedXL=378,unfinishedXL=143,totalFixedXL=521,currentNativeActors=6954,newlyInstalled=0,installationApproved=False,physicalAcceptance=False,publication=False,
  sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,humanDecisionRequired=False,state='held-for-compute',
  evidence=dict(identityPassed=True,sourceFaces=10130,fourWorldBuriedTriangles=0,wholeSourceProjectionCovered=True,nativeUid='landsd/255939:0',nativeFaces=12640,eachModeFiniteContactPairs=105,eachModePositiveSurfaceContactPairs=82,eachModeAreaContactPairs=7,basicSupportUid='landsd/233218:0',canonicalSamples=126,strictContacts=0,wallIntersections=116,unresolved=10),
  rawFailuresPreserved=[
   'Initial whole-tile merger rejected old tile hash before output; exact current building fields are identical. Existing unchanged-form refresh v1 revalidated full source/native/current form and completed selectionV2; old merger unchanged.',
   'Quick disjoint-only native checker rejected overlapping BlockJ bounds before approval. Existing overlapping-native V3 measured complete original10130/native12640faces in all4worlds and preserved all105contacts, not a waiver.',
   'First explicit BASIC adapter stopped on absent proceduralWindows flag before output. V2diagnostic addsFalse only when absent; no truefield override/sourcebytes/geometry change. Canonical current BASIC support stillfails:116wall intersections,0strictcontacts/10undersiderim samples at-.349998474m.'
  ],remainingWork=[
   'Classify full K/J finitecontact components/roles and raw7area contacts; preserve exact current J metadata/source/terrain. Existing source shapes or sharedauthoring are not automatically defect or acceptance proof.',
   'Resolve source support using canonical passing source/native evidence. Do not treat116wallintersections as existing strictsupport pass, move geometry, trim details, or silently waive requirement for other strict contacts.',
   'Investigate original podium233218/source support as needed using existing immutable provenance and current scene; old P/70279held records remain intact and are not globalabsence proof.',
   'Only after complete source/physical/support/currentneighbour review, run private desktop/mobile previews and guarded installation/live/fullreadbacks. No source/remodelling or human decision requirement established.'
  ],tracker=dict(issue='HKS-203',tuenMunInstalledCommit='250f7e72f',progressCommentId='f48656b7-142b-4f68-b34b-62edddadc998'))
 save(out/'remaining-work.json',result)
 module('beverly_k_progress_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'beverly-k-current-original-evidence-and-actionable-holds',list(dict.fromkeys(refs)),result)
 print(dict(completed=len(completed),newlyInstalled=0,state=result['state']),flush=True)
if __name__=='__main__':main()
