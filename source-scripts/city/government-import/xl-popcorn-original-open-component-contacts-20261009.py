"""Exhaustive unchanged open-shaft/low-panel contacts, source diagnostic only."""
import importlib.util,json,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from exact_original_shell_intersections_20261009 import rational_face,intersection_points

BATCH='government-xl-popcorn-original-open-component-contacts-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
GRAPH=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-wall-contact-20261009'
INPUT=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-pair-interface-20261009/exact-original-contact-inputs.json.gz'
GROUND=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-complete-face-ground-20261009'
UID='landsd/295538:0'

def main():
 assert not (DOC/'result.json').exists(),'Fresh immutable diagnostic required'
 source=next(r for r in read(INPUT)['rows'] if r['uid']==UID)
 tri=np.asarray(source['position'],float).reshape(-1,3,3)
 context=read(GROUND/'295538-0-complete-face-context.json.gz')
 binding=read(GROUND/'295538-0-complete-face-prefix.json.gz')['binding']
 assert digest(tri.astype('<f8').tobytes())==source['worldTriangleSHA256']==binding['decodedWorldTrianglesSHA256']
 parts=read(GRAPH/'affected-original-component-census.json.gz')['components']
 wanted=[14556,14658,14660,13330];assert {p['component'] for p in parts}.issuperset(wanted)
 claim=reservations.claim('popcorn-original-open-component-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
 try:
  lo=tri.min(axis=1);hi=tri.max(axis=1);cache={};rows=[]
  def rational(i):
   if i not in cache:cache[i]=rational_face(tri[i])
   return cache[i]
  for key in wanted:
   component=next(p for p in parts if p['component']==key);ids=component['originalFaces'];members=set(ids);contacts=[];tests=0
   for i in ids:
    for j0 in np.flatnonzero(np.all(hi>=lo[i],axis=1)&np.all(lo<=hi[i],axis=1)):
     j=int(j0)
     if j in members:continue
     tests+=1;points=intersection_points(rational(i),rational(j))
     if points:contacts.append({'componentSourceFace':i,'otherOriginalSourceFace':j,'positiveDimension':len(points)>1,'exactIntersectionPoints':[[str(v) for v in p] for p in sorted(points)],'otherNormalYRatio':context['faces'][j]['normalYRatio'],'otherContinuousMinimumGapM':context['faces'][j]['minimum']['minimumGapM']})
   vertices=np.unique(tri[ids].reshape(-1,3),axis=0);levels=sorted(set(vertices[:,1].tolist()));vertical_pairs={}
   for x,y,z in vertices:vertical_pairs.setdefault((float(x),float(z)),[]).append(float(y))
   row={'component':key,'originalFaces':ids,'originalUniqueVertices':vertices.tolist(),'uniqueOriginalHeightLevels':levels,'originalVerticalVertexGroups':[{'xz':list(k),'heights':sorted(v)} for k,v in sorted(vertical_pairs.items())],'wholeOriginalExternalAABBPairs':tests,'allExactOriginalExternalContacts':contacts,'wholeComponentGroundContexts':[context['faces'][i] for i in ids],'sourceOnlyDiagnostic':True,'installationApproved':False}
   save(DOC/(str(key)+'-whole-original-contact-context.json.gz'),row);rows.append({'component':key,'originalFaces':len(ids),'exactExternalContacts':len(contacts),'positiveDimensionalContacts':sum(c['positiveDimension'] for c in contacts),'originalHeightLevels':levels,'externalAABBPairs':tests});assert reservations.heartbeat(lease)['ok'];print(json.dumps(rows[-1]),flush=True)
  spec=importlib.util.spec_from_file_location('popcorn_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.freeze(BATCH,'complete-original-popcorn-open-component-contacts-v1',[Path(__file__),INPUT,GRAPH/'result.json',GRAPH/'affected-original-component-census.json.gz',GROUND/'295538-0-complete-face-context.json.gz',GROUND/'295538-0-complete-face-prefix.json.gz',HERE/'exact_original_shell_intersections_20261009.py'],{'uids':[UID],'rows':rows,'humanStatus':'held-unknown','requiresMoreComputeOrSourceEvidence':True,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'sourceOnlyDiagnostic':True,'currentDrawnTerrainAcceptance':False,'remainingReason':'unchanged-open-component-role-and-complete-current-physical-acceptance-pending','nextStep':'Interpret complete original shaft, low-panel and underside evidence without welding, changing source poses or using contacts as structural certification. Complete current physical/foreign/runtime/browser acceptance remains required.'})
 finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()
