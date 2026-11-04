"""Complete untouched Garden tower terrace and same-OP original podium context."""
import json,numpy as np,shapely
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
from source_closed_components import components
DOC=ROOT/'docs/astra-city/government-import/government-xl-garden-common-op-original-terrace-context-20261010'
BASE=DOC.parent

def polygon(rings):
 p=shapely.Polygon()
 for r in rings:p=p.symmetric_difference(shapely.Polygon(r))
 assert p.is_valid and p.area>0
 return p

def main():
 assert not DOC.exists()
 paths=[BASE/'xl-terrain-recovery-20261010-garden-two-foreign-current-inputs-v1/check-selection.json.gz',BASE/'xl-terrain-recovery-20261010-garden-terrace-podium-current-inputs-v1/check-selection.json.gz',BASE/'government-xl-garden-current-primary-identity-context-20261010/primary-context.json.gz',BASE/'government-xl-garden-exact-structure-permits-20261010/structure-context.json']
 own=next(r for r in read(paths[0])['rows'] if r['uid']=='landsd/109491:0');pod=next(r for r in read(paths[1])['rows'] if r['uid']=='landsd/162285:0');arrays=[]
 for r in [own,pod]:
  p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];paths.append(p);arrays.append(decode_original_world_triangles(raw))
 a,b=arrays;top=components(a);assert len(a)==10726 and len(b)==1418 and len(top['components'])==262
 ids=top['components'][0]['faceIndices'];assert len(ids)==96;plate=a[ids];proj=shapely.union_all(shapely.polygons(plate[:,:,[0,2]]));whole=shapely.union_all(shapely.polygons(a[:,:,[0,2]]));pproj=shapely.union_all(shapely.polygons(b[:,:,[0,2]]));primary=read(paths[2]);pfeature=next(f for f in primary['primaryRecords'] if f['attributes']['BuildingCSUID']=='3395615206P20060312');provider=polygon([[(x-834500,816500-y) for x,y in ring] for ring in pfeature['geometry']['rings']]);current=polygon(primary['currentGardenPodium']['building']['rings']);ownshape=polygon(own['source']['building']['rings']);far=np.flatnonzero(shapely.distance(shapely.points(a[:,:,[0,2]].reshape(-1,2)),ownshape).reshape(len(a),3).max(1)>10).tolist();assert set(far)<=set(ids)
 contacts=exact_component_contacts(a,ids,b,range(len(b)),maximum_pairs=1000000)
 owncontacts=exact_component_contacts(a,ids,a,[i for i in range(len(a)) if i not in set(ids)],maximum_pairs=1000000)
 metrics={}
 for label,q in [('currentPodium',current),('primaryPodium',provider),('originalPodiumProjection',pproj)]:
  metrics[label]={'plateProjectionM2':float(proj.area),'plateOutsideM2':float(proj.difference(q).area),'plateCoveredFraction':float(proj.intersection(q).area/proj.area),'maximumPlateVertexDistanceM':float(shapely.distance(shapely.points(plate[:,:,[0,2]].reshape(-1,2)),q).max()),'farFacesOutsideM2':float(shapely.union_all(shapely.polygons(a[far][:,:,[0,2]])).difference(q).area)}
 out={'ownUid':own['uid'],'podiumUid':pod['uid'],'ownSourceSHA256':own['sourceSHA256'],'podiumSourceSHA256':pod['sourceSHA256'],'ownCompleteWorldSHA256':digest(a.astype('<f8').tobytes()),'podiumCompleteWorldSHA256':digest(b.astype('<f8').tobytes()),'ownCompleteFaces':len(a),'ownCompleteParts':len(top['components']),'podiumCompleteFaces':len(b),'completeTerraceComponentId':0,'completeTerraceFaceIds':ids,'completeTerraceTriangles':plate.tolist(),'allFarFaceIds':far,'allFarTriangles':a[far].tolist(),'wholeSourceProjectionM2':float(whole.area),'metrics':metrics,'completeTerraceToWholeOriginalPodiumContacts':contacts,'completeTerraceToWholeOwnRemainderContacts':owncontacts,'completePrimaryPodiumFeature':pfeature,'completeCurrentPodiumForm':primary['currentGardenPodium']['building'],'exactPermitContext':read(paths[3]),'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in paths+[Path(__file__)]},'identityAccepted':False,'physicalAccepted':False,'qualification':'Complete source-owned terrace context with independent exact OP records; no legal ownership or load-bearing/support/foreign physical exemptions.'}
 save(DOC/'diagnostic.json.gz',out)
 print(json.dumps({'metrics':metrics,'podiumPositiveContacts':sum(c['dimension']>0 for c in contacts['contacts']),'ownPositiveContacts':sum(c['dimension']>0 for c in owncontacts['contacts']),'faces':len(ids),'farFaces':len(far)}),flush=True)
if __name__=='__main__':main()
