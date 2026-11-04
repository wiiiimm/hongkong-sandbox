"""UNEXECUTED: complete original component/footprint context, never acceptance.

ROOT review and maintained canonical supervisor required before normal execution.
No registration, role assignment, clearance/contact/grade or current model exports.
"""
import argparse,gzip,hashlib,importlib.util,json,subprocess,sys,uuid
from pathlib import Path

PACKET=Path(__file__).resolve().parent
ROOT=PACKET.parents[3]
HERE=ROOT/'source-scripts/city/government-import'
CONTRACT=PACKET/'comparison-input-contract.json'
BATCH='government-xl-lai-chi-kok281463-complete-original-site-podium-context-v1-20261013'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
LEASE=LOCAL/'reservation.json'
UID='landsd/281463:0'
SOURCE='1480540e0a32849425d5238eeea7ecb3a7124633226c1eae9cab2d041b968d86'
WORLD='d8ab9b872ef0696d3d95d8e47df0f64db2e540229961f0142d1e83af7cf08b22'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def preflight():
 contract=read(CONTRACT)
 assert contract['sourceSHA256']==SOURCE and contract['worldTrianglesSHA256']==WORLD
 assert contract['currentAcceptance'] is False and contract['sourceGeometryChanges']==0
 assert not DOC.exists() and 1<=len(contract['canonicalResources'])<=1000
 for rel,value in contract['allInputHashes'].items():assert sha(ROOT/rel)==value
 roles=read(ROOT/contract['priorRolePath']);assert roles['uid']==UID and roles['sourceSHA256']==SOURCE and roles['worldTrianglesSHA256']==WORLD
 assert roles['variants']['direct-shared-OSM']['stats']['sourceFacesBeyond10m']==106
 exact=read(PACKET/'provider-site-scope-findings.json')
 assert exact['exactProviderAttributes']['BuildingCSUID']=='3215622119P20070611'
 assert exact['exactProviderAttributes']['BuildingNameEN']=='LAI CHI KOK PARK SPORTS CENTRE'
 assert exact['sourceJSONMetadata']['meshes'][0]['primitives'][0]['indices']==3
 assert exact['sourceJSONMetadata']['accessors'][3]['count']==112731
 return contract,roles,exact
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--preflight-only',action='store_true');parser.add_argument('--owned',action='store_true');args=parser.parse_args()
 contract,prior,metadata=preflight()
 if args.preflight_only:
  print(json.dumps({'passed':True,'faces':37577,'expectedHistoricalFarFaces':106,'resources':len(contract['canonicalResources']),'noDB':True,'noLease':True,'noSourceDecode':True}));return
 sys.path.insert(0,str(HERE))
 from run import save,connect,reservations
 if not args.owned:
  assert not LOCAL.exists()
  claim=reservations.claim('lai-chi-kok-source-scope-'+str(uuid.uuid4()),contract['canonicalResources'],batch=BATCH,ttl=3600);assert claim['ok'],claim
  save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True);return
 lease=read(LEASE);assert lease['resources']==contract['canonicalResources'] and reservations.owns(lease)
 import numpy as np
 import shapely
 from shapely.geometry import Polygon
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 from exact_original_shared_edge_component_census_v2_20261011 import census
 from xl_source_stream_binding_20261009 import source_stream_binding
 raw=(ROOT/metadata['sourceAssetPath']).read_bytes();assert hashlib.sha256(raw).hexdigest()==SOURCE
 world=decode_original_world_triangles(raw)
 assert world.shape==(37577,3,3) and np.isfinite(world).all()
 assert hashlib.sha256(world.astype('<f8').tobytes()).hexdigest()==WORLD
 topology=census(world,list(range(len(world))))
 groups=topology['sharedEdgeConnectedComponents'];zeros=topology['exactNonrenderingOriginalFaces']
 represented=[i for ids in groups for i in ids]+zeros
 assert len(represented)==37577 and sorted(represented)==list(range(37577))
 form=metadata['currentFormVerbatim'];foot=Polygon(form['rings'][0],form['rings'][1:])
 # Identical old diagnostic threshold, solely to recover its unsaved face IDs.
 distances=shapely.distance(shapely.points(world[:,:,[0,2]].reshape(-1,2)),foot).reshape(-1,3)
 far=np.flatnonzero(distances.max(axis=1)>10).tolist();assert len(far)==106
 far_world=world[far]
 assert [far_world.min((0,1)).tolist(),far_world.max((0,1)).tolist()]==prior['variants']['direct-shared-OSM']['stats']['farSourceBounds']
 components=[{'component':i,'completeOriginalFaceIds':ids,'completeOriginalWorldTriangles':world[ids].tolist(),'worldBounds':[world[ids].min((0,1)).tolist(),world[ids].max((0,1)).tolist()],'historicalFarFaceIds':[face for face in ids if face in set(far)],'sourceRoleAccepted':False,'groundOrStructuralRootCredit':False} for i,ids in enumerate(groups)]
 out={'uid':UID,'modelId':'B321562211902063C0','sourceSHA256':SOURCE,'worldTrianglesSHA256':WORLD,'originalCoordinateView':'providerOriginal only; no runtime arithmetic views captured','completeOriginalFaces':37577,'completeSourceStreamBinding':source_stream_binding(raw),'completeOriginalTopology':topology,'completeComponents':components,'historicalFarFaceIdsRecovered':far,'historicalNonrenderingOriginalFacesUncredited':zeros,'exactNonrenderingOriginalPrimitiveWorldTriangles':world[zeros].tolist(),'priorRoleRecordVerbatim':prior,'providerAndOperatorScopeRecordVerbatim':metadata,'primaryImagesNotRegistered':True,'sourceGeometryChanges':0,'terrainGeometryChanges':0,'identityAccepted':False,'physicalAccepted':False,'currentAcceptance':False,'sourceRoleAccepted':False,'modelReviewWrites':0,'newlyInstalled':0}
 # Saved JSON representation must be the one sent to JSONB; no integer-key drift.
 out=json.loads(json.dumps(out,sort_keys=True));save(DOC/'diagnostic.json.gz',out)
 assert reservations.owns(lease)
 for rel,value in contract['allInputHashes'].items():assert sha(ROOT/rel)==value
 refs=[ROOT/rel for rel in contract['allInputHashes']]+[CONTRACT,DOC/'diagnostic.json.gz']
 spec=importlib.util.spec_from_file_location('lckp_scope_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');freezer=importlib.util.module_from_spec(spec);spec.loader.exec_module(freezer)
 receipt=freezer.freeze(BATCH,'exact-provider-named-park-podium-component-context-no-role-credit',refs,out)
 print(json.dumps({'jobId':receipt['jobId'],'completeOriginalFaces':37577,'historicalFarFaceIds':106,'currentAcceptance':False}),flush=True)
if __name__=='__main__':main()
