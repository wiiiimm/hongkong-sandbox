"""Compare complete pinned FBX authored geometry with frozen exact glTF projection.
Fresh FBX checks; frozen glTF metrics are read, not rerun or waived.
"""
import json,importlib.util
import numpy as np,shapely
from shapely.geometry import Polygon,shape,mapping
from run import ROOT,HERE,read,save,digest
DOC=ROOT/'docs/astra-city/government-import/government-xl-source-format-comparison-20261009';LOCAL=HERE/'local/government-xl-source-format-comparison-20261009';OLD=ROOT/'docs/astra-city/government-import/government-xl-identity-search-op-structures-20261009';CAUSE=ROOT/'docs/astra-city/government-import/government-xl-op-paired-coverage-cause-20261009'
s=importlib.util.spec_from_file_location('format_comparison_forms',HERE/'xl-final-script-pass.py');final=importlib.util.module_from_spec(s);s.loader.exec_module(final)
rows=[]
for pair in read(OLD/'paired-original-op-group-recovered-measures.json.gz')['rows']:
 uid=pair['uid'];prefix=uid.split('/')[1].replace(':','-');features=read(CAUSE/prefix/'exact-projection-difference.geojson')['features'];gltf=shape(next(f['geometry'] for f in features if f['properties']['role']=='complete-original-projection'));target=shapely.union_all([Polygon(f['rings'][0],f['rings'][1:]) for f in pair['groupForms']]);proofs=[];variants={};fulltri=[]
 for mode in ['raw-fbx','blender-inspection/legacy','blender-inspection/cpp']:
  projections=[];triangles=[]
  for source in pair['sourceProofs']:
   model=source['modelId'];base=LOCAL/mode/model;info=read(base/'inspection.json');tri=np.load(base/'full-world-triangles.npz')['triangles'];expected=info.get('worldTrianglesSHA256',info.get('fullWorldTrianglesSHA256'));assert digest(tri.astype('<f8').tobytes())==expected
   # Fixed frame expression only. Source metre/HKPD pose remains unchanged.
   viewer=tri.copy();viewer[:,:,0]=tri[:,:,0]-834500;viewer[:,:,1]=tri[:,:,2];viewer[:,:,2]=816500-tri[:,:,1];triangles.append(viewer);projections.append(shapely.union_all(shapely.polygons(viewer[:,:,[0,2]])))
   if mode=='raw-fbx':proofs.append(info);fulltri.append(viewer)
  projection=shapely.union_all(projections);missing=target.difference(projection);excess=projection.difference(target);bounds=projection.bounds;group={f['uid'] for f in pair['groupForms']};context=final.load_forms([bounds[0]-2,bounds[1]-2,bounds[2]+2,bounds[3]+2]);others=[p for b,p,_ in context if b['uid'] not in group];overlap=excess.intersection(shapely.union_all(others));boundarycoords=np.concatenate([np.array(p.exterior.coords) for p in projections if p.geom_type=='Polygon']+[np.array(q.exterior.coords) for p in projections if p.geom_type!='Polygon' for q in p.geoms if q.geom_type=='Polygon']);extent=float(shapely.distance(shapely.points(boundarycoords),target).max());metrics={'targetCoverage':float(target.intersection(projection).area/target.area),'maximumExtentM':extent,'unrelatedExcessOverlapM2':float(overlap.area)};diff=projection.symmetric_difference(gltf);variants[mode]={'measures':metrics,'triangles':sum(len(t) for t in triangles),'projectionAreaM2':float(projection.area),'uncoveredTargetAreaM2':float(missing.area),'gltfSymmetricDifferenceAreaM2':float(diff.area),'gltfHausdorffM':float(projection.hausdorff_distance(gltf)),'diagnosticPass':metrics['targetCoverage']>=.95 and metrics['maximumExtentM']<=10 and metrics['unrelatedExcessOverlapM2']<=1}
  save(DOC/prefix/(mode.replace('/','-')+'-exact-difference.geojson'),{'type':'FeatureCollection','coordinateFrame':'viewer x=East-834500,z=816500-North,metres','features':[{'type':'Feature','properties':{'role':name},'geometry':mapping(g)} for name,g in [('complete-FBX-projection',projection),('full-current-target',target),('uncovered-target',missing),('source-excess',excess),('unrelated-overlap',overlap),('FBX-glTF-symmetric-difference',diff)]]})
 item={'uid':uid,'structureIds':pair['structureIds'],'groupForms':pair['groupForms'],'gltfFrozenSourceProofs':pair['sourceProofs'],'gltfFrozenMeasures':pair['measures'],'fbxOriginalProofs':proofs,'variants':variants,'geometryChanges':0,'identityAccepted':False,'installationApproved':False,'qualification':'Raw FBX binary double vertices and all authored triangular polygons under exact original root translation. Legacy and C++ Blender imports independent diagnostic crosschecks only. New format hashes independently pinned. All source geometry/group forms/neighbours retained; no fitted alignment, threshold changes or inherited glTF approvals.'};rows.append(item);print(json.dumps({'uid':uid,'variants':variants}),flush=True)
save(DOC/'complete-source-format-comparison.json.gz',{'rows':rows})
