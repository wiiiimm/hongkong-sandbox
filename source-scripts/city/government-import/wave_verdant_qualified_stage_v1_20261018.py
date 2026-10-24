"""Qualified nine-original stage with original dependencies and three BASIC estimate corrections."""
from pathlib import Path
import shutil,sys
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave-verdant-qualified-stage-v1-20261018';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
REVIEW=BASE/'government-xl-wave-verdant-assembly-review-v1-20261018';OLD=HERE/'local/government-xl-wave-verdant-publication-proposal-v1-20261018';BROWSER=BASE/'government-xl-wave-verdant-private-browser-v5-20261018'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(r):assert ref(ROOT/r['path'])==r,r['path']
def main():
 assert not DOC.exists()and not STAGE.exists();r=read(REVIEW/'result.json');pins={};refs=[Path(__file__),REVIEW/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 decision=read(REVIEW/'ROOT-SOURCE-REVIEW.json');assert decision['originalSourceReviewAccepted']and decision['policyReasons']==[];check(decision['currentManifest'])
 shutil.copytree(OLD,STAGE);cat=read(STAGE/'catalogue.json');assert {m['uid']:m['sha256']for m in cat['models']}==decision['sourceSHA256ByUid'];unchanged={m['uid']:dict(m)for m in cat['models']}
 for m in cat['models']:
  assert digest((STAGE/m['asset']).read_bytes())==m['sha256'];m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceIdentityReview=ref(REVIEW/'ROOT-SOURCE-REVIEW.json'),sourceFunctionalApplicability=ref(REVIEW/'ROOT-SOURCE-REVIEW.json'),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,placementReview='Unchanged original fixed1x source and exact-source interface review; complete current terrain, neighbours, dependency and staged browser evidence accepted. Raw warnings preserved in review.')
  assert m['proceduralWindows']is False and not m.get('suppressesBuildingUids');assert m.get('supportDependencies')==unchanged[m['uid']].get('supportDependencies')
 save(STAGE/'catalogue.json',cat);plan=read(STAGE/'plan.json')
 def relocate(value):
  if isinstance(value,str):return value.replace(str(OLD.relative_to(ROOT)),str(STAGE.relative_to(ROOT)))
  if isinstance(value,list):return [relocate(x)for x in value]
  if isinstance(value,dict):return {k:relocate(v)for k,v in value.items()}
  return value
 plan=relocate(plan);save(STAGE/'plan.json',plan)
 config=read(HERE/'local'/BROWSER.name/'browser-config.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=plan['areas'][0]['destination'],terrain=plan['topLevelTerrainPatches']);save(STAGE/'browser-config.json',config)
 # The eventual live run uses actual published tiles, not the earlier private tile route.
 live=dict(config,catalogueReplacements=[]);save(STAGE/'live-browser-config.json',live)
 pub=module('wave_qualified_dry_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();dry=read(pub.DOC/'publication-plan.json');assert not dry['published']and len(dry['estimatedBases'])==2 and len(dry['illustrativeFoundations'])==1;check(decision['currentManifest'])
 save(DOC/'qualification.json',dict(privateStageQualified=True,sourceSHA256ByUid=decision['sourceSHA256ByUid'],currentManifest=decision['currentManifest'],sourceReview=ref(REVIEW/'ROOT-SOURCE-REVIEW.json'),terrainCandidate=plan['topLevelTerrainPatches'][0],noTerrainChange=False,models=9,estimatedBases=2,illustrativeFoundations=1,publication=False))
 refs.extend([HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/illustrative_foundations.py',*[p for p in STAGE.rglob('*')if p.is_file()]])
 out=module('wave_qualified_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'nine-original-qualified-stage-with-publisher-dry-run-v1',list(set(refs)),dict(uids=list(decision['sourceSHA256ByUid']),privateStageQualified=True,publication=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
