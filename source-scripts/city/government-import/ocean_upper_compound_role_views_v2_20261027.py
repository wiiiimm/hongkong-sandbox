"""Inspect complete original upper components behind existing compound warnings."""
from pathlib import Path
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_assembly_context_plot_v3_20261023 import clipped_faces
P='government-xl-after-waterfront-ocean-';BATCH='government-xl-ocean-upper-compound-role-views-v2-20261027';UP='landsd/156599:0';BASE='landsd/234188:0'
def main():
 docs=ROOT/'docs/astra-city/government-import';out=docs/BATCH;assert not out.exists();pins={};refs=[Path(__file__),HERE/'original_assembly_context_plot_v3_20261023.py'];
 def take(name,path):
  if name not in pins:pins[name]=authenticate(docs/name)[1];refs.append(docs/name/'result.json')
  assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 runtime=P+'four-corrected-runtime-v1-20261027';rows=take(runtime,docs/runtime/'selection.json.gz')['rows'];tri={}
 for uid in [UP,BASE]:
  r=next(r for r in rows if r['uid']==uid);path=ROOT/r['candidate']['path'];assert digest(path.read_bytes())==r['sourceSHA256'];refs.append(path);tri[uid]=decode_original_world_triangles(path.read_bytes());assert len(tri[uid])==r['triangles']
 name=P+'pair-compound-context-v1-20261027';old=take(name,docs/name/'original.json.gz');assert old['sourceWorldSHA256']==digest(tri[UP].tobytes());flagged={r['sourceFace']for r in old['faces']};assert len(flagged)==50
 for mode in ['literal','leftF32','balancedF32']:assert {r['sourceFace']for r in take(name,docs/name/(mode+'.json.gz'))['faces']}==flagged
 t=tri[UP];normals=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);sizes=np.linalg.norm(normals,axis=1);parents=list(range(len(t)));edges={}
 def root(i):
  while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
  return i
 for i,face in enumerate(t):
  if sizes[i]==0:continue
  v=list(map(tuple,face))
  for a,b in zip(v,v[1:]+v[:1]):
   if a==b:continue
   e=tuple(sorted((a,b)))
   if e in edges:parents[root(i)]=root(edges[e])
   else:edges[e]=i
 members=defaultdict(list)
 for i in range(len(t)):
  if sizes[i]>0:members[root(i)].append(i)
 groups=sorted({root(i)for i in flagged});assert len(groups)==3;out.mkdir();records=[]
 for number,key in enumerate(groups,1):
  ids=members[key];selected=sorted(flagged&set(ids));component=t[ids];lo=component.min((0,1));hi=component.max((0,1));assert len(ids)==old['components'][str(key)]['faces'];n=normals[ids,1]/sizes[ids]
  # Display full X/Z extent. Only the tall component's upper storeys are clipped.
  displaylo=lo-[2,1,2];displayhi=hi+[2,1,2];displayhi[1]=min(displayhi[1],float(t[selected,:,1].max())+3);offset=displaylo;span=displayhi-displaylo
  fig=plt.figure(figsize=(16,6),layout='constrained')
  for index,(elev,azim)in enumerate([(90,-90),(20,35),(12,215)]):
   ax=fig.add_subplot(1,3,index+1,projection='3d');planes=[(a,float(displaylo[a]),True)for a in range(3)]+[(a,float(displayhi[a]),False)for a in range(3)]
   for mesh,color,alpha in ([(component,'#596a78',.20),(t[selected],'#d94727',.9)] if index==0 else [(t[selected],'#d94727',1)] if index==1 else [(tri[BASE],'#2374ab',.18),(component,'#596a78',.20),(t[selected],'#d94727',.9)]):
    active=np.all(mesh.max(1)>=displaylo,axis=1)&np.all(mesh.min(1)<=displayhi,axis=1);polys=clipped_faces(mesh[active],planes)
    if len(polys):ax.add_collection3d(Poly3DCollection((polys-offset)[:,:,[0,2,1]],facecolors=color,edgecolors=color,alpha=alpha,linewidth=.25))
   for face in selected:
    if face in [59,111]:
     c=t[face].mean(0)-offset;ax.text(c[0],c[2],c[1],str(face),fontsize=9,color='#7f1d1d')
   ax.set(xlim=(0,span[0]),ylim=(0,span[2]),zlim=(0,span[1]),xlabel='X offset m',ylabel='Z offset m',zlabel='Y offset m');ax.set_box_aspect(span[[0,2,1]].copy());ax.view_init(elev,azim)
  fig.suptitle(f'Upper Ocean Centre original component {number}: {len(ids)} complete source facets, {len(selected)} flagged\nRed: compound flags. Left: source component; middle: flagged-only; right: original podium context. Display only; no approval.',fontsize=11)
  path=out/('component-'+str(number)+'.png');fig.savefig(path,dpi=140);plt.close(fig);refs.append(path)
  records.append(dict(componentRepresentative=key,completeComponentFaceIds=ids,flaggedFaceIds=selected,completeComponentFaces=len(ids),completeComponentBounds=[lo.tolist(),hi.tolist()],displayBounds=[displaylo.tolist(),displayhi.tolist()],componentNormalCounts=dict(upward=int(np.count_nonzero(n>.25)),downward=int(np.count_nonzero(n<-.25)),wallLike=int(np.count_nonzero(abs(n)<=.25))),flaggedFacetFacts=[r for r in old['faces']if r['sourceFace']in selected],image=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))))
 result=dict(uids=[UP,BASE],sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows if r['uid']in[UP,BASE]},rows=records,flaggedFaces=sorted(flagged),physicalAcceptance=False,sourceRoleAccepted=False,installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Complete exact positive shared-edge source components behind all50 compound flags, with their full original podium context. All4world flagged IDs authenticated; plots show original coordinates only. Crops affect diagnostic display only. No terrain or support approval, and no downward-normal-to-soffit assumption.')
 save(out/'summary.json',result);module('ocean_upper_role_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-upper-compound-component-role-views-v1',refs,result);print([(r['completeComponentFaces'],len(r['flaggedFaceIds']),r['componentNormalCounts'])for r in records])
if __name__=='__main__':main()
