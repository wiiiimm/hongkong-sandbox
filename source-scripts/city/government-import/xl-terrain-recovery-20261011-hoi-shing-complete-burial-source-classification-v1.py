"""All 510 raw source-side burial findings: geometry/context, not a role.

Complete original roofs/floors/bodies and exact finite negative witnesses stay.
Positive vertex exposure plus a negative point is not an independently proved
grade interface; roof reachability is not intentional basement/function credit.
Explicit undeployed derived terrain; no current/host/root acceptance.
"""
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction as F
import importlib.util
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-hoi-shing-complete-burial-source-classification-v1';DOC=BASE/BATCH
FINITE=BASE/'xl-terrain-recovery-20261011-hoi-shing-derived-ground-complete-original-finite-v2'
GRAPH=BASE/'xl-terrain-recovery-20261011-hoi-shing-complete-original-edge-contact-graph-v1'
PROBE=BASE/'government-xl-terrain-recovery-hoi-shing-two-original-current-probe-v1-20261011'
RIM=BASE/'xl-terrain-recovery-20261011-hoi-shing-derived-ground-original-rim-graph-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder in [FINITE,GRAPH,PROBE,RIM]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[folder.name]=r;refs.append(ref(folder/'result.json'))
 def bound(folder,p):assert ref(p)in receipts[folder.name]['evidenceRefs'];refs.append(ref(p));return read(p)
 finite=bound(FINITE,FINITE/'diagnostic.json.gz');graph=bound(GRAPH,GRAPH/'diagnostic.json.gz');selection=bound(PROBE,PROBE/'selection.json.gz');rim=bound(RIM,RIM/'diagnostic.json.gz');world=[]
 for row in selection['rows']:
  p=ROOT/row['candidate']['path'];assert ref(p)['sha256']==row['sourceSHA256'];world.append(decode_original_world_triangles(p.read_bytes()));refs.append(ref(p))
 joined=np.concatenate(world);assert joined.shape==(19374,3,3)and digest(joined.tobytes())==graph['binding']['completeOriginalWorldSHA256'];tri=world[1]
 data=finite['rows'][1];assert data['uid']==selection['rows'][1]['uid']=='landsd/318830:0'and data['completeOriginalWorldSHA256']==digest(tri.tobytes())and tri.shape==(5533,3,3)
 contexts=data['completeAllOriginalFacetContexts'];proofs=data['allFaces'];assert len(contexts)==len(proofs)==len(tri)and [r['sourceFace']for r in contexts]==list(range(len(tri)))
 affected=data['unprovedOriginalFaces'];assert len(affected)==510 and affected==[r['sourceFace']for r in proofs if not r['completeOriginalBoundProved']]
 normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);ratio=np.divide(normal[:,1],length,out=np.zeros(len(tri)),where=length>0)
 walls={int(i)for i in np.flatnonzero((length>0)&(np.abs(ratio)<=.25))};roofs={i for i,c in enumerate(contexts)if length[i]>0 and ratio[i]>.25 and c['groundProjectionCovered']is True and F(c['exactCertifiedLowerClearanceM'])>=F(-1,2)}
 assert not any(ratio[i]>.25 for i in affected)
 eligible=walls|roofs;edgefaces=defaultdict(list);adj={i:set()for i in eligible}
 for i in sorted(eligible):
  for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):edgefaces[tuple(sorted((tuple(a),tuple(b))))].append(i)
 for fs in edgefaces.values():
  for i in fs:adj[i].update(j for j in fs if j!=i)
 parent={i:None for i in roofs};todo=deque(sorted(roofs))
 while todo:
  i=todo.popleft()
  for j in sorted(adj[i]):
   if j in walls and j not in parent:parent[j]=i;todo.append(j)
 owner={};bodies=[]
 for k,component in enumerate(graph['components']):
  if component['actorUID']!='landsd/318830:0':continue
  ids=[fi-13841 for fi in component['globalOriginalFaces']];assert all(0<=i<len(tri)for i in ids)
  for i in ids:assert i not in owner;owner[i]=k
  if not set(ids)&set(affected):continue
  original_edges=defaultdict(list)
  for i in ids:
   for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):original_edges[tuple(sorted((tuple(a),tuple(b))))].append(dict(originalFace=i,directedOriginalEdge=[a.tolist(),b.tolist()]))
  bodies.append(dict(originalBody=k,completeOriginalFaces=ids,completeOriginalBodyWorldSHA256=digest(tri[ids].tobytes()),completeOriginalBounds=[tri[ids].min((0,1)).tolist(),tri[ids].max((0,1)).tolist()],completeOriginalEdgeIncidences=[dict(edge=list(map(list,e)),allOriginalIncidences=fs)for e,fs in sorted(original_edges.items())],rawOriginalBoundaryEdgeCount=sum(len(fs)==1 for fs in original_edges.values()),rawOriginalNonmanifoldEdgeCount=sum(len(fs)>2 for fs in original_edges.values()),closedSolidNotCertified=True,completeUpwardRoofFaces=[i for i in ids if length[i]>0 and ratio[i]>.25],completeDownwardFloorFaces=[i for i in ids if length[i]>0 and ratio[i]<-.25],completeExistingClassifierWallFaces=[i for i in ids if i in walls],allExactHorizontalOriginalFaces=[i for i in ids if tri[i,:,1].min()==tri[i,:,1].max()],completeStrictClearRoofFaces=[i for i in ids if i in roofs],historicalSampledSourceOnlyRimReached=k in rim['sourceOnlyDerivedGroundReachedBodies'],sourceFunctionOrBasementRoleInferred=False))
 records=[]
 for i in affected:
  ctx=contexts[i];paired=proofs[i]['pairedExactOriginalFiniteBound'];assert paired is not None and paired['sourceFaceSHA256']==digest(tri[i].tobytes())and paired['groundProjectionCovered']is True
  witness=[]
  for piece in paired['allExactFiniteSourceGroundPieces']:
   ordinary=piece.get('priorOrdinaryPrismProofVerbatim')
   if ordinary:
    for v in ordinary.get('allExactSourcePrismIntersectionVertices',[]):
     if F(v['exactGapM'])<0:
      point=v['exactOriginalSourcePoint'];assert F(point[1])-F(v['exactFiniteGroundHeightM'])==F(v['exactGapM']);witness.append(dict(originalSelectedDerivedGroundFace=piece['originalGroundFace'],exactSourcePoint=point,exactGroundHeightM=v['exactFiniteGroundHeightM'],exactGapM=v['exactGapM']))
   if 'exactCompleteFiniteColumnProof'in piece:
    for v in piece['exactCompleteFiniteColumnProof']['allExactBasicFeasibleColumnVertices']:
     if F(v['exactGapM'])<0:
      assert F(v['exactSourcePoint'][1])-F(v['exactGroundPoint'][1])==F(v['exactGapM']);witness.append(dict(originalSelectedDerivedGroundFace=piece['originalGroundFace'],exactSourcePoint=v['exactSourcePoint'],exactGroundPoint=v['exactGroundPoint'],exactGapM=v['exactGapM']))
  assert witness and min(F(v['exactGapM'])for v in witness)==F(ctx['exactCertifiedLowerClearanceM'])
  path=[i]
  if i in walls:
   while path[-1]in parent and parent[path[-1]]is not None:path.append(parent[path[-1]])
  records.append(dict(sourceFace=i,globalOriginalFace=i+13841,originalBody=owner[i],completeOriginalFacetVertices=tri[i].tolist(),originalNormal=normal[i].tolist(),normalizedNormalY=float(ratio[i]),existingClassifier='wall'if i in walls else'downward',completeFiniteContextVerbatim=ctx,actualFiniteNegativePointWitnesses=witness,hasNegativeFinitePointAndPositiveOriginalVertexEvidence=ctx['maximumObservedGapM']>0,originalSharedFullEdgeWallRoofPath=path,sharedFullEdgePathEndsAtStrictClearRoof=path[-1]in roofs,independentGradeInterfaceStillRequired=True,hostQualification=False,roleAssigned=False))
 refs.extend(ref(HERE/n)for n in ['exact_packed_world_geometry_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py']);assert all(ref(ROOT/r['path'])==r for r in refs)
 out=dict(uids=[r['uid']for r in selection['rows']],complete19374OriginalWorldSHA256=digest(joined.tobytes()),completeP5533OriginalFaces=True,all510RawClearanceNegativesPreserved=True,allAffectedOriginalBodyRoofFloorInventories=bodies,all510OriginalFacetRecords=records,sourceOnly=True,explicitUndeployedDerivedGroundSHA256=data['completeUndeployedDerivedGroundSHA256'],currentDrawnGround=False,sourceFunctionOrBasementRoleInferred=False,hostQualification=False,roleAssigned=False,structuralRootOrBridgeCredit=False,newlyInstalled=0,evidenceRefs=refs)
 save(DOC/'diagnostic.json.gz',out);spec=importlib.util.spec_from_file_location('freeze_hoi_burial_classification',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'all510-original-wall-floor-burial-evidence-and-source-roof-path-classification-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=out['uids'],sourceOnly=True,currentAcceptance=False,all510RawClearanceNegativesPreserved=True,roleAssigned=False,structuralRootOrBridgeCredit=False,newlyInstalled=0))
if __name__=='__main__':main()
