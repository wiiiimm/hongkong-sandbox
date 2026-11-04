"""Complete authored open-back boundary against rooted original finite walls.

Source-only diagnostic. A signed coordinate permutation reuses the exact fixed
contact-band mathematics; it never rotates/moves source meshes or adds a cap.
The result is not a visual role, ground root or structural support certificate.
"""
from collections import defaultdict
import hashlib,json
import numpy as np
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment

def canonical_sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def diagnose(triangles,component_faces,rooted_faces):
 tri=np.asarray(triangles,float);assert tri.ndim==3 and tri.shape[1:]==(3,3) and len(tri) and np.isfinite(tri).all()
 ids=list(component_faces);roots=list(rooted_faces);assert len(set(ids))==len(ids) and len(set(roots))==len(roots) and ids and roots and all(type(i)is int and 0<=i<len(tri) for i in ids+roots) and not set(ids)&set(roots)
 edges=defaultdict(list)
 for i in ids:
  vs=list(map(tuple,tri[i]))
  for a,b in zip(vs,vs[1:]+vs[:1]):edges[tuple(sorted((a,b)))].append((i,a,b))
 boundary=[];reasons=[]
 for edge,incidence in sorted(edges.items()):
  if len(incidence)==1:boundary.append(incidence[0])
  elif len(incidence)!=2 or incidence[0][1:]!=incidence[1][1:][::-1]:reasons.append('nonmanifold-or-inconsistent-original-winding')
 adjacency=defaultdict(list);incoming=defaultdict(list)
 for i,a,b in boundary:adjacency[a].append((b,i));incoming[b].append(a)
 if not boundary:reasons.append('no-authored-opening')
 if set(adjacency)!=set(incoming) or any(len(adjacency[v])!=1 or len(incoming[v])!=1 for v in set(adjacency)|set(incoming)):reasons.append('original-boundary-is-not-directed-closed-loop')
 loop=[]
 if boundary and not reasons:
  start=min(adjacency);v=start
  while not loop or v!=start:
   if len(loop)>len(boundary):reasons.append('invalid-original-boundary-cycle');break
   nxt,i=adjacency[v][0];loop.append((i,v,nxt));v=nxt
  if len(loop)!=len(boundary):reasons.append('multiple-original-openings')
 normal=np.sum([np.cross(a,b) for _,a,b in boundary],axis=0) if boundary else np.zeros(3);length=float(np.linalg.norm(normal));axis=int(np.argmax(np.abs(normal))) if length else 0
 if not length or axis==1 or abs(normal[1])>.25*length:reasons.append('opening-is-not-vertical-facade')
 n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);ln=np.linalg.norm(n,axis=1);source_nonzero=all(ln[i]>0 for i in ids)
 if not source_nonzero:reasons.append('degenerate-original-detail')
 bands=[];wallids=[];permutation=None;sign=None
 if not reasons:
  sign=1 if normal[axis]>0 else -1;other=2 if axis==0 else 0;permutation=[other,axis,1]
  wallids=[i for i in roots if ln[i]>0 and abs(n[i,1])<=.25*ln[i] and abs(n[i,axis])>=.8*ln[i]]
  if not wallids:reasons.append('no-rooted-original-vertical-host-facets')
  else:
   surfaces=tri[wallids][:,:,permutation].copy();surfaces[:,:,1]*=sign
   for sourceface,a,b in loop:
    segment=np.asarray([a,b],float)[:,permutation].copy();segment[:,1]*=sign;band=verify_contact_segment(segment,surfaces)
    band['completeOriginalSurfacePieces']=[{**p,'originalSourceFace':wallids[p['originalSurfaceFace']]} for p in band['completeOriginalSurfacePieces']]
    bands.append(dict(originalBoundaryFace=sourceface,originalBoundaryEdge=[list(a),list(b)],band=band))
   if not all(r['band']['verifiedCompleteOriginalEdgeContactBand'] for r in bands):reasons.append('complete-original-opening-perimeter-outside-fixed-facade-band')
 return dict(contract='complete-original-open-facade-boundary-fixed-band-diagnostic-v1',completeOriginalFaces=ids,completeRootedOriginalScopeFaces=roots,completeOriginalHostWallFaces=wallids,completeOriginalDirectedBoundaryEdges=[dict(sourceFace=i,vertices=[list(a),list(b)]) for i,a,b in boundary],originalOpeningNormal=normal.tolist(),signedCoordinatePermutation=permutation,heightCoordinateSign=sign,everyOriginalBoundaryEdgeContactBand=bands,sourceOnlyBoundaryBandPassed=not reasons,reasons=sorted(set(reasons)),completeOriginalWorldTrianglesSHA256=hashlib.sha256(tri.tobytes()).hexdigest(),originalSourceGeometryChanges=0,structuralRootCredit=False,visualRoleAccepted=False,syntheticCapCreated=False,installationApproved=False)
