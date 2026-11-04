"""DRAFT reuse exact current contacts; conditional graph never supplies a root."""
from collections import deque
import hashlib,json
UID='landsd/26195:0';SOURCE='50da67a3a009c3c832d2bfdbd08640c89d958ef8cf077d1c172e7059900f8af9'
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def conditional_paths(contacts,*,body_count,conditional_root=0,visual_only=(108,113)):
 assert type(body_count)is int and body_count>0 and 0<=conditional_root<body_count
 excluded=set(visual_only);assert conditional_root not in excluded
 adj={i:set()for i in range(body_count)if i not in excluded};credited=[];rejected=[]
 for index,r in enumerate(contacts):
  a,b=r['originalBodyLabels'];assert type(a)is int and type(b)is int and 0<=a<body_count and 0<=b<body_count and a!=b
  assert type(r['dimension'])is int and r['dimension']in [0,1,2]and len(r['actualFinitePrimitiveDimensions'])==2
  assert all(type(d)is int and d in [0,1,2]for d in r['actualFinitePrimitiveDimensions'])
  assert type(r['bothRelativeInteriorSurfaceCrossing'])is bool
  reason=None
  if r['dimension']==0:reason='point-only-no-bridge'
  elif any(d==0 for d in r['actualFinitePrimitiveDimensions']):reason='zero-primitive-no-bridge'
  elif a in excluded or b in excluded:reason='visual-only-no-structural-bridge'
  if reason:rejected.append(dict(savedContactIndex=index,reason=reason));continue
  adj[a].add(b);adj[b].add(a);credited.append(index)
 parents={conditional_root:None};queue=deque([conditional_root])
 while queue:
  a=queue.popleft()
  for b in sorted(adj[a]):
   if b not in parents:parents[b]=a;queue.append(b)
 paths={}
 for i in sorted(parents):
  path=[i]
  while parents[path[-1]]is not None:path.append(parents[path[-1]])
  paths[i]=list(reversed(path))
 return dict(conditionalPositiveDimensionalContactPaths=paths,creditedSavedContactIndices=credited,rejectedSavedContactContexts=rejected,unreachedNonvisualBodies=sorted(set(adj)-set(parents)),retainedProperInteriorContactIndices=[j for j,r in enumerate(contacts)if r['bothRelativeInteriorSurfaceCrossing']],actualIndependentRootProvided=False,bodySupportAccepted=False)
def binding(certificate,graph,finite,visual):return sha([certificate,graph,finite,visual])
def verify(certificate,graph,finite,visual,*,expected_binding):
 assert binding(certificate,graph,finite,visual)==expected_binding
 assert certificate['uid']==UID and certificate['sourceSHA256']==SOURCE and certificate['body0SourceRoleCandidateQualified']and not certificate['groundRootAccepted']and not certificate['physicalAccepted']
 assert certificate['remaining117BodyObligationsIndependent']and certificate['sourceFacet154SegmentOnly']
 streams=finite['allFourStreamBindings'];assert streams==graph['allFourStreamBindings']==visual['allFourStreamBindings']==certificate['allFourStreamBindings']
 bodies=finite['originalBodyCensus']['sharedEdgeConnectedComponents'];assert len(bodies)==118 and bodies[0]==certificate['completeBody0FaceIds'];flat=[i for ids in bodies for i in ids];assert len(flat)==46918 and sorted(flat)==list(range(46918))
 visual_roles=visual['typedSourceVisualRoleContext'];assert visual_roles['sourceVisualOnlyBodies']==[108,113]and not visual_roles['fullRoleReconciliationAccepted']
 result={}
 for key,f in finite['distinctCompleteFiniteProofs'].items():
  g=graph['distinctCompleteBodyDiagnostics'][key];assert g['completeOriginalBodyFaces']==bodies and len(g['all6903BodyPairSummaries'])==6903
  contacts=g['allExactCrossBodyContacts'];records=f['allWholeFacetProofs'];assert len(records)==46918
  for r in contacts:
   assert len(r['sourceFaces'])==2
   for face,body in zip(r['sourceFaces'],r['originalBodyLabels']):assert face in bodies[body]
  paths=conditional_paths(contacts,body_count=118);roles=[]
  for i,ids in enumerate(bodies):
   ordinary_failed=[j for j in ids if not records[j]['ordinaryFiniteProved']];strict_warning=[j for j in ids if not records[j]['strictPositiveFiniteProved']]
   assert i==0 or not ordinary_failed
   roles.append(dict(originalBody=i,completeSourceFaceIds=ids,ordinaryFailedFaces=ordinary_failed,strictWarningFaces=strict_warning,ordinaryClearDoesNotRequireStrictUpgrade=True,visualContextOnly=i in [108,113],conditionalPositiveDimensionalContactPath=paths['conditionalPositiveDimensionalContactPaths'].get(i),independentRootQualified=False,sourceRoleAccepted=False,physicalAccepted=False))
  assert len(roles[2]['strictWarningFaces'])==25 and not roles[2]['ordinaryFailedFaces']
  result[key]=dict(complete118BodyRoles=roles,exactSavedPositiveDimensionalGraph=paths,allProperInteriorCrossingFlagsRetained=[j for j,r in enumerate(contacts)if r['bothRelativeInteriorSurfaceCrossing']],sourceOriginalBodyLabelsForOtherArithmeticAreProvenanceOnly=True)
 common=set.intersection(*(set(x['exactSavedPositiveDimensionalGraph']['conditionalPositiveDimensionalContactPaths'])for x in result.values()))
 return dict(contract='west-wing-remaining-bodies-existing-positive-dimensional-contact-context-v2',sourceOnly=True,uid=UID,sourceSHA256=SOURCE,allFourStreamBindings=streams,distinctConditionalTypedBodies=result,commonConditionalPositiveDimensionalReachableBodies=sorted(common),all118BodiesRetained=True,remaining117ObligationsNotDischarged=True,visual108113NoRootOrBridge=True,literal113PointOnlyNegativeRetained=True,sourceFacet154SegmentOnly=True,actualIndependentGroundRootQualified=False,bodySupportAccepted=False,physicalAccepted=False,installationApproved=False,requires='Existing unchanged-original-ordinary-ground-root-contact-graph-v1 positive-dimensional adjacency reused; body0 candidate supplies no accepted root. Require source-bound actual root qualification and complete current identity/foreign/native/foundation/water/runtime/browser gates. Proper-interior flags retained without new categorical exclusion or engineering/solid claim. Visual interfaces remain separate and never bridge.')
