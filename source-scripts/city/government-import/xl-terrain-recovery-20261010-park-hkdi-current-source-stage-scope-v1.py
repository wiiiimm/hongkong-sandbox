"""Declare immutable completed Park2/HKDI1 source and staged-only evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import'
DOC=BASE/'xl-terrain-recovery-20261010-park-hkdi-current-source-stage-scope-v1'
SOURCE=BASE/'xl-terrain-recovery-20261010-park-hkdi-current-source-scope-v1/declared-scope.json'
STAGES=['government-xl-terrain-recovery-park-haven-two-typed-stage-v5-20261010','government-xl-terrain-recovery-hkdi-block-b-qualified-native-stage-v1-20261010']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();old=read(SOURCE);paths=set(old['closedPaths']);paths.add(str(SOURCE.relative_to(ROOT)))
 for name in STAGES:
  folder=BASE/name;acceptance=read(folder/'acceptance.json')
  assert acceptance['passed']is True and acceptance['publication']is False and acceptance['newlyInstalled']==0 and acceptance['livePublicationRequired']is True
  assert acceptance['manifestSHA256']=='afe71ffa851d82ab2d1350834b5a6cd1484f28e481bd6bf866ca7a6f73e05d0b'
  for r in acceptance['evidenceRefs']:assert ref(ROOT/r['path'])==r
  assert acceptance['stagedBrowser']==ref(folder/'staged-browser.json')
  paths.update(str(p.relative_to(ROOT))for p in folder.rglob('*')if p.is_file())
  paths.update(str(p.relative_to(ROOT))for p in (HERE/'accepted'/name).rglob('*')if p.is_file())
 scripts=['xl-terrain-recovery-20261010-park-haven-two-stage-install-v5.py','xl-terrain-recovery-20261010-hkdi-block-b-stage-v1.py','xl-terrain-recovery-20261010-multi-native-solid-browser-v5.mjs','xl-park-haven-hkdi-three-atomic-live-install-v1-20261010.py']
 paths.update(str((HERE/n).relative_to(ROOT))for n in scripts);paths.add(str(Path(__file__).relative_to(ROOT)))
 decision={**old,'closedPaths':sorted(paths),'closedExplicitPaths':sorted(paths),'presentFileBindings':[ref(ROOT/p)for p in sorted(paths)],'stageAndLiveExcluded':False,'livePublicationExcluded':True,'stagePublication':False,'newlyInstalled':0,'noNewMetadataLeaves':True,'noNewMetadataPointers':True,'completedStagedBatches':STAGES,'qualification':'Complete original/current numeric source closure inherited unchanged; both completed staged-only acceptances, source catalogues/assets, browser configurations, all20 owned/retained solid exports and3 load failures/retries included. Every original numerical/source reference remains recursive. Existing reviewed metadata leaf/pointer contracts unchanged. Atomic publisher is root-review draft only, not executed. Root unchanged closure verifier must fully pass before live publication.'}
 assert decision['metadataLeafPaths']==old['metadataLeafPaths'] and decision['metadataLeafJsonPointers']==old['metadataLeafJsonPointers']
 save(DOC/'declared-scope.json',decision);print(dict(paths=len(paths),publication=False,newlyInstalled=0),flush=True)
if __name__=='__main__':main()
