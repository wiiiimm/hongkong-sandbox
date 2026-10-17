"""Complete flagged Royal Green face and exact-edge neighbours against both terrain sources."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
from exact_projection_coverage_fallback_context_20261009 import apply_exact_coverage
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-royal-green3-retained-terrain-v1-20261017';LOCATION=BASE/'government-xl-royal-green3-contact-location-v1-20261017';BATCH='government-xl-royal-green3-grade-face-context-v1-20261018';DOC=BASE/BATCH
UID='landsd/11093:0'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [PRIOR,LOCATION]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 row=read(PRIOR/'selection.json.gz')['rows'][0];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];original=decode_original_world_triangles(raw)
 rtpath=HERE/'local'/PRIOR.name/'runtime-geometry.json.gz';g=read(rtpath)['rows'][0];assert g['uid']==UID and g['sourceSHA256']==row['sourceSHA256'];literal=np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert len(original)==len(literal)
 location=read(LOCATION/'contacts.json.gz');assert len(location['rows'])==1 and location['rows'][0]['incidentOriginalFaces']==[8310]
 decoder=module('royal_grade_decoder',HERE/'xl-second-pass.py');decoder.LOCAL=HERE/'local'/BATCH;parts=[]
 for sheet in read(PRIOR/'source-recovery.json')['sheets']:
  folder=ROOT/sheet['cache'];proof=read(folder/'original/download.json');assert proof['directorySHA256']==sheet['directorySHA256'];refs.append(folder/'original/download.json')
  for e in sheet['terrainFiles']:
   p=folder/'terrain'/e['name'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
   if p.suffix=='.gltf':parts.append(decoder.terrain_triangles(p))
 grounds={'candidate':np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3),'originalTin':np.concatenate(parts)};contexts=[]
 for mode,t in [('original',original),('literal',literal)]:
  target=t[8310];edges={tuple(sorted((tuple(a),tuple(b))))for a,b in zip(target,np.roll(target,-1,axis=0))};adj=[]
  for i,f in enumerate(t):
   if i!=8310 and any(tuple(sorted((tuple(a),tuple(b))))in edges for a,b in zip(f,np.roll(f,-1,axis=0))):adj.append(i)
  selected=[8310]+adj
  for terrain,ground in grounds.items():
   polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;gg=ground[valid];polygons=polygons[valid];tree=shapely.STRtree(polygons);rows=[]
   for i in selected:
    f=t[i];n=np.cross(f[1]-f[0],f[2]-f[0]);length=np.linalg.norm(n);q=face_ground_context(f,gg,polygons,tree)if length else degenerate_ground_context(f,gg,polygons,tree);q=apply_exact_coverage(q,f,gg);rows.append(dict(sourceFace=i,triangle=f.tolist(),normalYRatio=float(n[1]/length)if length else None,context=q))
   out=dict(uid=UID,sourceSHA256=row['sourceSHA256'],mode=mode,terrain=terrain,wholeSourceFaces=len(t),flaggedSourceFace=8310,exactEdgeNeighbours=adj,rows=rows,fullAcceptance=False);save(DOC/(mode+'-'+terrain+'.json.gz'),out);contexts.append(dict(mode=mode,terrain=terrain,adjacentFaces=adj,flagged=rows[0]));print(dict(mode=mode,terrain=terrain,adjacentFaces=adj,flagged=rows[0]),flush=True)
 save(DOC/'summary.json',dict(uid=UID,sourceSHA256=row['sourceSHA256'],contexts=contexts,fullAcceptance=False,qualification='Whole flagged finite face and every exact-shared-edge neighbour, original and actual literal geometry. Does not claim all other faces/four-world/current-map acceptance. Raw crossing retained.'))
 refs.extend([rtpath,HERE/'xl-second-pass.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'original_face_ground_crossing_v2_20261009.py',HERE/'original_face_ground_crossing_20261009.py',HERE/'original_degenerate_ground_context_20261009.py',HERE/'exact_projection_coverage_fallback_context_20261009.py',HERE/'exact_original_projection_coverage_20261009.py'])
 out=module('royal_grade_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'royal-green3-flagged-whole-face-original-candidate-context-v1',list(set(refs)),dict(uids=[UID],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
