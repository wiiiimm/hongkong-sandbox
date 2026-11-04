"""Reproduce named finite-silhouette identity evidence against fresh current inputs.
Diagnostic only; raw identity flags/reasons, all collisions and physical gates remain.
"""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from one_peking_installed_hullett_finite_silhouette_identity_20261010 import verify,OWN,FOREIGN,OWN_SHA,FOREIGN_SHA,projection,polygon,provider_polygon,PRIMARY
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-one-peking-after-twin-';BATCH=P+'fresh-primary-finite-identity-diagnostic-v1-20261101'
RAW=['fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap']
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(P+'runtime-v1-20261101','selection.json.gz');source=next(r for r in selection['rows']if r['uid']==OWN);assert source['sourceSHA256']==OWN_SHA
 raw_identity=take(P+'identity-v1-20261101','233985:0/identity.json');assert not raw_identity['passed']and raw_identity['reasons']==RAW and raw_identity['freshCurrentIdentity']['exactObjectAndCSUID']is True
 current_target=raw_identity['freshCurrentIdentity']['target'];assert current_target['uid']==OWN and current_target['buildingCSUID']==source['source']['building']['buildingCSUID']
 scope=take(P+'complete-source-scope-v1-20261101','summary.json');assert scope['currentManifestSHA256']==selection['manifestSHA256']
 forms=[r['building']for r in take(P+'complete-source-scope-v1-20261101','233985:0-forms.json.gz')]
 attrs=take(P+'attributes-v1-20261101','attributes.json.gz');assert attrs['startEndAllInputsVerified'];own_attr=next(r for r in attrs['rows']if r['uid']==OWN)
 contacts=P+'installed-native-contacts-v1-20261101';native=next(r for r in take(contacts,'native-input.json.gz')['rows']if r['uid']==FOREIGN);nattrs=take(contacts,'native-attributes.json.gz');assert nattrs['startEndAllInputsVerified']and nattrs['productionCataloguePreparationReplayed'];foreign_attr=next(r for r in nattrs['rows']if r['uid']==FOREIGN)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());assert msha==selection['manifestSHA256'];refs.append(manifest)
 for a in [attrs,nattrs]:
  for path,sha in a['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 catalogues=[ROOT/'3d-viewer'/u for u in read(manifest)['officialModelCatalogues']];entries=[(e,c)for c in catalogues for e in read(c)['models']if e['uid']==FOREIGN];assert len(entries)==1 and entries[0][0]==native['entry'];refs.extend(catalogues)
 worlds={}
 for uid,attr,path,sha in [(OWN,own_attr,ROOT/source['candidate']['path'],OWN_SHA),(FOREIGN,foreign_attr,ROOT/native['path'],FOREIGN_SHA)]:
  assert digest(path.read_bytes())==sha==attr['sourceSHA256'];refs.append(path);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);worlds[uid]={'original':decode_original_world_triangles(path.read_bytes()),**{mode:np.asarray(attr[key],dtype='<f8').reshape(-1,3)[ix]for mode,key in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]}}
 out.mkdir();primary=module('one_peking_fresh_primary_fetch',HERE/'xl-man-fuk-man-oi-primary-relations-20261010.py');primary.DOC=out
 where="BuildingCSUID IN ('3551217446P20050810','3553717452T20050430','3555317380P20090225')";features=primary.query(0,where,'exact-current-primary',True);assert len(features)==3
 # Existing narrowly named verifier retains its exact source/form/primary geometry,
 # unchanged1m2limit and all12original contact witnesses. No general exception.
 named=verify(worlds[OWN]['original'],worlds[FOREIGN]['original'],forms,features,[native['entry']],OWN_SHA);assert named['foreignSilhouetteInterpretationPassed']and not named['identityAccepted']and not named['collisionExemption']
 own_feature=next(f for f in features if f['attributes']['BuildingCSUID']==PRIMARY[OWN][0]);measurements=[]
 for mode in ['original','literal','leftF32','balancedF32']:
  a=worlds[OWN][mode];b=worlds[FOREIGN][mode];ap=projection(a);bp=projection(b)
  for target_name,target in [('current',polygon(source['source']['building']['rings'])),('provider',provider_polygon(own_feature))]:
   excess=ap.difference(target);others=[excess.intersection(polygon(f['rings']))for f in forms if f['uid']not in [OWN,FOREIGN]]
   import shapely
   effective=shapely.union_all([excess.intersection(bp),*others]);assert effective.area<=1,(mode,target_name,effective.area)
   measurements.append(dict(mode=mode,target=target_name,allForeignEffectiveExcessM2=float(effective.area),sourceWorldSHA256=digest(a.astype('<f8').tobytes()),installedForeignWorldSHA256=digest(b.astype('<f8').tobytes())))
 assert digest(manifest.read_bytes())==msha
 result=dict(uids=[OWN,FOREIGN],sourceSHA256ByUid={OWN:OWN_SHA,FOREIGN:FOREIGN_SHA},currentManifestSHA256=msha,currentNativeActorsChecked=next(r['currentNativeActorsChecked']for r in scope['rows']if r['uid']==OWN),rawIdentity=raw_identity,rawIdentityFlagsPreserved=True,rawReasonsReconsideredOnly=RAW,currentTargetObjectAndCSUIDVerified=True,allOriginalAndActualFourWorldInputsVerified=True,completeCurrentForeignEntry=native['entry'],namedFiniteSilhouette=named,currentEightModeTargetMeasurements=measurements,providerObjectIds={f['attributes']['BuildingCSUID']:f['attributes']['OBJECTID']for f in features},freshProviderObjectIdsClaimedEqualToLegacyViewerIds=False,ordinaryForeignLimitM2=1,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,collisionExemption=False,installationApproved=False,publication=False,qualification=__doc__+' Reproduces narrow named projection evidence under the existing limit, with current production geometry and fresh primary records. Positive identity review and every current terrain/support/collision/runtime/browser gate remain separate.')
 save(out/'summary.json',result);refs.extend([HERE/'one_peking_installed_hullett_finite_silhouette_identity_20261010.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-man-fuk-man-oi-primary-relations-20261010.py']);module('one_peking_current_primary_diagnostic_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-current-exact-original-finite-silhouette-identity-evidence-no-approval',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
