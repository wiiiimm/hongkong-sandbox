"""UNAPPROVED policy draft. Pure identity-context assessment; no executable worker.

Neither named adjacency nor proper source crossings proves an exact joint, solid
clearance, ownership or support. Caller must supply a freshly verified ordinary
identity proof; this module cannot approve installation or physical gates.
"""
from copy import deepcopy
from hashlib import sha256
import gzip
import json
import numpy as np
import shapely
from original_source_ownership import document, graph_reasons
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

UID='landsd/12728:0'; ADJACENT='landsd/12662:0'
POLICY='DRAFT-upton-named-adjacent-original-roof-wall-identity-context-v1'
REPLACE=frozenset({'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'})
BASE='docs/astra-city/government-import/'
SOURCE=BASE+'government-xl-upton-podium12728-12662-original-foreign-conflict-proposal-v1-20261011/source-inputs.json'
CONTEXT=BASE+'government-xl-upton-podium12728-12662-original-boundary-context-v1-20261011/context.json'
RAW=BASE+'government-xl-upton-podium12728-12662-complete-original-foreign-conflict-attribution-v1-20261011/diagnostic.json.gz'
ROLES=BASE+'government-xl-upton-podium-boundary23-exact-roles-official-context-v1-20261011/diagnostic.json.gz'
PRIMARY_DIR=BASE+'government-xl-upton-podium-boundary23-exact-roles-official-context-v1-20261011/'
PINS={SOURCE:'519bb1c58bff91c4fcef38639fbc7e74c438df2eb8bbbfaa740eec8ab0ee3141',CONTEXT:'d051396632aadda72d1c5f5a8afc824f2b8dc67bd0b77d0b6c03488be8383d12',RAW:'bc2405505a9488f87b2276f8875f0e841388fa02e5d9e9c9743fdccdcfc0d719',ROLES:'77a1b2b11095791fdcb5c96a6f3ad1cadfece168a26b67d4687af57595300997',PRIMARY_DIR+'tpb-site-plan-reader1.pdf':'0d577e33c0d44ce2c7c8ec061b63e93932a43625d382c97d1021873985fc9628',PRIMARY_DIR+'tpb-site-plan-reader2.pdf':'0d577e33c0d44ce2c7c8ec061b63e93932a43625d382c97d1021873985fc9628',PRIMARY_DIR+'tpb-2022-page5-site-plan-original.png':'e23ffea8ba18ff16afad4c8634f29eb6284c3d92d5080555e6114668968c2c08'}
# UID: original source SHA, complete world SHA, CSUID, provider model, face count.
EXACT={UID:('4f177100defad797c23530d4577676041bcbc6f6ee79de026f2af01c112552d2','de9d2b8aac972078d0e5855f729db40d76f290bca57f88036a80024eef9be0f0','3217816493P20150615','B321781649302063C0',1655),ADJACENT:('de06028267854749aac25761395c83ccdd4b56c4813c23d14bdfd72a8598e5f0','7fe91a56a2d841c4587f58fed96e86bc29c9ce089c590030101c11f4b0024622','3213516497P20060312','B321351649702063C0',392)}

def digest(raw):return sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def read(root,path):
 raw=(root/path).read_bytes()
 return json.loads(gzip.decompress(raw) if path.endswith('.gz') else raw)
def ring_poly(form):
 p=shapely.Polygon()
 for ring in form['rings']:p=p.symmetric_difference(shapely.Polygon(ring))
 assert p.is_valid and p.area>0
 return p

def frozen_context(root):
 """Only existing immutable original/source/primary evidence; no DB/live reads."""
 for path,h in PINS.items():assert digest((root/path).read_bytes())==h, path
 source=read(root,SOURCE);context=read(root,CONTEXT);raw=read(root,RAW);roles=read(root,ROLES)
 assert roles['errors']==[] and roles['originalContactMathReplayed'] is False
 assert len(source['sources'])==2
 triangles={}
 for row in source['sources']:
  uid=row['uid'];s,w,c,m,n=EXACT[uid];asset=root/row['candidate']['path'];b=asset.read_bytes()
  assert digest(b)==s and row['modelId']==m and row['source']['building']['buildingCSUID']==c
  g=document(b);assert not graph_reasons(g,m,n)
  t=decode_original_world_triangles(b);assert t.shape==(n,3,3) and np.isfinite(t).all() and digest(t.astype('<f8').tobytes())==w
  ctx=next(x for x in context['providerRootContext'] if x['uid']==uid)
  assert ctx['originalRoot']==g['nodes'][g['scenes'][0]['nodes'][0]]
  assert ctx['sourceEntry']=='BUILDING/'+m+'/'+m+'.gltf' and ctx['sourceSHA256']==s
  triangles[uid]=t
 contacts=raw['allExactFiniteOriginalContacts'];records=roles['complete23ContactsRetained']
 assert len(contacts)==len(records)==23 and [x['originalContact'] for x in records]==contacts
 for r in records:
  c=r['originalContact'];assert c['dimension']==1 and not c['coplanar'] and c['bothRelativeInteriorCrossing'] and c['body12728']==c['body12662']==0
  assert not r['authoredBoundarySeamQualified'] and len(r['sourceFaceRoles'])==2
  for role in r['sourceFaceRoles']:
   assert not role['wholeContactOnIncidentTriangleEdge'] and not role['wholeContactOnMainBodyIndexedBoundary']
 # Roles/projection/contacts are bound by complete immutable diagnostic hashes,
 # not recomputed using a sparse subset or inferred from a photograph.
 return dict(source=source,context=context,raw=raw,roles=roles),triangles

def assess_draft(root,previous,forms,current,context,triangles):
 """DRAFT only. No acceptance result or mutation; fails closed on stale tuples.

current contains exact fresh ordinary-proof and complete-form canonical hashes,
manifestSHA256, and actual current file refs by labels below. A later reviewed
producer must independently verify Neon results/full current tuple at both ends.
"""
 expected,actual=frozen_context(root)
 assert context==expected and set(triangles)==set(EXACT)
 for uid in EXACT:assert np.array_equal(triangles[uid],actual[uid])
 assert previous['uid']==UID and previous['sourceSHA256']==EXACT[UID][0] and previous['worldTrianglesSHA256']==EXACT[UID][1]
 assert current['ordinaryProofCanonicalSHA256']==digest(canonical(previous)) and current['completeFormsCanonicalSHA256']==digest(canonical(forms))
 assert set(current['requiredFileRefs'])=={'manifest','runtimeClosure','nativeCatalogue','buildingSourceCatalogue'}
 for e in current['requiredFileRefs'].values():assert digest((root/e['path']).read_bytes())==e['sha256']
 assert current['requiredFileRefs']['manifest']['path']=='3d-viewer/city/data/manifest.json'
 assert current['manifestSHA256']==current['requiredFileRefs']['manifest']['sha256']==previous['exactRouteManifestSHA256']
 for path,h in previous['exactRouteTileHashes'].items():assert digest((root/'3d-viewer'/path).read_bytes())==h
 assert len(forms)==len({f['uid'] for f in forms})
 own=next(f for f in forms if f['uid']==UID);adjacent=next(f for f in forms if f['uid']==ADJACENT)
 assert own==previous['exactCurrentComponentRoute']['source']['building']
 assert previous['exactCurrentComponentRoute']['qualified'] and previous['freshCurrentIdentity']['exactObjectAndCSUID']
 for uid,f in [(UID,own),(ADJACENT,adjacent)]:
  assert f['buildingCSUID']==EXACT[uid][2] and f['structureType']=='Podium'
  record=next(x for x in context['roles']['officialStableCSUIDContexts'] if x['uid']==uid)
  a=record['activeAttributes'];assert a['Status']=='Active' and a['BuildingCSUID']==EXACT[uid][2] and a['BuildingID']==f['buildingId']
 # 2D OBJECTID renumbering never transfers provider source ownership or pose.
 assert previous['originalOwnership']['sourceGraphVerified'] and previous['modelGeometryChanges']==0
 assert previous['exactWholeCellCoverage']['covered'] and previous['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==1655
 assert len(previous['exactWholeCellCoverage']['halves'])==2
 for half in previous['exactWholeCellCoverage']['halves']:
  assert half['completeGroundSHA256']==EXACT[UID][1] and half['completeOriginalGroundTrianglesAccounted']==1655 and half['exactProjectionCovered'] and half['exactUncoveredAreaM2']=='0' and half['noToleranceOrBufferCredit']
 assert previous['geographicCell']['targetCoversWholeCell'] and previous['geographicCell']['originalProjectionCoversWholeCell']
 target=ring_poly(own);projection=shapely.union_all(shapely.polygons(triangles[UID][:,:,[0,2]]));adj_projection=shapely.union_all(shapely.polygons(triangles[ADJACENT][:,:,[0,2]]))
 others=[f for f in forms if f['uid'] not in {UID,ADJACENT} and not(f.get('parent') and f.get('parent')==own.get('parent'))]
 foreign=shapely.union_all([ring_poly(f) for f in others]) if others else shapely.Polygon()
 coverage=projection.intersection(target).area/target.area;extent=float(shapely.distance(shapely.points(triangles[UID][:,:,[0,2]].reshape(-1,2)),target).max())
 unrelated=projection.difference(target).intersection(foreign).area
 # Existing >=95%, <=10m and <=1m² ordinary limits; no widening.
 assert coverage>=.95 and extent<=10 and unrelated<=1
 # Raw named GIS overlap is preserved, not converted into solid clearance.
 named=projection.difference(target).intersection(ring_poly(adjacent)).area
 source_overlap=projection.intersection(adj_projection).area
 assert source_overlap<=1  # Additional source-envelope context, never collision pass.
 remaining=[r for r in previous['reasons'] if r not in REPLACE]
 return dict(policy=POLICY,draftOnly=True,draftContextQualified=not remaining,proposedIdentityReasons=remaining,rawOrdinaryIdentity=deepcopy(previous),proposedNamedReasonsReplaced=sorted(set(previous['reasons'])&REPLACE),namedAdjacentUID=ADJACENT,complete23ProperInteriorCrossingsRetained=deepcopy(context['roles']['complete23ContactsRetained']),completeSourceFacesRetained=2047,sourceEvidencePins=deepcopy(PINS),currentBinding=deepcopy(current),completeCurrentFormsRetained=deepcopy(forms),ordinaryWholeProjection=dict(targetCoverage=coverage,extentM=extent,allOtherUnrelatedExcessM2=unrelated),rawNamedGISExcessM2=named,originalSourceProjectedIntersectionM2=source_overlap,identityAccepted=False,physicalAccepted=False,installationApproved=False,sharedEdgeCredit=False,rootCredit=False,solidClearanceCredit=False,authoredExactJointEstablished=False,commonOwnershipClaim=False,engineeringOrLegalClaim=False,sourceGeometryChanges=0,relatedForeignPhysicalExemption=False,qualification='Proposed source-specific identity context only: separately named adjacent podium roof/wall surface representations. All23 real face-interior crossings and raw foreign GIS failure survive. Every source body, all other actors and whole current physical/foreign/terrain/four-stream gates remain mandatory. ROOT judgement and a separately reviewed fresh replay are required.')
