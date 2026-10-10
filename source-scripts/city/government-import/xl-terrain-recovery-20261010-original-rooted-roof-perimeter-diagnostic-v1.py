"""Complete unchanged source lower perimeters against original rooted roof facets.

Diagnostic only. Roof ground-clearance remains independently mandatory; no
structural roots, component acceptance or installation credit are introduced.
"""
import argparse,collections,importlib.util,json,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--physical',required=True);p.add_argument('--support',required=True);p.add_argument('--batch',required=True);a=p.parse_args();base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;assert not doc.exists();physical=ROOT/a.physical;support=ROOT/a.support;g=read(support/'diagnostic.json.gz');receipt=read(support/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 selected={r['uid']:r for r in read(physical/'selection.json.gz')['rows']};pieces=[];assets=[]
 for actor in g['actors']:
  r=selected[actor['uid']];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==actor['sourceSHA256'];pieces.append(decode_original_world_triangles(asset.read_bytes()));assets.append(asset)
 tri=np.concatenate(pieces);assert digest(tri.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256'];n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(n,axis=1);ratio=np.divide(n[:,1],length,out=np.zeros(len(n)),where=length>0);rooted=g['resolvedOriginalComponents'];rootfaces=sorted(i for k in rooted for i in g['components'][k]['globalOriginalFaces'] if ratio[i]>.25);roofs=tri[rootfaces];assert len(roofs)
 claim=reservations.claim('original-roof-perimeters-'+str(uuid.uuid4()),['immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert claim['ok'];lease=claim['reservation'];results=[]
 try:
  for k in sorted(set(range(len(g['components'])))-set(rooted)):
   ids=g['components'][k]['globalOriginalFaces'];part=tri[ids];bottom=float(part[:,:,1].min());edges=collections.defaultdict(list)
   for i in ids:
    for x,y in zip(tri[i],np.roll(tri[i],-1,axis=0)):
     if x[1]==y[1]==bottom and tuple(x)!=tuple(y):edges[tuple(sorted((tuple(x),tuple(y))))].append(i)
   bands=[];adj=collections.defaultdict(set)
   for edge,faces in sorted(edges.items()):
    b=verify_contact_segment(np.asarray(edge),roofs);b['completeOriginalSurfacePieces']=[{**r,'originalSourceFace':rootfaces[r['originalSurfaceFace']]} for r in b['completeOriginalSurfacePieces']];bands.append(dict(originalLowerEdge=edge,exactOriginalEdgeSourceFaces=faces,band=b));x,y=edge;adj[x].add(y);adj[y].add(x)
   closed=bool(adj) and all(len(v)==2 for v in adj.values());loops=0;remaining=set(adj)
   while remaining:
    seen={min(remaining)};todo=list(seen)
    while todo:
     for j in adj[todo.pop()]:
      if j not in seen:seen.add(j);todo.append(j)
    remaining-=seen;loops+=1
   results.append(dict(component=k,actorUID=g['components'][k]['actorUID'],completeOriginalFaces=ids,completeOriginalBounds=g['components'][k]['bounds'],completeMinimumElevationOriginalEdges=bands,allMinimumEdgesWithinExistingBand=bool(bands) and all(r['band']['verifiedCompleteOriginalEdgeContactBand'] for r in bands),exactLowerEdgeClosedLoops=loops if closed else None,allOriginalNormalYRatios=ratio[ids].tolist(),independentlyRootedRoofGroundClearanceStillRequired=True,structuralRootCredit=False,visualRoleAccepted=False));assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(component=k,edges=len(bands),band=results[-1]['allMinimumEdgesWithinExistingBand'],closedLoops=results[-1]['exactLowerEdgeClosedLoops'])),flush=True)
  refs=[ref(p) for p in [Path(__file__),support/'diagnostic.json.gz',support/'result.json',physical/'selection.json.gz',HERE/'exact_original_segment_surface_contact_band_20261009.py',HERE/'test_exact_original_segment_surface_contact_band_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',*assets]];save(doc/'diagnostic.json.gz',dict(uids=[r['uid'] for r in g['actors']],completeOriginalWorldSHA256=digest(tri.tobytes()),independentlyRootedComponents=rooted,completeIndependentlyRootedUpwardOriginalRoofFaces=rootfaces,completeOriginalRoofTrianglesSHA256=digest(roofs.tobytes()),results=results,candidateWholeLowerPerimeterComponents=[r['component'] for r in results if r['allMinimumEdgesWithinExistingBand'] and r['exactLowerEdgeClosedLoops']],rawNoContactFailuresPreserved=True,fullAcceptance=False,installationApproved=False,evidenceRefs=refs));spec=importlib.util.spec_from_file_location('f',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(a.batch,'complete-original-rooted-roof-perimeter-band-diagnostic-v1',[ROOT/r['path'] for r in refs],dict(uids=[r['uid'] for r in g['actors']],completeUnresolvedComponents=len(results),candidateWholeLowerPerimeterComponents=[r['component'] for r in results if r['allMinimumEdgesWithinExistingBand'] and r['exactLowerEdgeClosedLoops']],fullAcceptance=False,structuralRootCredit=False))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
