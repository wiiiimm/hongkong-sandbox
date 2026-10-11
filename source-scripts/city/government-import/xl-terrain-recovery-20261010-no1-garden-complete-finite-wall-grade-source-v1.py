"""Complete original Man Fuk wall-grade investigation; no acceptance/publication.

Fresh original indexed topology is matched to every actual rendered face. The
old ordinary-rim failures remain in the new exact finite grade-root result.
"""
import argparse,importlib.util,json,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_exposed_wall_grade_root_graph_20261009 import verify,canonical
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--physical',required=True);p.add_argument('--support',required=True);p.add_argument('--context',required=True,action='append');p.add_argument('--batch',required=True);a=p.parse_args()
 physical=ROOT/a.physical;support=ROOT/a.support;doc=ROOT/'docs/astra-city/government-import'/a.batch;assert not doc.exists()
 graph=read(support/'diagnostic.json.gz');receipt=read(support/'result.json');selected=read(physical/'selection.json.gz');geometry=HERE/'local'/physical.name/'runtime-geometry.json.gz';runtime=read(geometry)
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 assert len(a.context)==len(selected['rows']);pieces=[];worldpieces=[];groundpieces=[];indexed=[];contexts=[];assets=[];ctxpaths=[];cursor=0
 for row,context_path in zip(selected['rows'],a.context):
  rawpath=ROOT/row['candidate']['path'];raw=rawpath.read_bytes();assert digest(raw)==row['sourceSHA256'];assets.append(rawpath)
  tri=decode_original_world_triangles(raw);r=next(r for r in runtime['rows'] if r['uid']==row['uid']);positions=np.asarray(r['position'],float).reshape(-1,3);index=np.asarray(r['index'],np.uint32).reshape(-1,3);world=positions[index];assert world.shape==tri.shape and np.max(np.abs(world-tri))<=1e-9
  original=np.empty_like(positions);assigned={}
  for ids,face in zip(index,tri):
   for i,v in zip(ids,face):
    i=int(i)
    if i in assigned:assert np.array_equal(assigned[i],v)
    else:assigned[i]=v;original[i]=v
  assert set(assigned)==set(range(len(positions))) and np.array_equal(original[index],tri)
  indexed.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],position=original.reshape(-1).tolist(),index=index.reshape(-1).tolist()))
  cp=ROOT/context_path/'diagnostic.json.gz';ctx=read(cp);ctxpaths.append(cp);assert ctx['uids']==[row['uid']] and len(ctx['completeCertifiedLowerBoundContexts'])==len(tri)
  for i,c in enumerate(ctx['completeCertifiedLowerBoundContexts']):assert c['sourceFace']==i and c['groundProjectionCovered'] is True
  contexts.extend({**c,'sourceFace':cursor+i} for i,c in enumerate(ctx['completeCertifiedLowerBoundContexts']));cursor+=len(tri);pieces.append(tri);worldpieces.append(world);groundpieces.append(np.asarray(r['drawnGroundGeometry'],float).reshape(-1,3,3))
 tri=np.concatenate(pieces);world=np.concatenate(worldpieces);ground=np.unique(np.concatenate(groundpieces).reshape(-1,9),axis=0).reshape(-1,3,3)
 assert digest(tri.tobytes())==graph['binding']['completeOriginalWorldTrianglesSHA256'] and digest(ground.tobytes())==graph['binding']['currentDrawnGroundSHA256'] and canonical(indexed)==graph['binding']['originalIndexedSourcesSHA256']
 binding={**graph['binding'],'completeCurrentFacetContextsSHA256':canonical(contexts),'exactOriginalContactListSHA256':canonical([]),'visualOnlyComponentsSHA256':canonical([])}
 claim=reservations.claim('coupled-wall-grade-source-'+str(uuid.uuid4()),['immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  result=verify(tri,graph['actors'],graph['components'],graph['contactWitnesses'],indexed,ground,contexts,[],[],expected_binding=binding,current_binding=binding)
  faces=sorted(set(r['sourceFace'] for r in result['exactCurrentUpperGradeInterfaces']));actual=exact_upper_ground_interfaces(world,faces,ground);assert set(r['sourceFace'] for r in actual)==set(faces),'Original zero-gap grade witness absent from actual render'
  refs=[ref(p) for p in [Path(__file__),physical/'selection.json.gz',physical/'result.json',geometry,support/'diagnostic.json.gz',support/'result.json',HERE/'original_exposed_wall_grade_root_graph_20261009.py',HERE/'test_original_exposed_wall_grade_root_graph_20261009.py',HERE/'original_strict_clear_cap_wall_paths_20261009.py',HERE/'exact_original_upper_ground_interfaces_20261009.py',*assets,*ctxpaths]]
  result.update(binding=binding,actors=graph['actors'],components=graph['components'],uids=[r['uid'] for r in selected['rows']],actualRenderedWallGradeInterfaces=actual,currentRenderedWorldSHA256=digest(world.tobytes()),completeSourceRenderedCorrespondenceVerified=True,sourceOnlyDiagnostic=True,currentAcceptancePassed=False,fullAcceptance=False,installationApproved=False,evidenceRefs=refs)
  save(doc/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('wall_grade_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(a.batch,'complete-coupled-original-finite-wall-grade-source-diagnostic-v1',[ROOT/r['path'] for r in refs],dict(uids=result['uids'],sourceOnlyDiagnostic=True,exactWallGradeRoots=result['exactExposedWallGradeRootComponents'],resolvedOriginalComponents=result['resolvedOriginalComponents'],unresolvedOriginalComponents=result['unresolvedOriginalComponents'],currentAcceptancePassed=False,fullAcceptance=False))
  print(json.dumps(dict(exactWallGradeRoots=result['exactExposedWallGradeRootComponents'],resolved=len(result['resolvedOriginalComponents']),unresolved=result['unresolvedOriginalComponents'],currentAcceptancePassed=False)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
