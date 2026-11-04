"""Closed complete Caine staged proof including unchanged negative witnesses."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import'
OUT=BASE/'xl-terrain-recovery-20261010-caine-road-stage-scope-declaration-v1'
SOURCE=BASE/'xl-terrain-recovery-20261010-caine-road-source-scope-declaration-v1/declared-scope.json'
STAGE=BASE/'government-xl-terrain-recovery-caine-road-two-typed-stage-v2-20261010'
SUP=BASE/'government-xl-terrain-recovery-caine-road-podium-solid-followup-v2-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists();source=read(SOURCE);stage=read(STAGE/'acceptance.json');supp=read(SUP/'acceptance.json');assert stage['passed'] and not stage['publication'] and stage['newlyInstalled']==0 and supp['passed'] and supp['allTenNativeOwnViewsRemainBoundToBaseStage'] and supp['noNativeOrSupportProofOmitted']
 assert ref(STAGE/'acceptance.json')==supp['baseCompleteStage'];assert ref(STAGE/'staged-browser.json')==supp['baseCompleteBrowser'];assert len(read(STAGE/'staged-browser.json')['retainedNativeOwnViews'])==40
 paths=set(source['closedExplicitPaths']);paths.add(str(SOURCE.relative_to(ROOT)));paths.add(str(Path(__file__).relative_to(ROOT)))
 dirs=[p for pattern in ['government-xl-terrain-recovery-caine-road-two-typed-stage-*','government-xl-terrain-recovery-caine-road-podium-solid-followup-*'] for p in BASE.glob(pattern) if p.is_dir()]
 dirs.extend(p for pattern in ['government-xl-terrain-recovery-caine-road-two-typed-stage-*'] for p in (HERE/'accepted').glob(pattern) if p.is_dir())
 for d in dirs:paths.update(str(p.relative_to(ROOT)) for p in d.rglob('*') if p.is_file())
 for pattern in ['xl-terrain-recovery-20261010-caine-road-two-stage-install-*.py','xl-terrain-recovery-20261010-caine-road-podium-solid-followup-*.py','xl-terrain-recovery-20261010-caine-road-two-live-install-*.py']:paths.update(str(p.relative_to(ROOT)) for p in HERE.glob(pattern))
 for r in stage['evidenceRefs']+supp['evidenceRefs']:assert ref(ROOT/r['path'])==r;paths.add(r['path'])
 result=dict(source,closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p) for p in sorted(paths)],stageAndLiveExcluded=False,publication=False,newlyInstalled=0,baseCompleteStage=ref(STAGE/'acceptance.json'),supplementaryPodiumWitness=ref(SUP/'acceptance.json'),qualification='Complete positive source/current role plus staged desktop/mobile day/night for both candidates, all40 retained-native own views, both load failures/retries; supplemental unobscured podium full-assembly overhead witness adds visual evidence only. All historical failed proposals and occluded witnesses retained. No live installed credit; root sole publisher.')
 save(OUT/'declared-scope.json',result);print(dict(paths=len(paths),sourceRole=source['currentRoleNeon'],staged=True,publication=False),flush=True)
if __name__=='__main__':main()
