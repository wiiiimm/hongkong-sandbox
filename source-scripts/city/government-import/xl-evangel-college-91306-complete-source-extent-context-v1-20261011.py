"""Unchanged complete original Evangel College context; historical footprint only.

Routine read-only source attribution. No current capture, identity acceptance,
role qualification, geometry change, structural/root/function credit.
"""
import json,uuid,sys,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
UID='landsd/91306:0';SOURCE='73dfaaf90f9dc8433f757ff796f90a0d8e3d02e2d48eb515f3286fa3eddc964b'
B=ROOT/'docs/astra-city/government-import';RANK=B/'government-xl-identity-primary-spatial-ranking-20261009/ranking.json.gz'
BATCH='government-xl-evangel-college-91306-complete-source-extent-context-v1-20261011';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();ranking=read(RANK);row=next(r for r in ranking['rows']if r['uid']==UID);assert row['sourceSHA256']==SOURCE and row['sourceTriangles']==13960 and row['primaryAttributes']['BuildingCSUID']=='4507318353T20070410'
 asset=ROOT/row['sourcePath'];raw=asset.read_bytes();assert digest(raw)==SOURCE
 tile=ROOT/'3d-viewer/city/data/tiles/5_-1.json';tilebytes=tile.read_bytes();assert digest(tilebytes)==ranking['inputHashes'][str(tile.relative_to(ROOT))]
 forms=[b for b in json.loads(tilebytes)['buildings']if b['uid']==UID];assert len(forms)==1;form=forms[0];assert form['buildingCSUID']=='4507318353T20070410'
 w=decode_original_world_triangles(raw);assert w.shape==(13960,3,3);topology=census(w,list(range(13960)))
 import shapely
 target=shapely.Polygon(form['rings'][0],form['rings'][1:]);assert target.is_valid
 distances=np.asarray([target.distance(shapely.Point(float(v[0]),float(v[2])))for v in w.reshape(-1,3)]).reshape(13960,3)
 ids=np.nonzero(distances.max(axis=1)>10)[0].tolist();parts=topology['sharedEdgeConnectedComponents'];mapping={i:k for k,p in enumerate(parts)for i in p};groups=sorted({mapping[i]for i in ids if i in mapping});out=[]
 for k in groups:
  faces=parts[k];t=w[faces];normals=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);out.append(dict(originalComponent=k,completeOriginalFaces=faces,completeOriginalGeometry=t.tolist(),completeOriginalBounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],farVertexWitnessFaces=sorted(set(faces)&set(ids)),completeNormalsDescriptiveOnly=normals.tolist(),rootOrAttachmentCredit=False))
 save(DOC/'diagnostic.json.gz',dict(uids=[UID],sourceSHA256=SOURCE,completeOriginalFaces=13960,completeOriginalWorldSHA256=digest(w.astype('<f8').tobytes()),completeOriginalTopology=topology,historicalRankingRow=row,historicalFootprintOnly=form,historicalTile=ref(tile),floatingVertexDistanceWitnesses=distances.tolist(),farVertexWitnessFaces=ids,completeFarWitnessComponentContexts=out,finiteMaximumExtentApproved=False,currentCapture=False,currentAcceptance=False,sourceGeometryChanges=0,terrainGeometryChanges=0,sourceOwnedAncillaryRoleAccepted=False,structuralRootOrBridgeCredit=False))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 fig=plt.figure(figsize=(12,9),dpi=200);ax=fig.add_subplot(111,projection='3d');ax.add_collection3d(Poly3DCollection(w[:,:,[0,2,1]],facecolors='#87999e',edgecolors='#465b61',alpha=.18,linewidths=.12));ax.add_collection3d(Poly3DCollection(w[ids][:,:,[0,2,1]],facecolors='#d86635',edgecolors='#8f2809',alpha=.85,linewidths=.45))
 lo=w.min((0,1));hi=w.max((0,1));ax.set_xlim(lo[0]-3,hi[0]+3);ax.set_ylim(lo[2]-3,hi[2]+3);ax.set_zlim(lo[1]-1,hi[1]+2);ax.set_box_aspect((hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]));ax.view_init(28,-55);ax.set_xlabel('Original world X / m');ax.set_ylabel('Original world Z / m');ax.set_zlabel('HKPD / m');ax.set_title('Complete unchanged Evangel College13960 original facets\nOrange = original faces with a floating >10m historical-footprint vertex witness; no identity credit');fig.tight_layout();fig.savefig(DOC/'complete-original-far-witness-context-2400x1800.png',dpi=200);plt.close(fig)
 fig,ax=plt.subplots(figsize=(12,9),dpi=200)
 from matplotlib.collections import PolyCollection
 ax.add_collection(PolyCollection(w[:,:,[0,2]],facecolors='#899da4',edgecolors='#526771',alpha=.12,linewidths=.12));ax.add_collection(PolyCollection(w[ids][:,:,[0,2]],facecolors='#d66c33',edgecolors='#90330b',alpha=.8,linewidths=.4))
 for ring in form['rings']:a=np.asarray(ring);ax.plot(a[:,0],a[:,1],color='black',linewidth=1.4)
 for k in groups:
  center=w[parts[k]].mean((0,1));ax.text(center[0],center[2],str(k),color='#7f1800',fontsize=8)
 ax.set_xlim(lo[0]-3,hi[0]+3);ax.set_ylim(lo[2]-3,hi[2]+3);ax.invert_yaxis();ax.set_aspect('equal');ax.set_xlabel('Original world X / m');ax.set_ylabel('Original world Z / m');ax.set_title('Complete original school + exact historical current footprint\nNo plan fitting, source edits, current acceptance or ancillary ownership claim');fig.tight_layout();fig.savefig(DOC/'complete-original-historical-footprint-2400x1800.png',dpi=200);plt.close(fig)
 assert reservations.owns(lease)and asset.read_bytes()==raw and tile.read_bytes()==tilebytes
 save(DOC/'provenance.json',dict(uids=[UID],evidenceRefs=[ref(Path(__file__)),ref(RANK),ref(asset),ref(tile),ref(HERE/'exact_packed_world_geometry_20261009.py'),ref(HERE/'exact_original_shared_edge_component_census_v2_20261011.py')],sourceOnly=True,currentCapture=False,currentAcceptance=False,qualification='Source context uses the exact historical ranked tile bytes; even if unchanged live, no fresh current qualification. Floating vertex witnesses are descriptive, not a full finite extent partition. Complete source and every exact nonzero-edge real component/zero facet retained.'))
 print(json.dumps(dict(completeOriginalFaces=13960,realComponents=len(parts),farVertexWitnessFaces=len(ids),farComponentContexts=groups)),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('evangel-source-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
