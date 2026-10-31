"""Every ORIGINAL geometric boundary edge; explicit topology defects retained.

Source-only diagnosis. Original nonmanifold/winding/branching evidence is never
hidden or converted to solid certification. Continuous finite-host distances
are measured under unchanged .1m independently of orientation. A positive
boundary distance is not a mounted role, closed shell or structural support.
"""
from collections import defaultdict
import numpy as np,hashlib
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify

def prepare_hosts(triangles,rooted_faces):
 tri=np.asarray(triangles,float);ids=list(rooted_faces);assert tri.ndim==3 and tri.shape[1:]==(3,3) and np.isfinite(tri).all() and ids and len(ids)==len(set(ids)) and all(type(i)is int and 0<=i<len(tri) for i in ids)
 return dict(triangles=tri,rootedFaces=ids,worldSHA256=hashlib.sha256(tri.tobytes()).hexdigest())
def diagnose(prepared,component_faces):
 tri=prepared['triangles'];ids=list(component_faces);assert ids and len(ids)==len(set(ids)) and all(type(i)is int and 0<=i<len(tri) for i in ids) and not set(ids)&set(prepared['rootedFaces']);edges=defaultdict(list);zero=[]
 for i in ids:
  face=tri[i];vs=list(map(tuple,face))
  if not np.any(np.cross(face[1]-face[0],face[2]-face[0])):zero.append(i)
  for a,b in zip(vs,vs[1:]+vs[:1]):edges[tuple(sorted((a,b)))].append((i,a,b))
 boundary=[(edge,m[0][0]) for edge,m in sorted(edges.items()) if len(m)==1 and edge[0]!=edge[1]];records=[];adj=defaultdict(set)
 for edge,i in boundary:
  b=verify(np.asarray(edge),tri[prepared['rootedFaces']]);b['exactFiniteOriginalEdgeIntervals']=[{**r,'originalSourceFace':prepared['rootedFaces'][r['originalSurfaceFace']]} for r in b['exactFiniteOriginalEdgeIntervals']];b['allFiniteOriginalFacetIntervals']=[{**r,'originalSourceFace':prepared['rootedFaces'][r['originalSurfaceFace']]} for r in b['allFiniteOriginalFacetIntervals']];records.append(dict(originalBoundaryEdge=edge,originalBoundaryFace=i,band=b));a,z=edge;adj[a].add(z);adj[z].add(a)
 conflicts=[dict(originalEdge=edge,allOriginalIncidences=m) for edge,m in sorted(edges.items()) if len(m)==2 and m[0][1:]!=m[1][1:][::-1]];nonmanifold=[dict(originalEdge=edge,allOriginalIncidences=m) for edge,m in sorted(edges.items()) if len(m)>2];reasons=[]
 if not boundary:reasons.append('no-original-geometric-boundary')
 if any(not r['band']['verifiedCompleteOriginalEdgeFiniteFacadeBand'] for r in records):reasons.append('complete-geometric-boundary-outside-existing-finite-facade-band')
 return dict(contract='original-every-geometric-boundary-finite-facade-distance-clipped-existing-gaps-diagnostic-v2',completeOriginalWorldTrianglesSHA256=prepared['worldSHA256'],completeOriginalFaces=ids,completeRootedOriginalScopeFaces=prepared['rootedFaces'],completeOriginalGeometricBoundaryBands=records,originalWindingConflicts=conflicts,originalNonmanifoldEdges=nonmanifold,originalZeroAreaFaces=zero,originalBoundaryVertexDegrees={str(v):len(ns) for v,ns in adj.items()},sourceOnlyBoundaryBandPassed=not reasons,reasons=reasons,strictBandM=.1,geometricDistanceOnly=True,originalOrientationCertified=False,closedSolidCertified=False,sourceGeometryChanges=0,visualRoleAccepted=False,structuralRootCredit=False,installationApproved=False)
