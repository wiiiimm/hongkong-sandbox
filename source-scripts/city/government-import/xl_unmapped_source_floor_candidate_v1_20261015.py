"""Private terrain caps from unchanged upward source facets, with whole-source diagnostics."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-unmapped-source-floor-candidate-v1-20261015';DOC=BASE/BATCH

def main():
 assert not DOC.exists();DOC.mkdir()
 prev=BASE/'government-xl-unmapped-continuous-native-ground-v1-20261015';receipt=read(prev/'result.json');refs=[Path(__file__),prev/'result.json',HERE/'primrose_private_terrain_floor_v5_20261015.py',HERE/'original_face_ground_crossing_v2_20261009.py',HERE/'original_degenerate_ground_context_20261009.py']
 for q in receipt['evidenceRefs']:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p)
 f=module('floor_candidate_decode',HERE/'xl-final-script-pass.py');recovery=read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows'];summaries=[]
 for summary in receipt['rows']:
  model=summary['modelId'];data=read(prev/(model+'.json.gz'));source=next(r for r in recovery if r['modelId']==model);asset=ROOT/source['asset']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes())
  original=np.concatenate([f.s.terrain_triangles(ROOT/p)for p in data['terrainPaths']]);ground=original.copy();polys=shapely.polygons(original[:,:,[0,2]]);tree=shapely.STRtree(polys);caps={};nominations=[]
  for i in summary['upwardBelowHalfMetreFaces']:
   face=tri[i];footprint=shapely.Polygon(face[:,[0,2]]);cap=float(face[:,1].min());hits=tree.query(footprint,predicate='intersects');keys=set()
   for vertex in original[hits].reshape(-1,3):
    key=tuple(vertex[[0,2]])
    if vertex[1]>cap:caps[key]=min(cap,caps.get(key,cap));keys.add(key)
   nominations.append({'sourceFace':i,'capHKPD':cap,'originalTerrainFaces':hits.tolist(),'nominatedXZ':sorted(keys)})
  for face in ground:
   for vertex in face:
    key=tuple(vertex[[0,2]])
    if key in caps:vertex[1]=min(vertex[1],caps[key])
  assert np.array_equal(original[:,:,[0,2]],ground[:,:,[0,2]]) and np.all(ground[:,:,1]<=original[:,:,1])
  changed=np.flatnonzero(np.any(ground!=original,axis=(1,2)));assert len(changed)
  lo,hi=tri.min((0,1)),tri.max((0,1));mask=(ground[:,:,0].max(1)>=lo[0])&(ground[:,:,0].min(1)<=hi[0])&(ground[:,:,2].max(1)>=lo[2])&(ground[:,:,2].min(1)<=hi[2]);ids=np.flatnonzero(mask);regional=ground[ids];polys=shapely.polygons(regional[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;regional=regional[valid];polys=polys[valid];tree=shapely.STRtree(polys);normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normals,axis=1);rows=[]
  for i,face in enumerate(tri):
   c=face_ground_context(face,regional,polys,tree)if length[i]>0 else degenerate_ground_context(face,regional,polys,tree);c['sourceFace']=i;rows.append(c)
   if i%1000==0:print(model,i,len(tri),flush=True)
  failures=[i for i,c in enumerate(rows)if c.get('minimum')and c['minimum']['minimumGapM']<-.5];up=[i for i in failures if length[i]and normals[i,1]/length[i]>.25];uncovered=[i for i,c in enumerate(rows)if not c['groundProjectionCovered']]
  out={'modelId':model,'sourceSHA256':source['sourceSHA256'],'completeSourceFaces':len(tri),'beforeFailures':summary['continuousBelowHalfMetreFaces'],'afterFailures':failures,'afterUpwardFailures':up,'uncoveredFaces':uncovered,'changedTerrainFaces':len(changed),'maximumLoweringM':float((original[:,:,1]-ground[:,:,1]).max()),'changedTerrainBounds':[ground[changed].min((0,1)).tolist(),ground[changed].max((0,1)).tolist()],'sourceGeometryChanges':0,'installationApproved':False};summaries.append(out)
  save(DOC/(model+'-private-terrain.json.gz'),{'terrainPaths':data['terrainPaths'],'allOriginalTerrainTriplets':original.tolist(),'allCandidateTerrainTriplets':ground.tolist(),'changedFaceIds':changed.tolist(),'sourceCaps':nominations,'sourceSHA256':source['sourceSHA256'],'publication':False})
  save(DOC/(model+'-whole-source.json.gz'),{'summary':out,'faces':rows,'regionalOriginalTerrainIndices':ids[valid].tolist(),'nonHeightFieldRegionalTerrainIndices':ids[~valid].tolist(),'qualification':'Floating continuous pair-minimum diagnostic; no maximum-envelope or runtime acceptance.'});print(out,flush=True)
 save(DOC/'summary.json',{'rows':summaries,'nextAction':'Construct parent-aligned runtime patch, nominate every affected actor using full coarse-cell extent and packed vertices, then complete source support, before/after neighbours and browser acceptance. Candidate caps are unapproved.'})
 bindings=BASE/'government-xl-unmapped-two-primary-evidence-v1-20261015/viewer-bindings.json';refs.append(bindings);uids=sorted({b['viewerUID']for r in read(bindings)['rows']for b in r['bindings']})
 module('freeze_floor_candidates',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-source-floor-candidate-full-face-diagnostic-v1',refs,{'uids':uids,'rows':summaries,'privateCandidateTerrainChanged':True,'liveTerrainChanged':False,'fullAcceptance':False})
if __name__=='__main__':main()
