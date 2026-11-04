"""Compare every final-terrain adverse podium face with immutable government TIN."""
import numpy as np,shapely
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
from exact_projection_coverage_fallback_context_20261009 import apply_exact_coverage
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave-verdant-podium-tin-comparison-v1-20261018';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-wave-verdant-podium-grade-context-v3-20261018'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 recovery=BASE/'government-xl-four-qualified-original-podiums-physical-20261007-301560-0/source-recovery.json';assert str(recovery.relative_to(ROOT))in pins
 decoder=module('wave_podium_source_decoder',HERE/'xl-second-pass.py');decoder.LOCAL=HERE/'local'/BATCH;grounds=[]
 for sheet in read(recovery)['sheets']:
  folder=ROOT/sheet['cache'];proof=read(folder/'original/download.json');assert proof['directorySHA256']==sheet['directorySHA256'];refs.append(folder/'original/download.json')
  for e in sheet['terrainFiles']:
   p=folder/'terrain'/e['name'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
   if p.suffix=='.gltf':grounds.append(decoder.terrain_triangles(p))
 ground=np.concatenate(grounds);polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;ground,polys=ground[valid],polys[valid];tree=shapely.STRtree(polys);sources={};attrs={}
 for n in ['wave-all-original-support-distance','wave-verdant-podium-support']:
  sources.update({x['uid']:x for x in read(BASE/('government-xl-'+n+'-v1-20261017')/'support-inputs.json')['sources']})
 for n in ['wave-actual-render-attributes','wave-verdant-actual-render-attributes']:
  attrs.update({x['uid']:x for x in read(BASE/('government-xl-'+n+'-v1-20261017')/'attributes.json.gz')['rows']})
 results=[]
 for uid in ['landsd/301560:0','landsd/304885:0']:
  row=sources[uid];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];a=attrs[uid];idx=np.asarray(a['completeOriginalIndex']).reshape(-1,3);worlds={'original':decode_original_world_triangles(raw)}
  for mode,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(a[key]).reshape(-1,3)[idx]
  for mode,tri in worlds.items():
   tri=np.asarray(tri,dtype='<f8');old=read(PRIOR/(uid.split('/')[1]+'-'+mode+'.json.gz'));assert digest(tri.tobytes())==old['completeWorldSHA256'];rows=[]
   for i in old['continuousNegativeFaceIds']:
    t=tri[i];c=face_ground_context(t,ground,polys,tree)if np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))>0 else degenerate_ground_context(t,ground,polys,tree);c=apply_exact_coverage(c,t,ground);before=old['faces'][i];rows.append(dict(sourceFace=i,sourceTriangle=t.tolist(),stagedContext=before,originalTinContext=c,minimumGapChangeM=before['minimum']['minimumGapM']-c['minimum']['minimumGapM']if c['minimum']else None))
   save(DOC/(uid.split('/')[1]+'-'+mode+'.json.gz'),dict(uid=uid,mode=mode,sourceSHA256=row['sourceSHA256'],rows=rows,qualification='Every adverse final-terrain face, not a complete original-TIN clearance proof. Raw continuous contexts retained.'))
   result=dict(uid=uid,mode=mode,comparedFaces=len(rows),originalTinNegative=sum(x['originalTinContext']['minimum']is not None and x['originalTinContext']['minimum']['minimumGapM']<-.5 for x in rows),missingOriginalCoverage=sum(not x['originalTinContext']['groundProjectionCovered']for x in rows),largestAbsoluteMinimumChangeM=max(abs(x['minimumGapChangeM'])for x in rows if x['minimumGapChangeM']is not None));results.append(result);print(result,flush=True)
 save(DOC/'summary.json',dict(rows=results,fullAcceptance=False,installationApproved=False,newlyInstalled=0))
 refs.extend([HERE/'xl-second-pass.py',HERE/'original_face_ground_crossing_v2_20261009.py',HERE/'original_face_ground_crossing_20261009.py',HERE/'original_degenerate_ground_context_20261009.py',HERE/'exact_projection_coverage_fallback_context_20261009.py',HERE/'exact_original_projection_coverage_20261009.py',HERE/'exact_packed_world_geometry_20261009.py'])
 out=module('wave_podium_tin_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-podium-all-adverse-faces-original-tin-comparison-v1',list(set(refs)),dict(uids=['landsd/301560:0','landsd/304885:0'],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
