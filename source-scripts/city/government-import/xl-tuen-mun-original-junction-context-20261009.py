"""Complete original hospital junction context; no identity/support waiver.

Owner's schematic is contextual only. Exact original source faces, current
footprints and every excess component remain independently recorded.
"""
import importlib.util, json
from pathlib import Path
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT, HERE, read, save, digest
from exact_mesh_components import face_components
from exact_original_component_contacts_20261009 import contact_measure
from exact_original_shell_intersections_20261009 import rational_face, intersection_points

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-tuen-mun-original-junction-context-20261009'
DOC=BASE/BATCH
SOURCE=BASE/'government-xl-tuen-mun-special-primary-counterpart-20261009'
OWNER=BASE/'government-xl-tuen-mun-hospital-owner-context-20261009'

def parity(rings):
 result=shapely.GeometryCollection()
 for ring in rings:result=result.symmetric_difference(shapely.Polygon(ring))
 assert result.is_valid and result.area>0
 return result

def main():
 assert not DOC.exists(), 'Use a fresh immutable diagnostic'
 data=read(SOURCE/'complete-original-inputs.json.gz')
 old=read(SOURCE/'diagnostic.json.gz')
 receipt=read(SOURCE/'result.json')
 for r in receipt['evidenceRefs']:
  assert digest((ROOT/r['path']).read_bytes())==r['sha256'],r['path']
 tower,podium=[np.asarray(r['position'],dtype='<f8').reshape(-1,3,3) for r in data['rows']]
 for r,t in zip(data['rows'],[tower,podium]):
  assert len(t)==r['completeOriginalFaces'] and digest(t.tobytes())==r['worldTrianglesSHA256']
 primary=read(SOURCE/'exact-primary.json')
 shapes={f['attributes']['BuildingCSUID']:parity([[(x-834500,816500-y) for x,y in ring] for ring in f['geometry']['rings']]) for f in primary['features']}
 own=shapes[data['rows'][0]['primaryAttributes']['BuildingCSUID']]
 foreign=parity(data['currentForms'][1]['rings'])
 projection=shapely.union_all(shapely.polygons(tower[:,:,[0,2]]))
 excess=projection.difference(own).intersection(foreign)
 assert abs(excess.area-old['rawForeignExcessM2'])<1e-9
 components=face_components(tower)
 assert sorted(i for c in components for i in c)==list(range(len(tower)))
 by_face={int(i):n for n,c in enumerate(components) for i in c}
 ids=old['allExcessContributingOriginalTowerFaces']
 normals=np.cross(tower[:,1]-tower[:,0],tower[:,2]-tower[:,0]);size=np.linalg.norm(normals,axis=1)
 ratio=np.divide(normals[:,1],size,out=np.zeros(len(tower)),where=size>0)
 contacts=[]
 for r in old['allExactOriginalExcessContacts']:
  points=intersection_points(rational_face(tower[r['towerFace']]),rational_face(podium[r['podiumFace']]))
  assert [[str(v) for v in p] for p in sorted(points)]==r['exactPoints']
  contacts.append(dict(towerFace=r['towerFace'],podiumFace=r['podiumFace'],**contact_measure(points)))
 grouped=[]
 for ci in sorted({by_face[i] for i in ids}):
  faces=[i for i in ids if by_face[i]==ci]
  positive=[r for r in contacts if r['dimension']>0 and r['towerFace'] in faces]
  areas=[shapely.Polygon(tower[i][:,[0,2]]).intersection(excess).area for i in faces]
  grouped.append(dict(component=ci,completeOriginalComponentFaces=list(map(int,components[ci])),excessContributingFaces=faces,excessFaceAreasM2=areas,excessBounds=[tower[faces].min(axis=(0,1)).tolist(),tower[faces].max(axis=(0,1)).tolist()],completeComponentBounds=[tower[components[ci]].min(axis=(0,1)).tolist(),tower[components[ci]].max(axis=(0,1)).tolist()],positiveExactContacts=positive,excessFacesDirectlyTouchingPodium=sorted({r['towerFace'] for r in positive}),upwardFaces=[i for i in faces if ratio[i]>.25],downwardFaces=[i for i in faces if ratio[i]<-.25],steepFaces=[i for i in faces if abs(ratio[i])<=.25]))
 DOC.mkdir(parents=True)
 result=dict(uids=[r['uid'] for r in data['rows']],sourceBindings=old['sourceBindings'],completeOriginalTowerComponents=len(components),completeOriginalTowerFaces=len(tower),completeOriginalPodiumFaces=len(podium),rawForeignExcessM2=excess.area,excessComponents=grouped,allContactsReplayed=contacts,ownerMapInterpretation='Hospital Authority schematic labels the Special Block immediately adjoining Main Block. It is not georeferenced, does not identify these source triangles, and cannot alone establish an owned source interface or structural support.',sourceGeometryChanges=0,identityAccepted=False,supportAccepted=False,physicalAccepted=False,installationApproved=False,remainingReason='Specific original excess ownership and complete current physical support remain unproved; ordinary own-primary coverage and all other foreign actors remain required.')
 save(DOC/'diagnostic.json.gz',result)
 fig,axes=plt.subplots(1,2,figsize=(16,9),layout='constrained')
 pts=np.asarray(list(shapely.get_coordinates(excess)))
 bounds=[pts[:,0].min()-10,pts[:,0].max()+10,pts[:,1].min()-10,pts[:,1].max()+10]
 for ax in axes:
  ax.add_collection(PolyCollection(podium[:,:,[0,2]],facecolors='#94b9db',edgecolors='none',alpha=.45))
  ax.add_collection(PolyCollection(tower[:,:,[0,2]],facecolors='#edc47f',edgecolors='none',alpha=.55))
  ax.add_collection(PolyCollection(tower[ids][:,:,[0,2]],facecolors='#c52a49',edgecolors='#a31b34',linewidths=.25,alpha=.6))
  for shape,col in [(own,'#886500'),(foreign,'#246494')]:
   for poly in shapely.get_parts(shape):
    x,y=poly.exterior.xy;ax.plot(x,y,color=col,linewidth=.7)
  ax.set_aspect('equal');ax.set_xlabel('Original local X (m)');ax.set_ylabel('Original local Z (m; north is down)')
 axes[0].autoscale_view();axes[0].set_title('Complete unchanged original source projections')
 axes[1].set_xlim(bounds[:2]);axes[1].set_ylim(bounds[2:]);axes[1].set_title('All 174 excess-contributing faces retained (red)')
 fig.suptitle('Tuen Mun Hospital: Special Block (gold), Main Block podium (blue)\nOriginal source and explicit primary footprints; no geometry or placement edits')
 fig.savefig(DOC/'complete-original-junction-2400x1350.png',dpi=150);plt.close(fig)
 save(DOC/'summary.json',dict(rawForeignExcessM2=excess.area,excessComponentCount=len(grouped),completeTowerComponents=len(components),groups=[{k:r[k] for k in ['component','excessBounds','completeComponentBounds','excessFacesDirectlyTouchingPodium','upwardFaces','downwardFaces','steepFaces']}|{'completeFaces':len(r['completeOriginalComponentFaces']),'excessFaces':len(r['excessContributingFaces']),'positiveContacts':len(r['positiveExactContacts'])} for r in grouped],fullAcceptance=False))
 paths=[Path(__file__),HERE/'exact_mesh_components.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',SOURCE/'complete-original-inputs.json.gz',SOURCE/'diagnostic.json.gz',SOURCE/'result.json',SOURCE/'exact-primary.json']+[p for p in OWNER.rglob('*') if p.is_file()]
 spec=importlib.util.spec_from_file_location('tuen_mun_junction_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'complete-original-excess-components-and-official-owner-context-v1',paths,dict(uids=result['uids'],rawForeignExcessM2=excess.area,exactOriginalContactsReplayed=len(contacts),excessComponentCount=len(grouped),identityAccepted=False,supportAccepted=False,requiresAIModelGeometry=False,requiresHumanDecision=False,remainingReason=result['remainingReason'],nextStep='Interpret actual whole original excess component roles and precise primary/source interface ownership. Owner schematic alone grants no exception. Preserve all source and current physics checks.'))
 print(json.dumps(read(DOC/'summary.json')),flush=True)

if __name__=='__main__':main()
