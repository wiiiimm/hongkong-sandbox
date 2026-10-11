"""DRAFT descriptive fixed spatial-identity attribution plus exact finite70279 contacts.
No change to identity bounds, source ownership, collision or support policy.
Actual foreign mesh comes solely from production createBuildingGeometry.
"""
from pathlib import Path
import importlib.util,json,subprocess
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts,primitive_census
from exact_original_shell_intersections_20261009 import rational_face,cross,sub,dot
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-beverly-podium233218-foreign70279-identity-attribution-v1-20261011';DOC=B/BATCH;CAP=B/'government-xl-beverly-podium233218-complete-current-ground-capture-v1-20261011';PRIOR=B/'government-xl-beverly-hill-k-j-original-podium233218-provenance-complete-contact-v2-20261011';UID='landsd/233218:0';FOREIGN='landsd/70279:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();pre=read(CAP/'source-preflight.json');review=read(CAP/'review.json');assert review['sourceOnly']and not review['wholeSourceIdentityAccepted']and len(review['rawHistoricalIdentityReasons'])==4;manifest=ROOT/pre['currentManifest']['path'];before=manifest.read_bytes();assert digest(before)==pre['currentManifest']['sha256'];scope=read(CAP/'capture-scope.json')
 def fence():
  assert manifest.read_bytes()==before
  for p,h in scope['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 fence();selection=next(r for r in read(CAP/'selection.json.gz')['rows']if r['uid']==UID);asset=ROOT/selection['candidate']['path'];source=decode_original_world_triangles(asset.read_bytes());assert source.shape==(4712,3,3)and digest(source.tobytes())==review['completeOriginalWorldSHA256'];census=read(PRIOR/'diagnostic.json.gz')['completeOriginalPodiumNonzeroBodyCensus'];bodies=census['sharedEdgeConnectedComponents'];assert len(bodies)==14 and sorted(i for b in bodies for i in b)==list(range(4712));body_for={f:b for b,faces in enumerate(bodies)for f in faces}
 helper=HERE/'beverly_podium233218_actual_basic70279_geometry_v1_20261011.mjs';subprocess.run(['node',str(helper)],cwd=ROOT,check=True);fence();actual=read(DOC/'complete-current-basic70279-geometry.json.gz')
 for p,h in actual['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 spec=importlib.util.spec_from_file_location('reviewed_identity_context',HERE/'xl-final-script-pass.py');final=importlib.util.module_from_spec(spec);spec.loader.exec_module(final)
 forms=[(r['building'],final.form_polygon(r['building']),r['tile'])for r in pre['allCurrentRelevantForeignBasicNativeForms']];target=next(f for f,p,t in forms if f['uid']==UID);polygon=next(p for f,p,t in forms if f['uid']==UID);foreignpolygon=next(p for f,p,t in forms if f['uid']==FOREIGN);assert actual['currentForm']==next(f for f,p,t in forms if f['uid']==FOREIGN)
 native_row=dict(uid=UID,native=dict(model=dict(candidate=dict(objectId=233218,buildingCSUID='3722614969P20060312'))));a=next(r for r in read(CAP/'actual-render-geometry.json.gz')['rows']if r['uid']==UID);index=np.asarray(a['completeOriginalIndex']).reshape(-1,3);streams={'providerOriginal':source}
 for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:streams[mode]=np.asarray(a[key],float).reshape(-1,3)[index]
 body=actual['completeCurrentRendererBody'];foreign=np.asarray(body['position'],float).reshape(-1,3)[np.asarray(body['index']).reshape(-1,3)];assert np.isfinite(foreign).all()and np.isfinite(source).all();cache={};bindings={}
 for mode,world in streams.items():
  assert world.shape==(4712,3,3)and np.isfinite(world).all();key=digest(world.tobytes());bindings[mode]=dict(completeWorldSHA256=key,completeFaces=4712,proofTupleSHA256=key)
  if key in cache:continue
  context=final.identity_context(native_row,world,forms);projection=final.projection(world);excess=projection.difference(polygon);coords=shapely.get_coordinates(excess);distance=shapely.distance(shapely.points(coords),polygon)if len(coords)else np.asarray([]);maxd=float(distance.max())if len(distance)else 0.;far=[dict(xz=list(map(float,c)),distanceM=float(d))for c,d in zip(coords,distance)if d==maxd];facepolys=shapely.polygons(world[:,:,[0,2]]);rows=[]
  for i,p in enumerate(facepolys):
   if p.area<=1e-10:continue
   outside=p.difference(polygon);foreignarea=float(outside.intersection(foreignpolygon).area)
   if outside.area>0:rows.append(dict(originalFace=i,genuineOriginalBody=body_for[i],sourceFacetYRange=[float(world[i,:,1].min()),float(world[i,:,1].max())],descriptiveProjectedExcessAreaM2=float(outside.area),descriptiveForeignExcessAreaM2=foreignarea,wholeProjectedFacetIntersects70279=bool(p.intersects(foreignpolygon))))
  contacts=exact_finite_contacts(world,list(range(4712)),foreign,list(range(len(foreign))));classified=[]
  for c in contacts['contacts']:
   x,y=rational_face(world[c['sourceFaceA']]),rational_face(foreign[c['sourceFaceB']]);nx=cross(sub(x[1],x[0]),sub(x[2],x[0]));ny=cross(sub(y[1],y[0]),sub(y[2],y[0]));coplanar=bool(any(nx)and any(ny)and not any(cross(nx,ny))and dot(nx,sub(y[0],x[0]))==0);classified.append(dict(**c,genuineOriginalPodiumBody=body_for[c['sourceFaceA']],exactNonzeroPlanesCoplanar=coplanar,physicalCollisionExemption=False))
  cache[key]=dict(rawCurrentFixedSpatialIdentityContext=context,descriptiveMaximumExcessCoordinates=far,allNonzeroProjectedExcessFacetAttributions=rows,projectedAreasAreNotAdditiveOrExactContactProof=True,completeSourcePrimitiveCensus=primitive_census(world),completeActualForeignPrimitiveCensus=primitive_census(foreign),completeActualForeignFaces=len(foreign),trianglePairsTested=contacts['trianglePairsTested'],allPairsExamined=contacts['allPairsExamined'],allExactFiniteContacts=classified,positiveDimensionalContacts=sum(c['dimension']>0 for c in classified),collisionCleared=False,foreignSupportCredit=False)
 fence()
 for p,h in actual['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 refs=[ref(p)for p in [Path(__file__),helper,asset,CAP/'result.json',CAP/'review.json',CAP/'source-preflight.json',CAP/'capture-scope.json',CAP/'selection.json.gz',CAP/'actual-render-geometry.json.gz',PRIOR/'diagnostic.json.gz',PRIOR/'result.json',DOC/'complete-current-basic70279-geometry.json.gz',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py']]
 save(DOC/'diagnostic.json.gz',dict(uids=[UID,FOREIGN],currentManifest=pre['currentManifest'],sourceOnly=True,currentAcceptance=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,rawHistoricalIdentityReasons=review['rawHistoricalIdentityReasons'],wholeSourceIdentityAccepted=False,fixedExtentBoundM=10,fixedUnrelatedExcessAreaBoundM2=1,noThresholdWaiver=True,fullOriginalFaces=4712,genuineOriginalBodies=14,allFourStreamBindings=bindings,allDistinctProofs=cache,exactFullWorldTupleReuseOnly=True,foreignCoverageScope='Only70279; all other current foreign/native obligations remain undischargeable by this diagnostic.',sourceOwnershipAndArchitecturalIntentNotInferred=True,qualification='Existing production Shapely identity context and projected facet attribution explain fixed raw extent/overlap failures; projected sourceFace Y range is not a finite3D overlap proof. Complete exact finite triangle contacts with production BASIC70279 are separate raw context, not a solid interior/collision clearance or footprint identity exemption. No component trimming, building shifts, recorded-bound edits or role/grade/root credit.',evidenceRefs=refs))
 print(json.dumps(dict(distinctProofs=len(cache),foreignFaces=len(foreign),sourceOnly=True,currentAcceptance=False)))
if __name__=='__main__':main()
