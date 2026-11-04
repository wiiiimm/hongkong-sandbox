"""DRAFT bounded unchanged-kernel first failure attribution; no candidate/waiver."""
import json,subprocess,numpy as np
from pathlib import Path
from fractions import Fraction as F
from run import ROOT,HERE,read,save,digest,connect
from exact_resumable_projected_inventory_v1_20261011 import decoded,encoded
from exact_faithful_multisurface_transition_domain_v1_20261011 import upper_anchors
from exact_compute_transition_mesh_v1_20261011 import faces,project,height,contains,edge_intersections
from exact_source_core_ten_metre_transition_domain_v1_20261011 import polygon
from exact_atomic_terrain_domain_boundary_ring_v1_20261011 import on,at
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
B=ROOT/'docs/astra-city/government-import';P='government-xl-mongkok-stadium240332-';OLD=B/(P+'faithful-multisurface-transition-candidate-v2-20261011');DOC=B/(P+'first-upper-boundary-discontinuity-attribution-v1-20261011');ATOMS=B/(P+'complete-bounded-source3d-atoms-three-join-integration-v1-20261011');CORE=HERE/'local'/(P+'actual-native-union-authentic-core-inventory-v2-20261011')/'actual-union-authentic-whole-source-facets.json.gz';FRINGE=HERE/'local'/(P+'adjacent15c-complete-fringe-coverage-crosssheet-seams-v1-20261011')/'complete-original15c-sheet-world.json.gz';JS=HERE/'mongkok_stadium240332_first_upper_boundary_discontinuity_runtime_v1_20261011.mjs'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();r=read(OLD/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 d=decoded(read(OLD/'diagnostic.json.gz'));assert not d['terrainCandidateCreated']and d['exactFailure']['reason']=='Closed authentic upper boundary discontinuity; no snap';assert ref(ROOT/d['currentManifest']['path'])==d['currentManifest'];dom=decoded(read(OLD/'exact-source-bound-domain.json.gz'));a=decoded(read(ATOMS/'diagnostic.json.gz'));o=read(CORE);f=read(FRINGE);source=np.asarray(o['completeSelectedOriginalFacets'],dtype='<f8');adj=np.asarray(f['allWholeOriginalSheetFacets'],dtype='<f8');assert digest(source.tobytes())==o['completeSelectedOriginalSHA256']and digest(adj.tobytes())==f['completeOriginalSheetWorldSHA256'];mapping={j:i for i,j in enumerate(o['completeSelectedOriginalSheetFacetIds'])};core=np.asarray([source[mapping[i]]if sheet=='14D'else adj[i]for sheet,i in a['completeOriginalSourceFacetBindings']],dtype='<f8');assert core.shape==(14798,3,3)and digest(core.tobytes())==a['completeRetainedOriginal3DSourceSHA256'];tri=faces(core)
 try:upper_anchors(dom['sourceUnionBoundarySegments'],tri)
 except AssertionError as e:
  assert str(e)=='Closed authentic upper boundary discontinuity; no snap';tb=e.__traceback__;frame=None
  while tb:
   if tb.tb_frame.f_code.co_name=='upper_anchors':frame=tb.tb_frame
   tb=tb.tb_next
  assert frame is not None;v=frame.f_locals;bi=v['bi'];owner=v['owner'];ids=v['ids'];u,w=v['u'],v['v'];ys=v['ys'];poly=v['polys']
 else:raise AssertionError('Expected exact unchanged first failure absent')
 failures=[];incident=[];queries=[];ground=CompleteGround(core)
 def source_row(i):return dict(selectedSourceFace=i,originalSheetAndFacet=a['completeOriginalSourceFacetBindings'][i],exactOriginalTriangle=tri[i])
 for k,p in enumerate([u,w]):
  closed=[i for i in ids if contains(poly[i],p)];heights=[dict(**source_row(i),exactHeight=height(tri[i],p))for i in closed];bad=[x for x in heights if x['exactHeight']>ys[k]]
  if not bad:continue
  top=max(x['exactHeight']for x in heights);failures.append(dict(endpoint=k,exactPointXZ=p,exactOwnerEndpointHeight=ys[k],owner=source_row(owner),allClosedOriginalHeights=heights,allHigherClosedOriginalPlanes=bad,exactMaxHeight=top,sourceCoreBoundary=True,computeTransitionNotYetCreated=True));queries.append(dict(label=f'failure-{k}',xz=list(map(float,p)),exactPointXZ=encoded(p)))
  for si,s in enumerate(dom['sourceUnionBoundarySegments']):
   aa,bb=s['start'],s['end'];t=on(aa,bb,p)
   if t is None or not 0<=t<=1 or at(aa,bb,t)!=p:continue
   nominated,proof=ground.select([(aa[0],F(0),aa[1]),(bb[0],F(0),bb[1])]);nominated=list(map(int,nominated));cuts={F(0),F(1),t}
   for i in nominated:
    q=poly[i]
    for c,z in zip(q,q[1:]+q[:1]):
     for x in edge_intersections(aa,bb,c,z):cuts.add(on(aa,bb,x))
   base=sorted(cuts)
   for lo,hi in zip(base,base[1:]):
    midpoint=at(aa,bb,(lo+hi)/2);active=[i for i in nominated if contains(poly[i],midpoint)]
    assert active
    for j,i in enumerate(active):
     for h in active[:j]:
      da=height(tri[i],at(aa,bb,lo))-height(tri[h],at(aa,bb,lo));db=height(tri[i],at(aa,bb,hi))-height(tri[h],at(aa,bb,hi))
      if da*db<0:cuts.add(lo+(hi-lo)*da/(da-db))
   for lo,hi in zip(sorted(cuts),sorted(cuts)[1:]):
    if t not in [lo,hi]:continue
    midpoint=at(aa,bb,(lo+hi)/2);active=[i for i in nominated if contains(poly[i],midpoint)];own=min(active,key=lambda i:(-height(tri[i],midpoint),i));limit=height(tri[own],p)
    incident.append(dict(failureEndpoint=k,sourceBoundarySegment=si,positiveExactParameterLength=hi-lo,wholeAtomicInterval=[lo,hi],exactXZEndpoints=[at(aa,bb,lo),at(aa,bb,hi)],exactInteriorWitnessXZ=midpoint,allWholeIntervalActiveSourceFaces=active,upperOwner=source_row(own),exactOwnerLimitHeightAtFailurePoint=limit,exactClosedPointMaxHeight=top,limitMatchesClosedMaximum=limit==top,completeSourceSelection=proof));queries.append(dict(label=f'incident-{len(incident)-1}',xz=list(map(float,midpoint)),exactPointXZ=encoded(midpoint)))
 assert failures and incident;refs=[ref(Path(__file__)),ref(JS),ref(OLD/'result.json'),ref(OLD/'diagnostic.json.gz'),ref(OLD/'exact-source-bound-domain.json.gz'),ref(ATOMS/'diagnostic.json.gz'),ref(CORE),ref(FRINGE)]+d['evidenceRefs'];raw=dict(firstRejectedSourceBoundarySegment=bi,completeOriginalSourceFaces=14798,originalSourceGeometryChanges=0,allFailingClosedEndpoints=failures,allPositiveLengthIncidentBoundaryIntervals=incident,noNewCandidate=True,currentAcceptance=False,evidenceRefs=refs);save(DOC/'exact-attribution.json.gz',encoded(raw));literal=core.tolist()+[[[float(q)for q in p]for p in t]for t in a['allOrientedGeneratedNominations']];positions=np.asarray(literal,dtype='<f8').reshape(-1).tolist();save(DOC/'runtime-inputs.json.gz',dict(uid='landsd/240332:0',currentManifest=d['currentManifest'],literalOriginalSourceAndThreeJoins=dict(position=positions,index=list(range(len(positions)//3))),completeFacets=14801,queries=queries,evidenceRefs=[ref(DOC/'exact-attribution.json.gz')]+refs));subprocess.run(['node',str(JS),str((DOC/'runtime-inputs.json.gz').relative_to(ROOT)),str((DOC/'runtime-result.json.gz').relative_to(ROOT))],cwd=ROOT,check=True);assert ref(ROOT/d['currentManifest']['path'])==d['currentManifest']and all(ref(ROOT/e['path'])==e for e in refs);print(json.dumps(dict(firstBoundary=bi,failingEndpoints=len(failures),incidentPositiveIntervals=len(incident),sourceOnly=True,noCandidate=True)))
if __name__=='__main__':main()
