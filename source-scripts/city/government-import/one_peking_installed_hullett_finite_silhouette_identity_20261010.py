"""Named source-only finite foreign-silhouette identity evidence.

The already installed complete original Hullett mesh supplies its actual finite
projection in place of one conservative current basic footprint proxy. Ordinary
1m² foreign limit remains; no source ownership, support or collision exemption.
Fresh current-manifest/native/raw-preflight adapter remains independently required.
"""
import hashlib,json
from functools import reduce
import numpy as np
import shapely
from exact_original_component_contacts_20261009 import exact_component_contacts
OWN='landsd/233985:0';FOREIGN='landsd/73140:0'
EXPECTED_FORMS={'landsd/73140:0','landsd/211916:0','landsd/225163:0','landsd/233985:0','landsd/240487:0'}
CURRENT_FORMS_SHA='b56e5fef6c7903b7efae9d46c821f1f56eb1bb2ed7a1d913a822c4856dd3adee'
OWN_SHA='73c65ee4568e2feb34e51e379db43a189824eb71eebba995b13de9d5456e9331'
FOREIGN_SHA='de03f5a51ec4b294a3e5c7d3e924324dbc21709f648f33c7d69254e19f484bc1'
OWN_WORLD='792cea04e0655691549eaec5fdf0a2894856b042f41be47ae2db119759ece936'
FOREIGN_WORLD='ee17396eec04aaf4016813f2f39e01e12087d1efd8db418a9a41ac586a03c79b'
PRIMARY={OWN:('3551217446P20050810',1108247443,'Podium',1123632000000,'9672fa86aa1b88e361cdfdb2718cbe5915c493fb680cada71282f2a429881e08'),FOREIGN:('3555317380P20090225',1108247450,'Podium',1235520000000,'31d5d56448a710b30d2fa53a1db94bf02e0dc0ed98e7f2656b634a016b6b9001')}
EXPECTED_FACES=[881,882,883,884,885,1374,1375,1376,1377,1378,2161,2222,2631,2787,2788,3096,3097,3098,3099,3100,3284,3458,3459,3460,3461,3462,3561,3562,3563,3564,3711,3716,3717,3733,3734,3852]
def digest(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def polygon(rings):
 assert isinstance(rings,list) and rings
 ps=[shapely.Polygon(r) for r in rings];assert all(p.is_valid and not p.is_empty for p in ps)
 out=reduce(lambda a,b:a.symmetric_difference(b),ps);assert out.is_valid and out.area>0;return out
def projection(tri):
 ps=shapely.polygons(tri[:,:,[0,2]]);return shapely.union_all(ps[shapely.area(ps)>0])
def provider_polygon(feature):
 rings=feature['geometry']['rings'];return polygon([[[p[0]-834500,816500-p[1]] for p in r] for r in rings])
def verify(own_triangles,foreign_triangles,current_forms,primary_features,installed_entries,own_source_sha):
 own=np.asarray(own_triangles,dtype='<f8');foreign=np.asarray(foreign_triangles,dtype='<f8')
 assert own.shape==(4114,3,3) and foreign.shape==(32635,3,3)
 assert np.isfinite(own).all() and np.isfinite(foreign).all()
 assert own_source_sha==OWN_SHA and digest(own.tobytes())==OWN_WORLD and digest(foreign.tobytes())==FOREIGN_WORLD
 assert len(current_forms)==5 and {b['uid'] for b in current_forms}==EXPECTED_FORMS
 assert len({b['uid'] for b in current_forms})==len(current_forms)
 assert digest(canonical(sorted(current_forms,key=lambda b:b['uid'])))==CURRENT_FORMS_SHA
 by={b['uid']:b for b in current_forms}
 primary={}
 for uid,(csuid,bid,typ,date,geomsha) in PRIMARY.items():
  candidates=[f for f in primary_features if f['attributes'].get('BuildingCSUID')==csuid]
  assert len(candidates)==1;f=candidates[0];a=f['attributes']
  assert a['Status']=='Active' and a['BuildingID']==bid and a['BuildingBlockType']==typ and a['DateCreate']==date and a['GeoRefNo']==csuid[:10]
  assert digest(canonical(f['geometry']))==geomsha
  b=by[uid];assert b['buildingCSUID']==csuid and b['buildingId']==bid and b['structureType']==typ
  primary[uid]=f
 # Caller must independently bind complete live manifest/catalogues and runtime
 # mesh to these exact bytes. Merely presenting a same-name/permit basic does not qualify.
 assert len(installed_entries)==1;entry=installed_entries[0]
 assert entry['uid']==FOREIGN and entry['buildingCSUID']==PRIMARY[FOREIGN][0]
 assert entry['modelId']=='B355531738002063C0' and entry['sha256']==FOREIGN_SHA and entry['triangles']==32635
 assert entry['rootTranslation']==[-834500,0,816500]
 assert all(entry[k] is True for k in ['publicationApproved','placementReviewed','identityReviewApproved','sourceIdentityReviewed'])
 assert entry['proceduralWindows'] is False
 assert np.max(np.abs(np.asarray(entry['worldBounds'])-np.stack([foreign.min(axis=(0,1)),foreign.max(axis=(0,1))])))<=.002
 own_projection=projection(own);foreign_projection=projection(foreign)
 target=polygon(by[OWN]['rings']);other=polygon(by[FOREIGN]['rings']);excess=own_projection.difference(target)
 for label,p in [('current',target),('provider',provider_polygon(primary[OWN]))]:
  coverage=own_projection.intersection(p).area/p.area
  extent=shapely.hausdorff_distance(own_projection,own_projection.intersection(p))
  # Ordinary full-source coverage/extent. No cell, provenance or physical credit.
  assert coverage>=.95 and extent<=10,(label,coverage,extent)
 raw_excess=excess.intersection(other).area;assert raw_excess>1
 ids=[i for i,p in enumerate(shapely.polygons(own[:,:,[0,2]])) if p.difference(target).intersection(other).area>0]
 assert ids==EXPECTED_FACES
 all_other=[]
 for b in current_forms:
  if b['uid'] in [OWN,FOREIGN]:continue
  p=polygon(b['rings']);all_other.append(excess.intersection(p))
 # Every other current actor stays foreign, including the already-suppressed
 # historical compound part; no same-name, shared-parent, permit or contact exemption.
 effective=excess.intersection(foreign_projection)
 complete_effective_foreign=shapely.union_all([effective,*all_other]);assert complete_effective_foreign.area<=1
 provider_excess=own_projection.difference(provider_polygon(primary[OWN]));provider_others=[provider_excess.intersection(polygon(b['rings'])) for b in current_forms if b['uid'] not in [OWN,FOREIGN]]
 provider_effective=shapely.union_all([provider_excess.intersection(foreign_projection),*provider_others]);assert provider_effective.area<=1
 contacts=exact_component_contacts(own,ids,foreign,list(range(len(foreign))))
 positive=[c for c in contacts['contacts'] if c['dimension']>0];assert len(positive)==12
 return dict(role='one-peking-exact-already-installed-hullett-complete-finite-silhouette-identity-only',ownUID=OWN,foreignUID=FOREIGN,completeOwnFaces=4114,completeInstalledForeignFaces=32635,allCurrentForms=len(current_forms),allOriginalAffectedFaces=ids,rawCurrentBasicProxyForeignExcessM2=float(raw_excess),currentCompleteInstalledOriginalForeignExcessM2=float(effective.area),currentAllForeignEffectiveExcessM2=float(complete_effective_foreign.area),providerAllForeignEffectiveExcessM2=float(provider_effective.area),completeOriginalExactPositiveContacts=positive,ordinaryForeignLimitM2=1,foreignSilhouetteInterpretationPassed=True,sharedOwnershipClaim=False,sourceGeometryChanges=0,sourceSuppression=0,identityAccepted=False,physicalAccepted=False,collisionExemption=False,installation=False,qualification='One named current foreign basic proxy replaced only for identity interpretation by its already-installed byte-bound complete original source finite projection, under unchanged1m². Complete current/native/raw-cell binding adapter and every source/literal physical actor/terrain/foundation/support/collision/runtime gate remain required; positive source contacts grant no support or collision clearance.')
