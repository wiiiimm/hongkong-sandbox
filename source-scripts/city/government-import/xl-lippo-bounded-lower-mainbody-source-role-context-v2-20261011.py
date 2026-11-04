"""Complete untouched tower/current BASIC overlay and mainbody source context.
No lower-interface role, physical or installation acceptance.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
BATCH='government-xl-lippo-bounded-lower-mainbody-source-role-context-v2-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH;BASE=DOC.parent
INPUT=BASE/'government-xl-lippo-tower-only-current-complete-inputs-v3-20261011';PARTITION=BASE/'government-xl-lippo-tower-current-basic-complete-lower-interface-partition-v2-20261011';CARRIER=BASE/'government-xl-lippo-current-basic-bounded-wall-grade-clear-cap-tower-paths-v3-20261011';FOREIGN=BASE/'government-xl-lippo-tower-only-complete-current-foreign-finite-contacts-v1-20261011';CONTACT=BASE/'government-xl-lippo-upper-originals-actual-basic-podium-support-diagnostic-v1-20261011';FAMILY=BASE/'government-xl-lippo-three-complete-original-edge-components-and-contacts-v1-20261011'
def main():
 assert not DOC.exists();inp=read(INPUT/'input.json.gz');g=read(INPUT/'complete-current-geometry.json.gz');partition=read(PARTITION/'diagnostic.json.gz');carrier=read(CARRIER/'diagnostic.json.gz');foreign=read(FOREIGN/'diagnostic.json.gz');contact=read(CONTACT/'diagnostic.json.gz');family=read(FAMILY/'diagnostic.json.gz')
 refs=[Path(__file__)]
 for folder in [INPUT,PARTITION,CARRIER,FOREIGN,CONTACT,FAMILY]:
  receipt=read(folder/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs += [folder/'result.json',folder/'diagnostic.json.gz' if (folder/'diagnostic.json.gz').exists() else folder/'complete-current-geometry.json.gz']
 row=inp['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];tower=decode_original_world_triangles(asset.read_bytes());basicrow=next(r for r in g['completeCurrentBasicGeometry'] if r['uid']=='landsd/231645:0');basic=np.array(basicrow['position'],dtype='<f8').reshape(-1,3)[np.array(basicrow['index'],dtype=np.int64).reshape(-1,3)]
 nodes=[n for n in contact['nodes'] if n['uid']==row['uid']];main=next(n for n in nodes if n['component']==6);body=main['completeOwnedSourceFaceIDs'];assert len(body)==3459
 complete=census(tower,list(range(3597)));assert sorted(next(p for p in complete['sharedEdgeConnectedComponents'] if 19 in p))==body
 upper=np.flatnonzero(np.all(tower[:,:,1]>float(basic[:,:,1].max()),axis=1));upnorm=np.cross(tower[:,1]-tower[:,0],tower[:,2]-tower[:,0]);clear_body_caps=[int(i) for i in upper if i in body and upnorm[i,1]>0];assert clear_body_caps
 for proof in partition['rows']:assert proof['originalComponentsWithGenuineCurrentBasicInterior']==[6] and proof['sourceFacesOmitted']==0
 owner=next(r for r in foreign['actors'] if r['uid']==basicrow['uid']);otheractors=[r for r in foreign['actors'] if r['uid']!=basicrow['uid']];assert all(t['positiveFiniteContacts']==0 and t['completeContacts']==[] for r in otheractors for t in r['trials'])
 source=next(r for r in partition['rows'] if r['mode']=='providerOriginal');clipped=[[[float(F(v)) for v in p] for p in r['exactFiniteClippedPolygon']] for r in source['strictPositiveSourceFacetInteriorPieces']]
 DOC.mkdir(parents=True)
 for name,elev,azim,detail in [('complete-original-and-current-basic-2400x1500.png',25,-65,False),('lower-interface-original-detail-2400x1500.png',15,-35,True)]:
  fig=plt.figure(figsize=(16,10),dpi=150);ax=fig.add_subplot(111,projection='3d');ax.add_collection3d(Poly3DCollection(basic,facecolors='#adb5bd',edgecolors='#777777',linewidths=.12,alpha=.22));ax.add_collection3d(Poly3DCollection(tower,facecolors='#208aa6',edgecolors='#14566a',linewidths=.10,alpha=.50));ax.add_collection3d(Poly3DCollection(clipped,facecolors='#df342d',edgecolors='#89140f',linewidths=.18,alpha=.95));lo=np.minimum(tower.min((0,1)),basic.min((0,1)));hi=np.maximum(tower.max((0,1)),basic.max((0,1)));ax.set_xlim(lo[0]-2,hi[0]+2);ax.set_ylim(lo[1]-2,hi[1]+2);ax.set_zlim(lo[2]-2,hi[2]+2)
  # Data order X,Y,Z is preserved, Y is the vertical HKPD axis. Plot rotation
  # only changes the camera; no source coordinate or mesh edits.
  if detail:ax.set_ylim(15.5,21.5)
  ax.set_xlabel('X metres');ax.set_ylabel('HKPD Y metres');ax.set_zlabel('Z metres');ax.view_init(elev=elev,azim=azim,vertical_axis='y');ax.set_box_aspect((hi[0]-lo[0],8 if detail else hi[1]-lo[1],hi[2]-lo[2]));ax.set_title('Complete unchanged tower cyan / actual BASIC podium grey / exact lower interior red\nAll source faces retained; genuine shallow mainbody overlap is diagnostic, not acceptance');fig.tight_layout();fig.savefig(DOC/name);plt.close(fig)
 result=dict(uid=row['uid'],currentCapturedManifest=inp['currentManifest'],completeOriginalTowerFaces=3597,completeActualBasicFaces=284,sourceSHA256=row['sourceSHA256'],mainbodyComponent=6,completeMainbodyFaces=3459,completeMainbodySourceFaceIDs=body,completeOriginalCensus=complete,strictlyAboveCurrentPodiumUpwardMainbodySourceFaces=clear_body_caps,allPenetratingSourcePartsAreSameConnectedOriginalMainbody=True,completeLowerInterfacePartitionRef=str((PARTITION/'diagnostic.json.gz').relative_to(ROOT)),raw183CarrierCollisionContactsRetained=True,fullCarrierContactProof=owner,completeOther19CurrentForeignActorsClearOfFiniteContacts=True,originalGovernmentPodiumUsedAsRuntimeSupport=False,allCurrentBasicSourceFacesRetained=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,terrainGeometryChanges=0,sourceRoleAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Context-only complete source/nonzero-edge mainbody and strict lower-source current carrier intersection inventory. All genuine original/literal/F32 interior fragments, complete183positive contacts and zero-area records remain visible. Explicitly separate from bounded actual BASIC grade/cap paths. Recorded18.6 primary/current join and exact authored source-family contacts may support a narrowly reviewed connected lower-mainbody interpretation; no detached/upper source piece, unrelated actor, whole BASIC ordinary bottom, absent original podium, legal ownership, surveyed interface or generic collision exemption is approved.')
 save(DOC/'diagnostic.json.gz',result);refs += [INPUT/'input.json.gz',asset,HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'test_exact_original_shared_edge_component_census_v2_20261011.py']
 s=importlib.util.spec_from_file_location('lippo_mainbody_context_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 receipt=m.freeze(BATCH,'complete-unchanged-tower-basic-lower-mainbody-source-context-v2',refs,dict(uids=[row['uid'],basicrow['uid']],completeOwnedFaces=3597,completeMainbodyFaces=3459,completeActualBasicFaces=284,sourceRoleAccepted=False,physicalAccepted=False,installationApproved=False))
 print(json.dumps(dict(jobId=receipt['jobId'],mainbodyFaces=3459,completeOwnedFaces=3597,upperMainbodyCaps=len(clear_body_caps))),flush=True)
if __name__=='__main__':main()
