"""Close source plus actual staged Parkview outputs, never live publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';SOURCE=BASE/'xl-terrain-recovery-20261011-parkview-block11-source-scope-v1';BATCH='government-xl-parkview-block11-authentic-current-stage-v1-20261011';STAGE=HERE/'accepted'/BATCH;DOC=BASE/'xl-terrain-recovery-20261011-parkview-block11-source-stage-scope-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();source=read(SOURCE/'declared-scope.json');receipt=read(BASE/BATCH/'acceptance.json');assert receipt['passed']and receipt['checksPassed']and not receipt['publication']and receipt['newlyInstalled']==0
 assert ref(BASE/BATCH/'staged-browser.json')==receipt['stagedBrowser'];paths=set(source['closedPaths']);paths.add(str((SOURCE/'declared-scope.json').relative_to(ROOT)))
 for folder in [BASE/BATCH,STAGE]:paths.update(str(p.relative_to(ROOT))for p in folder.rglob('*')if p.is_file())
 for name in ['xl-terrain-recovery-20261011-parkview-block11-authentic-current-stage-v1.py','xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs']:
  paths.add(str((HERE/name).relative_to(ROOT)))
 paths.add(str(Path(__file__).relative_to(ROOT)));save(DOC/'declared-scope.json',dict(source,closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],stageAndLiveExcluded=False,liveExcluded=True,sourceScope=ref(SOURCE/'declared-scope.json'),stagedAcceptance=ref(BASE/BATCH/'acceptance.json'),qualification='Complete unchanged Parkview one-source current proof plus actual staged browser, source catalogue/asset, exact four current native actors and complete explicit reviewed terrain replacement. All source numerical dependencies recursive; metadata/aliases are inherited unchanged from the source scope, with zero new leaves or pointer exceptions. Root alone independently verifies and publishes.'))
 print(dict(paths=len(paths),liveExcluded=True),flush=True)
if __name__=='__main__':main()
