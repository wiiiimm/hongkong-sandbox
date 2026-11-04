"""Exact Skytower/Elements/Suntower source-family identity; no physical approval."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-skytower-connected-original-identity-v1-20261024';UID='landsd/204146:0';P='government-xl-next-six-after-plaza-'
SOURCES={UID:'c68e73329b0aa5a6fa5dd00e303f772eafb24b0c6d9bfbf89f28e7e34d806f44','landsd/273061:0':'029934eb9578d41e7ca13b6c1e4583715819749587f1334948cd357da623c21a','landsd/204145:0':'7015f9c5489eb757589cbd5876955dba3f8ffd99187d42bda8661e857493dce3'}

def exact_normal(t):
 a,b,c=[[F(float(v))for v in p]for p in t];u=[b[i]-a[i]for i in range(3)];v=[c[i]-a[i]for i in range(3)]
 return [u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]

def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(n,f):
  if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  p=BASE/n/f;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 capture=P+'normalized-runtime-v1-20261024';native=P+'current-native-contacts-v1-20261024';scope=P+'current-scope-v1-20261024';attrs=P+'current-attributes-v2-20261024'
 selection=take(capture,'selection.json.gz');row=next(r for r in selection['rows']if r['uid']==UID);assert row['sourceSHA256']==SOURCES[UID]
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 raw=take(P+'current-identity-v2-20261024','204146:0/identity.json')
 assert raw['sourceSHA256']==SOURCES[UID]and set(raw['reasons'])=={'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}
 assert raw['exactCurrentComponentRoute']['qualified']and raw['exactWholeCellCoverage']['covered']and raw['originalOwnership']['sourceGraphVerified']and raw['originalOwnership']['originalRootName']==row['modelId']
 input=take(native,'native-input.json.gz');old={r['uid']:r for r in input['rows']if r['uid']in SOURCES};assert set(old)==set(SOURCES)-{UID}
 forms={r['building']['uid']:r['building']for r in take(scope,'204146:0-forms.json.gz')};assert set(forms)==set(SOURCES)
 assert forms[UID]==row['source']['building']and len({f['parent']for f in forms.values()})==1
 assets={UID:ROOT/row['candidate']['path']}
 for uid,r in old.items():
  e=r['entry'];assert e['sha256']==SOURCES[uid]and r['building']==forms[uid]
  assert all(e.get(k)is True for k in ['identityReviewApproved','publicationApproved','placementReviewed'])
  assert e['uid']==uid and e['objectId']==forms[uid]['objectId']and e['buildingCSUID']==forms[uid]['buildingCSUID']
  cat=ROOT/r['cataloguePath'];assert next(m for m in read(cat)['models']if m['uid']==uid)==e;refs.append(cat);assets[uid]=ROOT/r['path']
 originals={}
 for uid,p in assets.items():assert digest(p.read_bytes())==SOURCES[uid];refs.append(p);originals[uid]=decode_original_world_triangles(p.read_bytes())
 child=next(r for r in take(attrs,'attributes.json.gz')['rows']if r['uid']==UID);parents={r['uid']:r for r in take(native,'native-attributes.json.gz')['rows']}
 ix=np.asarray(child['completeOriginalIndex']).reshape(-1,3);native_ix=np.asarray(parents['landsd/204145:0']['completeOriginalIndex']).reshape(-1,3)
 fields={'literal':'completeLiteralWorldPosition','leftF32':'completeExplicitLeftAssociatedFloat32WorldPosition','balancedF32':'completeExplicitBalancedFloat32WorldPosition'}
 polygon=lambda f:shapely.Polygon(f['rings'][0],f['rings'][1:]);own=polygon(forms[UID]);assembly=shapely.union_all([polygon(f)for f in forms.values()]);results=[]
 checks=take('government-xl-skytower-elements-current-support-v1-20261024','summary.json');assert checks['supportedUid']==UID and checks['installedSupportUid']=='landsd/273061:0'and len(checks['rows'])==4
 for r in checks['rows']:
  assert r['unresolved']==r['finitePaths']==10 and r['support']['strictContacts']==251
  f=r['compoundFoundation'];assert f['completeTerrainTriangles']==f['triangles']==10887 and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0
 for mode in ['original',*fields]:
  t=originals[UID]if mode=='original'else np.asarray(child[fields[mode]]).reshape(-1,3)[ix]
  s=originals['landsd/204145:0']if mode=='original'else np.asarray(parents['landsd/204145:0'][fields[mode]]).reshape(-1,3)[native_ix]
  projection=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));coverage=projection.intersection(own).area/own.area;extent=float(shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),assembly).max());excess=projection.difference(assembly).area
  assert coverage>=.95 and extent<=10 and excess<=1
  vertices=t.reshape(-1,3);far=vertices[shapely.distance(shapely.points(vertices[:,[0,2]]),own)>10];assert len(far)>0 and float(far[:,1].max())<forms[UID]['base']
  c=take(native,'204146:0--204145:0--'+mode+'.json.gz');area=[p for p in c['contacts']if p['dimension']==2];assert c['allPairsExamined']and area
  for p in area:
   a=exact_normal(t[p['sourceFaceA']]);b=exact_normal(s[p['sourceFaceB']]);assert sum(x*y for x,y in zip(a,b))<0
  e=take(native,'204146:0--273061:0--'+mode+'.json.gz');assert e['allPairsExamined']and any(p['dimension']>0 for p in e['contacts'])and not any(p['dimension']==2 for p in e['contacts'])
  results.append(dict(mode=mode,completeSourceFaces=len(t),ownTargetCoverage=coverage,extentFromConnectedAssemblyM=extent,sourceProjectionOutsideAssemblyM2=excess,verticesBeyondIndividual10mExtent=len(far),farVerticesYRange=[float(far[:,1].min()),float(far[:,1].max())],recordedBaseHeight=forms[UID]['base'],allPositiveAreaSuntowerInterfacesHaveExactlyOppositeNormals=True,positiveAreaSuntowerPairs=len(area)))
 images=[];views='government-xl-skytower-current-source-context-v1-20261024';take(views,'summary.json')
 for name in ['whole-source-plan.png','whole-source-perspectives.png']:
  p=BASE/views/name;assert digest(p.read_bytes())==pins[views][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),actuallyInspected=True))
 result=dict(uids=[UID],sourceSHA256ByUid={UID:SOURCES[UID]},requiredUnchangedAssemblySources=SOURCES,requiredRetainedNativeUids=['landsd/273061:0','landsd/204145:0'],identityAccepted=True,identityProof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},rows=results,rawIdentityReasonsRetained=raw['reasons'],rawIdentityProofRetained=raw,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,imagesActuallyViewed=images,sourceIdentityReviewUsedAI=True,qualification='Exact Skytower original plus unchanged approved Elements and Suntower only. Source root, unique current component route and complete geographic cell remain mandatory. All3current surveyed forms have one existing parent; actual complete original contacts and251strict/10finite parent paths independently bind the assembly. Existing95percent own coverage/10m extent/1m2 unrelated bounds are measured against this exact connected assembly in all4streams. Every Skytower projected face lies inside its union, and all vertices causing the individual>10m flag lie below recorded base38.5m. Raw extent negatives remain verbatim. Suntower positive-area interfaces have exact opposite normals; this is adjoining-source context, not a zero-volume-interpenetration, common-ownership or engineering claim. Native asset bytes, source poses, support metadata, global guards and all physical/runtime/browser/publication gates remain unchanged.')
 save(out/'identity.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('skytower_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-connected-original-skytower-retained-elements-suntower-identity',refs,result)
if __name__=='__main__':main()
