"""DRAFT immutable complete Nam finite/role context, not physical approval."""
import argparse,json
from pathlib import Path
from fractions import Fraction as F
from nam_fung79099_actual_basic45779_full_owned_finite_role_context_draft_v1_20261012 import ROOT,HERE,read,ref,module,connect,reservations,inputs,body_context,DOC,LOCAL,BATCH,CAP,JOIN,UIDS,PROTECTED,MANIFEST_SHA

def main():
 p=argparse.ArgumentParser();p.add_argument('--lease-file',required=True);a=p.parse_args();lease=read(Path(a.lease_file));assert reservations.owns(lease)and not(DOC/'result.json').exists()
 pins,capture,join,scope,before,selections,prior=inputs();d=read(DOC/'diagnostic.json.gz')
 assert d['uid']==UIDS[0]and d['sourceSHA256']==prior['sourceSHA256']and d['completeFaces']==13061 and d['genuineOriginalBodyObligations']==569 and d['zeroOriginalFaceObligations']==75 and d['ordinaryThresholdM']=='-1/2'
 assert d['sourceOnly']and d['currentManifest']==scope['currentManifest']and d['currentNativeCount']==6649 and d['currentManifest']['sha256']==MANIFEST_SHA
 for key in ['identityAccepted','physicalAccepted','rootAccepted','installationApproved','all569RolesQualified','foreignHoldsDischarged','currentAll6649NativeClearanceProved']:assert d[key]is False
 assert d['sourceGeometryChanges']==d['terrainGeometryChanges']==0 and d['sourceInterpretationPending']
 assert d['originalBodyCensus']==prior['originalCensus']and d['completeGroundFaces']==818 and d['completeGroundSHA256']==prior['completeGroundSHA256']
 bindings=d['allFourStreamBindings'];assert set(bindings)=={'original','literal','explicitLeftF32','explicitBalancedF32'}and {x['wholeWorldSHA256']for x in bindings.values()}==set(d['distinctCompleteFiniteProofs'])
 assert set(d['completeUnusedPOSITIONBindings'])==set(bindings)-{'original'}
 labels={i:b for b,ids in enumerate(prior['originalCensus']['sharedEdgeConnectedComponents'])for i in ids};zeros=set(prior['originalCensus']['exactNonrenderingOriginalFaces'])
 for name,b in bindings.items():assert b['completeFaces']==13061 and b['groundSHA256']==d['completeGroundSHA256']and b['wholeWorldSHA256']==prior['fourWorldBindings'][name]['wholeWorldSHA256']and b['proofTupleSHA256']
 for sh,proof in d['distinctCompleteFiniteProofs'].items():
  rows=proof['allWholeFacetProofs'];assert proof['completeFaces']==len(rows)==13061 and [r['face']for r in rows]==list(range(13061));az=set(prior['distinctSourcePrismContactProofs'][sh]['actualBodyCensus']['exactNonrenderingOriginalFaces'])
  for r in rows:
   i=r['face'];assert r['originalBody']==labels.get(i)and r['originalZeroFace']==(i in zeros)and r['actualWorldZeroFace']==(i in az)
   assert r['ordinaryFiniteProved']==bool(r['completeProjectionCovered']and F(r['exactLowerM'])>=-F(1,2))and r['strictPositiveFiniteProved']==bool(r['completeProjectionCovered']and F(r['exactLowerM'])>0)and not r['gradeRootCredit']
  assert proof['ordinaryFailingFaces']==[r['face']for r in rows if not r['ordinaryFiniteProved']]and proof['coverageFailingFaces']==[r['face']for r in rows if not r['completeProjectionCovered']]and proof['strictUncertifiedFaces']==[r['face']for r in rows if not r['strictPositiveFiniteProved']]
  assert proof['bodyObligations']==body_context(prior,sh,rows)
 context=d['savedBASICCarrierGradeCapContext'];assert context['diagnostic']==ref(JOIN/'diagnostic.json.gz')and context['completeBasicFaces']==432 and context['availabilityOnly']and not context['wholeBasicReaccepted']
 assert context['rawCoarseOrdinaryUnprovedFaceIds']==[r['face']for r in prior['allActualBasicFiniteProofs']if not r['proof']['existingOrdinaryClearanceBoundProved']]
 assert context['strictUpwardCapIds']==prior['strictPositiveCaps']and context['qualifiedGradeWholeEdgeCapRouteCount']==len(prior['qualifiedGradeWallWholeEdgeCapRoutes'])
 for e in d['evidenceRefs']:assert ref(ROOT/e['path'])==e,e
 walker=module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','nam_finite_freezer');paths=set();walker.local_imports(Path(__file__),paths);walker.declared_refs(d,paths);paths.update(ROOT/e['path']for e in capture['evidenceRefs']+join['evidenceRefs']);paths.update(q for q in DOC.rglob('*')if q.is_file());paths.update(q for q in LOCAL.rglob('*')if q.is_file())
 note='Complete unchanged13061 original-source faces/all four worlds/569 genuine original body obligations/75 zeros against full818 captured tower+BASIC relevant ground. Fixed ordinary>=-.5m; strict separate, exact coarse→paired refinement. Every saved202 finite contacts/717 prism fragments/109 BASIC grade-cap contexts is reused byte-identically, never rerun or promoted. All325 coarse BASIC ordinary warnings remain; whole BASIC not reaccepted. Source architectural interpretation, actual mainbody support and every terminal/structural body, full current identity/foreign/native/foundation/runtime remain unapproved. No rejection solely because a source face is within the coarse BASIC prism, no all-faces-strict/interior-contact ban/global watertight gate. No original rejected podium installation. No source/terrain/pose/scale changes or legacy/review/installation approval.'
 (DOC/'REVIEW.md').write_text(note+'\n');paths.add(DOC/'REVIEW.md');assert reservations.owns(lease);inputs()
 result=walker.F.freeze(BATCH,'nam-complete-owned-finite-and-explicit-original-role-obligations-no-root',sorted(paths),dict(uids=UIDS+[PROTECTED],sourceOnly=True,currentManifestSHA256=MANIFEST_SHA,currentNativeCount=6649,completeFaces=13061,genuineOriginalBodyObligations=569,zeroOriginalFaceObligations=75,physicalAccepted=False,rootAccepted=False,installationApproved=False,originalGovernmentPodiumUsedAsSupport=False,wholeBasicReaccepted=False,sourceGeometryChanges=0,terrainGeometryChanges=0,modelReviewWrites=0))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e,e
 inputs();assert reservations.owns(lease);print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),physicalAccepted=False)))
if __name__=='__main__':main()
