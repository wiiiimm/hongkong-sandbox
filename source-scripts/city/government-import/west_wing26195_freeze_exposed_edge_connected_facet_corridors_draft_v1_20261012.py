"""DRAFT diagnostic-only freezer: exact bounded corridor evidence, no root credit."""
import argparse,json,itertools
from pathlib import Path
from fractions import Fraction as Q
from run import ROOT,HERE,read,connect,reservations,digest
import west_wing26195_exposed_edge_connected_facet_corridors_draft_v1_20261012 as G

def main():
 a=argparse.ArgumentParser();a.add_argument('--lease-file',required=True);a=a.parse_args();lease=read(Path(a.lease_file));assert reservations.owns(lease)and not(G.DOC/'result.json').exists();valid=G.validation();receipt,scope,worlds,ground,finite,old=G.inputs();d=read(G.DOC/'diagnostic.json.gz')
 assert d['sourceOnly']and d['uid']==G.P.F.UID and d['currentManifest']==scope['currentManifest']and d['nativeCount']==6649 and d['completeSourceFaces']==46918 and d['completeGroundFaces']==3240 and d['wholeGroundSHA256']==G.P.F.GROUND_SHA
 assert d['allFourStreamBindings']==old['allFourStreamBindings']and set(d['allFourStreamBindings'])==G.P.F.NAMES
 assert d['all42OrdinaryFailuresAnd443StrictUncertifiedRetained']and d['all118OriginalBodyObligationsAndOther117SupportObligationsRetained']and d['legacyDeliveryAnd15ReviewsUnchanged']
 assert not any(d[k]for k in ['physicalAccepted','gradeRootAccepted','burialRoleAccepted','installationApproved','sourceGeometryChanges','terrainGeometryChanges'])
 assert set(d['distinctBoundedCorridorDiagnostics'])=={v['proofTupleSHA256']for v in d['allFourStreamBindings'].values()}
 def cert(p,*,strict=False,expected=None):
  s=p['selection'];assert s['completeGroundSHA256']==G.P.F.GROUND_SHA and s['completeGroundFacetCount']==3240 and s['everyNoncandidateStrictlyDisjoint']and s['touchingAndCollapsedProjectionsRetained'];assert p['originalGroundFaceBySelectedKernelFace']==s['selectedOriginalGroundFaces']
  if expected is not None:
   exact=list(map(G.point,expected));assert exact[0]!=exact[1]and s['exactProjectedLower']==[str(min(v[k]for v in exact))for k in [0,2]]and s['exactProjectedUpper']==[str(max(v[k]for v in exact))for k in [0,2]]
   if p['selectedGroundKernelProof']is not None:assert endpoints(p)==expected
  if strict:assert p['closedWholeSegmentProjectionCovered']and p['strictlyExposedWholePositiveInterface']and Q(p['exactMinimumGapM'])>0
 def endpoints(p):return p['selectedGroundKernelProof']['exactEndpoints']
 for name,binding in d['allFourStreamBindings'].items():
  world=worlds[name];assert digest(world.tobytes())==binding['wholeWorldSHA256'];key=binding['proofTupleSHA256'];p=d['distinctBoundedCorridorDiagnostics'][key];prior=old['distinctBoundedRouteDiagnostics'][key];records=finite['distinctCompleteFiniteProofs'][key]['allWholeFacetProofs'];grades={r['seedFace']:r for r in prior['routes']};seeds=sorted(i for i,r in grades.items()if not r['boundedOriginalPath']);saved=prior['allExaminedWholeEdgeProofs']
  assert p['wholeWorldSHA256']==binding['wholeWorldSHA256']and p['completeGroundSHA256']==G.P.F.GROUND_SHA and p['exact25UnresolvedSeeds']==seeds and len(seeds)==25 and len(saved)==88 and p['exact88SavedWholeEdgesPreserved']==saved
  assert p['previous17PathsRetainedVerbatim']==[r for r in prior['routes']if r['boundedOriginalPath']]and len(p['previous17PathsRetainedVerbatim'])==17
  assert p['completeFixedSourceFacetContext']==sorted(set(seeds)|{i for e in saved for i in e['faces']})and len(p['edgeExposureDiagnostics'])==88
  assert p['wholeEdgePredicateUnchanged']and not p['pointOrEndpointOnlyRouteCredit']and p['noFiniteOrGradeArithmeticRerun']and not p['sourceOrTerrainGeometryChanges']and not p['physicalAccepted']
  nodes=p['allDiagnosticNodes'];corridors=p['allWithinFacetSegmentCertificates'];anchors=p['allGradeToExposedNodeCertificates'];edges=p['edgeExposureDiagnostics'];context=set(p['completeFixedSourceFacetContext'])
  def membership(face,ends):return G.source_segment([G.strings(G.exact(v))for v in world[face]],ends)
  for n in nodes:
   i=n['sourceFace'];assert i in context and (records[i]['strictPositiveFiniteProved']or i in grades and grades[i]['genuineExposedGradeDiagnostic']);other=G.strings(G.exact(world[i,0] if G.point(n['exactPoint'])!=G.exact(world[i,0])else world[i,1]));membership(i,[n['exactPoint'],other])
  for i,e in enumerate(edges):
   assert e['savedWholeEdgeVerbatim']==saved[i];expected=[G.strings(G.exact(v))for v in saved[i]['unchangedOriginalWholeSharedEdge']];assert e['exposureClassification']==G.classify(saved[i]['completeFiniteEdgeProof'],expected_ground_sha=G.P.F.GROUND_SHA,expected_ground_faces=3240,expected_endpoints=expected)
   for face in saved[i]['faces']:
    actual={tuple(sorted((G.exact(world[face,k]),G.exact(world[face,(k+1)%3]))))for k in range(3)};assert tuple(sorted(map(G.point,expected)))in actual
   expectedParts=e['exposureClassification']['positiveLengthExposedNominees']
   if saved[i]['completeFiniteEdgeProof']['strictlyExposedWholePositiveInterface']:expectedParts=[dict(exactClosedInteriorParameterInterval=['0','1'],exactEndpoints=expected,representativePoint=G.strings(G.at(*map(G.point,expected),Q(1,2))))]
   assert [{k:x[k]for k in ['exactClosedInteriorParameterInterval','exactEndpoints','representativePoint']}for x in e['subsegmentCertificates']]==expectedParts
   for part in e['subsegmentCertificates']:
    proof=part['completeGroundSegmentCertificate'];cert(proof,strict=part['independentlyStrictPositive'],expected=part['exactEndpoints']);assert part['independentlyStrictPositive']==proof['strictlyExposedWholePositiveInterface'];assert G.point(part['representativePoint'])==G.at(*map(G.point,part['exactEndpoints']),Q(1,2))
    for face in saved[i]['faces']:membership(face,part['exactEndpoints'])
    if part['wholeEdgeProofReused']:assert proof==saved[i]['completeFiniteEdgeProof']and part['exactClosedInteriorParameterInterval']==['0','1']
    else:assert {k:part[k]for k in ['exactClosedInteriorParameterInterval','exactEndpoints','representativePoint']}in e['exposureClassification']['positiveLengthExposedNominees']
  for c in corridors:
   i=c['sourceFace'];a,b=c['nodeIds'];assert a!=b and nodes[a]['sourceFace']==nodes[b]['sourceFace']==i;ends=[nodes[a]['exactPoint'],nodes[b]['exactPoint']];assert c['exactSourceFacetMembership']==membership(i,ends);cert(c['completeGroundSegmentCertificate'],strict=c['strictConnectedCorridor'],expected=ends);assert c['strictConnectedCorridor']==c['completeGroundSegmentCertificate']['strictlyExposedWholePositiveInterface']
  expectedPairs={tuple([i,a,b])for i in context for a,b in itertools.combinations([j for j,n in enumerate(nodes)if n['sourceFace']==i],2)};actualPairs=[tuple([c['sourceFace']]+c['nodeIds'])for c in corridors];assert len(actualPairs)==len(set(actualPairs))and set(actualPairs)==expectedPairs and len(corridors)<=G.MAX_PAIRS
  for anchor in anchors:
   seed=anchor['seedFace'];n=anchor['nodeId'];proof=anchor['completeGroundSegmentCertificate'];ends=anchor['exactOriginalFacetMembership']['exactEndpoints'];cert(proof,expected=ends);assert seed in seeds and nodes[n]['sourceFace']==seed and ends[1]==nodes[n]['exactPoint'];assert anchor['exactOriginalFacetMembership']==membership(seed,ends);contacts={G.at(*map(G.point,v['nominatedInterval']['exactSegmentEndpoints']),Q(1,2))for v in grades[seed]['verifiedPositiveUpperGroundIntervals']};assert G.point(ends[0])in contacts
   if anchor['nonnegativeGradeConnectionStrictExceptStart']:
    assert proof['closedWholeSegmentProjectionCovered']and Q(proof['exactMinimumGapM'])==0;exposure=G.classify(proof,expected_ground_sha=G.P.F.GROUND_SHA,expected_ground_faces=3240,expected_endpoints=endpoints(proof));assert anchor['exactExposureClassification']==exposure and exposure['strictPositiveExceptInitialEndpoint']and exposure['initialEndpointGapM']=='0'
  expectedAnchors={(seed,j,contact)for seed in seeds for j,n in enumerate(nodes)if n['sourceFace']==seed for contact in {G.at(*map(G.point,v['nominatedInterval']['exactSegmentEndpoints']),Q(1,2))for v in grades[seed]['verifiedPositiveUpperGroundIntervals']}if contact!=G.point(n['exactPoint'])};actualAnchors=[(x['seedFace'],x['nodeId'],G.point(x['exactOriginalFacetMembership']['exactEndpoints'][0]))for x in anchors];assert len(actualAnchors)==len(set(actualAnchors))and set(actualAnchors)==expectedAnchors
  assert [r['seedFace']for r in p['boundedConnectedRoutes']]==seeds
  for route in p['boundedConnectedRoutes']:
   seed=route['seedFace'];starts=sorted({a['nodeId']for a in anchors if a['seedFace']==seed and a['nonnegativeGradeConnectionStrictExceptStart']});assert route['nonnegativeGradeConnectedStartNodes']==starts and route['faceBudget']==64 and len(route['visitedSourceFaces'])<=64
   path=route['boundedConnectedNodePath'];assert route['diagnosticRouteFound']==bool(path)and len(route['completePathTransitionCertificates'])==max(0,len(path)-1)
   if not path:assert route['strictPositiveNonsteepCapFace']is None and route['exactStrictPositiveCapCertificate']is None;continue
   assert path[-1]in starts and len(path)==len(set(path));cap=nodes[path[0]]['sourceFace'];normal=G.P.F.exact_orientation(world[cap]);n=list(map(Q,normal['exactNormal']));assert records[cap]['strictPositiveFiniteProved']and n[1]>0 and 16*n[1]*n[1]>sum(v*v for v in n);assert route['strictPositiveNonsteepCapFace']==cap and route['exactStrictPositiveCapCertificate']==dict(sourceFace=cap,unchangedFullFacetProof=records[cap],exactOriginalOrientation=normal)
   for (a,b),link in zip(zip(path,path[1:]),route['completePathTransitionCertificates']):
    assert set(link['nodeIds'])=={a,b}
    if link['kind']=='complete-strict-within-original-facet-corridor':
     c=corridors[link['corridorIndex']];assert c['strictConnectedCorridor']and set(c['nodeIds'])=={a,b}
    else:
     assert link['kind']=='positive-length-genuine-original-edge-subsegment';e=edges[link['savedEdgeIndex']];part=e['subsegmentCertificates'][link['partIndex']];assert part['independentlyStrictPositive']and set(link['sourceFaces'])==set(e['savedWholeEdgeVerbatim']['faces'])=={nodes[a]['sourceFace'],nodes[b]['sourceFace']};assert nodes[a]['exactPoint']==nodes[b]['exactPoint']==part['representativePoint']
 walker=G.P.F.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwing_corridor_freezer');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(Path(G.__file__),paths)
 for e in receipt['evidenceRefs']+d['evidenceRefs']+valid:assert G.ref(ROOT/e['path'])==e;paths.add(ROOT/e['path'])
 paths.add(G.DOC/'diagnostic.json.gz');paths.add(G.PROPOSAL/'no-worker-schema-hash-validation.json');paths.add(Path(a.lease_file));paths.update(p for p in G.LOCAL.rglob('*')if p.is_file());G.inputs();assert reservations.owns(lease)
 result=walker.F.freeze(G.BATCH,'bounded-original-exposed-subinterval-within-facet-corridor-context-no-root-credit',sorted(paths),dict(uids=[G.P.F.UID],sourceOnly=True,physicalAccepted=False,gradeRootAccepted=False,burialRoleAccepted=False,installationApproved=False,legacyInstalledDeliveryPreserved=True,modelReviewWrites=0,completeFaces=46918,completeGroundFaces=3240,unresolvedSeedsExamined=25,savedWholeEdgesPreserved=88,all118OriginalBodyObligationsRetained=True))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert G.ref(ROOT/e['path'])==e
 G.inputs();assert reservations.owns(lease);print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
