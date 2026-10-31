"""Narrow reviewed original exterior wall roles; no whole-building acceptance.

Ordinary/upward faces retain strict continuous clearance. Original open winding
is preserved, not certified closed. Foreign actor scope cannot be omitted.
"""
import hashlib
import numpy as np
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
from unchanged_open_exterior_paths_v2_20261009 import original_open_paths
from original_coplanar_exterior_continuation_20261009 import diagnose
from unchanged_closed_column_role_v2_20261009 import canonical_sha
from exact_original_shell_intersections_20261009 import intersection_points,rational_face

def verify_wall_role(triangles,ground,contexts,*,expected_binding,current_binding,expected_role,foreign_scope):
 tri=np.asarray(triangles,float);ground=np.asarray(ground,float)
 assert tri.ndim==3 and tri.shape[1:]==(3,3) and np.isfinite(tri).all()
 assert ground.ndim==3 and ground.shape[1:]==(3,3) and len(ground) and np.isfinite(ground).all()
 assert expected_binding==current_binding and expected_binding
 assert current_binding['decodedWorldTrianglesSHA256']==hashlib.sha256(tri.tobytes()).hexdigest()
 assert current_binding['drawnGroundSHA256']==hashlib.sha256(ground.tobytes()).hexdigest()
 assert current_binding['continuousFaceContextsSHA256']==canonical_sha(contexts)
 assert expected_role['role']=='original-provider-exterior-ground-crossing-walls'
 assert expected_role['sourceSHA256']==current_binding['sourceSHA256']
 assert expected_role['originalFaceCount']==len(tri)
 assert expected_role['providerExteriorProvenanceBinding'],'Missing positive original provider exterior provenance'
 assert current_binding['reviewedOriginalWallRoleSHA256']==canonical_sha(expected_role)
 assert len(contexts)==len(tri) and [c['sourceFace'] for c in contexts]==list(range(len(tri)))
 assert all(c['groundProjectionCovered'] and c['minimum'] for c in contexts),'Missing whole-face ground context'
 affected=[i for i,c in enumerate(contexts) if c['minimum']['minimumGapM']<-.5]
 assert affected and affected==expected_role['wallFaces'],'Unclassified or changed original failing faces'
 paths=original_open_paths(tri,contexts,affected,range(len(tri)),expected_binding=expected_binding,current_binding=current_binding)
 reasons=[]
 # Preserve the original per-triangle exposure failures. A separately bound,
 # exact coplanar original sheet may cross the ground beyond that authored cut.
 below=[r['sourceFace'] for r in paths['faces'] if r['reasons']==['no-exposed-wall-witness']]
 continuation=diagnose(tri,contexts,below) if below else {'rows':[],'wholeOriginalFacesAccounted':len(tri),'diagnosticOnly':True}
 expected_groups=expected_role.get('exactCoplanarExteriorContinuationGroups',{})
 assert set(map(int,expected_groups))==set(below),'Unreviewed or stale exterior sheet role'
 accepted=set()
 for row in continuation['rows']:
  i=row['sourceFace'];faces=expected_groups.get(str(i),expected_groups.get(i))
  assert faces==row['exactConnectedCoplanarSheetFaces'],'Changed original coplanar sheet membership'
  if row['hasActualAboveGroundExteriorContinuation']:accepted.add(i)
 if any(r['reasons'] and not(r['sourceFace'] in accepted and r['reasons']==['no-exposed-wall-witness']) for r in paths['faces']):reasons.append('affected-original-face-has-no-ground-crossing-wall-roof-role')
 # Every non-role face, including collapsed original lines/points, remains strict.
 assert all(contexts[i]['minimum']['minimumGapM']>=-.5 for i in set(range(len(tri)))-set(affected))
 normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1)
 ratio=np.divide(normal[:,1],length,out=np.zeros(len(tri)),where=length>0)
 if any(length[i]==0 or abs(ratio[i])>.25 for i in affected):reasons.append('buried-original-face-is-not-steep-exterior-wall')
 if any(c['minimum']['minimumGapM']<-.5 for i,c in enumerate(contexts) if ratio[i]>.25):reasons.append('buried-upward-original-surface')
 assert foreign_scope and foreign_scope['completeCurrentActorScope'],'Missing complete current foreign scope'
 boundary=foreign_scope['currentGroupBoundaryBinding'];assert boundary
 assert boundary['candidateUID']==expected_role['uid'] and boundary['ownedUIDs']==[expected_role['uid']]
 assert boundary['manifestSHA256'] and boundary['currentFormInputHashes'] and boundary['nativeCatalogueInputHashes']
 actors=foreign_scope['actors'];manifest=foreign_scope['expectedActorManifest']
 expected_uids=set(boundary['currentScopeUIDs'])-set(boundary['ownedUIDs'])
 assert len({a['uid'] for a in actors})==len(actors) and {a['uid'] for a in actors}==expected_uids,'Omitted or repeated current actor'
 pieces=[]
 for face in tri[affected]:
  xz=face[:,[0,2]];p=Polygon(xz)
  pieces.append(p if p.area>0 else LineString(xz) if len(set(map(tuple,xz)))>1 else Point(xz[0]))
 projection=unary_union(pieces);actual=[];separation=[];hits=[]
 for actor in actors:
  mode=actor.get('proofType','exact-world-triangles');uid=actor['uid'];source=actor['currentSourceBinding'];assert source
  if mode=='current-basic-full-footprint':
   rings=actor['originalCurrentRings'];polygon=Polygon(rings[0],rings[1:]);assert polygon.is_valid and polygon.area>0
   assert polygon.disjoint(projection),'Current basic footprint intersects credited wall; exact runtime mesh required'
   record={'uid':uid,'proofType':mode,'originalCurrentRingsSHA256':canonical_sha(rings),'currentSourceBinding':source}
   separation.append({'uid':uid,'proofType':mode,'projectionDistanceM':polygon.distance(projection)})
  elif mode=='complete-original-native-bounds':
   bounds=np.asarray(actor['originalWholeSourceBounds'],float);assert bounds.shape==(2,3) and np.isfinite(bounds).all() and (bounds[1]>=bounds[0]).all()
   assert all(np.any(bounds[0]>face.max(axis=0)) or np.any(bounds[1]<face.min(axis=0)) for face in tri[affected]),'Native whole bounds touch credited wall; complete original export required'
   record={'uid':uid,'proofType':mode,'originalWholeSourceBoundsSHA256':canonical_sha(bounds.tolist()),'currentSourceBinding':source};separation.append({'uid':uid,'proofType':mode,'wholeBoundsStrictlyDisjointFromEveryCreditedWall':True})
  elif mode=='exact-world-triangles':
   mesh=np.asarray(actor['worldTriangles'],float);assert mesh.ndim==3 and mesh.shape[1:]==(3,3) and len(mesh) and np.isfinite(mesh).all()
   record={'uid':uid,'worldTrianglesSHA256':hashlib.sha256(mesh.tobytes()).hexdigest(),'currentSourceBinding':source}
   lo=mesh.min(axis=1);hi=mesh.max(axis=1)
   for i in affected:
    face=tri[i];candidates=np.flatnonzero(np.all(hi>=face.min(axis=0),axis=1)&np.all(lo<=face.max(axis=0),axis=1))
    for j in candidates:
     if intersection_points(rational_face(face),rational_face(mesh[j])):hits.append({'uid':uid,'sourceFace':i,'foreignFace':int(j)})
  else:raise AssertionError('Unsupported complete foreign evidence mode')
  actual.append(record)
 assert sorted(actual,key=lambda r:r['uid'])==sorted(manifest,key=lambda r:r['uid']),'Changed current actor evidence'
 scope={k:foreign_scope[k] for k in ['completeCurrentActorScope','expectedActorManifest','currentGroupBoundaryBinding']}
 assert current_binding['currentForeignScopeSHA256']==canonical_sha(scope)
 if hits:reasons.append('credited-original-wall-intersects-foreign-runtime-geometry')
 return {'contract':'unchanged-authored-exact-coplanar-exterior-sheet-wall-v1','verifiedWallRole':not reasons,'reasons':reasons,'sourceSpecificOriginalRole':expected_role,'completeSourceFaces':len(tri),'ordinaryStrictFaces':len(tri)-len(affected),'creditedWallFaces':affected,'originalOpenPaths':paths,'exactOriginalCoplanarExteriorContinuation':continuation,'creditedBelowFaceOriginalSheets':sorted(accepted),'foreignIntersections':hits,'strictlySeparatedActors':separation,'completeCurrentForeignScope':scope,'rawClearanceFailingFacesRetained':affected,'closedSolidCertified':False,'sourceGeometryChanges':0,'installationApproved':False,'qualification':'Source-specific exact coplanar exterior sheet ground-crossing role only; raw individual-triangle exposure failures are preserved and exact connected above-ground original continuation is independently bound.  source, terrain, support, complete ordinary/native neighbours and runtime/browser/publication remain independent.'}
