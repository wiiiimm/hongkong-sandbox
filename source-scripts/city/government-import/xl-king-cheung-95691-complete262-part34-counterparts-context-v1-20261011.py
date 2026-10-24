"""Complete original part34 counterpart contacts and literal face799 context.

No proximity, winding, property or function assumption grants root credit.
Every source primitive survives the full18742 counterpart census and plots.
"""
import importlib.util,json,sys,uuid,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from king_cheung_complete_ancillary_proposal_20261011 import UID,SOURCE_SHA
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011'
GRADE=BASE/'government-xl-king-cheung-95691-complete262-part34-current-grade-cause-v1-20261011'
TOPO=BASE/'government-xl-king-cheung-95691-complete-original-extra-context-v1-20261011'
BATCH='government-xl-king-cheung-95691-complete262-part34-counterparts-context-v1-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
IDS=list(range(555,813))+[2779,2780,2795,2796]
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [INPUT,GRADE,TOPO]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for pin in r['evidenceRefs']:
    p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 data=read(INPUT/'complete-four-stream-ground-inputs.json.gz');capture=read(INPUT/'complete-current-actual-source-and-ground.json.gz');prior=read(GRADE/'diagnostic.json.gz')
 topology=read(TOPO/'diagnostic.json.gz')['completeTopology']['sharedEdgeConnectedComponents'];assert topology[34]==IDS
 face_component={f:i for i,part in enumerate(topology)for f in part}
 assert data['uid']==UID and data['sourceSHA256']==SOURCE_SHA
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==capture['inputHashes']['3d-viewer/city/data/manifest.json']
 rows=[];others=[i for i in range(18742)if i not in set(IDS)]
 for mode,stream in data['completeWorldStreams'].items():
  world=np.asarray(stream['completeWorldTriangles'],dtype='<f8');assert world.shape==(18742,3,3)and digest(world.tobytes())==stream['completeWorldTriangleSHA256']
  contacts=exact_finite_contacts(world,IDS,world,others);assert contacts['allPairsExamined']and contacts['sourceFacesOmitted']==0
  grade=next(r for r in prior['rows']if r['arithmetic']==mode);assert grade['localFaceToOriginalSourceFace']==IDS
  neighbours=[]
  for face_id in range(798,805):
   face=world[face_id];edges={tuple(sorted((tuple(a),tuple(b))))for a,b in zip(face,np.roll(face,-1,axis=0))if not np.array_equal(a,b)}
   exact_edge_neighbours=[]
   for i in IDS:
    if i==face_id:continue
    f=world[i];other_edges={tuple(sorted((tuple(a),tuple(b))))for a,b in zip(f,np.roll(f,-1,axis=0))if not np.array_equal(a,b)}
    shared=edges&other_edges
    if shared:exact_edge_neighbours.append(dict(originalSourceFace=i,completeOriginalFace=f.tolist(),completeSharedNonzeroEdges=[list(map(list,e))for e in sorted(shared)]))
   neighbours.append(dict(originalSourceFace=face_id,completeOriginalFace=face.tolist(),completeExactSharedEdgeNeighbours=exact_edge_neighbours,
                          completeRawFiniteAndExposure=grade['complete262FaceInventory'][IDS.index(face_id)],
                          allOtherSourceComponentContacts=[dict(contactVerbatim=c,otherOriginalComponent=face_component.get(c['sourceFaceB']))for c in contacts['contacts']if c['sourceFaceA']==face_id]))
  rows.append(dict(arithmetic=mode,completeWorldSHA256=stream['completeWorldTriangleSHA256'],completePart34OriginalFaceIds=IDS,
                   completePart34WorldBounds=[world[IDS].min((0,1)).tolist(),world[IDS].max((0,1)).tolist()],
                   completeAllOther18742PrimitiveContacts=contacts,completeSevenWallNeighbours=neighbours,
                   counterpartComponentIds=sorted({face_component[c['sourceFaceB']]for c in contacts['contacts']if c['sourceFaceB']in face_component}),
                   sourceOwnedHostRoleAccepted=False,physicalAccepted=False))
 save(DOC/'diagnostic.json.gz',dict(uids=[UID],sourceSHA256=SOURCE_SHA,rows=rows,sourceGeometryChanges=0,terrainGeometryChanges=0,
      face799WhollyBuriedExposureNegativeRetained=True,currentAcceptance=False,groundRootAccepted=False,installationApproved=False))
 # Literal source and current planar ground plot; camera only, no fitted source pose.
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 world=np.asarray(data['completeWorldStreams']['providerOriginal']['completeWorldTriangles'],dtype='<f8');part=world[IDS];ground=np.asarray(data['completeDrawnGround'],dtype='<f8')
 fig=plt.figure(figsize=(12,9),dpi=200);ax=fig.add_subplot(111,projection='3d')
 ax.add_collection3d(Poly3DCollection(part[:,:,[0,2,1]],facecolors='#8098a7',edgecolors='#223849',linewidths=.3,alpha=.65))
 ax.add_collection3d(Poly3DCollection(world[list(range(798,805))][:,:,[0,2,1]],facecolors='#d94e34',edgecolors='#8d170a',linewidths=1,alpha=.9))
 ax.add_collection3d(Poly3DCollection(world[[799]][:,:,[0,2,1]],facecolors='#ffdf20',edgecolors='#a16c00',linewidths=2,alpha=1))
 lo=part.min((0,1));hi=part.max((0,1));ax.set_xlim(lo[0]-1,hi[0]+1);ax.set_ylim(lo[2]-1,hi[2]+1);ax.set_zlim(lo[1]-.5,hi[1]+.5)
 ax.add_collection3d(Poly3DCollection(ground[:,:,[0,2,1]],facecolors='#56b8db',edgecolors='#247997',alpha=.12))
 ax.set_box_aspect((max(hi[0]-lo[0],1),max(hi[2]-lo[2],1),max(hi[1]-lo[1],1)));ax.view_init(elev=27,azim=-55)
 ax.set_xlabel('Original world X / m');ax.set_ylabel('Original world Z / m');ax.set_zlabel('HKPD / m')
 ax.set_title('Complete262 original part34; seven raw walls red, wholly buried face799 yellow\nBlue plane is current drawn ground14m; no foundation/host role inferred')
 fig.tight_layout();image=DOC/'complete-original-part34-seven-walls-current-grade-2400x1800.png';fig.savefig(image,dpi=200);plt.close(fig)
 assert reservations.owns(lease)and manifest.read_bytes()==before
 for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 refs +=[HERE/n for n in ['king_cheung_complete_ancillary_proposal_20261011.py','exact_original_finite_triangle_contacts_20261010.py']]
 s=importlib.util.spec_from_file_location('king_part34_counterparts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 r=m.freeze(BATCH,'complete262-original-component34-all18742-counterparts-and-literal-buried799-context-no-role-credit',refs+[DOC/'diagnostic.json.gz',image],dict(uids=[UID],completeOwnedPartFaces=262,currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(dict(jobId=r['jobId'],counterpartComponents={r['arithmetic']:r['counterpartComponentIds']for r in rows})),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('king-cheung-part34-counterparts-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok']
 save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
