"""DRAFT complete unchanged original bodies and62 far-facet authored connectivity only."""
from pathlib import Path
from collections import defaultdict,deque
import json,numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-spatial-surface-roles-20261009/240332-0.json.gz';LEDGER=B/'government-xl-identity-190-actionable-ledger-20261010/ledger.json.gz';DISP=B/'government-xl-current-320-blocker-families-20261009/dispositions.json.gz';SECTION=B/'government-xl-source-sections-196-20261006/240332-0.json.gz';METHOD=B/'government-xl-mongkok-stadium-original-extent-membership-method-v1-20261011/METHOD.md';DOC=B/'government-xl-mongkok-stadium-complete-original-far-extent-body-attribution-v1-20261011';UID='landsd/240332:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();old=read(OLD);lr=next(r for r in read(LEDGER)['rows']if r['uid']==UID);dr=next(r for r in read(DISP)['rows']if r['uid']==UID);section=read(SECTION);assert old['uid']==section['uid']==UID and old['sourceSHA256']==lr['sourceSHA256']==dr['sourceSHA256']==section['sourceSHA256']=='896138f962db178400870c74c41d5eae3a2ba99e0c978fad49790956c0a50bdd';assert not lr['installed']and not dr['installed']and dr['reasons']==['source-identity-fit'];asset=ROOT/old['originalPath'];assert ref(asset)['sha256']==old['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());assert tri.shape==(15456,3,3)and digest(tri.astype('<f8').tobytes())==old['worldTrianglesSHA256']==section['worldTrianglesSHA256']=='9cb0fd4ea699487958ff12aea7370ac8a872b0ccc5a791da2eb2687d63f5330c';variant=old['variants']['direct-shared-OSM'];forms=variant['groupForms'];assert len(forms)==1 and forms[0]['uid']==UID and forms[0]['buildingCSUID']=='3583620831T20111031';foot=shapely.Polygon(forms[0]['rings'][0],forms[0]['rings'][1:]);dist=shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),foot).reshape(-1,3);far=list(map(int,np.flatnonzero(dist.max(1)>10)));assert len(far)==variant['stats']['sourceFacesBeyond10m']==62 and float(dist.max())==variant['stats']['maximumSourceExtentM'];c=census(tri,list(range(len(tri))));bodies=c['sharedEdgeConnectedComponents'];labels={f:k for k,fs in enumerate(bodies)for f in fs};zeros=c['exactNonrenderingOriginalFaces'];assert set(labels)|set(zeros)==set(range(len(tri)));projection=shapely.polygons(tri[:,:,[0,2]]);target=set(map(int,np.flatnonzero(shapely.area(shapely.intersection(projection,foot))>0)))&set(labels);inc=defaultdict(set);faceedges={}
 for i in sorted(labels):
  keys=[]
  for j in range(3):
   a,b=tuple(tri[i,j]),tuple(tri[i,(j+1)%3]);assert a!=b;key=tuple(sorted([a,b]));inc[key].add(i);keys.append(key)
  faceedges[i]=keys
 parent={i:None for i in sorted(target)};queue=deque(sorted(target))
 while queue:
  i=queue.popleft()
  for key in faceedges[i]:
   for j in sorted(inc[key]-{i}):
    if j not in parent:parent[j]=i;queue.append(j)
 rows=[]
 for i in far:
  path=[]
  if i in parent:
   path=[i]
   while parent[path[-1]]is not None:path.append(parent[path[-1]])
  rows.append(dict(originalFace=i,exactNonrendering=i in zeros,genuineSourceBody=labels.get(i),completeOriginalTriangle=tri[i].tolist(),descriptiveVertexDistancesToHistoricalTargetM=dist[i].tolist(),wholeSourceExactSharedEdgePathToTargetProjectedOriginalFacet=path,pathIsGeometricOnlyNoOwnershipOrSupport=True))
 vertex_incidence=defaultdict(set)
 for i,f in enumerate(tri):
  for v in f:vertex_incidence[tuple(v)].add(i)
 far_vertex_rows=[dict(exactOriginalCoordinate=list(v),allIncidentOriginalFaces=sorted(vertex_incidence[v]),incidentExactZeroFaces=sorted(vertex_incidence[v]&set(zeros)),vertexContactProvidesNoBodyBridge=True)for v in sorted({tuple(v)for i in far for v in tri[i]})]
 details=[]
 for k in sorted({labels[i]for i in far if i in labels}):
  fs=bodies[k];v=tri[fs];details.append(dict(originalBody=k,completeOriginalFaces=fs,completeOriginalBounds=[v.min((0,1)).tolist(),v.max((0,1)).tolist()],farOriginalFaces=[i for i in far if labels.get(i)==k],originalTargetProjectedFacets=sorted(target&set(fs)),architectureFunctionAndMembershipUnresolved=True))
 refs=[ref(p)for p in [Path(__file__),asset,OLD,LEDGER,DISP,SECTION,METHOD,HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'test_exact_original_shared_edge_component_census_v2_20261011.py']];save(DOC/'diagnostic.json.gz',dict(uid=UID,source=ref(asset),completeOriginalWorldSHA256=old['worldTrianglesSHA256'],completeOriginalFaces=15456,prior12964WasTargetIntersectingFacetCountOnly=True,completeOriginalNonzeroBodyCensus=c,all62OriginalFarFaceAttributions=rows,allFarOriginalCoordinateVertexIncidences=far_vertex_rows,completeFarOwningBodyDetails=details,historicalTargetForm= forms[0],preservedHistoricalSpatialStats=variant['stats'],preservedIdentityReasons=dr['reasons'],priorOSMParentAndMidheightFailuresRemain=True,installedDistinct240527NotChanged=True,sourceOnly=True,historicalInputsOnly=True,currentMembershipVerified=False,currentAcceptance=False,identityAccepted=False,architectureRoleAccepted=False,structuralRootCredit=False,installationApproved=False,geometryChanges=0,qualification='Full15456 unchanged original source genuine body census and complete62 far-facet incidence/shared-edge attribution to original target-projected facets. The fixed10m descriptive failure remains, all350.641m2 excess remains, no original face is suppressed. Source connectivity does not establish ownership, stairs/stand function, physical support or a footprint/extent exemption. Historical190 ledger/source metadata are not refreshed remaining membership or current ground/physical/foreign/native/runtime proof. Current acceptance and all body/detail obligations remain independent.',evidenceRefs=refs));print(json.dumps(dict(sourceOnly=True,completeFaces=len(tri),genuineBodies=len(bodies),farFaces=len(rows),farOwningBodies=len(details),farFacetsWithGeometricTargetPath=sum(bool(r['wholeSourceExactSharedEdgePathToTargetProjectedOriginalFacet'])for r in rows),currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
