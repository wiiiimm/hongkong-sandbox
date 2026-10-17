"""Render unchanged source and six unresolved façade examples for role review."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='xl-terrain-recovery-20261010-mei-yat-original-facade-visual-v1';DOC=ROOT/'docs/astra-city/government-import'/BATCH;assert not DOC.exists();DOC.mkdir()
PHYS=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-mei-yat-original-physical-v3-20261010';SUP=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261010-mei-yat-complete-original-support-v1';row=read(PHYS/'selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());graph=read(SUP/'diagnostic.json.gz');assert digest(tri.tobytes())==graph['binding']['completeOriginalWorldTrianglesSHA256'];un=sorted(set(range(len(graph['components'])))-set(graph['resolvedOriginalComponents']));chosen=[0,62,193,721,722,799];assert set(chosen)<=set(un)
def axes(ax,t,el=20,az=140):
 lo=t.min(axis=(0,1));hi=t.max(axis=(0,1));ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[2],hi[2]);ax.set_zlim(lo[1],hi[1]);ax.set_box_aspect((max(.1,hi[0]-lo[0]),max(.1,hi[2]-lo[2]),max(.1,hi[1]-lo[1])));ax.view_init(el,az);ax.set_axis_off()
fig=plt.figure(figsize=(18,12),dpi=100)
for k,az in enumerate([45,135]):
 ax=fig.add_subplot(2,2,k+1,projection='3d');p=Poly3DCollection(tri[:,:,[0,2,1]],facecolor='#aaa',edgecolor='none',alpha=1);ax.add_collection3d(p)
 ids=[i for c in un for i in graph['components'][c]['globalOriginalFaces']];ax.add_collection3d(Poly3DCollection(tri[ids][:,:,[0,2,1]],facecolor='#d3452a',edgecolor='none'));axes(ax,tri,az=az);ax.set_title('Complete original: unresolved details shown orange')
for k,cs in enumerate([chosen[:3],chosen[3:]]):
 ax=fig.add_subplot(2,2,k+3,projection='3d');ids=[i for c in cs for i in graph['components'][c]['globalOriginalFaces']];t=tri[ids];lo=t.min(axis=(0,1))-2;hi=t.max(axis=(0,1))+2;near=np.flatnonzero(np.all(tri.max(axis=1)>=lo,axis=1)&np.all(tri.min(axis=1)<=hi,axis=1));ax.add_collection3d(Poly3DCollection(tri[near][:,:,[0,2,1]],facecolor='#ddd',edgecolor='none'));ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolor='#d3452a',edgecolor='#733',linewidth=.2));axes(ax,tri[near],az=135);ax.set_title('Actual original components '+str(cs))
fig.tight_layout();fig.savefig(DOC/'original-facade-1800x1200.png');plt.close(fig)
refs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())) for p in [asset,SUP/'diagnostic.json.gz',SUP/'result.json',PHYS/'selection.json.gz',HERE/'exact_packed_world_geometry_20261009.py',__import__('pathlib').Path(__file__)]]
save(DOC/'visual-context.json',dict(uids=[row['uid']],faces=len(tri),components=len(graph['components']),rootedComponents=len(graph['resolvedOriginalComponents']),unresolvedComponents=un,selectedExamples=chosen,evidenceRefs=refs,sourceGeometryChanges=0,visualRoleAccepted=False,structuralSupportAccepted=False))
print(json.dumps(dict(originalFaces=len(tri),unresolved=len(un),render=str(DOC/'original-facade-1800x1200.png'))))
