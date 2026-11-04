"""Complete bounded original-wall routes using existing strict ground anchors/interfaces."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_shell_intersections_20261009 import intersection_points,rational_face
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grand-aquarium-raised-rim-contacts-v2-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();refs=[Path(__file__)];pins={}
 def take(batch,name,local=False):
  folder=BASE/batch;_,p=authenticate(folder);path=(HERE/'local'/batch if local else folder)/name;assert digest(path.read_bytes())==p[str(path.relative_to(ROOT))];refs.extend([folder/'result.json',path]);return read(path)
 prior=take('government-xl-grand-aquarium-raised-rim-contacts-v1-20261022','contacts.json.gz');ctx=take('government-xl-grand-aquarium-crack-repaired-continuous-v1-20261022','93424:0.json.gz');g=take('government-xl-grand-aquarium-crack-repaired-runtime-v1-20261022','runtime-geometry.json.gz',True)['rows'][0];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert digest(tri.tobytes())==ctx['sourceBinding']['decodedWorldTrianglesSHA256'];rows=[]
 for item in prior['rows']:
  witness=item['witness'];point=np.asarray(witness['point']);route=None
  if item['positiveIncidentContact']:route=dict(kind='finite-incident-source-ground-contact',proof=item['positiveIncidentContact'])
  if route is None:
   for i in witness['originalIncidentFaces']:
    c=ctx['faces'][i];anchor=c['minimum']
    if c['groundProjectionCovered']and anchor and -.1<=anchor['minimumGapM']<=.1 and anchor['position'][1]<=point[1]+.001:
     n=np.cross(tri[i,1]-tri[i,0],tri[i,2]-tri[i,0]);a=np.asarray(anchor['position']);residual=abs(float((a-tri[i,0])@n))/float(np.linalg.norm(n));assert residual<=.001
     route=dict(kind='same-original-convex-wall-to-strict-ground-anchor',sourceFace=i,sourceAnchor=anchor,strictContactBandM=[-.1,.1],anchorSourcePlaneResidualM=residual,maximumStraightPathHeightM=max(float(point[1]),float(a[1])),endpointHeightCeilingM=float(point[1]+.001));break
  if route is None:
   for other in prior['rows']:
    contact=other['positiveIncidentContact']
    if not contact or other['witness']['point']!=witness['point']:continue
    for i in witness['originalIncidentFaces']:
     j=contact['sourceFace'];points=intersection_points(rational_face(tri[i]),rational_face(tri[j]))
     if len(points)<2:continue
     route=dict(kind='exact-positive-dimensional-original-wall-interface-to-finite-ground-contact',sourceFaces=[i,j],exactInterfacePoints=[[str(v)for v in p]for p in sorted(points)],sharedAuthenticatedSourcePoint=witness['point'],groundContact=contact,maximumPathHeightM=contact['maximumStraightPathHeightM'],endpointHeightCeilingM=float(point[1]+.001),vertexOnlyInterfaceNotCredited=True);assert route['maximumPathHeightM']<=route['endpointHeightCeilingM'];break
    if route:break
  rows.append(dict(witness=witness,route=route));print(dict(sample=witness['sampleIndex'],route=route['kind']if route else None),flush=True)
 result=dict(uids=['landsd/93424:0'],sourceSHA256=g['sourceSHA256'],sourceBinding=ctx['sourceBinding'],raisedRimWarnings=len(rows),qualifiedContactNominations=sum(r['route']is not None for r in rows),unresolvedSamples=[r['witness']['sampleIndex']for r in rows if r['route']is None],rows=rows,rawWarningsRetained=True,installationApproved=False,sourceGeometryChanges=0,newlyInstalled=0,qualification='Source-specific contact nominations only. Existing strict .1m anchor band and .001m endpoint/residual bounds retained. Source incident faces and positive-dimensional exact interfaces remain unchanged. All below-grade wall roles, current foreign scope, full physics and publication gates are independent.');save(doc/'contacts.json.gz',result);summary={k:v for k,v in result.items()if k not in ['rows','sourceBinding']};save(doc/'summary.json',summary);refs.append(HERE/'exact_original_shell_intersections_20261009.py');module('aquarium_rim_routes_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-wall-contact-route-nominations',refs,summary)
if __name__=='__main__':main()
