"""Check complete original faces continuously against an authenticated private terrain."""
import argparse,numpy as np,shapely
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_face_ground_finite_witness_context_v1_20261025 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
from xl_source_stream_binding_20261009 import source_stream_binding
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--batch',required=True);ap.add_argument('--runtime',required=True);a=ap.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
 base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;assert not doc.exists();prior=base/a.runtime;receipt,pins=authenticate(prior);gp=HERE/'local'/a.runtime/'runtime-geometry.json.gz';sp=prior/'selection.json.gz'
 for p in [gp,sp]:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 geometry=read(gp);selection=read(sp);refs=[Path(__file__),prior/'result.json',gp,sp];results=[]
 for g in geometry['rows']:
  row=next(r for r in selection['rows']if r['uid']==g['uid']);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==g['sourceSHA256']==row['sourceSHA256'];refs.append(asset)
  tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);ratio=np.divide(normal[:,1],length,out=np.zeros(len(tri)),where=length>0);polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;ground,polygons=ground[valid],polygons[valid];tree=shapely.STRtree(polygons);contexts=[]
  for i,t in enumerate(tri):
   c=face_ground_context(t,ground,polygons,tree)if length[i]>0 else degenerate_ground_context(t,ground,polygons,tree);contexts.append(dict(c,sourceFace=i,normalYRatio=float(ratio[i])if length[i]>0 else None))
   if i%1000==0:print(dict(uid=g['uid'],facesChecked=i,total=len(tri)),flush=True)
  affected=[i for i,c in enumerate(contexts)if c['minimum']and c['minimum']['minimumGapM']<-.5];walls=[i for i in affected if length[i]>0 and abs(ratio[i])<=.25];binding=source_stream_binding(raw);binding.update(decodedWorldTrianglesSHA256=digest(tri.tobytes()),drawnGroundSHA256=digest(ground.tobytes()))
  result=dict(uid=g['uid'],sourceSHA256=g['sourceSHA256'],sourceBinding=binding,wholeSourceFaces=len(tri),wholeSourceUncoveredFaces=sum(not c['groundProjectionCovered']for c in contexts),continuousAffectedFaces=affected,affectedWallFaces=walls,otherAffectedFaces=[i for i in affected if i not in walls],upwardContinuousMinimumGapM=min(c['minimum']['minimumGapM']for i,c in enumerate(contexts)if ratio[i]>.25 and c['minimum']),faces=contexts,installationApproved=False,sourceGeometryChanges=0);out=doc/(g['uid'].split('/')[1]+'.json.gz');save(out,result);results.append({k:v for k,v in result.items()if k not in ['faces','sourceBinding']});print(results[-1],flush=True)
 for p in [gp,sp]:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 refs.extend(HERE/n for n in ['original_face_ground_finite_witness_context_v1_20261025.py','original_face_ground_rank_context_v1_20261024.py','exact_original_paired_finite_clearance_v2_20261010.py','exact_original_paired_finite_clearance_20261010.py','exact_original_triangle_pair_column_gap_20261010.py','original_face_ground_crossing_v2_20261009.py','original_face_ground_crossing_20261009.py','original_degenerate_ground_context_20261009.py','xl_source_stream_binding_20261009.py']);summary=dict(uids=receipt['uids'],rows=results,installationApproved=False,sourceGeometryChanges=0,newlyInstalled=0);save(doc/'summary.json',summary);module('selected_continuous_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'whole-original-continuous-ground-context',refs,summary)
if __name__=='__main__':main()
