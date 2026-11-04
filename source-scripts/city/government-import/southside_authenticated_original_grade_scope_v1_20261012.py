"""Source-specific saved-proof scope and diagnostic path accounting, not acceptance."""
import hashlib,json
SOURCES={'landsd/315025:0':'85be44e7ab9410c850d3b7d59d05df2cd45fc1072ec2f984ddbb7b43c4d9ff7c','landsd/300867:0':'2293ba8925406abcdbd848486a772dfa8baa01caf0cfe96e749d5a3cd51210f1'}
COUNTS={'landsd/315025:0':11699,'landsd/300867:0':1191}
GROUND_COUNTS={'landsd/315025:0':25388,'landsd/300867:0':7186}
def canonical_sha(row):
 return hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def prepare(world,ground,current,authenticated,binding):
 uid=authenticated['uid'];assert uid in COUNTS and current['uid']==uid and current['arithmetic']==authenticated['arithmetic']
 assert canonical_sha(current)==binding['currentRowCanonicalSHA256']and canonical_sha(authenticated)==binding['authenticatedRowCanonicalSHA256']
 assert current['sourceSHA256']==authenticated['sourceSHA256']==SOURCES[uid]
 assert world.shape==(COUNTS[uid],3,3)and ground.shape==(GROUND_COUNTS[uid],3,3)
 wsha=hashlib.sha256(world.tobytes()).hexdigest();gsha=hashlib.sha256(ground.tobytes()).hexdigest()
 assert current['completeWorldSHA256']==authenticated['completeWorldSHA256']==wsha and authenticated['completeUnfilteredSelectedGroundSHA256']==gsha
 a=current['allCompleteOriginalFiniteRecords'];b=authenticated['completeOriginalFaceComparisons'];assert len(a)==len(b)==COUNTS[uid]
 assert [q['sourceFace']for q in a]==[q['sourceFace']for q in b]==list(range(COUNTS[uid]))
 records=[]
 for i,(old,new)in enumerate(zip(a,b)):
  fsha=hashlib.sha256(world[i].tobytes()).hexdigest();assert old['completeOriginalFacetSHA256']==new['completeOriginalFacetSHA256']==fsha
  assert new['currentDrawnGroundComparisonRetainedVerbatim']==old['currentDrawnGroundComparison']and new['orientationDescriptiveOnly']==old['exactOrientationDiagnostic']
  proof=new['unfilteredAuthenticatedOriginalGroundComparison'];assert type(proof['completeFiniteOrdinaryBoundProved'])is bool
  for p in [proof['coarse']]+([]if proof['paired']is None else[proof['paired']]):assert p['sourceFaceSHA256']==fsha and p['completeCurrentGroundSHA256']==gsha and p['fullAcceptance']is False and p['installationApproved']is False
  records.append(dict(sourceFace=i,completeOriginalFacetSHA256=fsha,exactOrientationDiagnostic=old['exactOrientationDiagnostic'],currentDrawnGroundComparison=old['currentDrawnGroundComparison'],authenticatedOriginalGroundComparison=proof))
 topology=current['completeOriginalTopology'];zeros=set(topology['exactNonrenderingOriginalFaces']);groups=topology['sharedEdgeConnectedComponents'];mapping={}
 for j,ids in enumerate(groups):
  assert ids and len(ids)==len(set(ids))
  for i in ids:assert i not in zeros and i not in mapping;mapping[i]=j
 assert set(mapping)==set(range(COUNTS[uid]))-zeros
 failed={q['sourceFace']for q in records if not q['authenticatedOriginalGroundComparison']['completeFiniteOrdinaryBoundProved']};assert sorted(failed)==authenticated['allAuthenticatedGroundFailuresRetained']
 assert authenticated['allCurrentFailuresRetainedVerbatim']==current['allRawFailedFaces']
 steep={q['sourceFace']for q in records if q['exactOrientationDiagnostic']=='steep-wall'};assert not steep&zeros
 nonsteep=failed-steep-zeros;eligible=sorted(set(range(COUNTS[uid]))-zeros-nonsteep)
 return dict(records=records,topology=topology,zeros=zeros,steep=steep,failed=failed,nonsteep=nonsteep,eligible=eligible,componentMap=mapping)
def account_path(ids,*,eligible,component_map,positive_grade_ids,terminal_cap_strict,interfaces,raw_helper_path):
 assert ids and len(ids)==len(set(ids))and set(ids)<=set(eligible)
 assert len({component_map[i]for i in ids})==1
 assert len(interfaces)==len(ids)-1
 nonempty=len(ids)>1 and bool(interfaces)
 genuine=ids[0]in positive_grade_ids
 edges=all(q['hasWholeStrictlyExposedOriginalEdge']for q in interfaces)
 cap=bool(raw_helper_path['hasExactOriginalStrictClearCapRoofPath']and terminal_cap_strict)
 return dict(nonemptyOriginalWallPath=nonempty,sourceFaceHasGenuinePositiveDimensionalGradeContact=genuine,diagnosticGradeToWholeClearCapAndExposedEdges=bool(nonempty and genuine and cap and edges),terminalCapWholeFiniteStrictlyClear=cap,allPathInterfacesHaveWholeExposedSharedEdge=edges,rootCredit=False,fullBodyRootProved=False)
