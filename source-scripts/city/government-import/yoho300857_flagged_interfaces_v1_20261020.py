"""Exact finite original interface evidence for known cap/junction flags."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_face_conservative_clearance_v5_20261010 import verify
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho300857-flagged-interfaces-v1-20261020';DOC=BASE/BATCH;CAP=BASE/'government-xl-yoho300857-private-terrain-capture-v2-20261020';UID='landsd/300857:0';POD='landsd/301636:0'
assert not DOC.exists();r=read(CAP/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),CAP/'result.json']
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
def consume(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
rows=consume(CAP/'selection.json.gz')['rows'];attrs=consume(CAP/'attributes.json.gz');rt={x['uid']:x for x in consume(HERE/'local'/CAP.name/'runtime-geometry.json.gz')['rows']};worlds={'original':{}}
for row in rows:
 p=ROOT/row['candidate']['path'];raw=p.read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(p);worlds['original'][row['uid']]=decode_original_world_triangles(raw)
for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]={x['uid']:np.asarray(x[field],dtype='<f8').reshape(-1,3)[np.asarray(x['completeOriginalIndex']).reshape(-1,3)]for x in attrs['rows']}
summary=[]
for mode,w in worlds.items():
 t,p=w[UID],w[POD];ground=np.asarray(rt[POD]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);flags=[18215,18216];edges=set()
 for f in p[flags]:
  for a,b in zip(f,np.roll(f,-1,axis=0)):edges.add(tuple(sorted((tuple(a),tuple(b)))))
 adjacent=[]
 for i,f in enumerate(p):
  if i not in flags and any(tuple(sorted((tuple(a),tuple(b))))in edges for a,b in zip(f,np.roll(f,-1,axis=0))):adjacent.append(i)
 cap=p[flags];n=np.cross(cap[:,1]-cap[:,0],cap[:,2]-cap[:,0]);assert (n[:,1]<0).all() and np.ptp(cap[:,:,1])<1e-5
 contact=exact_finite_contacts(p,adjacent,ground,list(range(len(ground))));positive=[x for x in contact['contacts']if x['sourcePrimitiveDimensionA']==2 and x['sourcePrimitiveDimensionB']==2 and x['dimension']>0]
 towerGround=np.asarray(rt[UID]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);clear=verify(t[14801],towerGround);joint=exact_finite_contacts(t,[14801],p,list(range(len(p))));jp=[x for x in joint['contacts']if x['sourcePrimitiveDimensionA']==2 and x['sourcePrimitiveDimensionB']==2 and x['dimension']>0]
 out=dict(mode=mode,sourceWorldHashes={u:digest(v.tobytes())for u,v in w.items()},podiumCapFaces=flags,podiumImmediateEdgeAdjacentFaces=adjacent,podiumCapYRange=[float(cap[:,:,1].min()),float(cap[:,:,1].max())],podiumSideTerrainContacts=contact,towerFaceGroundClearance=clear,towerFacePodiumContacts=joint,installationApproved=False)
 save(DOC/(mode+'.json.gz'),out);line=dict(mode=mode,capAdjacentFaces=adjacent,positiveSideGroundContacts=len(positive),sideFacesContactingGround=sorted({x['sourceFaceA']for x in positive}),towerWholeFaceGroundClear=clear['existingOrdinaryClearanceBoundProved'],positiveTowerPodiumContacts=len(jp));summary.append(line);print(line,flush=True)
refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_finite_triangle_contacts_20261010.py']);module('yoho_flagged_interface_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-cap-and-junction-interfaces',refs,dict(uids=[UID,POD],rows=summary,installationApproved=False,geometryChanges=0))
