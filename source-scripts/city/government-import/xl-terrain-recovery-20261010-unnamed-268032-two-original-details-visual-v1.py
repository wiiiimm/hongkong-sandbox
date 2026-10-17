"""Original source-only part context for two unresolved visual details."""
import json,importlib.util
from pathlib import Path
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='xl-terrain-recovery-20261010-unnamed-268032-two-original-details-visual-v1';DOC=ROOT/'docs/astra-city/government-import'/BATCH;assert not DOC.exists();DOC.mkdir()
PHYS=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-unnamed-268032-nested-original-pair-current-physical-v3-20261010';SUP=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261010-unnamed-268032-complete-original-support-v1';g=read(SUP/'diagnostic.json.gz');rows={r['uid']:r for r in read(PHYS/'selection.json.gz')['rows']};assets=[ROOT/rows[a['uid']]['candidate']['path']for a in g['actors']];tri=np.concatenate([decode_original_world_triangles(p.read_bytes())for p in assets]);assert digest(tri.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256'];assert sorted(set(range(len(g['components'])))-set(g['resolvedOriginalComponents']))==[70,202]
fig=plt.figure(figsize=(18,9),dpi=100);records=[]
for k,c in enumerate([70,202]):
 ids=g['components'][c]['globalOriginalFaces'];t=tri[ids];lo=t.min(axis=(0,1));hi=t.max(axis=(0,1));margin=np.asarray([2,2,2]);near=np.where(np.all(tri.max(axis=1)>=lo-margin,axis=1)&np.all(tri.min(axis=1)<=hi+margin,axis=1))[0]
 for j,az in enumerate([40,130]):
  ax=fig.add_subplot(2,2,k*2+j+1,projection='3d',computed_zorder=False);ax.add_collection3d(Poly3DCollection(tri[near][:,:,[0,2,1]],facecolor='#cbd5df',edgecolor='#888',linewidth=.25,alpha=.3,zorder=1));ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolor='#e0442a',edgecolor='#661c0c',linewidth=.7,zorder=2));ax.set_xlim(lo[0]-1,hi[0]+1);ax.set_ylim(lo[2]-1,hi[2]+1);ax.set_zlim(lo[1]-1,hi[1]+1);ax.set_box_aspect((hi[0]-lo[0]+2,hi[2]-lo[2]+2,hi[1]-lo[1]+2));ax.view_init(25,az);ax.set_axis_off();ax.set_title(f'Original component {c}, {len(ids)} faces, bearing {az}')
 records.append(dict(component=c,faces=ids,nearbyOriginalFaceIds=near.tolist(),normalVectors=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]).tolist(),completeTriangles=t.tolist(),bounds=[lo.tolist(),hi.tolist()]))
fig.tight_layout();fig.savefig(DOC/'original-two-details-1800x900.png');plt.close(fig)
refs=[Path(__file__),SUP/'diagnostic.json.gz',SUP/'result.json',PHYS/'selection.json.gz',*assets,HERE/'exact_packed_world_geometry_20261009.py'];result=dict(uids=['landsd/101781:0','landsd/268032:0'],completeOriginalFaces=len(tri),worldSHA256=digest(tri.tobytes()),parts=records,sourceOnlyVisualContext=True,visualRoleAccepted=False,structuralRootCredit=False,fullAcceptance=False);save(DOC/'visual-context.json',result)
s=importlib.util.spec_from_file_location('f',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'unchanged-unnamed-two-original-detail-visual-context-v1',refs,json.loads(json.dumps(result)))
