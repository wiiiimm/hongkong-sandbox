"""DRAFT diagnostic freezer. Wall154 has segment credit only, never full-facet credit."""
import argparse,json,itertools
from fractions import Fraction as Q
from pathlib import Path
from run import ROOT,HERE,read,connect,reservations
import west_wing26195_seed153_two_edge_corridor_expansion_draft_v1_20261012 as D

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--lease-file',required=True);args=parser.parse_args();D.validation();lease=read(Path(args.lease_file));assert reservations.owns(lease);receipt,scope,worlds,ground,finite,old,corridor=D.inputs();d=read(D.DOC/'diagnostic.json.gz');complete=D.CompleteGround(ground)
 assert d['sourceOnly']and not d['physicalAccepted']and not d['gradeRootAccepted']and not d['installationApproved']and d['completeFaces']==46918 and d['completeGroundFaces']==3240 and d['all118BodyObligationsRetained']and d['all42OrdinaryFailuresAnd443StrictUncertifiedRetained']and d['noFiniteOrGradeArithmeticRerun']
 assert d['currentManifest']==scope['currentManifest']and d['allFourStreamBindings']==finite['allFourStreamBindings']and d['priorAll24NewAnd17EarlierPathsPreserved']==D.ref(D.G.DOC/'diagnostic.json.gz')
 assert set(d['distinctBoundedDiagnostics'])=={v['proofTupleSHA256']for v in d['allFourStreamBindings'].values()}
 def cert(p,ends,strict=False):
  s=p['selection'];assert s['completeGroundSHA256']==D.G.P.F.GROUND_SHA and s['completeGroundFacetCount']==3240 and s['everyNoncandidateStrictlyDisjoint']and s['touchingAndCollapsedProjectionsRetained'];assert p['originalGroundFaceBySelectedKernelFace']==s['selectedOriginalGroundFaces'];v=list(map(D.G.point,ends));assert v[0]!=v[1]
  assert s['exactProjectedLower']==[str(min(x[k]for x in v))for k in [0,2]]and s['exactProjectedUpper']==[str(max(x[k]for x in v))for k in [0,2]]
  if p['selectedGroundKernelProof']is not None:assert p['selectedGroundKernelProof']['exactEndpoints']==ends
  if strict:assert p['closedWholeSegmentProjectionCovered']and p['strictlyExposedWholePositiveInterface']and Q(p['exactMinimumGapM'])>0
 for name,world in worlds.items():
  binding=d['allFourStreamBindings'][name];assert D.digest(world.tobytes())==binding['wholeWorldSHA256'];key=binding['proofTupleSHA256'];r=d['distinctBoundedDiagnostics'][key];records=finite['distinctCompleteFiniteProofs'][key]['allWholeFacetProofs'];edges=D.source_context(world,records)
  seed=next(x for x in old['distinctBoundedRouteDiagnostics'][key]['routes']if x['seedFace']==153);assert r['wholeWorldSHA256']==binding['wholeWorldSHA256']and r['sourceContextFaces']==[153,154,44545]and r['seedGradeProofReusedVerbatim']==seed and r['ordinaryPassSteepCorridorOnlyFacet154']==records[154]and r['strictFullCap44545']==records[44545]and r['capOrientation']==D.G.P.F.exact_orientation(world[44545])and not r['wholeFacet154StrictPositiveClaim']and not r['newGradeRootClaim']
  assert len(r['edgeDiagnostics'])==2
  for edge,er in zip(edges,r['edgeDiagnostics']):
   assert er['edge']==edge;proof=er['completeWholeEdgeCertificate'];cert(proof,edge['exactEndpoints']);c=D.G.classify(proof,expected_ground_sha=D.G.P.F.GROUND_SHA,expected_ground_faces=3240,expected_endpoints=edge['exactEndpoints']);assert c==er['exactExposureClassification'];nom=c['positiveLengthExposedNominees']
   if proof['strictlyExposedWholePositiveInterface']:nom=[dict(exactClosedInteriorParameterInterval=['0','1'],exactEndpoints=edge['exactEndpoints'],representativePoint=D.G.strings(D.G.at(*map(D.G.point,edge['exactEndpoints']),Q(1,2))))]
   assert [{k:p[k]for k in ['exactClosedInteriorParameterInterval','exactEndpoints','representativePoint']}for p in er['positiveLengthSubsegments']]==nom
   for p in er['positiveLengthSubsegments']:
    cert(p['completeGroundSegmentCertificate'],p['exactEndpoints'],p['strictPositive']);assert p['strictPositive']==p['completeGroundSegmentCertificate']['strictlyExposedWholePositiveInterface']
    for face in edge['faces']:D.membership(world,face,p['exactEndpoints'])
  contacts={D.G.at(*map(D.G.point,v['nominatedInterval']['exactSegmentEndpoints']),Q(1,2))for v in seed['verifiedPositiveUpperGroundIntervals']};entries=[p for p in r['edgeDiagnostics'][0]['positiveLengthSubsegments']if p['strictPositive']];exits=[p for p in r['edgeDiagnostics'][1]['positiveLengthSubsegments']if p['strictPositive']];expected={(c,tuple(e['representativePoint']),tuple(x['representativePoint']))for c,e,x in itertools.product(contacts,entries,exits)if c!=D.G.point(e['representativePoint'])and D.G.point(e['representativePoint'])!=D.G.point(x['representativePoint'])};actual=[]
  for attempt in r['allBoundedAttempts']:
   c=D.G.point(attempt['exactGradeStart']);entry=attempt['entrySubsegment'];exit=attempt['exitSubsegment'];assert c in contacts and entry in entries and exit in exits;start=[attempt['exactGradeStart'],entry['representativePoint']];middle=[entry['representativePoint'],exit['representativePoint']];actual.append((c,tuple(entry['representativePoint']),tuple(exit['representativePoint'])))
   assert attempt['seedMembership']==D.membership(world,153,start)and attempt['corridorOnlyWallMembership']==D.membership(world,154,middle);sp=attempt['gradeToEntryCertificate'];mp=attempt['withinWallCertificate'];cert(sp,start);cert(mp,middle,attempt['withinWallStrictPositive']);assert attempt['withinWallStrictPositive']==mp['strictlyExposedWholePositiveInterface'];sc=None;ok=False
   if sp['closedWholeSegmentProjectionCovered']and sp['exactMinimumGapM']is not None and Q(sp['exactMinimumGapM'])==0 and not any(x.get('collapsedProjectionConservative')for x in sp['selectedGroundKernelProof']['allFinitePieces']):sc=D.G.classify(sp,expected_ground_sha=D.G.P.F.GROUND_SHA,expected_ground_faces=3240,expected_endpoints=start);ok=sc['strictPositiveExceptInitialEndpoint']and sc['initialEndpointGapM']=='0'
   assert attempt['gradeToEntryExposure']==sc and attempt['gradeConnectorStrictExceptStart']==ok and attempt['boundedDiagnosticRouteFound']==(ok and mp['strictlyExposedWholePositiveInterface'])
  assert len(actual)==len(set(actual))and set(actual)==expected and len(actual)<=1024 and r['diagnosticRouteFound']==any(x['boundedDiagnosticRouteFound']for x in r['allBoundedAttempts'])
 walker=D.G.P.F.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwing153freezer');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(Path(D.__file__),paths)
 for e in receipt['evidenceRefs']+d['evidenceRefs']:assert D.ref(ROOT/e['path'])==e;paths.add(ROOT/e['path'])
 paths.add(D.DOC/'diagnostic.json.gz');paths.add(Path(args.lease_file));paths.update(p for p in D.LOCAL.rglob('*')if p.is_file());paths.update(p for p in D.PROPOSAL.iterdir()if p.is_file());D.inputs();assert reservations.owns(lease);complete.verify_binding()
 result=walker.F.freeze(D.BATCH,'bounded-seed153-ordinary-steep-wall-segment-only-corridor-no-root-credit',sorted(paths),dict(uids=[D.G.P.F.UID],sourceOnly=True,physicalAccepted=False,gradeRootAccepted=False,installationApproved=False,modelReviewWrites=0,completeFaces=46918,completeGroundFaces=3240,sourceContextFaces=[153,154,44545],all118BodyObligationsRetained=True))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert D.ref(ROOT/e['path'])==e
 D.inputs();assert reservations.owns(lease);print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
