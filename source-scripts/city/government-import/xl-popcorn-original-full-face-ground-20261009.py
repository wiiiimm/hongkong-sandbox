"""Continuous original PopCorn face/TIN context; source-only, no acceptance.

Every original source face is retained, including the detached side panel.
The terrain is the original provider sheet, not a proposed live replacement.
"""
import importlib.util,json,uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
from unchanged_open_exterior_paths_v2_20261009 import original_open_paths
from xl_source_stream_binding_20261009 import source_stream_binding

BATCH='government-xl-popcorn-original-complete-face-ground-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/government-xl-popcorn-source-support-roles-20261009/exact-original-mall-ground-contact-inputs.json.gz'
SOURCE_INPUT=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-pair-interface-20261009/exact-original-contact-inputs.json.gz'
SELECTION=ROOT/'docs/astra-city/government-import/government-xl-popcorn-complete-original-current-pair-20261009/selection.json.gz'

def main():
 assert not (DOC/'result.json').exists(),'Fresh immutable diagnosis required'
 data=read(INPUT);ground=np.array(data['terrain']['position']).reshape(-1,3,3)
 assert digest(ground.astype('<f8').tobytes())==data['terrain']['worldTriangleSHA256']
 polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;ground,polygons=ground[valid],polygons[valid];tree=shapely.STRtree(polygons)
 inputs=read(SOURCE_INPUT)['rows'];selection={r['uid']:r for r in read(SELECTION)['rows']};uids=sorted(r['uid'] for r in inputs)
 claim=reservations.claim('popcorn-complete-source-ground-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
 rows=[];assets=[]
 try:
  for source in inputs:
   row=selection[source['uid']];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==source['sourceSHA256'];assets.append(asset)
   tri=np.array(source['position']).reshape(-1,3,3);assert len(tri)==source['triangles'];assert digest(tri.astype('<f8').tobytes())==source['worldTriangleSHA256'];normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);ratios=np.divide(normal[:,1],length,out=np.zeros(len(tri)),where=length>0)
   binding=source_stream_binding(raw);binding.update(decodedWorldTrianglesSHA256=digest(tri.tobytes()),drawnGroundSHA256=digest(ground.tobytes()))
   context_binding={**binding,'sourceInputSHA256':digest(SOURCE_INPUT.read_bytes()),'terrainInputSHA256':digest(INPUT.read_bytes()),'faceContextHelperSHA256':digest((HERE/'original_face_ground_crossing_v2_20261009.py').read_bytes()),'faceContextBaseSHA256':digest((HERE/'original_face_ground_crossing_20261009.py').read_bytes()),'degenerateHelperSHA256':digest((HERE/'original_degenerate_ground_context_20261009.py').read_bytes())}
   prefix=DOC/(source['uid'].split('/')[1].replace(':','-')+'-complete-face-prefix.json.gz')
   contexts=[]
   if prefix.exists():
    cached=read(prefix);assert cached['binding']==context_binding,'Changed source/ground/helper cannot reuse prefix';contexts=cached['faces'];assert len(contexts)<=len(tri);assert [c['sourceFace'] for c in contexts]==list(range(len(contexts)))
   for i in range(len(contexts),len(tri)):
    t=tri[i]
    c=face_ground_context(t,ground,polygons,tree) if length[i]>0 else degenerate_ground_context(t,ground,polygons,tree)
    contexts.append(dict(c,sourceFace=i,normalYRatio=float(ratios[i]) if length[i]>0 else None))
    if i%500==0:assert reservations.heartbeat(lease)['ok'];save(prefix,{'binding':context_binding,'faces':contexts,'complete':False});print(json.dumps({'uid':source['uid'],'originalFacesChecked':i,'total':len(tri)}),flush=True)
   # Save complete numeric work before role composition; a later adapter failure
   # cannot discard it. A prefix never grants complete-source acceptance.
   save(prefix,{'binding':context_binding,'faces':contexts,'complete':True})
   affected=[i for i,c in enumerate(contexts) if c['minimum'] and c['minimum']['minimumGapM']<-.5]
   walls=[i for i in affected if length[i]>0 and abs(ratios[i])<=.25]
   paths=original_open_paths(tri,contexts,walls,range(len(tri)),expected_binding=binding,current_binding=binding)
   out={'uid':source['uid'],'sourceSHA256':source['sourceSHA256'],'wholeSourceFaces':len(tri),'faces':contexts,'continuousAffectedFaces':affected,'affectedWallFaces':walls,'otherAffectedFaces':[i for i in affected if i not in walls],'wholeSourceUncoveredFaces':sum(not c['groundProjectionCovered'] for c in contexts),'upwardContinuousMinimumGapM':min(c['minimum']['minimumGapM'] for i,c in enumerate(contexts) if ratios[i]>.25 and c['minimum']),'originalZeroAreaFaces':np.flatnonzero(length==0).tolist(),'originalOpenExteriorPaths':paths,'allAffectedWallsHaveRoles':paths['allAffectedWallsHaveRoles'],'sourceOnlyDiagnostic':True,'installationApproved':False}
   save(DOC/(source['uid'].split('/')[1].replace(':','-')+'-complete-face-context.json.gz'),out);rows.append({k:v for k,v in out.items() if k not in ['faces','originalOpenExteriorPaths']});print(json.dumps({'uid':out['uid'],'wholeSourceFaces':len(tri),'continuousAffectedFaces':len(affected),'affectedWallFaces':len(walls),'otherAffectedFaces':out['otherAffectedFaces'],'wholeSourceUncoveredFaces':out['wholeSourceUncoveredFaces'],'allAffectedWallsHaveRoles':out['allAffectedWallsHaveRoles']}),flush=True)
  spec=importlib.util.spec_from_file_location('popcorn_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  scripts=['original_face_ground_crossing_v2_20261009.py','original_face_ground_crossing_20261009.py','original_degenerate_ground_context_20261009.py','unchanged_open_exterior_paths_v2_20261009.py','xl_source_stream_binding_20261009.py']
  m.freeze(BATCH,'complete-original-provider-tin-face-context-v1',[Path(__file__),INPUT,SOURCE_INPUT,SELECTION,*assets,*[HERE/s for s in scripts]],{'uids':uids,'rows':rows,'humanStatus':'held-unknown','requiresMoreComputeOrSourceEvidence':True,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'currentDrawnTerrainAcceptance':False,'sourceOnlyDiagnostic':True,'remainingReason':'complete-source-specific-wall-upper-envelope-and-ancillary-roles-plus-current-physical-acceptance-pending','nextStep':'Interpret complete original face roles using unchanged original source components. Any publication requires fresh complete current drawn terrain/identity/foreign/runtime/staged-live browser proof.'})
 finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()
