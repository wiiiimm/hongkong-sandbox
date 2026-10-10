"""All original source faces against the complete proposed residual terrain surface."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from native_parent_child_flat_composition_20261010 import faces
from actual_native_parent_transition_v3_20261010 import height_facet_indices
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
BATCH='government-xl-tung-sing-full-original-residual-candidate-context-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
CAND=DOC.parent/'government-xl-tung-sing-parent-residual-gap-candidate-20261010/candidate-single-native-residual-surface.json';SELECT=DOC.parent/'government-xl-tung-sing-interior-current-identity-inputs-20261010/selection.json.gz'
assert not DOC.exists();allground=faces(read(CAND));ground=allground[height_facet_indices(allground)];poly=shapely.polygons(ground[:,:,[0,2]]);tree=shapely.STRtree(poly);rows=[];hashes={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [CAND,SELECT,Path(__file__)]}
for row in read(SELECT)['rows']:
 asset=ROOT/row['candidate']['path'];source=decode_original_world_triangles(asset.read_bytes());hashes[str(asset.relative_to(ROOT))]=digest(asset.read_bytes());n=np.cross(source[:,1]-source[:,0],source[:,2]-source[:,0]);length=np.linalg.norm(n,axis=1);ratio=np.divide(n[:,1],length,out=np.zeros(len(length)),where=length>0);contexts=[]
 for i,t in enumerate(source):
  c=face_ground_context(t,ground,poly,tree) if length[i]>0 else degenerate_ground_context(t,ground,poly,tree);contexts.append({'originalFace':i,'normalYRatio':float(ratio[i]) if length[i]>0 else None,**c})
  if i%500==0:save(DOC/'progress.json',{'uid':row['uid'],'originalFacesChecked':i,'completeOriginalFaces':len(source)});print({'uid':row['uid'],'checked':i,'total':len(source)},flush=True)
 affected=[c['originalFace'] for c in contexts if c['minimum'] and c['minimum']['minimumGapM']<-.5];up=[c for c in contexts if c['normalYRatio'] is not None and c['normalYRatio']>.25 and c['minimum']];rows.append({'uid':row['uid'],'allOriginalFaceContexts':contexts,'completeOriginalFaces':len(source),'rawUncoveredFaces':[c['originalFace'] for c in contexts if not c['groundProjectionCovered']],'affectedFaces':affected,'affectedUpwardFaces':[c['originalFace'] for c in up if c['originalFace'] in affected],'minimumContinuousUpwardGapM':min(c['minimum']['minimumGapM'] for c in up)})
save(DOC/'diagnostic.json.gz',{'rows':rows,'completeCandidateFacets':len(allground),'exactNonzeroProjectedCandidateFacets':len(ground),'inputHashes':hashes,'modelGeometryChanges':0,'candidateTerrainTriangulationChanged':True,'physicalAccepted':False,'qualification':'Complete source-only alloriginal finite face diagnosis for a proposed residual domain that explicitly exceeds subquantum raw gaps. This is not current foundation/foreign/retained actor/runtime/publication acceptance; all source components retained and genuine missing/buried witnesses remain.'});print([{'uid':r['uid'],'uncovered':len(r['rawUncoveredFaces']),'affectedUp':len(r['affectedUpwardFaces']),'minUp':r['minimumContinuousUpwardGapM']} for r in rows],flush=True)
