"""Complete 72-face original rooftop-unit lower boundary diagnosis, not acceptance.

All eight open edges and three-incidence geometry stay recorded. Only the six
actual minimum-height boundary edges form the authored lower loop. Upper free
edges are separately measured, never deleted or claimed as footing interfaces.
"""
from collections import defaultdict
from pathlib import Path
import importlib.util
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-parkview-original-roof-unit324-interface-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-parkview-block11-complete-original-current-probe-v1-20261010'
GRAPH=BASE/'xl-terrain-recovery-20261010-parkview-block11-complete-original-support-v1'
PATHS=BASE/'xl-terrain-recovery-20261011-parkview-owned-complete-edge-carrier-paths-v1'
FINITE=BASE/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-complete-conservative-v3'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [PATHS,FINITE]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  assert ref(folder/'diagnostic.json.gz')in r['evidenceRefs'];refs.extend([ref(folder/'result.json'),ref(folder/'diagnostic.json.gz')])
 paths=read(PATHS/'diagnostic.json.gz');g=read(GRAPH/'diagnostic.json.gz');selected=read(PROBE/'selection.json.gz')['rows'];assets=[ROOT/r['candidate']['path']for r in selected]
 for r,p in zip(selected,assets):assert digest(p.read_bytes())==r['sourceSHA256']
 original=np.concatenate([decode_original_world_triangles(p.read_bytes())for p in assets]);runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';rt=read(runtimepath);literal=np.concatenate([np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in rt['rows']]);assert original.shape==literal.shape==(73812,3,3)
 ids=g['components'][324]['globalOriginalFaces'];assert len(ids)==72 and g['components'][324]['actorUID']=='landsd/255647:0';finite=next(r for r in read(FINITE/'diagnostic.json.gz')['rows']if r['uid']=='landsd/255647:0')
 rows=[];renderhost=None
 for mode,key,t,pathrow in zip(['providerOriginal','capturedActualLiteral'],['completeOriginal','actualRendered'],[original,literal],paths['rows']):
  assert digest(t.tobytes())==pathrow['completeCombinedWorldSHA256']and pathrow['unresolvedOwnedComponents']==[324]and 285 in pathrow['conditionallyReachedOwnedComponents']
  assert digest(t[63133:].tobytes())==finite['completeOriginalWorldSHA256'if key=='completeOriginal'else'completeActualRenderedWorldSHA256']
  edges=defaultdict(list)
  for i in ids:
   proof=finite['allFaces'][i-63133][key];assert proof['sourceFaceSHA256']==digest(t[i].tobytes())and proof['groundProjectionCovered']is True and proof['existingOrdinaryClearanceBoundProved']is True
   for a,b in zip(t[i],np.roll(t[i],-1,axis=0)):edges[tuple(sorted([tuple(a),tuple(b)]))].append(i)
  boundary=sorted(e for e,v in edges.items()if len(v)==1);minimum=float(t[ids,:,1].min());lower=[e for e in boundary if e[0][1]==e[1][1]==minimum];upper=[e for e in boundary if e not in lower];assert len(boundary)==8 and len(lower)==6 and len(upper)==2
  adjacency=defaultdict(set)
  for a,b in lower:adjacency[a].add(b);adjacency[b].add(a)
  reached={min(adjacency)};todo=list(reached)
  while todo:
   for j in adjacency[todo.pop()]:
    if j not in reached:reached.add(j);todo.append(j)
  closed=all(len(v)==2 for v in adjacency.values())and reached==set(adjacency)
  hostfaces=g['components'][285]['globalOriginalFaces'];n=np.cross(t[hostfaces,1]-t[hostfaces,0],t[hostfaces,2]-t[hostfaces,0]);length=np.linalg.norm(n,axis=1);ratio=np.divide(n[:,1],length,out=np.zeros(len(n)),where=length>0);roofs=[i for i,r in zip(hostfaces,ratio)if r>.25]
  # Exact helper itself clips against finite facets; AABB pruning includes every
  # facet touching the complete unit projection, including equality endpoints.
  lo=t[ids][:,:,[0,2]].min(axis=(0,1));hi=t[ids][:,:,[0,2]].max(axis=(0,1));roofs=[i for i in roofs if np.all(t[i][:,[0,2]].max(axis=0)>=lo)and np.all(t[i][:,[0,2]].min(axis=0)<=hi)]
  assert roofs
  for i in roofs:
   p=finite['allFaces'][i-63133][key];assert p['sourceFaceSHA256']==digest(t[i].tobytes())and p['groundProjectionCovered']is True and p['existingOrdinaryClearanceBoundProved']is True
  bands=[]
  for e in boundary:
   p=verify_contact_segment(np.asarray(e),t[roofs]);p['completeOriginalSurfacePieces']=[{**r,'originalSourceFace':roofs[r['originalSurfaceFace']]}for r in p['completeOriginalSurfacePieces']]
   bands.append(dict(originalBoundaryEdge=[list(v)for v in e],originalIncidentFaces=edges[e],isExactMinimumHeightLowerBoundary=e in lower,band=p))
  rows.append(dict(mode=mode,completeCombinedWorldSHA256=digest(t.tobytes()),component=324,completeOriginalFaces=ids,completeOriginalBounds=[t[ids].min(axis=(0,1)).tolist(),t[ids].max(axis=(0,1)).tolist()],completeEveryOriginalBoundaryEdge=bands,minimumHeightLowerBoundaryClosed=closed,allSixMinimumHeightEdgesWithinExistingBand=all(r['band']['verifiedCompleteOriginalEdgeContactBand']for r in bands if r['isExactMinimumHeightLowerBoundary']),allEightBoundaryEdgesWithinExistingBand=all(r['band']['verifiedCompleteOriginalEdgeContactBand']for r in bands),originalMoreThanTwoFaceIncidences=[dict(originalEdge=[list(v)for v in e],completeOriginalIncidentFaces=v)for e,v in edges.items()if len(v)>2],completeActualFiniteHostRoofFaces=roofs,conditionalHostComponent=285,hostHasOnlyConditionalAuthenticTINCarrierRoute=True,roofUnitRootOrBridgeCredit=False,visualRoleAccepted=False,openBodyClosedSolidCertified=False))
  if mode=='providerOriginal':renderhost=roofs
  print(dict(mode=mode,complete72Faces=len(ids),allBoundaryEdges=len(boundary),lowerLoopClosed=closed,lowerWithinBand=rows[-1]['allSixMinimumHeightEdgesWithinExistingBand'],allBoundaryWithinBand=rows[-1]['allEightBoundaryEdgesWithinExistingBand'],nonmanifoldEdges=len(rows[-1]['originalMoreThanTwoFaceIncidences'])),flush=True)
 DOC.mkdir(parents=True);fig=plt.figure(figsize=(18,9),dpi=100);unit=original[ids];host=original[renderhost];center=unit.mean(axis=(0,1));display=(unit-center)[:,:,[0,2,1]];h=(host-center)[:,:,[0,2,1]]
 for k,(elev,azim)in enumerate([(24,-55),(25,140)],1):
  ax=fig.add_subplot(1,2,k,projection='3d');ax.add_collection3d(Poly3DCollection(h,facecolors='#9bb8ce',edgecolors='#46657f',linewidths=.6,alpha=.75));ax.add_collection3d(Poly3DCollection(display,facecolors='#d8b470',edgecolors='#553a20',linewidths=.65,alpha=1));allv=np.concatenate([display.reshape(-1,3),h.reshape(-1,3)]);lo=allv.min(axis=0);hi=allv.max(axis=0);mid=(lo+hi)/2;span=max(hi-lo);ax.set_xlim(mid[0]-span*.55,mid[0]+span*.55);ax.set_ylim(mid[1]-span*.55,mid[1]+span*.55);ax.set_zlim(-.4,3.4);ax.set_box_aspect((1,1,.6));ax.view_init(elev,azim);ax.set_xlabel('original X relative to unit');ax.set_ylabel('original Z relative to unit');ax.set_zlabel('original Y relative to unit');ax.set_title('All 72 original unit faces and complete finite host roof facets')
 fig.tight_layout();png=DOC/'original-roof-unit324-and-host-1800x900.png';fig.savefig(png);plt.close(fig)
 refs.extend(ref(p)for p in [png,*assets,runtimepath,PROBE/'selection.json.gz',GRAPH/'diagnostic.json.gz',GRAPH/'result.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_segment_surface_contact_band_20261009.py',HERE/'test_exact_original_segment_surface_contact_band_20261009.py'])
 for r in refs:assert ref(ROOT/r['path'])==r
 result=dict(uids=[r['uid']for r in selected],rows=rows,evidenceRefs=refs,sourceOnly=True,notCurrentDrawnGround=True,terrainProposalRequired=True,addedGroundRoots=[],nativeReacceptance=False,sourceGeometryChanges=0,currentAcceptance=False,fullAcceptance=False,installationApproved=False,newlyInstalled=0);save(DOC/'diagnostic.json.gz',result)
 s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-original-parkview-roof-unit324-lower-boundary-finite-host-band-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],sourceOnly=True,nativeReacceptance=False,currentAcceptance=False,newlyInstalled=0))
if __name__=='__main__':main()
