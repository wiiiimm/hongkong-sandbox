"""Complete original low ancillary part and exact interfaces; diagnosis only."""
import collections, importlib.util, json, uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
from xl_source_stream_binding_20261009 import source_stream_binding
BATCH='xl-terrain-recovery-20261009-118230-low-ancillary-context-v1'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE=ROOT/'docs/astra-city/government-import'
CONTEXT=BASE/'xl-terrain-recovery-20261009-118230-wall-context/diagnostic.json.gz'
PARTS=BASE/'xl-terrain-recovery-20261009-118230-original-components/diagnostic.json.gz'
PATHS=BASE/'government-xl-two-harbourfront-complete-original-roof-paths-20261009/diagnostic.json.gz'
SELECTION=BASE/'government-xl-two-harbourfront-attached-boundary-current-identity-20261009/selection.json.gz'
UID='landsd/118230:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();claim=reservations.claim('harbourfront-low-ancillary-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  row=read(SELECTION)['rows'][0];source=ROOT/row['candidate']['path'];raw=source.read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);ctx=read(CONTEXT);parts=read(PARTS);paths=read(PATHS)
  assert len(tri)==19438 and digest(tri.tobytes())==paths['decodedWorldTrianglesSHA256'] and digest(raw)==ctx['sourceSHA256']==paths['sourceSHA256']==parts['sourceSHA256']
  own=set(parts['components'][432]['originalFaces']);assert len(own)==54
  unresolved={r['sourceFace'] for r in paths['affectedFacePaths'] if not r['geometricNecessaryConditionsSatisfied']};assert unresolved=={17716,17736,17738,17739,17846,17850,17851}
  normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);size=np.linalg.norm(normals,axis=1);ratio=np.divide(normals[:,1],size,out=np.zeros(len(tri)),where=size>0)
  edges=collections.defaultdict(list)
  for i in sorted(own):
   for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
    if tuple(a)!=tuple(b):edges[tuple(sorted((tuple(a),tuple(b))))].append(dict(face=i,direction=1 if tuple(a)<tuple(b) else -1))
  boundary=[dict(vertices=k,incidents=v) for k,v in edges.items() if len(v)==1]
  conflicts=[dict(vertices=k,incidents=v) for k,v in edges.items() if len(v)==2 and v[0]['direction']==v[1]['direction']]
  nonmanifold=[dict(vertices=k,incidents=v) for k,v in edges.items() if len(v)>2]
  lo=tri.min(axis=1);hi=tri.max(axis=1);rational={};contacts=[];candidates=0
  def face(i):
   if i not in rational:rational[i]=rational_face(tri[i])
   return rational[i]
  for n,i in enumerate(sorted(own)):
   assert reservations.heartbeat(lease)['ok']
   for j in np.flatnonzero(np.all(hi>=lo[i],axis=1)&np.all(lo<=hi[i],axis=1)):
    j=int(j)
    if j in own:continue
    candidates+=1;points=intersection_points(face(i),face(j))
    if points:contacts.append(dict(originalFaces=[i,j],**contact_measure(points),otherFaceContext=ctx['faces'][j],otherOriginalVertices=tri[j].tolist()))
  rows=[dict(sourceFace=i,originalVertices=tri[i].tolist(),originalNormal=normals[i].tolist(),areaM2=float(size[i]/2),normalYRatio=float(ratio[i]),historicalGroundContext=ctx['faces'][i],completeOriginalRoofPath=next((r for r in paths['affectedFacePaths'] if r['sourceFace']==i),None)) for i in sorted(own)]
  result=dict(uid=UID,sourceSHA256=digest(raw),originalSourceStreams=source_stream_binding(raw),completeSourceFaces=len(tri),completeSourceWorldSHA256=digest(tri.tobytes()),component432OriginalFaces=sorted(own),originalComponentBounds=[tri[sorted(own)].min(axis=(0,1)).tolist(),tri[sorted(own)].max(axis=(0,1)).tolist()],everyComponentFace=rows,completeSourceInterfaceCandidates=candidates,everyExternalOriginalInterface=contacts,boundaryEdges=boundary,windingConflicts=conflicts,nonmanifoldEdges=nonmanifold,closedSolidCertified=False,sevenRawExposureFailures=sorted(unresolved),strictOtherFacesPreserved=True,evidenceRefs=[ref(p) for p in [Path(__file__),source,SELECTION,CONTEXT,PARTS,PATHS,HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl_source_stream_binding_20261009.py']],diagnosticOnly=True,currentPhysicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Complete original 54-face low ancillary component with every original external finite-triangle interface. Historical terrain context is diagnostic only. Open exterior is not a closed solid; exact contacts do not themselves prove structural or below-grade roles. No face or current physical failure is waived.')
  save(DOC/'diagnostic.json.gz',result)
  summary=dict(originalFaces=len(own),boundaryEdges=len(boundary),windingConflicts=len(conflicts),nonmanifoldEdges=len(nonmanifold),positiveExternalInterfaces=sum(r['dimension']>0 for r in contacts),pointExternalInterfaces=sum(r['dimension']==0 for r in contacts),rawExposureFailures=sorted(unresolved),completeSourceInterfaceCandidates=candidates,currentPhysicalAccepted=False)
  save(DOC/'summary.json',summary)
  spec=importlib.util.spec_from_file_location('ancillary_source_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.freeze(BATCH,'complete-original-low-ancillary-exterior-source-context-v1',[ROOT/r['path'] for r in result['evidenceRefs']],dict(uids=[UID],sourceSHA256=digest(raw),scriptFullAcceptancePassed=False,rawExposureFailures=sorted(unresolved),componentFaceCount=54,nextStep='Recompute complete current physical ground/source/foreign gates; investigate actual authored low exterior wall/base connectivity without granting closed-solid or buried-roof credit.'))
  print(json.dumps(summary),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
