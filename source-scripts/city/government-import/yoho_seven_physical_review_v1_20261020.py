"""Bounded physical interpretation of seven unchanged YOHO sources, not publication."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-seven-physical-review-v1-20261020';DOC=BASE/BATCH
NAMES={'capture':'government-xl-yoho-seven-private-terrain-v1-20261020','foundations':'government-xl-yoho-seven-four-mode-foundations-v1-20261020','originalPaths':'government-xl-yoho-seven-original-paths-v1-20261020','runtimePaths':'government-xl-yoho-seven-runtime-paths-v1-20261020','originalClub':'government-xl-yoho-clubhouse-finite-path-verification-v1-20261020','runtimeClub':'government-xl-yoho-clubhouse-runtime-finite-path-verification-v1-20261020','interfaces':'government-xl-yoho300857-flagged-interfaces-v1-20261020','cap':'government-xl-yoho-podium-cap-rim-v1-20261020','rim':'government-xl-yoho-podium-rim-verification-v1-20261020'}
assert not DOC.exists();pins={};refs=[Path(__file__)]
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for key,name in NAMES.items():
  d=BASE/name;r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[key]={e['path']:e['sha256']for e in r['evidenceRefs']}
def consume(k,f):
 p=BASE/NAMES[k]/f;assert digest(p.read_bytes())==pins[k][str(p.relative_to(ROOT))];refs.append(p);return read(p)
rows=consume('capture','selection.json.gz')['rows'];uids=sorted(x['uid']for x in rows);bindings=consume('cap','bindings.json');rims=consume('cap','rim.json')['rows'];accounts=[]
runtime=HERE/'local'/NAMES['capture']/'runtime-geometry.json.gz';assert digest(runtime.read_bytes())==pins['capture'][str(runtime.relative_to(ROOT))];refs.append(runtime);g=next(x['drawnGroundGeometry']for x in read(runtime)['rows']if x['uid']=='landsd/301636:0');assert digest(np.asarray(g,dtype='<f8').reshape(-1,3,3).tobytes())==bindings['drawnGroundSHA256']
for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
 pathkey='originalPaths'if mode=='original'else'runtimePaths';clubkey='originalClub'if mode=='original'else'runtimeClub';paths=consume(pathkey,mode+'-verified.json.gz')['rows'];graphs=consume(pathkey,mode+'-graph.json.gz')['rows'];club=consume(clubkey,mode+'.json');interface=consume('interfaces',mode+'.json.gz');cap=next(x for x in rims if x['mode']==mode);finite=consume('rim',mode+'.json');byuid={x['uid']:x for x in paths}
 assert cap['proof']['samples']==26 and cap['proof']['contacts']==12 and cap['proof']['missing']==0 and len(cap['proof']['failed'])==14
 assert {tuple(x['position'])for x in cap['proof']['failed']}=={tuple(x['target'])for x in finite['rows']}
 assert finite['sourceWorldSHA256']==bindings['worldSHA256ByMode'][mode] and finite['supportWorldSHA256']==bindings['drawnGroundSHA256']
 assert all(x['finitePathVerified']and x['withinEndpointHeight']and x['terminalContactOnSourceBoundary']for x in finite['rows'])
 for row in rows:
  uid=row['uid'];f=consume('foundations',uid.split('/')[1]+'-'+mode+'.json');assert f['foundation']['completeTerrainTriangles']==row['candidate']['entry']['triangles']and f['foundation']['fullyBuriedUpwardTriangles']==0
  if uid=='landsd/301636:0':
   assert f['foundation']['fullyBuriedTriangles']==2 and f['worldSHA256']==bindings['worldSHA256ByMode'][mode]==interface['sourceWorldHashes'][uid]
   assert interface['podiumCapFaces']==[18215,18216]and interface['podiumImmediateEdgeAdjacentFaces']==[18217,18219,18221,18223]
   positive=[x for x in interface['podiumSideTerrainContacts']['contacts']if x['dimension']>0];assert set(x['sourceFaceA']for x in positive)=={18217,18219,18221,18223}
   accounts.append(dict(uid=uid,mode=mode,samples=26,strict=12,boundedFiniteGroundPaths=14,unresolved=0,worldSHA256=f['worldSHA256'],rawBuriedFaces=2));continue
  p=byuid[uid];graph=next(x for x in graphs if x['uid']==uid);assert f['worldSHA256']==p['worldSHA256'];failed={tuple(x['position'])for x in p['details']if not x['verified']}
  if uid=='landsd/300895:0':
   assert failed=={tuple(x['target'])for x in club['rows']}and len(failed)==3 and club['sourceWorldSHA256']==f['worldSHA256']
   assert all(x['finitePathVerified']and x['withinEndpointHeight']and x['allSteepWallFaces']and x['terminalContactOnSourceBoundary']for x in club['rows'])
  else:assert not failed
  if uid=='landsd/300857:0':
   assert f['foundation']['fullyBuriedTriangles']==1 and interface['sourceWorldHashes'][uid]==f['worldSHA256']and interface['towerFaceGroundClearance']['existingOrdinaryClearanceBoundProved']
   assert any(x['dimension']>0 for x in interface['towerFacePodiumContacts']['contacts'])
  else:assert f['strictFoundationAccepted']
  accounts.append(dict(uid=uid,mode=mode,strict=graph['strictSamples'],boundedOriginalPaths=p['boundedPaths'],additionalClubhouseBoundaryPaths=len(failed),unresolved=0,worldSHA256=f['worldSHA256'],rawBuriedFaces=f['foundation']['fullyBuriedTriangles']))
review=dict(uids=uids,sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},sourceSpecificPhysicalInterpretationAccepted=True,rawStrictFailuresRetained=True,accounts=accounts,reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,basis='Every canonical low-rim sample has strict support or a finite original-face path to source/ground contact bounded by its own endpoint heights in all four representations. Podium has14 below-ground rim samples:10 lie on its two downward bottom-cap faces;4 on partially embedded adjoining-source walls. Ground contacts are on finite original boundaries; paths are retained rather than moving the building. Two cap-interior paths traverse an original underside before reaching an adjacent wall and are not labelled wall-only. All4 cap-adjacent walls intersect drawn ground. These below-ground bottoms are authored contact geometry, not a floating or completely buried building. Only the two known downward podium caps and tower underside trigger whole-face highest-surface flags. Tower underside clears complete drawn ground and intersects its original podium. Other five sources pass complete strict foundations. No engineering role, watertightness, generic tolerance change or removal of original faces is asserted. Whole identity, neighbour/collision, loader/runtime, visual and publication checks remain required.')
save(DOC/'ROOT-PHYSICAL-REVIEW.json',review)
module('yoho_seven_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'seven-exact-original-support-and-foundation-interpretation',list(dict.fromkeys(refs)),dict(uids=uids,sourceSpecificPhysicalInterpretationAccepted=True,installationApproved=False))
