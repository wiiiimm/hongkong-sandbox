"""Compose exact original Kai Tak acceptance evidence; never alter raw failures."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-kai-tak-cruise-functional-applicability-v1-20261019';DOC=BASE/BATCH
POD='landsd/263423:0';SHA='44839b47ec51db17f72eca474516b1f7a960476f4426990e180c7f8dafe3e341'
def folder(n):return BASE/('government-xl-kai-tak-cruise-'+n+'-20261019')
def qualify():
 ground=read(folder('source-relationship-review-v1')/'ROOT-SOURCE-RELATIONSHIP-REVIEW.json');roof=read(folder('component-interface-review-v1')/'ROOT-INTERFACE-REVIEW.json')
 assert ground['uid']==POD and ground['sourceSHA256']==SHA and ground['reviewer']=='Codex ROOT'
 assert ground['originalSurveyedRelationshipAccepted'] and ground['rawStrictFoundationPassed'] and not ground['rawStrictGroundContactPassed'] and ground['geometryOrPoseChanges']==0
 assert roof['reviewer']=='Codex ROOT' and roof['sourceSpecificInterfaceInterpretationAccepted'] and roof['rawStrictFailuresRetained']
 assert roof['sourceGeometryChanges']==roof['sourcePoseChanges']==0
 rows=read(folder('assembly-validation-v1')/'selection.json.gz')['rows'];sources={r['uid']:r['sourceSHA256']for r in rows};assert len(sources)==14 and sources[POD]==SHA
 assert {r['uid']:r['sourceSHA256']for r in roof['sourceBindings']}=={u:s for u,s in sources.items()if u!=POD}
 for r in rows:assert digest((ROOT/r['candidate']['path']).read_bytes())==r['sourceSHA256']
 modes={'original','literal','explicitLeftF32','explicitBalancedF32'};assert {r['mode']for r in ground['checks']}==modes
 for r in ground['checks']:assert r['foundation']['triangles']==r['foundation']['completeTerrainTriangles']==45925 and r['foundation']['fullyBuriedTriangles']==r['foundation']['fullyBuriedUpwardTriangles']==0
 assert len(ground['reviewedFaceIds'])==143 and ground['rawContactSummary']['maximumTerrainDifferenceMetres']<5e-6
 v=read(folder('assembly-validation-v1')/'validation.json');assert v['models']==v['loaderAccepted']==v['checksPassed']==14 and v['exceptions']==0
 assert {r['uid']for r in v['results']}==set(sources)
 for r in v['results']:assert r['concerns']==([]if r['uid']==POD else ['sampled-ground-gap-below-model-bottom'])
 near=read(folder('assembly-validation-v1')/'neighbour-checks.json');assert len(near['rows'])==212 and all(not r['reasons']for r in near['rows'])
 native=read(folder('assembly-validation-v1')/'native-neighbour-checks.json');assert not set(native['blocked'])-set(native['resolved'])
 assert len(native['rows'])==1 and native['rows'][0]['uid']=='landsd/299814:0' and native['rows'][0]['passed']
 t=native['rows'][0]['terrain'];assert t['maximumBurialIncrease']==t['newlyWhollyBuried']==t['newlyUpwardWhollyBuried']==0
 scope=read(BASE/'government-xl-remaining-three-current-scope-v1-20261019/scope.json');assert scope['allCurrentActorsNominated'] and scope['currentNativeActors']==6728
 domain=next(r for r in scope['rows']if r['uid']==POD);assert domain['touchingBaseDomainNativeUids']==['landsd/299814:0']
 eq=read(folder('terrain-ownership-v1')/'metadata-equivalence.json');candidate=read(folder('terrain-ownership-v1')/'terrain-candidates.json')[0]
 assert eq['completePayloadEqualAfterRemovingOnlyOwnershipAndEvidenceReference'] and eq['overlapEvidenceEqualExceptPayloadBinding'] and eq['terrainValidationPassed'] and eq['renderedGeometryChanges']==0
 assert set(eq['replacementTargetUids'])==set(sources)|{'landsd/299814:0'}
 assert eq['replacementTerrain']==dict(path=candidate['path'],sha256=candidate['sha256'])
 for q in [eq['previousTerrain'],eq['replacementTerrain']]:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 assert eq['previousTerrain']=={k:read(folder('assembly-validation-v1')/'terrain-candidates.json')[0][k]for k in ['path','sha256']}
 return dict(uids=sorted(sources),sourceBindings=[dict(uid=u,sourceSHA256=s)for u,s in sorted(sources.items())],sourceScopedApplicabilityAccepted=True,remainingPhysicalReasons=[],rawStrictGroundContactPassed=False,rawStrictFailuresRetained=True,rawDiagnosticConcerns=v['concerns'],sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,publicationApproved=False,installationApproved=False,qualification='Exact unchanged terminal/TIN relationship and thirteen original roof interfaces only. Source-specific signed reviews preserve all raw failed samples. Current whole-source terrain, loader and all nominated neighbours pass; no generic tolerance change.')
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 folders=[folder(n)for n in ['source-relationship-review-v1','component-interface-review-v1','assembly-validation-v1','terrain-ownership-v1']]+[BASE/'government-xl-remaining-three-current-scope-v1-20261019']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in folders:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 q=qualify();save(DOC/'qualification.json',q)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 module('kai_functional_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-fourteen-exact-original-functional-applicability',list(dict.fromkeys(refs)),dict(uids=q['uids'],sourceScopedApplicabilityAccepted=True,installationApproved=False))
if __name__=='__main__':main()
