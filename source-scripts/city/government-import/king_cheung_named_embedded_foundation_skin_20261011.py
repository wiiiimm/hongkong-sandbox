"""Named complete original foundation skin34, with clear body23 and genuine grade.

The buried leaf799 is retained as an interpreted original foundation surface.
It supplies no exposed bridge. No closed solid, invented cap or load claim.
"""
from collections import deque,defaultdict
from fractions import Fraction as F
import hashlib,json
import numpy as np
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from original_bound_facet_wall_context_v3_20261010 import contexts
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_paths
UID='landsd/95691:0'
SOURCE='daad7e84a632e97cd7af9c354dd3d6c122e2e1afc0afdc751f752a0f909cd119'
IDS=list(range(555,813))+[2779,2780,2795,2796]
FINITE_ROWS={'actualLiteral': '76d166c878fc3fdf05cb351439305bd6536602458a5d63ddda54f615a218b429', 'explicitBalancedF32ModelMatrix': '4a47758fda4de2689f3e6175efe78da0cb433987c4e88e837e54263a84393034', 'explicitLeftAssociatedF32ModelMatrix': '4a47758fda4de2689f3e6175efe78da0cb433987c4e88e837e54263a84393034', 'providerOriginal': '4a47758fda4de2689f3e6175efe78da0cb433987c4e88e837e54263a84393034'}
WORLD_SHA='534046e403d3eb70a384e56be5294b294e5469e48aea57b9e3edd8e5d4028a78'
LITERAL_SHA='c2ce44c1121a357256bfca027cf262b5d89a494ae3d67f6e50ba8bc9fc43fd12'
GROUND_SHA='f8e4a0fd261497235a48c090f3fe73e6bc5b112d6f2bf2e3dac71a6385d92049'
ROLE='King Cheung original complete262 embedded foundation perimeter skin34'
def sha(a):return hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest()
def canonical(a):return hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def verify(world,ground,finite_rows,*,mode,interpreted_role,expected_binding,current_binding):
 w=np.asarray(world,dtype='<f8');g=np.asarray(ground,dtype='<f8')
 assert w.shape==(18742,3,3) and np.isfinite(w).all() and g.shape==(4,3,3) and np.isfinite(g).all()
 assert expected_binding==current_binding and interpreted_role==ROLE
 assert mode in FINITE_ROWS and sha(w)==(LITERAL_SHA if mode=='actualLiteral'else WORLD_SHA) and sha(g)==GROUND_SHA
 assert canonical(finite_rows)==FINITE_ROWS[mode]
 assert current_binding['uid']==UID and current_binding['sourceSHA256']==SOURCE
 assert current_binding['mode']==mode and current_binding['completeWorldSHA256']==sha(w)
 assert current_binding['completeGroundSHA256']==sha(g) and current_binding['completeFiniteRowsSHA256']==canonical(finite_rows)
 assert set(g[:,:,1].reshape(-1))=={14.0} and len(finite_rows)==18742 and [r['sourceFace']for r in finite_rows]==list(range(18742))
 topology=census(w,list(range(18742)));parts=topology['sharedEdgeConnectedComponents']
 assert len(parts)==908 and parts[34]==IDS and len(parts[23])==1899 and topology['exactNonrenderingOriginalFaces']==[1149]
 host=parts[23];ids=sorted(IDS+host);index={f:i for i,f in enumerate(ids)};t=w[ids]
 normals=np.cross(w[IDS,1]-w[IDS,0],w[IDS,2]-w[IDS,0]);assert np.all(normals[:,1]==0) and np.all(np.any(normals!=0,axis=1))
 records=[finite_rows[i]['groundComparisons']['currentDrawn']for i in ids]
 adapted=[dict(sourceFace=i,priorCoarseBoundProofVerbatim=dict(sourceFace=i,completeOriginal=r['coarse']),pairedExactOriginalFiniteBound=r['paired'],completeOriginalBoundProved=r['completeFiniteOrdinaryBoundProved'])for i,r in enumerate(records)]
 binding=dict(completeOriginalWorldTrianglesSHA256=sha(t),completeDrawnGroundSHA256=sha(g),completeFiniteFacetProofRowsSHA256=canonical(adapted))
 ctx=contexts(t,g,adapted,expected_binding=binding,current_binding=binding)
 raw=[ids[i]for i,r in enumerate(records)if not r['completeFiniteOrdinaryBoundProved']];assert raw==list(range(798,805))
 for i in host:assert records[index[i]]['completeFiniteOrdinaryBoundProved'] and F(ctx[index[i]]['exactCertifiedLowerClearanceM'])>0
 grade=exact_finite_contacts(w,IDS,g,range(4),maximum_pairs=len(IDS)*4)
 assert grade['allPairsExamined'] and grade['sourceFacesOmitted']==0
 positives=[c for c in grade['contacts']if c['dimension']==1 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
 assert len(positives)==240 and len({c['sourceFaceA']for c in positives})==238
 interfaces=exact_finite_contacts(w,IDS,w,host,maximum_pairs=len(IDS)*len(host));assert interfaces['allPairsExamined']and interfaces['sourceFacesOmitted']==0
 pairs=sorted({tuple(sorted((index[c['sourceFaceA']],index[c['sourceFaceB']])))for c in interfaces['contacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2})
 assert pairs
 for c in interfaces['contacts']:
  if c['dimension']>0:assert all(F(p[1])>14 for p in c['exactPoints'])
 pathbinding=dict(completeOriginalWorldTrianglesSHA256=sha(t),completeCurrentFacetContextsSHA256=canonical(ctx),exactOriginalContactListSHA256=canonical([list(p)for p in pairs]))
 paths=cap_paths(t,ctx,[list(p)for p in pairs],expected_binding=pathbinding,current_binding=pathbinding)
 assert paths['allAffectedHavePaths'] and {ids[p['sourceFace']]for p in paths['paths']}==set(raw)
 assert [ids[i]for i in paths['rawExposureFailures']]==[799]
 edges=defaultdict(list)
 for i in IDS:
  for a,b in zip(w[i],np.roll(w[i],-1,axis=0)):
   if tuple(a)!=tuple(b):edges[tuple(sorted((tuple(a),tuple(b))))].append(i)
 adjacency={i:set()for i in IDS}
 for members in edges.values():
  for i in members:adjacency[i].update(set(members)-{i})
 assert adjacency[799]=={798} and max(w[799,:,1])<14 and ctx[index[799]]['maximumObservedGapM']<0
 # The buried leaf remains inventoried, but is excluded from all exposed paths.
 roots={c['sourceFaceA']for c in positives};seen=set(roots);queue=deque(sorted(roots))
 while queue:
  for j in sorted(adjacency[queue.popleft()]-seen):seen.add(j);queue.append(j)
 assert seen==set(IDS)
 return dict(contract='King-Cheung-named-complete262-foundation-skin-and-clear-body23-v1',mode=mode,binding=current_binding,
  completeFoundationOriginalFaces=IDS,completeStrictlyClearHostOriginalFaces=host,complete2161FacetContexts=ctx,
  completeActualFoundationGradeContacts=grade,completeFoundationToClearBodyContacts=interfaces,completeStrictClearCapPaths=paths,
  sourceBackedFoundationLeaf799=dict(completeOriginalFace=w[799].tolist(),soleSharedEdgeNeighbour=798,rawWhollyBuriedExposureNegativeRetained=True,exposedBridgeCredit=False),
  completeFoundationSharedEdgeTopology=census(w,IDS),genuineGroundedFoundationRoleProposed=True,
  strictClearHostBody23ConnectedToGrade=True,originalGroundingProposedOnly=True,closedSolidCertified=False,loadBearingClaim=False,
  syntheticCapCreated=False,sourceGeometryChanges=0,terrainGeometryChanges=0,fullCurrentAcceptance=False,installationApproved=False)
