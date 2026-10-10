"""Frozen-baseline source-only Parkview owned edge census/carrier path diagnosis.

The native170 cap has bounded authentic-TIN grade paths, not current acceptance.
No other legacy native component may bridge an owned path. All exact zero-area
faces stay accounted; historical vertex grouping alone never grants support.
"""
from collections import deque
from pathlib import Path
import importlib.util
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census,exact_nonrendering
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-parkview-owned-complete-edge-carrier-paths-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-parkview-block11-complete-original-current-probe-v1-20261010'
GRAPH=BASE/'xl-terrain-recovery-20261010-parkview-block11-complete-original-support-v1'
CAP=BASE/'xl-terrain-recovery-20261011-parkview-bounded-authentic-grade-clear-cap-paths-v1'
EDGE=BASE/'xl-terrain-recovery-20261011-parkview-authentic-carrier-edge-census-v1'
FINITE=BASE/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-complete-conservative-v3'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [GRAPH,CAP,EDGE,FINITE]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  numeric=read(folder/'diagnostic.json.gz')
  if ref(folder/'diagnostic.json.gz')not in receipt['evidenceRefs']:
   assert folder==GRAPH and all(read(folder/'result.json').get(k)==v for k,v in numeric.items()),'Only the historical inline graph receipt may bind its complete numeric value directly'
  refs.extend([ref(folder/'result.json'),ref(folder/'diagnostic.json.gz')])
 g=read(GRAPH/'diagnostic.json.gz');cap=read(CAP/'diagnostic.json.gz');edge=read(EDGE/'diagnostic.json.gz');finite=read(FINITE/'diagnostic.json.gz')
 selected=read(PROBE/'selection.json.gz')['rows'];assert [r['uid']for r in selected]==['landsd/254491:0','landsd/255647:0']
 assets=[ROOT/r['candidate']['path']for r in selected]
 for r,p in zip(selected,assets):assert digest(p.read_bytes())==r['sourceSHA256']
 original=np.concatenate([decode_original_world_triangles(p.read_bytes())for p in assets])
 runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';rt=read(runtimepath)
 assert [r['uid']for r in rt['rows']]==[r['uid']for r in selected]
 literal=np.concatenate([np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in rt['rows']])
 assert original.shape==literal.shape==(73812,3,3)and digest(original.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256']
 owned={i for i,c in enumerate(g['components'])if c['actorUID']=='landsd/255647:0'};assert owned==set(range(285,366))
 assert sum(len(g['components'][i]['globalOriginalFaces'])for i in owned)==10679
 assert sorted(j for i in owned for j in g['components'][i]['globalOriginalFaces'])==list(range(63133,73812))
 allowed=owned|{170};f=next(r for r in finite['rows']if r['uid']=='landsd/255647:0')
 assert f['completeOriginalFaces']==10679 and [r['sourceFace']for r in f['allFaces']]==list(range(10679))
 rows=[]
 for mode,key,t,caprow,er in zip(['providerOriginal','capturedActualLiteral'],['completeOriginal','actualRendered'],[original,literal],cap['rows'],edge['rows']):
  assert digest(t[:63133].tobytes())==er['completeSourceWorldSHA256']
  assert digest(t[63133:].tobytes())==f['completeOriginalWorldSHA256'if key=='completeOriginal'else'completeActualRenderedWorldSHA256']
  assert caprow['strictClearCapFace']==57951 and sum(p['hasExactEligibleSharedEdgePathToStrictCap']for p in caprow['everyGradeWallPath'])==177
  assert set(er['capNonzeroEdgeBodyFaces'])==set(g['components'][170]['globalOriginalFaces']) and len(er['sharedEdgeProof']['sharedEdgeConnectedComponents'])==1
  componentproofs=[];bodies={170:set(er['capNonzeroEdgeBodyFaces'])};splits=[];nonrendering=[]
  for i in sorted(owned):
   faces=g['components'][i]['globalOriginalFaces'];p=census(t,faces);cs=p['sharedEdgeConnectedComponents']
   componentproofs.append(dict(historicalVertexComponent=i,completeOriginalFaces=len(faces),sharedEdgeProof=p))
   if len(cs)!=1:splits.append(dict(component=i,renderableEdgeBodies=len(cs)))
   else:bodies[i]=set(p['completeRenderableFaceIds'])
   for j in set(faces)-set(p['completeRenderableFaceIds']):
    assert exact_nonrendering(original[j])and exact_nonrendering(literal[j])and exact_nonrendering(literal[j].astype(np.float32).astype(np.float64)), 'Nonrendering accounting must hold independently in original/literal/F32'
    nonrendering.append(j)
   for j in faces:
    proof=f['allFaces'][j-63133][key];assert proof['sourceFaceSHA256']==digest(t[j].tobytes())and proof['completeCurrentGroundSHA256']==f['completeGroundSHA256']and proof['groundProjectionCovered']is True and proof['existingOrdinaryClearanceBoundProved']is True
   print(dict(mode=mode,component=i,completeFaces=len(faces),renderableEdgeBodies=len(cs)),flush=True)
  contacts=[];negative=[];adj={i:set()for i in allowed};pairs={}
  for c in g['contactWitnesses']:
   a,b=c['components']
   if a not in allowed or b not in allowed:continue
   fa,fb=c['globalOriginalFaces'];assert fa in g['components'][a]['globalOriginalFaces']and fb in g['components'][b]['globalOriginalFaces']
   points=intersection_points(rational_face(t[fa]),rational_face(t[fb]));positive=len(points)>=2 and fa in bodies.get(a,set())and fb in bodies.get(b,set())
   if 170 in [a,b]:assert set([fa,fb])=={57951,63133}, 'Only the independently clear native cap interface is eligible'
   r=dict(components=[a,b],globalOriginalFaces=[fa,fb],exactContactPoints=[[str(v)for v in p]for p in points],positiveDimensionalNonzeroEdgeBodyInterface=positive)
   (contacts if positive else negative).append(r)
   if positive:adj[a].add(b);adj[b].add(a);pairs[tuple(sorted([a,b]))]=r
  parents={170:None};todo=deque([170])
  while todo:
   a=todo.popleft()
   for b in sorted(adj[a]):
    if b not in parents:parents[b]=a;todo.append(b)
  paths=[dict(child=i,parent=p,exactPositiveInterface=pairs[tuple(sorted([i,p]))])for i,p in sorted(parents.items())if p is not None]
  rows.append(dict(mode=mode,completeCombinedWorldSHA256=digest(t.tobytes()),completeOwnedFaces=10679,completeOwnedHistoricalComponents=81,completeOwnedComponentEdgeCensus=componentproofs,splitOrPureNonrenderingHistoricalComponentsRetained=splits,exactOriginalLiteralF32NonrenderingFacesRetained=sorted(nonrendering),allRestrictedContactRecords=contacts,rawMissingOrPointOnlyContactsRetained=negative,diagnosticCarrier=170,strictClearCap=57951,completeRestrictedParents=parents,completePositiveDimensionalPaths=paths,conditionallyReachedOwnedComponents=sorted(owned&set(parents)),unresolvedOwnedComponents=sorted(owned-set(parents)),allOwnedComponentsHaveBoundedConditionalCarrierPaths=owned<=set(parents),excludedLegacyNativeComponents=sorted(set(range(285))-{170}),carrierGroundRootApproved=False))
  print(dict(mode=mode,owned=81,reached=len(owned&set(parents)),splitComponents=len(splits),exactRestrictedContacts=len(contacts),rejectedContacts=len(negative)),flush=True)
 refs.extend(ref(p)for p in [*assets,runtimepath,PROBE/'selection.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'test_exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_shell_intersections_20261009.py'])
 for r in refs:assert ref(ROOT/r['path'])==r
 result=dict(uids=[r['uid']for r in selected],rows=rows,evidenceRefs=refs,sourceOnly=True,frozenHistoricalBaseline=True,notCurrentDrawnGround=True,terrainProposalRequired=True,addedGroundRoots=[],addedBridges=[],sourceGeometryChanges=0,nativeReacceptance=False,currentAcceptance=False,installationApproved=False,fullAcceptance=False,newlyInstalled=0)
 save(DOC/'diagnostic.json.gz',result);s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-parkview-owned-source-literal-nonzero-edge-restricted-carrier-path-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],sourceOnly=True,nativeReacceptance=False,newlyInstalled=0,conditionalReachedOwnedCounts={r['mode']:len(r['conditionallyReachedOwnedComponents'])for r in rows}))
if __name__=='__main__':main()
