"""Exact unchanged open-cylinder interfaces against every other original face.

No role/installation credit: the existing wall-only rejection remains visible.
Collapsed faces are inventoried but cannot provide a contact/roof anchor.
"""
import json,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
BATCH='xl-terrain-recovery-20261009-118230-open-column-contacts';DOC=ROOT/'docs/astra-city/government-import'/BATCH
GEOMETRY=HERE/'local/government-xl-two-harbourfront-terrain-continuation-v3-20261005/runtime-geometry.json.gz'
COMPONENTS=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-118230-original-components/diagnostic.json.gz'
CONTEXT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-118230-wall-context/diagnostic.json.gz'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists()
 d=read(COMPONENTS);context=read(CONTEXT);g=read(GEOMETRY)['rows'][0];tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 assert d['sourceSHA256']==context['sourceSHA256']==g['sourceSHA256'] and len(tri)==19438
 lo=tri.min(axis=1);hi=tri.max(axis=1);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);valid=length>0
 seeds=[c for c in d['components'] if c['originalFaceCount']==260 and c['affectedFaces'] and not c['clearUpwardRoofFaces']];assert len(seeds)==2
 rational={};rows=[]
 def face(i):
  if i not in rational:rational[i]=rational_face(tri[i])
  return rational[i]
 for c in seeds:
  members=set(c['originalFaces']);contacts=[];pairs=0
  for i in c['originalFaces']:
   candidates=np.flatnonzero(valid&np.all(hi>=lo[i],axis=1)&np.all(lo<=hi[i],axis=1))
   for j in candidates:
    j=int(j)
    if j in members:continue
    pairs+=1;points=intersection_points(face(i),face(j))
    if points:
     p=[[float(x) for x in point] for point in sorted(points)]
     contacts.append({'sourceFace':i,'otherOriginalFace':j,'originalIntersectionPoints':p,'positiveLength':len(points)>1,'otherFaceClearanceMinimumM':context['faces'][j]['minimum']['minimumGapM'],'otherOriginalNormalYRatio':context['faces'][j]['normalYRatio']})
  boundary={}
  for i in c['originalFaces']:
   for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
    key=tuple(sorted([tuple(a),tuple(b)]));boundary[key]=boundary.get(key,0)+1
  edges=[[[float(v) for v in p] for p in key] for key,n in boundary.items() if n==1]
  rows.append({'originalFaces':c['originalFaces'],'bounds':c['bounds'],'wholeOtherOriginalNondegenerateFacesAccounted':int(valid.sum())-len(members),'ordinaryCollapsedOriginalFacesAccounted':np.flatnonzero(~valid).tolist(),'boundaryEdges':edges,'strictAABBCandidatePairs':pairs,'exactOriginalInterfaces':contacts})
 result={'uid':g['uid'],'sourceSHA256':g['sourceSHA256'],'completeSourceFaces':len(tri),'rows':rows,'evidenceRefs':[ref(p) for p in [Path(__file__),GEOMETRY,COMPONENTS,CONTEXT,HERE/'exact_original_shell_intersections_20261009.py']],'sourceGeometryChanges':0,'publication':False,'installationApproved':False,'qualification':'Exact original owned component interfaces only. No tolerance weld, source edits, closed-cylinder claim, wall-role override or live current physical acceptance. Every original nondegenerate face tested by conservative exact AABB candidate enumeration; collapsed originals inventoried but cannot become structural anchors. Source exterior provenance, current foreign scope, below-grade semantics and full independent gates remain unproved.'}
 save(DOC/'diagnostic.json.gz',result)
 print(json.dumps({'uid':g['uid'],'rows':[{'boundaryEdges':len(r['boundaryEdges']),'candidatePairs':r['strictAABBCandidatePairs'],'interfaces':len(r['exactOriginalInterfaces']),'positiveLength':sum(x['positiveLength'] for x in r['exactOriginalInterfaces'])} for r in rows]}),flush=True)
if __name__=='__main__':main()
