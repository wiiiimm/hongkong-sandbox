"""Complete original 18742-face low-appendage attribution; no identity/support credit.
Distance-to-current-form is a floating diagnostic. A >10m vertex witness is
not a complete finite far-region partition or a new tolerance/extent approval.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import primitive_census
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'government-xl-king-cheung-95691-untouched-original-recovery-v1-20261011'
BATCH='government-xl-king-cheung-95691-complete-original-extra-context-v1-20261011';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipt=read(INPUT/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 selection=read(INPUT/'selection.json.gz');row=selection['rows'][0];assert len(selection['rows'])==1 and row['uid']=='landsd/95691:0'
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert selection['manifestSHA256']==start['sha256']
 tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];assert next(b for b in read(tile)['buildings']if b['uid']==row['uid'])==row['source']['building']
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']=='daad7e84a632e97cd7af9c354dd3d6c122e2e1afc0afdc751f752a0f909cd119'
 world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(18742,3,3)and np.isfinite(world).all()
 rings=row['source']['building']['rings'];assert len(rings)==1;poly=shapely.Polygon(rings[0]);assert poly.is_valid
 distances=shapely.distance(shapely.points(world[:,:,0].ravel(),world[:,:,2].ravel()),poly).reshape(-1,3)
 ids=np.flatnonzero(distances.max(1)>10).tolist();assert len(ids)==69
 topology=census(world,list(range(len(world))));groups=topology['sharedEdgeConnectedComponents'];face_component={f:i for i,faces in enumerate(groups)for f in faces}
 far=[]
 for i in ids:
  face=world[i];n=np.cross(face[1]-face[0],face[2]-face[0]);far.append(dict(sourceFace=i,completeOriginalFace=face.tolist(),component=face_component.get(i),normal=n.tolist(),vertexDistancesToCurrentFormMetres=distances[i].tolist()))
 save(DOC/'diagnostic.json.gz',dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],source=ref(asset),originalRootModelId=row['modelId'],completeOriginalWorldSHA256=digest(world.tobytes()),completeFaces=18742,completeTopology=topology,completeFinitePrimitiveCensus=primitive_census(world),currentManifest=start,currentForm=row['source']['building'],farFaceCandidatesByVertexWitness=far,farVertexWitnessCount=len(ids),farYRangeHKPD=[float(world[ids,:,1].min()),float(world[ids,:,1].max())],maximumVertexDistanceToCurrentFormMetres=float(distances.max()),
  allOriginalFacesPreserved=True,completeFiniteFarRegionProved=False,sourceGeometryChanges=0,sourceOnly=True,currentAcceptance=False,structuralSupportAccepted=False,installationApproved=False))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 for cropped,name in [(False,'complete-original-2400x1800.png'),(True,'authored-lower-extra-context-2400x1800.png')]:
  fig=plt.figure(figsize=(12,9));ax=fig.add_subplot(projection='3d')
  shown=world[world[:,:,1].min(1)<=18]if cropped else world
  ax.add_collection3d(Poly3DCollection(shown[:,:,[0,2,1]],facecolors='#4f86cb',edgecolors='none',alpha=.25))
  ax.add_collection3d(Poly3DCollection(world[ids][:,:,[0,2,1]],facecolors='#c93e49',edgecolors='#833641',linewidths=.3,alpha=.8))
  r=np.asarray(rings[0]);ax.plot(r[:,0],r[:,1],[row['source']['building']['base']]*len(r),color='black',linewidth=1.5)
  lo=world.min((0,1));hi=world.max((0,1));ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[2],hi[2]);ax.set_zlim(lo[1],18 if cropped else hi[1]);span=(hi-lo)[[0,2,1]];span[2]=(18-lo[1])if cropped else span[2];ax.set_box_aspect(span)
  ax.view_init(elev=35 if cropped else 22,azim=-130);ax.set_xlabel('Viewer east(m)');ax.set_ylabel('Viewer south(m)');ax.set_zlabel('HKPD(m)')
  ax.set_title('King Cheung original: red >10m vertex-witness faces / black current Tower outline'+('\n13–18m height crop; complete original unchanged'if cropped else '\nComplete18742 faces; source-only context'))
  fig.savefig(DOC/name,dpi=200);plt.close(fig)
 refs=[Path(__file__),INPUT/'result.json',INPUT/'selection.json.gz',asset,tile,manifest,HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py']
 assert ref(manifest)==start and digest(tile.read_bytes())==row['source']['tileSHA256']
 s=importlib.util.spec_from_file_location('king_cheung_original_extra_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'complete-original-low-appendage-vertex-witness-attribution-and-body-census-source-context-only',refs,dict(uids=[row['uid']],completeFaces=18742,farVertexWitnessFaces=69,sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(dict(components=len(groups),farComponents=sorted({r['component']for r in far if r['component']is not None}),farYRange=[float(world[ids,:,1].min()),float(world[ids,:,1].max())])),flush=True)
if __name__=='__main__':main()
