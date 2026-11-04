"""Fresh exact-source/current-installed finite silhouette identity adapter only.
Replays ordinary raw identity. Reconsiders only two named footprint-proxy reasons,
using the complete installed foreign source. Physical/collision gates stay separate.
"""
from copy import deepcopy
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,digest,connect,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from guarded_original_exact_cell_identity_v1_20261023 import apply_exact_cell
from routed_original_cell_identity import verify as routed_verify
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
from one_peking_fresh_finite_silhouette_identity_v1_20261101 import verify,OWN,FOREIGN,OWN_SHA,FOREIGN_SHA,polygon,provider_polygon,projection
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-one-peking-after-twin-'
RAW=['fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'];MODES=['original','literal','leftF32','balancedF32']

def accept_named(raw,named,measurements):
 assert raw['uid']==OWN and raw['sourceSHA256']==OWN_SHA and raw['passed']is False and raw['reasons']==RAW
 assert named['foreignSilhouetteInterpretationPassed']and named['identityAccepted']is False and named['physicalAccepted']is False and named['collisionExemption']is False
 assert named['ownUID']==OWN and named['foreignUID']==FOREIGN and named['ordinaryForeignLimitM2']==1
 assert len(measurements)==32 and {(r['ownMode'],r['foreignMode'],r['target'])for r in measurements}=={(a,b,c)for a in MODES for b in MODES for c in ['current','provider']}
 assert all(np.isfinite(r['allForeignEffectiveExcessM2'])and 0<=r['allForeignEffectiveExcessM2']<=1 for r in measurements)
 proof=deepcopy(raw);proof.update(passed=True,reasons=[],identityAccepted=True,rawFullCellIdentity=deepcopy(raw),namedIdentityOnlyReasonsReplaced=RAW,namedFiniteSilhouette=named,completeThirtyTwoWorldTargetMeasurements=measurements,physicalAccepted=False,collisionExemption=False,installationApproved=False,sourceGeometryChanges=0,freshProviderObjectIdsClaimedEqualToLegacyViewerIds=False)
 return proof

def replay_complete_current(row,context,selection):
 # Reproduce the CURRENT selected_original_identity_v3 pipeline, including its
 # complete-record projection and full two-source territory route. The older
 # verify_files shim follows a different projection/route representation.
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']
 final=module('peking_fresh_complete_record_context',HERE/'xl-final-script-pass.py');final.projection=lambda faces:shapely.union_all(shapely.polygons(np.asarray(faces)[:,:,[0,2]]))
 sources=[];route_hashes={};prefixes={r['modelId'][1:11]for r in selection['rows']}
 for tile in read(manifest)['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];raw=path.read_bytes();matching=[f for f in read(path)['buildings']if str(f.get('buildingCSUID')or'')[:10]in prefixes]
  if matching:route_hashes[tile['url']]=digest(raw);sources.extend(dict(building=f,tile=tile['url'],tileSHA256=digest(raw))for f in matching)
 raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);assert len(tri)==row['triangles']
 lo,hi=tri.min((0,1)),tri.max((0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);current=dict(sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,forms),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms});assert current==context
 routed=routed_verify(raw,row,current,tri,current_identity=current['identity'],sources=[s for s in sources if str(s['building'].get('buildingCSUID')or'')[:10]==row['modelId'][1:11]])
 binding=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],decodedWorldTrianglesSHA256=digest(tri.astype('<f8').tobytes()));proof=apply_exact_cell(routed,tri,expected_binding=binding,current_binding=binding);proof.update(exactRouteManifestSHA256=selection['manifestSHA256'],exactRouteTileHashes=route_hashes,completeRecordProjection=True)
 assert digest(manifest.read_bytes())==selection['manifestSHA256']
 for tile,sha in route_hashes.items():assert digest((ROOT/'3d-viewer'/tile).read_bytes())==sha
 return proof

def verify_files(row,context,local):
 pins={};refs=[]
 def take(batch,path):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(P+'runtime-v1-20261101',BASE/(P+'runtime-v1-20261101')/'selection.json.gz');expected=next(r for r in selection['rows']if r['uid']==row['uid']);assert row==expected
 ctx=take(P+'identity-v1-20261101',BASE/(P+'identity-v1-20261101')/row['uid'].split('/')[1]/'context.json');assert context==ctx
 old=take(P+'identity-v1-20261101',BASE/(P+'identity-v1-20261101')/row['uid'].split('/')[1]/'identity.json');raw=replay_complete_current(row,context,selection);assert raw==old,'Full raw current identity changed'
 manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());assert msha==selection['manifestSHA256'];refs.append(manifest)
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');source=db.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()
 assert source and source[0]==row['native']['resultSha']and next(m for m in source[1]['models']if m['modelId']==row['modelId'])==row['native']['model']
 if row['uid']!='landsd/233985:0':assert raw['passed'];return dict(raw,currentBinding=dict(manifestSHA256=msha,evidenceRefs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in set(refs)]))
 assert row['sourceSHA256']==OWN_SHA
 diagnostic=take(P+'fresh-primary-finite-identity-diagnostic-v2-20261101',BASE/(P+'fresh-primary-finite-identity-diagnostic-v2-20261101')/'summary.json');assert diagnostic['currentManifestSHA256']==msha and diagnostic['rawIdentity']==raw and diagnostic['allOriginalAndActualFourWorldInputsVerified']and diagnostic['currentNativeActorsChecked']==7069
 scope=take(P+'complete-source-scope-v1-20261101',BASE/(P+'complete-source-scope-v1-20261101')/'233985:0-forms.json.gz');forms=[r['building']for r in scope]
 final=module('peking_fresh_identity_forms',HERE/'xl-final-script-pass.py');tri=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());lo,hi=tri.min((0,1)),tri.max((0,1));current=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);assert forms==[b for b,_,_ in current]
 refs.extend(ROOT/'3d-viewer'/url for _,_,url in current)
 entries=[]
 for url in read(manifest)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;refs.append(path)
  for e in read(path)['models']:
   if e['uid']==FOREIGN:entries.append((e,path.parent/e['asset']))
 assert len(entries)==1;foreign,foreignpath=entries[0];assert foreign==diagnostic['completeCurrentForeignEntry']and digest(foreignpath.read_bytes())==FOREIGN_SHA;refs.append(foreignpath)
 attrs=take(P+'attributes-v1-20261101',BASE/(P+'attributes-v1-20261101')/'attributes.json.gz');nattrs=take(P+'installed-native-contacts-v1-20261101',BASE/(P+'installed-native-contacts-v1-20261101')/'native-attributes.json.gz');worlds={}
 for uid,sha,path,attributes in [(OWN,OWN_SHA,ROOT/row['candidate']['path'],attrs),(FOREIGN,FOREIGN_SHA,foreignpath,nattrs)]:
  assert attributes['startEndAllInputsVerified'];a=next(r for r in attributes['rows']if r['uid']==uid);assert a['sourceSHA256']==sha==digest(path.read_bytes());refs.append(path)
  for name,h in attributes['inputHashes'].items():assert digest((ROOT/name).read_bytes())==h;refs.append(ROOT/name)
  ix=np.asarray(a['completeOriginalIndex']).reshape(-1,3);worlds[uid]=dict(original=decode_original_world_triangles(path.read_bytes()),**{mode:np.asarray(a[field],dtype='<f8').reshape(-1,3)[ix]for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]})
 revision=P+'fresh-primary-revision-context-v1-20261101';take(revision,BASE/revision/'summary.json');primarypath=BASE/(P+'fresh-primary-finite-identity-diagnostic-v1-20261101')/'exact-current-primary.json';assert digest(primarypath.read_bytes())==pins[revision][str(primarypath.relative_to(ROOT))];refs.append(primarypath);features=read(primarypath)['features'];named=verify(worlds[OWN]['original'],worlds[FOREIGN]['original'],forms,features,[foreign],OWN_SHA)
 own_feature=next(f for f in features if f['attributes']['BuildingCSUID']=='3551217446P20050810');measurements=[]
 for am in MODES:
  for bm in MODES:
   own=worlds[OWN][am];fp=projection(worlds[FOREIGN][bm]);op=projection(own)
   for target_name,target in [('current',polygon(row['source']['building']['rings'])),('provider',provider_polygon(own_feature))]:
    excess=op.difference(target);foreign_union=shapely.union_all([excess.intersection(fp),*[excess.intersection(polygon(f['rings']))for f in forms if f['uid']not in [OWN,FOREIGN]]]);measurements.append(dict(ownMode=am,foreignMode=bm,target=target_name,allForeignEffectiveExcessM2=float(foreign_union.area)))
 proof=accept_named(raw,named,measurements);assert digest(manifest.read_bytes())==msha;refs.extend([HERE/'one_peking_fresh_finite_silhouette_identity_v1_20261101.py',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'routed_original_cell_identity.py',HERE/'guarded_original_exact_cell_identity_v1_20261023.py',HERE/'selected_original_identity_v3_20261023.py'])
 proof['currentBinding']=dict(manifestSHA256=msha,currentNativeActors=7069,fullRawIdentityRecomputed=True,originalNativeRunSourceMembershipVerified=True,currentSourceFormsExact=True,completeInstalledForeignEntry=foreign,freshPrimaryRevisionVerified=True,evidenceRefs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in sorted(set(refs))])
 return proof
