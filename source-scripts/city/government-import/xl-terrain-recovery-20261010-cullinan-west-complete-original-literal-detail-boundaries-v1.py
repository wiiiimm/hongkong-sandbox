"""Complete untouched Cullinan West detail boundaries against independently rooted faces.

Diagnostic only: every original edge/incidence survives, including free edges,
nonmanifold/winding conflicts and failed distances. No sign/structural approval.
Source and literal contexts are independently measured with unchanged .1m.
"""
import collections,importlib.util,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as edge_band
from exact_original_facet_orthogonal_finite_facade_band_20261010 import verify as facet_band
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261010-cullinan-west-complete-original-literal-detail-boundaries-v1';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261010-cullinan-west-three-current-original-complete-support-v1'
PROBE=BASE/'government-xl-terrain-recovery-cullinan-west-three-complete-original-current-probe-v1-20261010'
PARTS=[270,294,295]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def measure(tri,g,mode):
 rootids=np.array(sorted(i for k in g['resolvedOriginalComponents']for i in g['components'][k]['globalOriginalFaces']),int);out=[]
 for k in PARTS:
  ids=g['components'][k]['globalOriginalFaces'];piece=tri[ids];lo=np.nextafter(piece.min(axis=(0,1))-.1,-np.inf);hi=np.nextafter(piece.max(axis=(0,1))+.1,np.inf)
  near=rootids[np.all(tri[rootids].max(axis=1)>=lo,axis=1)&np.all(tri[rootids].min(axis=1)<=hi,axis=1)]
  edges=collections.defaultdict(list)
  for i in ids:
   vs=list(map(tuple,tri[i]))
   for a,b in zip(vs,vs[1:]+vs[:1]):edges[tuple(sorted((a,b)))].append((i,a,b))
  boundary=[]
  for e,inc in sorted(edges.items()):
   if len(inc)!=1 or e[0]==e[1]:continue
   band=edge_band(np.asarray(e),tri[near]) if len(near)else None
   boundary.append(dict(edge=e,allIncidences=inc,completeCandidateRootedHostFaces=near.tolist(),band=band,insideExistingFiniteHostBand=bool(band and band['verifiedCompleteOriginalEdgeFiniteFacadeBand'])))
  adj=collections.defaultdict(set)
  for r in boundary:
   if r['insideExistingFiniteHostBand']:
    a,b=r['edge'];adj[a].add(b);adj[b].add(a)
  conflicts=[dict(edge=e,incidences=m)for e,m in sorted(edges.items())if len(m)==2 and m[0][1:]!=m[1][1:][::-1]]
  nonmanifold=[dict(edge=e,incidences=m)for e,m in sorted(edges.items())if len(m)>2]
  # The tiny one-face fragment needs a whole-facet measurement, not a point.
  whole=[dict(face=i,band=facet_band(tri[i],tri[near]))for i in ids]if k==40 and len(near)else []
  out.append(dict(component=k,mode=mode,completeFaces=ids,completeBounds=[piece.min(axis=(0,1)).tolist(),piece.max(axis=(0,1)).tolist()],completeOriginalEdgeIncidences=[dict(edge=e,incidences=m)for e,m in sorted(edges.items())],completeGeometricBoundary=boundary,passingBoundaryEdges=sum(r['insideExistingFiniteHostBand']for r in boundary),passingBoundaryClosedCycle=bool(adj)and all(len(v)==2 for v in adj.values()),originalWindingConflicts=conflicts,originalNonmanifoldEdges=nonmanifold,wholeFacetBands=whole,roleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False))
  print(dict(mode=mode,component=k,faces=len(ids),boundary=len(boundary),passing=out[-1]['passingBoundaryEdges'],closed=out[-1]['passingBoundaryClosedCycle'],winding=len(conflicts),nonmanifold=len(nonmanifold)),flush=True)
 return out
def main():
 assert not DOC.exists();g=read(GRAPH/'diagnostic.json.gz');selected=read(PROBE/'selection.json.gz')['rows'];assets=[ROOT/next(r for r in selected if r['uid']==a['uid'])['candidate']['path']for a in g['actors']]
 original=np.concatenate([decode_original_world_triangles(p.read_bytes())for p in assets]);assert digest(original.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256']
 runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';runtime=read(runtimepath);literal=np.concatenate([np.asarray(next(r for r in runtime['rows']if r['uid']==a['uid'])['position'],float).reshape(-1,3)[np.asarray(next(r for r in runtime['rows']if r['uid']==a['uid'])['index'],np.uint32).reshape(-1,3)]for a in g['actors']]);assert literal.shape==original.shape==(154603,3,3)
 refs=[ref(p)for p in [__import__('pathlib').Path(__file__),*assets,runtimepath,GRAPH/'diagnostic.json.gz',GRAPH/'result.json',PROBE/'selection.json.gz',PROBE/'result.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_edge_finite_facade_distance_band_v2_20261010.py',HERE/'exact_original_edge_finite_facade_distance_band_20261010.py',HERE/'exact_original_facet_orthogonal_finite_facade_band_20261010.py']]
 for folder in [GRAPH,PROBE]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 rows=measure(original,g,'untouched-provider-original')+measure(literal,g,'captured-actual-runtime-literal')
 for r in refs:assert ref(ROOT/r['path'])==r
 result=dict(uids=[a['uid']for a in g['actors']],rows=rows,sourceOnlyFrozenBaseline=True,originalWorldSHA256=digest(original.tobytes()),literalWorldSHA256=digest(literal.tobytes()),manifestSHA256=read(PROBE/'selection.json.gz')['manifestSHA256'],fullFaceClearanceNotYetComplete=True,independentlyRootedComponents=g['resolvedOriginalComponents'],completeSourceComponents=len(g['components']),completeSourceFaces=len(original),sourceGeometryChanges=0,installationApproved=False,nativeReacceptance=False,evidenceRefs=refs)
 save(DOC/'diagnostic.json.gz',result);sp=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(sp);sp.loader.exec_module(f);f.freeze(BATCH,'complete-original-literal-three-detail-existing-finite-host-boundary-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],sourceOnlyDiagnostic=True,sourceGeometryChanges=0,roleAccepted=False,nativeReacceptance=False))
if __name__=='__main__':main()
