"""Overlay feasibility: actual unchanged native parent cannot be lowered by overlay."""
import numpy as np,shapely
from run import ROOT,read,save,digest
from native_parent_child_flat_composition_20261010 import faces
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_ground_crossing_v2_20261009 import face_ground_context
BATCH='government-xl-tung-sing-original-upward-vs-interior-candidate-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
PARENT=DOC.parent/'government-xl-tung-sing-actual-parent-interior-composition-20261010/candidate-single-native-original-surface.json'
INPUT=DOC.parent/'government-xl-tung-sing-nested-current-identity-inputs-20261010/selection.json.gz'
def main():
 assert not DOC.exists();t=faces(read(PARENT));n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ground=t[np.abs(n[:,1])>1e-10];poly=shapely.polygons(ground[:,:,[0,2]]);tree=shapely.STRtree(poly);rows=[];hashes={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [PARENT,INPUT]}
 for row in read(INPUT)['rows']:
  p=ROOT/row['candidate']['path'];source=decode_original_world_triangles(p.read_bytes());hashes[str(p.relative_to(ROOT))]=digest(p.read_bytes());normal=np.cross(source[:,1]-source[:,0],source[:,2]-source[:,0]);length=np.linalg.norm(normal,axis=1);ratio=np.divide(normal[:,1],length,out=np.zeros(len(length)),where=length>0);up=np.flatnonzero(ratio>.25);contexts=[]
  for j,i in enumerate(up):
   c=face_ground_context(source[i],ground,poly,tree);contexts.append({'originalFace':int(i),'originalTriangle':source[i].tolist(),'normalYRatio':float(ratio[i]),**c})
   if j%250==0:save(DOC/'progress.json',{'uid':row['uid'],'upwardFacesChecked':j,'completeUpwardFaces':len(up)});print({'uid':row['uid'],'upwardFacesChecked':j,'completeUpwardFaces':len(up)},flush=True)
  bad=[r for r in contexts if r['minimum'] and r['minimum']['minimumGapM']<-.5];rows.append({'uid':row['uid'],'completeOriginalFaces':len(source),'completeOriginalUpwardFaces':len(up),'allUpwardOriginalCurrentParentContexts':contexts,'upwardFacesBuriedBeyondOrdinaryWallAllowance':bad,'minimumContinuousUpwardGapM':min((r['minimum']['minimumGapM'] for r in contexts if r['minimum']),default=None)})
 save(DOC/'diagnostic.json.gz',{'rows':rows,'completeActualCurrentNativeParentFacets':len(t),'inputHashes':hashes,'candidateActualParentSurfaceCheck':True,'sourceGeometryChanges':0,'terrainGeometryChanges':0,'physicalAccepted':False,'qualification':'Every original upward face tested continuously against the complete candidate Float32 single native finite facets; full independent physical/runtime acceptance remains pending. Height grid fallback and other support/current actor checks remain independent. This does not authorize lowering, moving source geometry or dropping parent facets.'});print([{'uid':r['uid'],'upwardFaces':r['completeOriginalUpwardFaces'],'buriedFaces':len(r['upwardFacesBuriedBeyondOrdinaryWallAllowance']),'minGap':r['minimumContinuousUpwardGapM']} for r in rows],flush=True)
if __name__=='__main__':main()
