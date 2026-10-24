"""Freeze current seven-XL recovery and exact original-support next actions."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';B='government-xl-next-seven-original-support-checkpoint-v1-20261024'
def main():
 out=BASE/B;assert not out.exists();refs=[Path(__file__)];jobs={}
 names=['government-xl-current-unfinished-exact-source-inventory-v1-20261024']
 names += ['government-xl-next-seven-after-greenfield-'+p+'-v1-20261024'for p in ['acquisition','selection','runtime','attributes','identity','model-scope','native-contacts','basic-contacts']]
 names += ['government-xl-next-seven-with-supports-'+p+'-v1-20261024'for p in ['selection','runtime','attributes','identity','model-scope','pairs','support-followthrough']]
 names += ['government-xl-next-seven-support-'+u+'-acquisition-v1-20261024'for u in ['233190','79883','233218']]
 names += ['government-xl-next-seven-source-'+u+'-original-terrain-v2-20261024'for u in ['79883','237751','277890','323185']]
 names += ['government-xl-next-seven-source-'+u+'-fresh-terrain-v3-20261024'for u in ['233190','233218']]
 names += ['government-xl-royal-green8-podium-current-runtime-v1-20261024','government-xl-royal-green8-podium-current-prephysical-v1-20261024','government-xl-royal-green8-adjoining7521-original-v1-20261024','government-xl-royal-green8-tower-runtime-v1-20261024','government-xl-royal-green8-tower-census-v1-20261024','government-xl-royal-green8-tower-interfaces-v1-20261024','government-xl-royal-green8-joined-source-fourworld-paths-v1-20261024','government-xl-parc-palais2-current-original-installed-support-v1-20261024','government-xl-parc-palais-adjoining-two-originals-v1-20261024','government-xl-fung-yip79883-original-grade-inset-v1-20261024','government-xl-fung-yip79883-original-grade-inset-v2-20261024']
 for name in names:
  result,pins=authenticate(BASE/name);jobs[name]=result['jobId'];refs.append(BASE/name/'result.json')
  for file in ['summary.json','selection.json.gz','nominations.json']:
   path=BASE/name/file
   if path.exists():assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path)
 # Preserve terminal setup/revision errors explicitly, never as corrupt-source credit.
 for name in ['government-xl-next-seven-original-terrain-sequence-v1-20261024','government-xl-next-seven-original-terrain-sequence-v2-20261024']:
  refs.extend(p for p in (BASE/name).rglob('*')if p.is_file())
 rows=[
 dict(uid='landsd/235598:0',name='Royal Green8',identityPassed=True,completed='1701face original podium passes full current-ground prephysical suite. Tower376strict contacts;18remaining unchanged after1506component pairs and975finite bridges replayed in4worlds. Adjoining7521original recovered.',nextAction='Review the18exact source components and their authored attachment; preserve raw strict/path failures. No source geometry edits.'),
 dict(uid='landsd/237751:0',name='Wah Shun Gardens',identityPassed=False,completed='Fresh original/source/current bindings. OriginalTIN removes4current buried faces but tower remains16.774m above original ground.',nextAction='Recover recorded original podium235644 and verify actual support. Resolve target/full-coordinate-cell identity separately.'),
 dict(uid='landsd/238671:0',name='Parc Palais Block2',identityPassed=False,completed='Installed original podium266063 passes42finite support paths in all4worlds; zero whole/upward buried source faces. Both adjoining originals238669/238856 recovered.',nextAction='Check complete three-tower original joint and source-owned low extensions; keep both raw neighbour contact sets. Then qualified desktop/mobile preview.'),
 dict(uid='landsd/254815:0',name='Fung Yip Building',identityPassed=True,completed='Original podium79883 recovered;32finite paths per world pass. Podium clears exact originalTIN. Newinset retains original planes through tiny clipping fragments, then fails unchanged final boundary-height validator.',nextAction='Use terrain-aware retained-native boundary/replacement route, preserving originals12728/79882 and named party-edge evidence. No boundary waiver.'),
 dict(uid='landsd/255543:0',name='Beverly HillK',identityPassed=True,completed='Original podium233218 recovered;21finite paths per world pass. Current podium burial1591faces/442upward; fresh explicitly separate originalTIN still234buried faces.',nextAction='Derive faithful bounded source-terrain/retained-neighbour treatment; retain all buried-face negatives. Do not adopt support as publication approval.'),
 dict(uid='landsd/277890:0',name='Unnamed original277890',identityPassed=False,completed='Full current/source captures. OriginalTIN reduces to4wholly buried source faces/no upward burial, minimumgap-19.790m;28currentforms retained.',nextAction='Resolve named source ownership/extent and4buried-face architectural roles; compare bounded current terrain without changing building mesh.'),
 dict(uid='landsd/323185:0',name='Plaza Hollywood',identityPassed=False,completed='Current125buried/23upward; authenticated originalTIN leaves7buried/no upward. All14currentforms and exact current neighbour contacts retained.',nextAction='Review7original lower faces and extended source identity; generate bounded original-grade proposal with complete neighbour scope.')]
 for row in rows:row.update(humanStatus='held-compute',requiresCompute=True,requiresAI=False,requiresHumanDecision=False,installationApproved=False,permanentRejection=False)
 result=dict(uids=[r['uid']for r in rows],fixedXLTotal=521,fixedXLInstalled=352,fixedXLUnfinished=169,currentNativeActors=6896,rows=rows,completedJobs=jobs,scriptExternalAICalls=0,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,newlyInstalled=0,installationApproved=False,qualification='Completed diagnostic/support evidence and concrete next actions, not installation or permanent rejection. Historical native acquisition state and changed-terrain revision never transfer acceptance. No model remodel or optimisation performed.')
 save(out/'remaining-work.json',result);module('seven_support_checkpoint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B,'current-seven-xl-completed-original-recovery-and-support-checkpoint',refs,result)
if __name__=='__main__':main()
