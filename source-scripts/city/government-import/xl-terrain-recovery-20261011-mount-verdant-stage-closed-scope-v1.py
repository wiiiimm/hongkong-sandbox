"""Declare immutable source+staged evidence; root independently verifies closure.

Inherits the reviewed exact metadata boundaries without any new source,
geometry, ground, kernel, actor or numerical exemption. No publication.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import'
SOURCE=BASE/'xl-terrain-recovery-20261011-mount-langham-hoi-source-checkpoint-scope-v2/declared-scope.json'
CERT=BASE/'government-xl-mount-verdant-source-root-closure-v1-20261011/root-closed-scope.json'
STAGED='government-xl-terrain-recovery-mount-verdant-two-typed-stage-v1-20261011'
DOC=BASE/'government-xl-mount-verdant-stage-declared-scope-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();source=read(SOURCE);cert=read(CERT)
 assert cert['independentlyVerified'] and cert['verifiedReferenceVersions']==8424
 acceptance=read(BASE/STAGED/'acceptance.json')
 assert acceptance['passed']and not acceptance['publication']and acceptance['newlyInstalled']==0
 paths=set(cert['paths'])|set(source['closedExplicitPaths'])|{str(SOURCE.relative_to(ROOT)),str(CERT.relative_to(ROOT)),str(Path(__file__).relative_to(ROOT))}
 for folder in [BASE/STAGED,HERE/'accepted'/STAGED,ROOT/'docs/astra-city/model-integration-20260909'/STAGED]:
  assert folder.exists()
  paths.update(str(p.relative_to(ROOT))for p in folder.rglob('*')if p.is_file())
 paths.add(str((HERE/'xl-terrain-recovery-20261011-mount-verdant-two-live-install-v1.py').relative_to(ROOT)))
 out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],metadataLeafPaths=source['metadataLeafPaths'],metadataLeafJsonPointers=source['metadataLeafJsonPointers'],historicalManifestAliases=source['historicalManifestAliases'],sourceDeclaration=ref(SOURCE),independentlyVerifiedSourceCertificate=ref(CERT),stageAcceptance=ref(BASE/STAGED/'acceptance.json'),stageBrowser=ref(BASE/STAGED/'staged-browser.json'),fullNumericalSourceClosureRequired=True,newMetadataLeaves=False,newMetadataPointerContract=False,sourceGeometryChanges=0,publication=False,newlyInstalled=0,livePublicationRequired=True)
 assert out['metadataLeafPaths']==source['metadataLeafPaths']and out['metadataLeafJsonPointers']==source['metadataLeafJsonPointers']
 save(DOC/'declared-scope.json',out);print(dict(paths=len(paths),publication=False,newNumericLeaves=False),flush=True)
if __name__=='__main__':main()
