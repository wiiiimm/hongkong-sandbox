"""Bound exact three-source/podium association; never approve physics/publication."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-parc-palais-three-';BATCH=P+'shared-podium-identity-v2-20261024';PARENT='landsd/266063:0'
SOURCES={'landsd/238669:0':'ff0f3b80ffb448a3c2a800e723dcd905b71bef82d68ebd527fe5347e0ccc1bb0','landsd/238671:0':'e5cb9cd513a1fb3882a9f21e07d7b1ba8a151a360d9c996fd2fb5349ca7253d4','landsd/238856:0':'e9d01d1a9b88d9ee1494ef64997ed633e1bfc574344a666e23cae4f5904319ef'}
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(P+'runtime-v1-20261024','selection.json.gz');assert{r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
 scope=take(P+'model-scope-v1-20261024','summary.json');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==scope['currentManifestSHA256'];refs.append(manifest)
 forms={}
 for uid in SOURCES:
  for f in take(P+'model-scope-v1-20261024',uid.split('/')[1]+'-forms.json.gz'):
   path=ROOT/'3d-viewer'/f['tile'];assert digest(path.read_bytes())==f['tileSHA256']and next(b for b in read(path)['buildings']if b['uid']==f['building']['uid'])==f['building'];refs.append(path);forms[f['building']['uid']]=f['building']
 assert set(forms)==set(SOURCES)|{PARENT}
 polygon=lambda uid:shapely.Polygon(forms[uid]['rings'][0],forms[uid]['rings'][1:]);parentpoly=polygon(PARENT)
 parents=[]
 for url in read(manifest)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url
  for e in read(path)['models']:
   if e['uid']==PARENT:parents.append(e);refs.append(path);asset=path.parent/e['asset'];assert digest(asset.read_bytes())==e['sha256'];refs.append(asset)
 assert len(parents)==1 and parents[0]['triangles']==35028 and parents[0]['buildingCSUID']==forms[PARENT]['buildingCSUID']
 pairs=take(P+'pairs-v1-20261024','summary.json');assert pairs['sourceSHA256ByUid']==SOURCES and pairs['completeUnorderedPairs']==3 and len(pairs['rows'])==12
 for uid in ['landsd/238669:0','landsd/238856:0']:
  joint=[r for r in pairs['rows']if{r['uid'],r['peerUid']}=={uid,'landsd/238671:0'}];assert len(joint)==4 and all(not r['strictBoundsSeparated']and r['positiveSurfaceContacts']>0 for r in joint)
 native=take(P+'native-contacts-v1-20261024','summary.json');assert len(native['rows'])==3
 rows=[]
 for row in selection['rows']:
  uid=row['uid'];raw=take(P+'identity-v1-20261024',uid.split('/')[1]+'/identity.json');assert raw['sourceSHA256']==SOURCES[uid]and raw['originalOwnership']['sourceGraphVerified']and raw['originalOwnership']['originalRootName']==row['modelId']and raw['exactCurrentComponentRoute']['qualified']and raw['exactWholeCellCoverage']['covered']and raw['completeRecordProjection']
  expected={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}if uid=='landsd/238671:0'else set();assert set(raw['reasons'])==expected
  n=next(r for r in native['rows']if r['uid']==uid);assert n['nativeUid']==PARENT and n['sourceSHA256']==SOURCES[uid]and n['nativeSHA256']==parents[0]['sha256']and n['rawCurrentNativeEntry']==parents[0];assert{m['mode']for m in n['modes']}=={'original','literal','leftF32','balancedF32'}and all(m['positiveSurfaceContactPairs']>0 for m in n['modes'])
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[uid];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==row['triangles'];projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));target=polygon(uid);excess=projection.difference(target);coverage=projection.intersection(target).area/target.area;extent=float(shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),target).max());outside=float(excess.difference(parentpoly).area)
  assert coverage>=.95 and extent<=10
  if uid=='landsd/238671:0':assert outside==0
  else:assert raw['passed']and not raw['reasons']
  rows.append(dict(uid=uid,sourceSHA256=SOURCES[uid],completeOriginalFaces=len(tri),ownTargetCoverage=coverage,completeVertexMaximumExtentM=extent,excessAreaM2=float(excess.area),excessOutsideExactInstalledPodiumM2=outside,rawReasonsRetained=raw['reasons'],identityAccepted=True,proof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']}))
 diagrams=P+'original-context-v1-20261024'
 for file in ['complete-original-assembly.png','base-only-diagnostic.png']:
  if diagrams not in pins:pins[diagrams]=authenticate(BASE/diagrams)[1];refs.append(BASE/diagrams/'result.json')
  path=BASE/diagrams/file;assert digest(path.read_bytes())==pins[diagrams][str(path.relative_to(ROOT))];refs.append(path)
 result=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,requiredUnchangedAssembly=SOURCES,requiredInstalledPodiumUid=PARENT,requiredInstalledPodiumEntry=parents[0],rows=rows,identityAccepted=True,reviewer='ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,interpretation='Only these three exact separately routed authored tower sources and this unchanged installed podium. Every source passes its own complete GeoRef cell, unique IDs/root ownership,95percent own footprint and10m complete-vertex extent. Block2 projected extensions stay inside the exact podium footprint; the other two retain their existing passing individual identities. Current scope consists only of the three towers and that podium. Complete original joint and lower-joint diagrams were inspected. Block2 two raw unrelated-overlap flags concern the other explicitly included original tower footprints within this podium; this source-association review does not assert common property ownership or clear peer collisions/embedding. All raw source/source and source/podium contacts, actual-ground/whole-face clearance, visual recovery, retained supports and publication remain independent requirements.')
 save(out/'identity.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('parc_compound_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-three-original-shared-installed-podium-source-association',refs,result)
if __name__=='__main__':main()
