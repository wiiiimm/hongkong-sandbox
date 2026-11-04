"""Bounded source-wall interpretation; never whole-model/terrain acceptance."""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-elegant-garden-four-wall-role-v1-20261027';P='government-xl-elegant-garden-';FACES=[10385,10388,10389,10506]
SOURCES={'landsd/173532:0':'d6f98cee5009a166605a167130796583594e997913853f5b052e4b184bba4852','landsd/236170:0':'fad45b9cd6a3e7a71eeb09832ed70b74f51979f10bd5c4b21428499780d87635'}
def verify(mode,foundation,paths,view,raw):
 assert all(r['mode']==mode for r in [foundation,paths,view,raw])
 assert foundation['excludedSourceFaces']==view['sourceFaces']==FACES
 assert foundation['ordinarySourceFaces']==[i for i in range(10893)if i not in FACES]
 ordinary=foundation['ordinaryFoundation'];wall=foundation['fourWallFoundation']
 assert ordinary['triangles']==ordinary['completeTerrainTriangles']==10889 and ordinary['fullyBuriedTriangles']==ordinary['fullyBuriedUpwardTriangles']==0 and ordinary['minimumGapM']>=-.5
 assert wall['triangles']==4 and wall['fullyBuriedTriangles']==wall['fullyBuriedUpwardTriangles']==0
 assert len(view['unitNormals'])==4 and all(abs(n[1])<.01 for n in view['unitNormals'])
 assert 21.60<view['minimumY']<21.62 and 22.64<view['maximumY']<22.66
 assert raw['support']['maximumEmbeddingM']==.5 and raw['passed']is False and raw['support']['strictContacts']==112
 assert len(paths['rows'])==7 and [r['witness']for r in paths['rows']]==raw['support']['unresolved']
 for row in paths['rows']:
  assert row['hasUnrestrictedFiniteAttachment']and row['passesExistingEndpointHeight']and row['riseAboveEndpointsM']==0 and row['maximumResidualM']<=.001
  assert set(row['faces'])<=set(FACES) and row['supportApproved']is False
  contact=row['terminal']['contact'];assert contact['dimension']>0 and contact['sourcePrimitiveDimensionA']==contact['sourcePrimitiveDimensionB']==2
 assert raw['compoundFoundation']==foundation['rawWholeFoundation']and raw['compoundFoundation']['fullyBuriedTriangles']==raw['compoundFoundation']['fullyBuriedUpwardTriangles']==0
 return True

def main():
 p=argparse.ArgumentParser();p.add_argument('--lease',required=True);a=p.parse_args();lease=read(Path(a.lease));assert reservations.owns(lease)and {'building:'+u for u in SOURCES}<=set(lease['resources'])
 out=BASE/BATCH;assert not out.exists();pins={};refs=[Path(__file__)]
 def take(suffix,name='summary.json'):
  batch=P+suffix+'-20261027'
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 raw=take('block2-four-world-support-v1');foundation=take('four-wall-foundation-v1');views=take('seven-witness-views-v2');paths=take('seven-witness-paths-v1')
 assert all(r['sourceSHA256ByUid']==SOURCES for r in [raw,foundation,views,paths])
 assert {r['mode']for r in views['rows']}=={'original','literal','leftF32','balancedF32'}
 for view in views['rows']:
  mode=view['mode'];f=take('four-wall-foundation-v1',mode+'.json.gz');p=take('seven-witness-paths-v1',mode+'.json.gz');r=next(r for r in raw['rows']if r['mode']==mode);assert verify(mode,f,p,view,r)
 image=ROOT/views['image']['path'];assert digest(image.read_bytes())==views['image']['sha256'];refs.append(image)
 result=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,sourceWallRoleAccepted=True,sourceFaces=FACES,allOther10889FacesPassOrdinaryFoundation=True,all28PathsWithinExistingEndpointHeight=True,actuallyInspectedThreeAngleImage=views['image'],sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,currentMapPlacementAccepted=False,physicalSupportAccepted=False,installationApproved=False,sourceGeometryChanges=0,interpretation='The exact four original near-vertical panels form the low21.61–22.649m wall/podium interface shown in the inspected three-angle plot. Every saved low-rim witness connects through unchanged full original edges to a positive finite original podium contact, with zero rise above endpoints. Every other10889facet passes unchanged ordinary foundation policy. This accepts only these source wall roles; raw0.5m embedding/support negatives remain false. No horizontal floor/closed-solid/room claim, provider identity approval, companion foundation approval, current-map terrain/foreign-form approval or installation is granted.',remaining=['Current source identity/assembly and podium/root foundation binding','Four flagged BASIC forms and three retained originals','Complete original-pair/native/foreign interfaces','Fresh current-map browser and guarded installation/readback'])
 save(out/'ROOT-SOURCE-WALL-ROLE.json',result);assert reservations.owns(lease)
 module('elegant_four_wall_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-four-original-lower-wall-source-role-review',refs,result)
if __name__=='__main__':main()
