"""Twenty-four exact Elements source parts, visual proposals only.

The mounting boundary is derived from the complete original topology BEFORE
looking at host proximity. A qualified nonvisual host never becomes qualified
through this layer. Free edges and unproved interior proximity stay explicit.
The adapter must independently pin the source assets and completed numerical
receipts; expected_binding is their immutable canonical per-part binding.
"""
from collections import defaultdict
from fractions import Fraction as F
import hashlib,json
import numpy as np
from exact_original_shared_edge_component_census_v2_20261011 import census

MODES=('providerOriginal','actualLiteral','explicitLeftFloat32','explicitBalancedFloat32')
SOURCE_SHA={
 'landsd/204145:0':'7015f9c5489eb757589cbd5876955dba3f8ffd99187d42bda8661e857493dce3',
 'landsd/204143:0':'1909183cb05d9e94ae441fb9b391b5718883ccb89f5bf81a976b2aeff024f5ce'}
NAMED_SOURCE_PART_FACES={68:[1886],71:[2339,2340,2341],72:[2357,2358,2359],80:[2766,2767,2768,2769,2770,2771,2772,2773,2774],764:[14387,14388,14389],765:[14390,14391,14392],766:[14456,14457,14458],769:[14494,14495,14496],913:[21026,22194,22195,22196],920:[21829],922:[22108,22109,22110,22111,22112,22113,22114],500:[9080,9081],501:[9082,9083],977:[23715,23716],979:[23719,23720],980:[23721,23722],982:[23725,23726],997:[23807,23808],507:[11331,11332,11333,11334,11335,11336],509:[11367,11368,11369,11370],511:[11373,11374,11375,11376],513:[11379,11380,11381,11382],515:[11385,11386,11387,11388],934:[23486,23487,23488,23489,23490,23491]}
WHOLE={68,71,72,80,764,765,766,769,913,920,922}
U_FREE_AXIS={500:(0,1),501:(0,-1),977:(1,1),979:(1,1),980:(1,1),982:(1,1),997:(1,1)}
FOLDED_TERMINALS={507,509,511,513,515}

def canonical(value):
 return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def world_sha(world):return hashlib.sha256(np.asarray(world,np.float64).tobytes()).hexdigest()
def key(edge):return tuple(sorted(tuple(float(v)for v in p)for p in edge))
def edges(world,faces):
 rows=defaultdict(list)
 for f in faces:
  tri=world[f]
  for a,b in zip(tri,np.roll(tri,-1,axis=0)):
   assert tuple(a)!=tuple(b),'Collapsed original edge'
   rows[key([a,b])].append(f)
 assert all(len(fs)in(1,2)for fs in rows.values()),'Unapproved nonmanifold topology'
 return rows,{e for e,fs in rows.items()if len(fs)==1}
def connected_path(edge_set,vertices):
 adj={v:set()for v in vertices}
 for a,b in edge_set:
  assert a in adj and b in adj;adj[a].add(b);adj[b].add(a)
 assert len(edge_set)==len(vertices)-1 and sorted(map(len,adj.values())).count(1)==2
 assert all(1<=len(v)<=2 for v in adj.values())
 seen={min(vertices)};todo=list(seen)
 while todo:
  for v in adj[todo.pop()]:
   if v not in seen:seen.add(v);todo.append(v)
 assert seen==vertices,'Incomplete mounting chain'
 return {v for v,n in adj.items()if len(n)==1}

def original_mount(part,world,faces):
 """Independent source geometry, no supplied proximity values consulted."""
 _,boundary=edges(world,faces)
 if part in WHOLE:return dict(role='whole-original-near-host-visual-surface',mount=boundary,free=set(),lower=set(),terminals=set())
 if part in U_FREE_AXIS:
  assert len(faces)==2 and len(boundary)==4
  vertices={v for e in boundary for v in e};assert len(vertices)==4
  degree=defaultdict(int)
  for e in boundary:
   for v in e:degree[v]+=1
  assert set(degree.values())=={2}
  axis,sign=U_FREE_AXIS[part]
  score={e:sign*sum(F(v[axis])for v in e)/2 for e in boundary};best=max(score.values())
  free={e for e,s in score.items()if s==best};assert len(free)==1,'Named free source edge is not unique'
  mount=boundary-free;connected_path(mount,vertices)
  return dict(role='original-three-side-U-mounted-visual-panel',mount=mount,free=free,lower=set(),terminals=set())
 assert part in FOLDED_TERMINALS|{934}
 vertices={v for e in boundary for v in e};assert len(vertices)==(8 if part==934 else 6)
 # The authored upright strip has two complete boundary chains separated in Y.
 # Rank separation accounts slanted packed heights, without a numerical band.
 ordered=sorted(vertices,key=lambda p:(F(p[1]),p));n=len(vertices)//2
 low=set(ordered[:n]);high=set(ordered[n:]);assert max(v[1]for v in low)<min(v[1]for v in high)
 lower={e for e in boundary if set(e)<=low};upper={e for e in boundary if set(e)<=high}
 lowends=connected_path(lower,low);highends=connected_path(upper,high)
 terminals=boundary-lower-upper
 assert len(terminals)==2 and {v for e in terminals for v in e}==lowends|highends
 assert all(len(set(e)&low)==len(set(e)&high)==1 for e in terminals)
 assert len(boundary)==2*n and len(lower)==len(upper)==n-1
 mount=lower|terminals if part in FOLDED_TERMINALS else lower
 return dict(role='original-lower-chain-and-terminal-mounted-folded-visual-sheet'if part in FOLDED_TERMINALS else 'original-complete-lower-backbone-mounted-open-folded-visual-sheet',mount=mount,free=boundary-mount,lower=lower,terminals=terminals)

def binding(part,uid,source_sha,worlds,contexts,qualified_hosts):
 return dict(part=part,uid=uid,sourceSHA256=source_sha,originalFaceIds=NAMED_SOURCE_PART_FACES.get(part),completeOwnedWorldSHA256={m:world_sha(worlds[m])for m in MODES},completedPartContextSHA256={m:canonical(contexts[m])for m in MODES},qualifiedNonvisualHostFacesSHA256={m:canonical(sorted(qualified_hosts[m]))for m in MODES})

def verify(part,uid,source_sha,worlds,contexts,qualified_hosts,*,expected_binding):
 assert part in NAMED_SOURCE_PART_FACES,'Not a named original source part'
 faces=NAMED_SOURCE_PART_FACES[part];actor='landsd/204145:0'if max(faces)<12129 else 'landsd/204143:0'
 assert uid==actor and source_sha==SOURCE_SHA[actor]
 assert set(worlds)==set(contexts)==set(qualified_hosts)==set(MODES)
 arrays={m:np.asarray(worlds[m],np.float64)for m in MODES}
 assert all(w.shape==(23809,3,3)and np.isfinite(w).all()for w in arrays.values())
 bound=binding(part,uid,source_sha,arrays,contexts,qualified_hosts)
 assert bound==expected_binding,'Frozen source/current/host numerical binding changed'
 source=arrays['providerOriginal'];mount=original_mount(part,source,faces);_,source_boundary=edges(source,faces);results=[]
 for mode in MODES:
  w=arrays[mode];ctx=contexts[mode];a=ctx['association'];f=ctx['allCompletePartFiniteFaces']
  assert a['originalBody']==part and a['completeOriginalFaceIds']==faces
  assert ctx['completeOwnedWorldSHA256']==world_sha(w)
  c=census(w,faces);assert c['sharedEdgeConnectedComponents']==[faces]and not c['exactNonrenderingOriginalFaces']and c['nonmanifoldEdges']==0 and c['twoFaceOrientationConflicts']==0
  _,boundary=edges(w,faces)
  correspondence={}
  for orig,actual in zip(source[faces].reshape(-1,3),w[faces].reshape(-1,3)):
   o=tuple(orig);v=tuple(actual)
   if o in correspondence:assert correspondence[o]==v,'Original shared vertex split'
   correspondence[o]=v
  assert len(set(correspondence.values()))==len(correspondence),'Nonzero source vertices collapsed'
  mapped={key([correspondence[x]for x in e])for e in source_boundary};assert mapped==boundary
  hs=a['completeHostSelection'];selected=set(hs['selectedGlobalHostFaces']);qualified=set(qualified_hosts[mode])
  assert selected and selected<=qualified and not selected&set(faces)
  assert all((h<12129)==(actor=='landsd/204145:0')for h in selected)
  assert hs['exactFixedBandM']==.1 and hs['allSelectedHostsBelongToNonvisualQualifiedPaths']is True
  assert hs['actualSelectedHostWorldSHA256']==world_sha(w[sorted(selected)])
  assert hs['completeQualifiedSameActorHostFaces']==sorted(qualified)
  offset=0 if actor=='landsd/204145:0'else 12129
  assert [z['sourceFace']+offset for z in f]==faces
  assert all(z['closedProjectionCovered']is True and z['existingOrdinaryClearanceBoundProved']is True and z['strictlyExposedWholeFacet']is True for z in f)
  ep={key(e['completeActualBoundaryEdge']):e for e in a['allActualIncidenceOneBoundaryEdgeProofs']}
  assert set(ep)==boundary
  required={key([correspondence[x]for x in e])for e in mount['mount']}
  assert all(ep[e]['wholeEdgeWithinExistingFiniteHostBand']is True and ep[e]['actualSubsetWholeEdgeHostProofVerbatim']['verifiedCompleteOriginalEdgeFiniteFacadeBand']is True for e in required),'Incomplete named mounting chain'
  if part in WHOLE:
   fp=a['allActualFacetProofs'];assert [z['globalOriginalFace']for z in fp]==faces
   assert all(z['wholeFacetWithinExistingFiniteHostBand']is True and z['completeActualFacetSHA256']==world_sha(w[[z['globalOriginalFace']]])for z in fp)
  results.append(dict(mode=mode,completePartFiniteClearance=True,completeNamedMountEdgeCount=len(required),allRequiredMountEdgesWithinUnchangedBand=True,unqualifiedFreeEdgeFindings=[ep[e]for e in sorted(boundary-required)],wholeInteriorBandPositive=a['allFacetsWithinFixedBand']))
 return dict(contract='elements24-named-original-mounted-visual-source-proposal-v1',binding=bound,originalBody=part,uid=uid,completeOriginalFaces=faces,namedSourceVisualInterpretation=mount['role'],allFourStreamProofs=results,conditionalSourceVisualRoleProposal=True,sourceFunctionInferred=False,wholeInteriorBandNotInvented=True,freeOriginalEdgesPreserved=True,structuralRootCredit=False,structuralBridgeCredit=False,visualPartsNeverQualifyHosts=True,nativeReacceptance=False,currentAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0)
