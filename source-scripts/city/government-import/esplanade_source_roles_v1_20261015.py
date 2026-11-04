"""Existing wall-cap/grade diagnostics and exact-edge tower connectivity; no approval."""
from collections import defaultdict,deque
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_paths
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from original_bound_facet_wall_context_20261010 import canonical
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/'government-xl-esplanade-source-roles-v1-20261015';PREV=BASE/'government-xl-esplanade-original-support-ground-v1-20261015';PHYSICAL=BASE/'government-xl-esplanade-pair-current-physical-v3-20261015';LOCAL=HERE/'local'/PHYSICAL.name

def main():
 prior=read(PREV/'result.json')
 for r in prior['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 witness=read(DOC/'tower-contact-witnesses.json')
 for p,h in witness['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 rt=read(LOCAL/'runtime-geometry.json.gz')['rows'];tower=next(r for r in rt if r['uid']=='landsd/268828:0');tri=np.asarray(tower['position'],float).reshape(-1,3)[np.asarray(tower['index']).reshape(-1,3)];valid=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)>0;edges=defaultdict(list)
 for i in np.flatnonzero(valid):
  for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
   if tuple(a)!=tuple(b):edges[tuple(sorted((tuple(a),tuple(b))))].append(int(i))
 adj=defaultdict(set)
 for members in edges.values():
  for i in members:adj[i].update(set(members)-{i})
 roots={r['faceIndex']for c in witness['contacts']for r in c['sourceFaces']if valid[r['faceIndex']]};todo=deque(sorted(roots));parent={i:None for i in roots}
 while todo:
  i=todo.popleft()
  for j in sorted(adj[i]):
   if j not in parent:parent[j]=i;todo.append(j)
 support=read(PREV/'support-checks.json.gz')['rows'][0];out=[]
 for r in support['unresolved']:
  faces=[x['faceIndex']for x in r['originalSourceFaces']];paths=[]
  for i in faces:
   if i in parent:
    path=[i]
    while parent[path[-1]]is not None:path.append(parent[path[-1]])
    paths.append(path)
  out.append(dict(position=r['position'],reason=r['reason'],incidentFaces=faces,exactSharedEdgePathsToSampledContact=paths))
 save(DOC/'tower-connectivity.json',dict(completeFaces=len(tri),zeroAreaFaces=np.flatnonzero(~valid).tolist(),sampledContactFaces=sorted(roots),reachableFaces=len(parent),rows=out,sourceWorldSHA256=digest(tri.tobytes()),installationApproved=False,qualification='Exact positive-length shared edges on literal loader geometry, excluding zero-area faces. Contact roots and incident-face lookup are existing sampled diagnostics, not exact rational contact/body/structural certificates.'))
 row=next(r for r in read(PHYSICAL/'selection.json.gz')['rows']if r['uid']=='landsd/309385:0');raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);ctx=read(PREV/'podium-ground.json.gz')['faces'];ground=np.asarray(next(r for r in rt if r['uid']==row['uid'])['drawnGroundGeometry'],float).reshape(-1,3,3)
 binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),completeCurrentFacetContextsSHA256=canonical(ctx),exactOriginalContactListSHA256=canonical([]));paths=cap_paths(tri,ctx,[],expected_binding=binding,current_binding=binding);grade=exact_upper_ground_interfaces(tri,paths['affectedOriginalWallFaces'],ground)
 save(DOC/'podium-grade-paths.json',dict(binding=binding,capPaths=paths,gradeInterfaces=grade,drawnGroundSHA256=digest(ground.tobytes()),installationApproved=False,qualification='Existing source cap-path helper with floating continuous-minimum contexts plus exact rational exposed-grade contacts. This does not upgrade contexts to certified finite bounds or approve architectural roles.'))
 print(dict(towerUnresolved=len(out),towerPointsWithContactPath=sum(bool(r['exactSharedEdgePathsToSampledContact'])for r in out),podiumAffectedFaces=paths['affectedOriginalWallFaces'],allHaveCapPaths=paths['allAffectedHavePaths'],exposureFailures=paths['rawExposureFailures'],gradeContacts=len(grade)),flush=True)
if __name__=='__main__':main()
