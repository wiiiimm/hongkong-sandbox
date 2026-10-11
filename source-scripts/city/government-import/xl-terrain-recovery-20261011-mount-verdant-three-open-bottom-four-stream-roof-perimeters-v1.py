"""Diagnostic only: three complete authored open bottoms on original podium roofs.

No floor is generated. Every original lower edge is tested continuously against
the finite upper envelope of ALL upward faces in the genuine 576-face podium
main body. Four frozen arithmetic representations stay separate. This supplies
no current availability, structural root, bridge or accepted component role.
"""
from pathlib import Path
from collections import defaultdict, Counter
import importlib.util, uuid, json
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-mount-verdant-three-open-bottom-four-stream-roof-perimeters-v1'
DOC=BASE/BATCH
CAPTURE=BASE/'xl-terrain-recovery-20261011-mount-verdant-two-current-render-attribute-capture-v1'
LONG=BASE/'xl-terrain-recovery-20261011-mount-verdant-three-long-original-backing-facets-v1'
GRADE=BASE/'xl-terrain-recovery-20261011-mount-verdant-podium-grade-cap-lower-loops-v2'
RIM=BASE/'xl-terrain-recovery-20261011-mount-verdant-three-strips-ordinary-rim-source-diagnostic-v1'
FINITE=BASE/'xl-terrain-recovery-20261011-mount-verdant-tower-authentic-four-stream-finite-v1'
def ref(p): return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists(); refs=[ref(Path(__file__))]; receipts={}
 for folder in [CAPTURE,LONG,GRADE,RIM,FINITE]:
  receipt=read(folder/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY'); assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  receipts[folder.name]=receipt; refs.append(ref(folder/'result.json'))
 def bound(folder,name):
  p=folder/name; assert ref(p) in receipts[folder.name]['evidenceRefs']; refs.append(ref(p)); return read(p)
 source=bound(CAPTURE,'literal-source-inputs.json.gz'); actual=bound(CAPTURE,'actual-render-attributes.json.gz')
 long=bound(LONG,'diagnostic.json.gz'); grade=bound(GRADE,'diagnostic.json.gz'); bound(RIM,'diagnostic.json.gz'); bound(FINITE,'diagnostic.json.gz')
 uids=['landsd/261717:0','landsd/75782:0']; assert [r['uid'] for r in source['rows']]==[r['uid'] for r in actual['rows']]==uids
 modes=['untouched-provider-original','captured-literal','explicit-left-associated-Float32','explicit-balanced-Float32']; fields=['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']; worlds=[[],[],[],[]]
 for row,record,count in zip(source['rows'],actual['rows'],[14938,641]):
  asset=ROOT/row['path']; assert digest(asset.read_bytes())==row['entry']['sha256']==record['sourceSHA256']; refs.append(ref(asset)); tri=decode_original_world_triangles(asset.read_bytes()); index=np.asarray(record['completeOriginalIndex'],np.uint32).reshape(-1,3); assert tri.shape==(count,3,3) and len(index)==count; worlds[0].append(tri)
  for k,field in enumerate(fields,1):
   position=np.asarray(record[field],float).reshape(-1,3); assert np.isfinite(position).all() and np.all(index<len(position)); worlds[k].append(position[index])
 worlds=[np.concatenate(parts) for parts in worlds]; assert all(w.shape==(15579,3,3) for w in worlds)
 mainfaces=grade['completeMainBody576OriginalFaces']; assert len(mainfaces)==576 and census(worlds[0][14938:],list(range(641)))['sharedEdgeConnectedComponents'][0]==mainfaces
 assert digest(worlds[0][14938:].tobytes())==grade['completeOriginalWorldSHA256']; bodyrows=long['all30OriginalLongStripFaces']; assert [r['originalBody'] for r in bodyrows]==[311,312,313]
 helpernames=['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_segment_surface_contact_band_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py']; refs.extend(ref(HERE/n) for n in helpernames)
 claim=reservations.claim('mount-three-open-bottom-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600); assert claim['ok']; lease=claim['reservation']; rows=[]
 try:
  for mode,world in zip(modes,worlds):
   podium=world[14938:]; normal=np.cross(podium[:,1]-podium[:,0],podium[:,2]-podium[:,0]); length=np.linalg.norm(normal,axis=1); ratio=np.divide(normal[:,1],length,out=np.zeros(len(podium)),where=length!=0)
   roofs=[i for i in mainfaces if ratio[i]>.25]; assert roofs; rooftri=podium[roofs]
   for body in bodyrows:
    ids=body['all10CompleteOriginalFaces']; assert len(ids)==10; tri=world[ids]; inv=census(world,ids); assert len(inv['sharedEdgeConnectedComponents'])==1 and not inv['exactNonrenderingOriginalFaces']; bottom=float(tri[:,:,1].min()); top=float(tri[:,:,1].max()); edges=defaultdict(list)
    for fi in ids:
     for a,b in zip(world[fi],np.roll(world[fi],-1,axis=0)):
      if tuple(a)!=tuple(b): edges[tuple(sorted((tuple(a),tuple(b))))].append(fi)
    lower=sorted(e for e,m in edges.items() if len(m)==1 and e[0][1]==e[1][1]==bottom); boundary=sorted(e for e,m in edges.items() if len(m)==1); degree=Counter(v for e in lower for v in e)
    assert lower==boundary and len(lower)==4 and len(degree)==4 and all(n==2 for n in degree.values())
    n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); size=np.linalg.norm(n,axis=1); r=n[:,1]/size; caps=[ids[i] for i in range(10) if np.all(tri[i,:,1]==top) and r[i]>.25]; bottomfacets=[ids[i] for i in range(10) if np.all(tri[i,:,1]==bottom)]
    assert len(caps)==2 and not bottomfacets and all(r[i]==0 for i in range(10) if ids[i] not in caps)
    proofs=[]
    for edge in lower:
     proof=verify_contact_segment(np.asarray(edge),rooftri); proof['completeOriginalSurfacePieces']=[{**p,'originalPodiumMainBodyRoofFace':roofs[p['originalSurfaceFace']]} for p in proof['completeOriginalSurfacePieces']]; proofs.append(dict(completeOriginalLowerEdge=[list(v) for v in edge],continuousUpperRoofBand=proof)); assert reservations.heartbeat(lease)['ok']
    rows.append(dict(mode=mode,originalBody=body['originalBody'],completeAll10OriginalGlobalFaces=ids,completeBodyArithmeticSHA256=digest(tri.tobytes()),completeBodyEdgeCensus=inv,completeOriginalTopCapFaces=caps,completeOriginalBottomFacetIDs=bottomfacets,completeAuthoredOpenBottomBoundary=[[list(v) for v in e] for e in lower],completeAllBodyEdges=[dict(edge=[list(v) for v in e],incidentOriginalFaces=m) for e,m in sorted(edges.items())],complete576HostMainBodyLocalFaces=mainfaces,completeAllMainBodyUpwardRoofFaces=roofs,completeRoofArithmeticSHA256=digest(rooftri.tobytes()),allFourContinuousLowerEdgeProofs=proofs,conditionalEntireOpenBottomWithinExistingBand=all(p['continuousUpperRoofBand']['verifiedCompleteOriginalEdgeContactBand'] for p in proofs),priorFacadeLoopAndOrdinaryGroundOnlyNegativesPreserved=True,mainPodiumGroundingAndAllCreditedRoofsStillRequireIndependentQualification=True,sourceOnly=True,structuralRootOrBridgeCredit=False))
  assert reservations.heartbeat(lease)['ok'] and all(ref(ROOT/r['path'])==r for r in refs)
  summary=[dict(mode=mode,positiveBodies=[r['originalBody'] for r in rows if r['mode']==mode and r['conditionalEntireOpenBottomWithinExistingBand']],negativeBodies=[r['originalBody'] for r in rows if r['mode']==mode and not r['conditionalEntireOpenBottomWithinExistingBand']]) for mode in modes]
  out=dict(uids=uids,allThreeCompleteOpenBottomsEveryFourStreams=rows,summary=summary,frozenCapturedManifestSHA256=source['currentManifest']['sha256'],sourceGeometryChanges=0,generatedFloorFaces=0,sourceOnly=True,currentPodiumAvailability=False,hostGroundingQualified=False,structuralRootOrBridgeCredit=False,authoredRoleAccepted=False,freshCurrentAcceptance=False,newlyInstalled=0,evidenceRefs=refs); save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); m.freeze(BATCH,'mount-three-authored-open-bottom-four-stream-complete-upper-roof-band-diagnostic-v1',[ROOT/r['path'] for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=uids,summary=summary,sourceOnly=True,currentAcceptance=False,newlyInstalled=0)); print(json.dumps(summary),flush=True)
 finally: assert reservations.release(lease)['ok']
if __name__=='__main__': main()
