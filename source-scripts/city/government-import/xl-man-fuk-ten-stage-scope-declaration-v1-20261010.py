"""Close both corrected staging and the preserved failed original audit attempt."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import'
OUT=BASE/'xl-man-fuk-ten-stage-scope-declaration-v1-20261010'
SOURCE=BASE/'xl-man-fuk-ten-source-scope-declaration-v2-20261010/declared-scope.json'
STAGE=BASE/'government-xl-man-fuk-ten-complete-typed-stage-v2-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists();source=read(SOURCE);stage=read(STAGE/'acceptance.json')
 assert stage['passed'] and stage['checksPassed'] and stage['publication'] is False and stage['newlyInstalled']==0
 assert len(stage['uids'])==10 and len(read(STAGE/'staged-browser.json')['retainedNativeOwnViews'])==4
 paths=set(source['closedExplicitPaths'])|{str(SOURCE.relative_to(ROOT)),str(Path(__file__).relative_to(ROOT))}
 dirs=[p for p in BASE.glob('government-xl-man-fuk-ten-complete-typed-stage-*') if p.is_dir()]
 dirs.append(BASE/'government-xl-man-fuk-podium-solid-followup-v1-20261010')
 dirs.extend(p for p in (HERE/'accepted').glob('government-xl-man-fuk-ten-complete-typed-stage-*') if p.is_dir())
 for d in dirs:paths.update(str(p.relative_to(ROOT)) for p in d.rglob('*') if p.is_file())
 for pattern in ['xl-man-fuk-ten-complete-typed-stage-*.py','xl-caine-man-fuk-twelve-atomic-live-install-*.py','xl-man-fuk-podium-solid-followup-*.py']:
  paths.update(str(p.relative_to(ROOT)) for p in HERE.glob(pattern))
 for r in stage['evidenceRefs']:assert ref(ROOT/r['path'])==r;paths.add(r['path'])
 extra=read(BASE/'government-xl-man-fuk-podium-solid-followup-v1-20261010/acceptance.json');assert extra['passed'] and extra['allRetainedNativeOwnViewsRemainBoundToBaseStage']
 for r in extra['evidenceRefs']:assert ref(ROOT/r['path'])==r;paths.add(r['path'])
 save(OUT/'declared-scope.json',dict(source,closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p) for p in sorted(paths)],stageAndLiveExcluded=False,publication=False,newlyInstalled=0,completeStage=ref(STAGE/'acceptance.json'),qualification='All ten unchanged originals staged desktop/mobile day/night, retained ManOi four own views, all ten failed-load retries, and complete source/current proof replay. Corrected final overlap audit preserves every qualified terrain numeric field and is independently checked against production sampler/rays. Earlier publication-validator failure and stale audit remain preserved; no live installed credit. Root sole publisher.'))
 print(dict(paths=len(paths),currentRoleNeon=source['currentRoleNeon'],staged=True,publication=False),flush=True)
if __name__=='__main__':main()
