"""Complete original finite wall-top counterparts to six below-ground undersides.

Source diagnosis only. Open wall ends, raw depths and all failed gates remain.
"""
import importlib.util
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from source_closed_components import components

BATCH='government-xl-popcorn-original-wall-base-counterparts-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE=DOC.parent
INPUT=BASE/'government-xl-popcorn-original-pair-interface-20261009/exact-original-contact-inputs.json.gz'
CURRENT=BASE/'government-xl-popcorn-current-complete-face-ground-20261009/295538-0-complete-face-context.json.gz'
ORIGINAL=BASE/'government-xl-popcorn-original-complete-face-ground-20261009/295538-0-complete-face-context.json.gz'
PAIRS=[([13332,13333],[13336,13337]),([13377,13378],[13373,13374]),([13388,13389],[13384,13385])]

def main():
 assert not DOC.exists()
 row=next(r for r in read(INPUT)['rows'] if r['uid']=='landsd/295538:0')
 tri=np.asarray(row['position'],dtype='<f8').reshape(-1,3,3)
 assert len(tri)==15367 and digest(tri.tobytes())==row['worldTriangleSHA256']
 original,current=read(ORIGINAL),read(CURRENT)
 assert original['sourceSHA256']==current['sourceSHA256']==row['sourceSHA256']
 assert sorted(f for pair,_ in PAIRS for f in pair)==original['otherAffectedFaces']==current['otherAffectedFaces']
 normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);edges={}
 for f,triangle in enumerate(tri):
  for a,b in [(0,1),(1,2),(2,0)]:edges.setdefault(tuple(sorted((tuple(triangle[a]),tuple(triangle[b])))),[]).append(f)
 parts=components(tri)['components'];rows=[]
 for undersides,tops in PAIRS:
  lower=shapely.union_all(shapely.polygons(tri[undersides][:,:,[0,2]]));upper=shapely.union_all(shapely.polygons(tri[tops][:,:,[0,2]]))
  assert lower.area>0 and lower.equals(upper) and lower.difference(upper).area==upper.difference(lower).area==0
  assert all(normals[f,1]<0 and normals[f,0]==normals[f,2]==0 for f in undersides)
  assert all(normals[f,1]>0 and normals[f,0]==normals[f,2]==0 for f in tops)
  assert tri[undersides,:,1].min()==tri[undersides,:,1].max() and tri[tops,:,1].min()==tri[tops,:,1].max()
  assert tri[tops,:,1].min()>tri[undersides,:,1].max()
  component=next(c for c in parts if set(undersides+tops)<=set(c['faceIndices']))
  boundary=lower.boundary;incidence=[]
  for f in undersides:
   for a,b in [(0,1),(1,2),(2,0)]:
    edge=tuple(sorted((tuple(tri[f,a]),tuple(tri[f,b]))));others=[i for i in edges[edge] if i not in undersides]
    if others or shapely.LineString([edge[0][::2],edge[1][::2]]).within(boundary):
     incidence.append({'sourceFace':f,'exactOriginalEdge':edge,'allAdjacentOriginalFaces':others,'adjacentOriginalVerticalFaces':[i for i in others if normals[i,1]==0],'openEdgeRetained':not others})
  item={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'worldTrianglesSHA256':row['worldTriangleSHA256'],'completeSourceFaces':len(tri),'originalDownwardUndersides':undersides,'exactFiniteOriginalUpwardCounterparts':tops,'lowerY':float(tri[undersides,:,1].min()),'upperY':float(tri[tops,:,1].min()),'completeProjectionAreaM2':lower.area,'uncoveredByActualFiniteOriginalTopM2':lower.difference(upper).area,'originalExactEdgeIncidence':incidence,'completeComponentFaceIds':component['faceIndices'],'rawComponentTopology':{k:v for k,v in component.items() if k!='faceIndices'},'rawOriginalGroundContexts':[original['faces'][i] for i in undersides+tops],'rawHistoricalCurrentGroundContexts':[current['faces'][i] for i in undersides+tops],'sourceGeometryChanges':0,'physicalAccepted':False,'installationApproved':False}
  rows.append(item);print({'undersides':undersides,'tops':tops,'wholeProjectionAreaM2':lower.area,'uncoveredM2':0},flush=True)
 save(DOC/'diagnostic.json.gz',{'rows':rows,'sourceGeometryChanges':0,'physicalAccepted':False,'installationApproved':False,'qualification':'Three named original downward wall-base rectangles have exact complete finite upward counterparts and unchanged vertical side incidences. All open ends, non-manifold global topology and raw depths remain. No closed volume, new support/root, below-grade clearance exemption or current physical acceptance is claimed.'})
 spec=importlib.util.spec_from_file_location('popcorn_wall_base_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'six-original-wall-base-finite-counterparts-v1',[Path(__file__),INPUT,ORIGINAL,CURRENT,HERE/'source_closed_components.py'],{'uids':[row['uid']],'identityAccepted':False,'physicalAccepted':False,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'source-specific-wall-base-underface-role-and-complete-current-support-pending','nextStep':'Review exact finite counterpart/source wall evidence against fresh current ground, retain all raw open-shell/depth failures; complete all original component support and physical/runtime/browser checks before installation.'})

if __name__=='__main__':main()
