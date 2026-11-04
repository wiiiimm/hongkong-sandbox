"""New full-original contact paths through strictly clear authored cap surfaces.

Source-only diagnosis. A geometric path is not a structural certificate, and
historical terrain contexts cannot grant fresh current physical acceptance.
"""
import collections, importlib.util, json, uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
from original_coplanar_exterior_continuation_20261009 import diagnose
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-two-harbourfront-complete-original-roof-paths-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
GEOMETRY=HERE/'local/government-xl-two-harbourfront-terrain-continuation-v3-20261005/runtime-geometry.json.gz'
BASE=ROOT/'docs/astra-city/government-import'
CONTEXT=BASE/'xl-terrain-recovery-20261009-118230-wall-context/diagnostic.json.gz'
PARTS=BASE/'xl-terrain-recovery-20261009-118230-original-components/diagnostic.json.gz'
CONTACTS=BASE/'xl-terrain-recovery-20261009-118230-open-column-contacts/diagnostic.json.gz'
UID='landsd/118230:0'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists()
 claim=reservations.claim('harbourfront-original-paths-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600)
 assert claim['ok'],claim
 lease=claim['reservation']
 try:
  g=read(GEOMETRY)['rows'][0];ctx=read(CONTEXT);parts=read(PARTS);old=read(CONTACTS)
  historical=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
  assert digest(historical.tobytes())==ctx['originalOpenExteriorPaths']['sourceAndPhysicalBindings']['decodedWorldTrianglesSHA256']
  selection=read(BASE/'government-xl-two-harbourfront-attached-boundary-current-identity-20261009/selection.json.gz')['rows'][0]
  source=ROOT/selection['candidate']['path'];assert digest(source.read_bytes())==g['sourceSHA256']
  tri=decode_original_world_triangles(source.read_bytes())
  assert len(tri)==19438 and digest(tri.tobytes())=='b276304c2b94878d7c47665b7536a1dca385cf0bd52dd8264dff92d7dc9c5863'
  assert g['sourceSHA256']==ctx['sourceSHA256']==parts['sourceSHA256']==old['sourceSHA256']
  fc=ctx['faces'];assert len(fc)==len(tri) and [r['sourceFace'] for r in fc]==list(range(len(tri)))
  normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);size=np.linalg.norm(normal,axis=1);valid=size>0
  ratio=np.divide(normal[:,1],size,out=np.zeros(len(tri)),where=valid)
  roofs={i for i in range(len(tri)) if valid[i] and ratio[i]>.25 and fc[i]['groundProjectionCovered'] and fc[i]['minimum'] and fc[i]['minimum']['minimumGapM']>=-.5}
  # Only strictly clear non-wall originals may bridge a wall to a clear roof.
  admissible={i for i in range(len(tri)) if valid[i] and fc[i]['groundProjectionCovered'] and fc[i]['minimum'] and (abs(ratio[i])<=.25 or fc[i]['minimum']['minimumGapM']>=-.5)}
  edges=collections.defaultdict(list);adj={i:set() for i in admissible};edge_count=0
  for i in sorted(admissible):
   for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
    if tuple(a)==tuple(b):continue
    edges[tuple(sorted((tuple(a),tuple(b))))].append(i)
  for members in edges.values():
   for k,i in enumerate(members):
    for j in members[k+1:]:adj[i].add(j);adj[j].add(i);edge_count+=1
  contact_records=[];seen=set();candidate_pairs=0;lo=tri.min(axis=1);hi=tri.max(axis=1);rational={}
  def exact_face(i):
   if i not in rational:rational[i]=rational_face(tri[i])
   return rational[i]
  for row in old['rows']:
   own=set(row['originalFaces'])
   for i in row['originalFaces']:
    for j in np.flatnonzero(valid&np.all(hi>=lo[i],axis=1)&np.all(lo<=hi[i],axis=1)):
     j=int(j)
     if j in own:continue
     key=tuple(sorted((i,j)))
     if key in seen:continue
     seen.add(key);candidate_pairs+=1;points=intersection_points(exact_face(i),exact_face(j))
     if not points:continue
     measured=contact_measure(points);accepted=measured['dimension']>0 and i in admissible and j in admissible
     contact_records.append({'originalFaces':[i,j],**measured,'admissibleClearSurfaceContact':accepted,'sourceFaceNormalYRatio':float(ratio[i]),'otherFaceNormalYRatio':float(ratio[j]),'otherFaceHistoricalMinimumGapM':fc[j]['minimum']['minimumGapM']})
     if accepted:adj[i].add(j);adj[j].add(i)
  previous={i:None for i in sorted(roofs)};todo=collections.deque(sorted(roofs))
  while todo:
   i=todo.popleft()
   for j in sorted(adj[i]):
    if j not in previous:previous[j]=i;todo.append(j)
  affected=ctx['continuousAffectedFaces'];no_exposure=[i for i in affected if fc[i]['maximumObservedGapM'] is None or fc[i]['maximumObservedGapM']<=0]
  coplanar=diagnose(tri,fc,no_exposure);coplanar_rows={r['sourceFace']:r for r in coplanar['rows']}
  paths=[]
  for i in affected:
   path=[i]
   while path[-1] in previous and previous[path[-1]] is not None:path.append(previous[path[-1]])
   strict_nonwalls=[j for j in path if abs(ratio[j])>.25]
   exposure=fc[i]['maximumObservedGapM'] is not None and fc[i]['maximumObservedGapM']>0
   sheet=coplanar_rows.get(i)
   paths.append({'sourceFace':i,'originalPath':path,'hasAdmissibleOriginalPathToClearUpwardRoof':path[-1] in roofs,'strictlyClearNonWallBridgeFaces':strict_nonwalls,'pathNonWallMinimumGapM':min((fc[j]['minimum']['minimumGapM'] for j in strict_nonwalls),default=None),'rawFaceHasExposure':exposure,'exactCoplanarExposureContinuation':bool(sheet and sheet['hasActualAboveGroundExteriorContinuation']),'geometricNecessaryConditionsSatisfied':path[-1] in roofs and (exposure or bool(sheet and sheet['hasActualAboveGroundExteriorContinuation']))})
  result={'uid':UID,'sourceSHA256':g['sourceSHA256'],'decodedWorldTrianglesSHA256':digest(tri.tobytes()),'historicalExportWorldSHA256':digest(historical.tobytes()),'historicalFloat32PackingExactlyMatchesOriginal':bool(np.array_equal(tri.astype('<f4').astype(float),historical)),'maximumOriginalVersusHistoricalCoordinateDifferenceM':float(np.max(np.abs(tri-historical))),'completeOriginalFaceCount':len(tri),'completeOriginalComponentCount':len(parts['components']),'collapsedFacesRetainedWithoutBridgeCredit':np.flatnonzero(~valid).tolist(),'historicalContinuousContext':ref(CONTEXT),'clearOriginalRoofFaces':sorted(roofs),'admissibleOriginalFaces':sorted(admissible),'exactOriginalEdgePairs':edge_count,'allCylinderToOtherOriginalCandidatePairs':candidate_pairs,'exactCylinderInterfaces':contact_records,'affectedFacePaths':paths,'exactCoplanarExposureDiagnostic':coplanar,'rawWallOnlyFailuresPreserved':ctx['originalOpenExteriorPaths'],'evidenceRefs':[ref(p) for p in [Path(__file__),source,GEOMETRY,CONTEXT,PARTS,CONTACTS,HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'original_coplanar_exterior_continuation_20261009.py']],'diagnosticOnly':True,'sourceGeometryChanges':0,'currentPhysicalAccepted':False,'installationApproved':False,'publication':False,'qualification':'Complete unchanged original face inventory. Exact source root-matrix world geometry decoded afresh; complete cylinder-to-all-original contacts recomputed, not reused from historical Float32 export. Historical per-face continuous terrain contexts classify potential route only and grant no current physical credit. Exact authored edges plus exact positive-dimensional original contacts; point contacts and collapsed faces receive zero bridge credit. Geometric connection is not load-bearing certification; complete fresh current physical/foreign/runtime gates and source-specific role review remain independent.'}
  save(DOC/'diagnostic.json.gz',result)
  summary={'affectedFaces':len(paths),'roofPaths':sum(r['hasAdmissibleOriginalPathToClearUpwardRoof'] for r in paths),'exposureNecessaryConditions':sum(r['geometricNecessaryConditionsSatisfied'] for r in paths),'nonWallBridges':sorted({j for r in paths for j in r['strictlyClearNonWallBridgeFaces']}),'unresolvedFaces':[r['sourceFace'] for r in paths if not r['geometricNecessaryConditionsSatisfied']],'positiveInterfaces':sum(r['admissibleClearSurfaceContact'] for r in contact_records),'pointContacts':sum(r['dimension']==0 for r in contact_records),'currentPhysicalAccepted':False}
  save(DOC/'summary.json',summary);print(json.dumps(summary),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
