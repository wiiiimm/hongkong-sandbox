"""Whole original exact-edge component diagnosis, never role acceptance."""
import json,collections,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
BATCH='xl-terrain-recovery-20261009-272986-original-components';DOC=ROOT/'docs/astra-city/government-import'/BATCH
GEOMETRY=HERE/'local/government-xl-fourteen-positive-cell-sequence-20261008-272986-0/runtime-geometry.json.gz'
CONTEXT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-272986-wall-context/diagnostic.json.gz'
LEASE='/tmp/xl-terrain-recovery-20261009-272986-role-lease.json'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();assert reservations.heartbeat(read(LEASE))['ok']
 g=read(GEOMETRY)['rows'][0];d=read(CONTEXT);tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 assert d['sourceSHA256']==g['sourceSHA256'] and len(tri)==d['wholeSourceFaces']==12314
 assert digest(tri.tobytes())==d['originalOpenExteriorPaths']['sourceAndPhysicalBindings']['decodedWorldTrianglesSHA256']
 affected=set(d['continuousAffectedFaces']);roofs=set(d['originalOpenExteriorPaths']['roofFaces']);collapsed=set(d['originalZeroAreaFaces']);edges={};adj={i:set() for i in range(len(tri))}
 for i,t in enumerate(tri):
  if i in collapsed:continue
  for a,b in zip(t,np.roll(t,-1,axis=0)):
   key=tuple(sorted([tuple(a),tuple(b)]));edges.setdefault(key,[]).append(i)
 for faces in edges.values():
  for i in faces:adj[i].update(j for j in faces if j!=i)
 remaining=set(range(len(tri)));components=[]
 while remaining:
  seed=min(remaining);members={seed};todo=[seed]
  while todo:
   for j in adj[todo.pop()]:
    if j not in members:members.add(j);todo.append(j)
  remaining-=members;f=sorted(members);points=tri[f].reshape(-1,3)
  components.append({'originalFaces':f,'originalFaceCount':len(f),'affectedFaces':sorted(members&affected),'clearUpwardRoofFaces':sorted(members&roofs),'bounds':[points.min(axis=0).tolist(),points.max(axis=0).tolist()]})
 # Broader graph is recorded only to find the actual original connection cause.
 # It never changes the wall-only role kernel or grants buried-segment credit.
 previous={i:None for i in roofs};todo=collections.deque(sorted(roofs))
 while todo:
  i=todo.popleft()
  for j in sorted(adj[i]):
   if j not in previous:previous[j]=i;todo.append(j)
 paths=[]
 for i in sorted(affected):
  path=[i]
  while path[-1] in previous and previous[path[-1]] is not None:path.append(previous[path[-1]])
  paths.append({'sourceFace':i,'hasUnrestrictedOriginalEdgeRoofPath':path[-1] in roofs,'originalPath':path,'crossesNonWallFaces':[j for j in path[:-1] if abs(d['faces'][j].get('normalYRatio') or 0)>.25]})
 result={'uid':g['uid'],'sourceSHA256':g['sourceSHA256'],'completeSourceFaces':len(tri),'components':components,'unrestrictedDiagnosticPaths':paths,'rawWallOnlyContractAccepted':False,'originalCollapsedFacesAccounted':sorted(collapsed),'evidenceRefs':[ref(p) for p in [Path(__file__),GEOMETRY,CONTEXT]],'sourceGeometryChanges':0,'publication':False,'installationApproved':False,'qualification':'Exact original geometric edges only, no tolerance weld. Every face remains accounted; collapsed faces cannot bridge. A broader path is diagnosis of existing authored topology, not a wall/segment/structural acceptance contract. Current source/context, full strict independent physical and foreign checks remain mandatory.'}
 save(DOC/'diagnostic.json.gz',result)
 print(json.dumps({'components':len(components),'affectedComponents':[{k:r[k] for k in ['originalFaceCount','bounds']}|{'affected':len(r['affectedFaces']),'clearRoofs':len(r['clearUpwardRoofFaces'])} for r in components if r['affectedFaces']],'unrestrictedPaths':sum(r['hasUnrestrictedOriginalEdgeRoofPath'] for r in paths),'pathCrossingNonWalls':sum(bool(r['crossesNonWallFaces']) for r in paths)}),flush=True)
if __name__=='__main__':main()
