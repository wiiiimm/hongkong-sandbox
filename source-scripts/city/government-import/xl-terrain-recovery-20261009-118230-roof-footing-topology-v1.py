"""Whole original roof-post topology and unresolved islands, diagnostic only."""
import collections,json
import numpy as np
from run import ROOT,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261009-118230-roof-footing-topology-v1';DOC=BASE/BATCH
def main():
 assert not DOC.exists() or not list(DOC.iterdir())
 g=read(BASE/'xl-terrain-recovery-20261009-118230-original-world-current-support-v1/diagnostic.json.gz');t=read(BASE/'xl-terrain-recovery-20261009-118230-current-original-grade-support-v1/typed-support.json.gz');d=read(BASE/'xl-terrain-recovery-20261009-118230-original-roof-perimeters-v1/diagnostic.json.gz')
 row=read(BASE/'government-xl-terrain-recovery-harbourfront-boundary-nested-physical-v3-20261009/selection.json.gz')['rows'][0];raw=(ROOT/row['candidate']['path']).read_bytes();tri=decode_original_world_triangles(raw);assert digest(tri.tobytes())==d['completeOriginalWorldSHA256']
 adj={k:set() for k in range(446)}
 for r in t['ordinaryRootGraphPreserved']['exactOriginalContacts']:
  a,b=r['components'];adj[a].add(b);adj[b].add(a)
 seen=set(t['resolvedOriginalComponents'])|{0,85};todo=list(seen)
 while todo:
  for j in adj[todo.pop()]:
   if j!=422 and j not in seen:seen.add(j);todo.append(j)
 roofs=tri[d['completeStrictRootedOriginalRoofFaces']];rows=[]
 for k in [0,85,330,332,333,417,418,419,420,444]:
  ids=g['components'][k]['globalOriginalFaces'];part=tri[ids];edges=collections.defaultdict(list)
  for i in ids:
   for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):edges[tuple(sorted((tuple(a),tuple(b))))].append(dict(face=i,forward=bool(tuple(a)<tuple(b))))
  boundary=[dict(originalEdge=e,incidence=r,band=verify_contact_segment(np.asarray(e),roofs)) for e,r in sorted(edges.items()) if len(r)==1]
  normal=np.cross(part[:,1]-part[:,0],part[:,2]-part[:,0]);length=np.linalg.norm(normal,axis=1);ratio=np.divide(normal[:,1],length,out=np.zeros(len(length)),where=length>0)
  rows.append(dict(component=k,completeOriginalFaces=ids,completeOriginalVertices=part.tolist(),bounds=g['components'][k]['bounds'],originalBoundaryEdges=boundary,allBoundaryEdgesWithinExistingStrictRoofBand=bool(boundary) and all(r['band']['verifiedCompleteOriginalEdgeContactBand'] for r in boundary),originalNonmanifoldEdges=[dict(edge=e,incidence=r) for e,r in edges.items() if len(r)>2],originalWindingConflicts=[dict(edge=e,incidence=r) for e,r in edges.items() if len(r)==2 and r[0]['forward']==r[1]['forward']],normalYRatios=ratio.tolist(),completeOriginalAreaM2=float(length.sum()/2),exactPositiveContactNeighbours=sorted(adj[k]),hypotheticalRootCredit=False))
  print(json.dumps(dict(component=k,boundary=len(boundary),wholeBoundaryBand=rows[-1]['allBoundaryEdgesWithinExistingStrictRoofBand'],winding=len(rows[-1]['originalWindingConflicts']),nonmanifold=len(rows[-1]['originalNonmanifoldEdges']))),flush=True)
 result=dict(sourceSHA256=digest(raw),completeOriginalWorldSHA256=digest(tri.tobytes()),everyInvestigatedComponent=rows,hypotheticalPosts=[0,85],hypotheticalResolvedCount=len(seen),remainingIfBothPostsIndependentlyProved=sorted(set(range(446))-seen-{422}),structuralRootCredit=False,fullAcceptance=False,installationApproved=False,sourceGeometryChanges=0)
 save(DOC/'diagnostic.json.gz',result)
if __name__=='__main__':main()
