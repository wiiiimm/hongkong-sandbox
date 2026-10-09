"""Exact source-face interfaces diagnose an authored edge/T-junction blind spot."""
import json,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from exact_original_shell_intersections_20261009 import intersection_points,rational_face
DOC=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-272986-roof-contact-diagnosis'
CONTEXT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-272986-wall-context/diagnostic.json.gz'
GEOMETRY=HERE/'local/government-xl-fourteen-positive-cell-sequence-20261008-272986-0/runtime-geometry.json.gz'
LEASE='/tmp/xl-terrain-recovery-20261009-272986-role-lease.json'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();assert reservations.heartbeat(read(LEASE))['ok']
 d=read(CONTEXT);g=read(GEOMETRY)['rows'][0];tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 assert len(tri)==12314 and d['affectedWallFaces']==[10379] and d['sourceSHA256']==g['sourceSHA256']
 normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);valid=np.linalg.norm(normal,axis=1)>0;lo=tri.min(axis=1);hi=tri.max(axis=1)
 source=tri[10379];candidates=np.flatnonzero(valid&np.all(hi>=source.min(axis=0),axis=1)&np.all(lo<=source.max(axis=0),axis=1));contacts=[]
 for j in candidates:
  j=int(j)
  if j==10379:continue
  points=intersection_points(rational_face(source),rational_face(tri[j]))
  if points:
   c=d['faces'][j];contacts.append({'otherOriginalFace':j,'intersectionPoints':[[float(v) for v in p] for p in sorted(points)],'positiveLength':len(points)>1,'otherNormalYRatio':c['normalYRatio'],'otherMinimumGapM':c['minimum']['minimumGapM'],'otherGroundCoverage':c['groundProjectionCovered'],'otherIsClearOriginalUpwardRoof':c['normalYRatio']>.25 and c['minimum']['minimumGapM']>=-.5 and c['groundProjectionCovered']})
 result={'uid':g['uid'],'sourceSHA256':g['sourceSHA256'],'sourceFace':10379,'originalSourceVertices':source.tolist(),'wholeSourceFacesAccounted':len(tri),'collapsedOriginalFacesAccounted':np.flatnonzero(~valid).tolist(),'conservativeAABBOriginalCandidatePairs':len(candidates)-1,'exactOriginalContacts':contacts,'evidenceRefs':[ref(p) for p in [Path(__file__),CONTEXT,GEOMETRY,HERE/'exact_original_shell_intersections_20261009.py']],'sourceGeometryChanges':0,'publication':False,'installationApproved':False,'qualification':'Diagnostic only: exact original shared surfaces may expose strict full-edge graph incompleteness. No tolerance welding, copied geometry, source modification or acceptance override. Whole current provider/source/ground/foreign and independent physical gates remain required.'}
 save(DOC/'diagnostic.json.gz',result);print(json.dumps({'contacts':len(contacts),'positiveLengthClearOriginalRoofContacts':sum(r['positiveLength'] and r['otherIsClearOriginalUpwardRoof'] for r in contacts)}),flush=True)
if __name__=='__main__':main()
