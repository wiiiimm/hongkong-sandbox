"""Full untouched PopCorn wall graph and affected component census, diagnostic only."""
import collections,importlib.util,json,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from exact_original_wall_contact_paths_20261009 import contact_paths
from original_shell_diagnostic_20261009 import shell_context

BATCH='government-xl-popcorn-original-wall-contact-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PRIOR=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-complete-face-ground-20261009'
INPUT=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-pair-interface-20261009/exact-original-contact-inputs.json.gz'
UID='landsd/295538:0'

def main():
 assert not (DOC/'result.json').exists(),'Use a fresh immutable diagnostic batch'
 context=read(PRIOR/'295538-0-complete-face-context.json.gz')
 prefix=read(PRIOR/'295538-0-complete-face-prefix.json.gz');assert prefix['complete'] and context['faces']==prefix['faces']
 source=next(r for r in read(INPUT)['rows'] if r['uid']==UID)
 tri=np.asarray(source['position'],float).reshape(-1,3,3)
 assert digest(tri.astype('<f8').tobytes())==source['worldTriangleSHA256']==prefix['binding']['decodedWorldTrianglesSHA256']
 claim=reservations.claim('popcorn-original-wall-contact-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600)
 assert claim['ok'],claim
 lease=claim['reservation']
 try:
  parents=list(range(len(tri)));edges={}
  def root(i):
   while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
   return i
  for i,t in enumerate(tri):
   for a,b in zip(t,np.roll(t,-1,axis=0)):
    key=tuple(sorted((tuple(a),tuple(b))))
    if key in edges:parents[root(i)]=root(edges[key])
    else:edges[key]=i
  groups=collections.defaultdict(list)
  for i in range(len(tri)):groups[root(i)].append(i)
  affected=set(context['continuousAffectedFaces']);rows=[]
  for ids in groups.values():
   if not affected.intersection(ids):continue
   shell=shell_context(tri[ids],[0])
   faces=[context['faces'][i] for i in ids]
   rows.append({'component':min(ids),'originalFaces':ids,'shellContext':shell,
    'affectedOriginalFaces':sorted(affected.intersection(ids)),
    'noExposedOriginalFaces':[c['sourceFace'] for c in faces if c['maximumObservedGapM'] is not None and c['maximumObservedGapM']<=0],
    'upwardFaces':[c['sourceFace'] for c in faces if c['normalYRatio'] is not None and c['normalYRatio']>.25],
    'completeSourceFaceAccounting':True})
  save(DOC/'affected-original-component-census.json.gz',{'uid':UID,'sourceBinding':prefix['binding'],'components':rows,'originalComponents':len(groups),'completeOriginalInventoryFaces':len(tri),'sourceGeometryChanges':0,'installationApproved':False})
  def heartbeat(count,total):
   assert reservations.heartbeat(lease)['ok']
   if count%1000==0:print(json.dumps({'originalEligibleFacesChecked':count,'total':total}),flush=True)
  graph=contact_paths(tri,context['faces'],context['affectedWallFaces'],expected_source_binding=prefix['binding'],current_source_binding=prefix['binding'],heartbeat=heartbeat)
  save(DOC/'complete-original-wall-contact-graph.json.gz',graph)
  assert reservations.heartbeat(lease)['ok']
  spec=importlib.util.spec_from_file_location('popcorn_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  helpers=['exact_original_wall_contact_paths_20261009.py','exact_original_shell_intersections_20261009.py','original_shell_diagnostic_20261009.py']
  m.freeze(BATCH,'complete-original-popcorn-wall-contact-v1',[Path(__file__),INPUT,PRIOR/'result.json',PRIOR/'295538-0-complete-face-context.json.gz',PRIOR/'295538-0-complete-face-prefix.json.gz',*[HERE/p for p in helpers]],
   {'uids':[UID],'wholeSourceFaces':len(tri),'wholeOriginalComponents':len(groups),'affectedComponents':len(rows),'affectedWalls':len(context['affectedWallFaces']),'allAffectedHaveExactContactRoofPaths':graph['allAffectedHaveExactContactRoofPaths'],'wallsWithoutExactRoofPath':[p['sourceFace'] for p in graph['paths'] if not p['hasExactPositiveDimensionPathToClearRoof']],'humanStatus':'held-unknown','requiresMoreComputeOrSourceEvidence':True,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'currentDrawnTerrainAcceptance':False,'sourceOnlyDiagnostic':True,'remainingReason':'whole-original-exposure-bottom-ancillary-and-current-physical-role-acceptance-pending','nextStep':'Interpret exact original component roles and positive-dimensional wall paths; retain every original surface and all raw failed tests. Whole current identity/terrain/foundation/foreign/native-neighbour/runtime and staged/live browser gates remain required.'})
 finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()
