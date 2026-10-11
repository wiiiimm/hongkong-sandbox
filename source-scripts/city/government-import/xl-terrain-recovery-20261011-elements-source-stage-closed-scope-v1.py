"""Declare completed private stage plus already root-closed Elements source.

No duplicate source numerical work, new metadata leaves or pointer exceptions.
Root verifies/seals the exact stage and source declaration before live execution.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-elements-source-stage-closed-scope-v1';DOC=BASE/BATCH
SOURCE=BASE/'government-xl-elements-complete-current-source-root-closure-v1-20261011/root-closed-scope.json'
OLD=BASE/'xl-terrain-recovery-20261011-elements-completed-source-checkpoint-scope-v2/declared-scope.json'
STAGE=BASE/'government-xl-terrain-recovery-elements-sun-star-two-qualified-native-stage-v2-20261011'
ASSETS=HERE/'accepted'/STAGE.name
CURRENT='de8db939e48be0ed3661a9f3bf59454d92ff27f4a1024f34a401b17612e03e54'
PUBLISHER=HERE/'xl-elements-sun-star-two-unchanged-live-install-v1-20261011.py'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();source=read(SOURCE);old=read(OLD);acceptance=read(STAGE/'acceptance.json')
 assert source['independentlyVerified']is True and source['currentManifestSHA256']==CURRENT and source['newlyInstalled']==0
 assert acceptance['passed']and acceptance['checksPassed']and acceptance['publication']is False and acceptance['newlyInstalled']==0 and acceptance['manifestSHA256']==CURRENT
 assert ref(STAGE/'staged-browser.json')==acceptance['stagedBrowser'];report=read(STAGE/'staged-browser.json');assert report['passed']and report['errors']==[]
 for pin in acceptance['evidenceRefs']:assert ref(ROOT/pin['path'])==pin
 paths=set(source['paths']);paths.update([str(SOURCE.relative_to(ROOT)),str(OLD.relative_to(ROOT)),str(Path(__file__).relative_to(ROOT)),str(PUBLISHER.relative_to(ROOT))])
 paths.update(str(p.relative_to(ROOT))for root in [STAGE,ASSETS]for p in root.rglob('*')if p.is_file())
 aliases=list(old['historicalManifestAliases'])
 for alias in source['historicalManifestAliases']:
  if alias not in aliases:aliases.append(alias)
 paths.add(str((DOC/'declared-scope.json').relative_to(ROOT)))
 output=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)if p!=str((DOC/'declared-scope.json').relative_to(ROOT))],sourceCertificate=ref(SOURCE),historicalManifestAliases=aliases,metadataLeafPaths=old['metadataLeafPaths'],metadataLeafJsonPointers=old['metadataLeafJsonPointers'],inheritedMetadataScope=old['inheritedMetadataScope'],immutablePriorScope=ref(OLD),currentManifestSHA256=CURRENT,fullNumericalSourceClosureRequired=True,newMetadataLeaves=False,newMetadataPointerContract=False,completedPrivateStageAcceptance=ref(STAGE/'acceptance.json'),livePublisherDraft=ref(PUBLISHER),sourceGeometryChanges=0,terrainChanges=0,stageOnly=True,publication=False,nativeReacceptance=False,installationApproved=False,newlyInstalled=0)
 assert output['metadataLeafPaths']==old['metadataLeafPaths']and output['metadataLeafJsonPointers']==old['metadataLeafJsonPointers'];save(DOC/'declared-scope.json',output);print(dict(paths=len(paths),sourceAlreadyIndependentlyClosed=True,newNumericalLeaves=False,newlyInstalled=0),flush=True)
if __name__=='__main__':main()
