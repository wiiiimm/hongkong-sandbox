"""Complete literal open-end boundaries versus finite original roof-chamber walls."""
from collections import Counter,defaultdict
from pathlib import Path
import importlib.util,json,numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-two-original-open-end-host-context-20261010'
PRIOR=DOC.parent/'government-xl-tung-sing-two-detached-original-context-20261010/diagnostic.json.gz'
def main():
 assert not DOC.exists();d=read(PRIOR);source=next(ROOT/k for k in d['inputHashes'] if k.endswith('.glb.gz'));raw=source.read_bytes();assert digest(raw)==d['sourceSHA256'];t=decode_original_world_triangles(raw);assert digest(t.astype('<f8').tobytes())==d['wholeSourceWorldSHA256'];s=importlib.util.spec_from_file_location('tung_full_finite_original_host_distances',HERE/'xl-tung-sing-two-original-continuous-counterparts-20261010.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);out=[]
 for part in d['rows']:
  count=Counter();ids=part['allOriginalFaces']
  for f in t[ids]:
   for a,b in zip(f,np.roll(f,-1,axis=0)):
    a,b=tuple(a),tuple(b);count[tuple(sorted((a,b)))]+=1
  boundary=[e for e,n in count.items() if n==1];assert len(boundary)==8 and all(n in [1,2] for n in count.values());adj=defaultdict(list)
  for a,b in boundary:adj[a].append(b);adj[b].append(a)
  assert all(len(v)==2 for v in adj.values());unseen=set(adj);loops=[]
  while unseen:
   start=min(unseen);loop=[start];previous=None;current=start
   while True:
    options=[p for p in adj[current] if p!=previous];nxt=options[0]
    if nxt==start:break
    assert nxt not in loop;loop.append(nxt);previous,current=current,nxt
   unseen-=set(loop);assert len(loop)==4;loops.append(loop)
  assert len(loops)==2;hostids=sorted({v['mainbodyOriginalFace'] for v in part['wholeOriginalVertexWitnesses']});host=t[hostids];result=[]
  for loop in loops:
   facets=[];verts=np.asarray(loop)
   for a,b in zip(verts,np.roll(verts,-1,axis=0)):
    n=512;points=a+(b-a)*np.linspace(0,1,n+1)[:,None];evaluated=m.distances(points,host);diameter=float(np.linalg.norm(b-a)/n);facets.append({'completeLiteralOriginalBoundarySegment':[a.tolist(),b.tolist()],'partitionSegments':n,'maximumDistanceToFiniteOriginalCounterpartsM':float(evaluated.max()),'continuousCompleteSegmentDistanceUpperBoundM':float(evaluated.max())+diameter,'originalEndpointDistancesM':[float(evaluated[0]),float(evaluated[-1])]})
   normal=np.cross(verts[1]-verts[0],verts[2]-verts[0]);normal/=np.linalg.norm(normal);result.append({'completeLiteralOriginalOpenBoundaryLoop':verts.tolist(),'loopNormal':normal.tolist(),'completeBoundarySegments':facets,'continuousWholeOpenLoopHostDistanceUpperBoundM':max(v['continuousCompleteSegmentDistanceUpperBoundM'] for v in facets)})
  out.append({'originalComponent':part['component'],'allOriginalFaces':ids,'allOriginalLiteralTriangles':t[ids].tolist(),'completeLiteralOpenBoundaryEdges':[[list(a),list(b)] for a,b in boundary],'completeOriginalOpenBoundaryLoops':result,'finiteOriginalHostFaceIDs':hostids,'finiteOriginalHostFaces':host.tolist()})
 refs=[Path(__file__),source,PRIOR,HERE/'xl-tung-sing-two-original-continuous-counterparts-20261010.py'];save(DOC/'diagnostic.json.gz',{'uid':d['uid'],'sourceSHA256':d['sourceSHA256'],'wholeSourceWorldSHA256':d['wholeSourceWorldSHA256'],'all16OriginalFaces':16,'all16OpenBoundarySegments':16,'rows':out,'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in refs},'exactNoContactFailurePreserved':True,'physicalAccepted':False,'sourceGeometryChanges':0,'qualification':'Both complete original eight-face pieces are four-sided horizontally oriented open-ended tubes, with two four-edge boundary loops each. Finite original roof-chamber host distances cover EVERY complete open boundary segment through a conservative1-Lipschitz certificate. This diagnostic does not certify fixture function, direct contact, mounting/support/physical acceptance, a global tolerance or model edits.'});print(json.dumps([{'component':v['originalComponent'],'loopCompleteBoundsM':[p['continuousWholeOpenLoopHostDistanceUpperBoundM'] for p in v['completeOriginalOpenBoundaryLoops']]} for v in out]),flush=True)
if __name__=='__main__':main()
