"""Exact unchanged Block16 upper-source context; all seven obligations unknown."""
import json,gzip,struct,importlib.util
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-block16-original-roof-context-v1-20261011';D=B/BATCH;G=B/'government-xl-parkview-block16-complete-original-support-graph-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not D.exists();r=read(G/'diagnostic.json.gz');p=ROOT/r['source']['path'];assert ref(p)==r['source'];raw=p.read_bytes();original=decode_original_world_triangles(raw);assert digest(original.tobytes())==r['completeOriginalWorldSHA256'];assert r['unreachedBodies']==[57,58,59,60,61,62,121]
 D.mkdir(parents=True);t=original[:,:,[0,2,1]];cs=r['completeSourceEdgeBodyFaces'];visible=np.flatnonzero(original[:,:,1].min(1)>=375);bodies=r['unreachedBodies'];assert all(set(cs[b])<=set(visible)for b in bodies)
 save(D/'visual-subset-scope.json',dict(completeOriginalWorldSHA256=digest(original.tobytes()),originalFaceIDs=list(map(int,visible)),renderOnlySelection='Complete unchanged original facets with every vertex Y>=375m; no source triangles clipped or altered.',notWholeSourceProof=True,sourceGeometryChanges=0))
 save(D/'seven-body-original-boundary-census.json',dict(rows=[dict(body=b,originalFaces=cs[b],completeOriginalBodyCensus=census(original,cs[b]),roleUnresolved=True)for b in bodies],groundRootUnproved=True,sourceGeometryChanges=0,notRoleApproval=True))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 colors=['#d7191c','#fdae61','#2c7bb6','#abd9e9','#7b3294','#008837','#e78ac3'];lo=t[visible].min((0,1));hi=t[visible].max((0,1));fig=plt.figure(figsize=(15,7),dpi=180);ax=fig.add_subplot(121);ax.add_collection(PolyCollection(t[visible,:,:2],facecolors='#cccccc',edgecolors='#555555',linewidths=.2,alpha=.55))
 for b,col in zip(bodies,colors):
  ax.add_collection(PolyCollection(t[cs[b],:,:2],facecolors=col,edgecolors='black',linewidths=.4));v=t[cs[b]].mean((0,1));ax.annotate(str(b),(v[0],v[1]),xytext=(6,10),textcoords='offset points',fontsize=8,color=col,arrowprops=dict(arrowstyle='-',color=col))
 ax.set_xlim(lo[0]-1,hi[0]+1);ax.set_ylim(lo[1]-1,hi[1]+1);ax.set_aspect('equal');ax.set_xlabel('original X');ax.set_ylabel('original Z');ax.set_title('Original upper facets; seven unqualified bodies marked')
 ax=fig.add_subplot(122,projection='3d');ax.add_collection3d(Poly3DCollection(t[visible],facecolors='#cccccc',edgecolors='#555555',linewidths=.2,alpha=.4))
 for b,col in zip(bodies,colors):
  ax.add_collection3d(Poly3DCollection(t[cs[b]],facecolors=col,edgecolors='black',linewidths=.4));v=t[cs[b]].mean((0,1));ax.text(v[0],v[1],v[2]+.08,str(b),color=col,fontsize=8)
 ax.set_xlim(lo[0]-1,hi[0]+1);ax.set_ylim(lo[1]-1,hi[1]+1);ax.set_zlim(375,hi[2]+.5);ax.set_box_aspect((hi[0]-lo[0]+2,hi[1]-lo[1]+2,max(hi[2]-375+.5,2)));ax.view_init(elev=30,azim=-60);ax.set_xlabel('original X');ax.set_ylabel('original Z');ax.set_zlabel('original Y');ax.set_title('Unchanged provider geometry; function and role unresolved');fig.tight_layout();fig.savefig(D/'original-roof-context.png');plt.close(fig)
 b=gzip.decompress(raw)if raw[:2]==b'\x1f\x8b'else raw;n,_=struct.unpack_from('<II',b,12);gl=json.loads(b[20:20+n]);save(D/'original-node-context.json',dict(originalSourceSHA256=digest(raw),completeOriginalNodes=gl['nodes'],completeOriginalMeshes=gl['meshes'],sourceOnly=True,roleApproval=False))
 refs=[ref(x)for x in [Path(__file__),p,G/'result.json',G/'diagnostic.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py']];save(D/'review.json',dict(uids=['landsd/256319:0'],unresolvedBodies=bodies,sourceOnly=True,finding='All seven unreached original bodies occur in recorded unchanged upper-source subset. Context is provider geometry, not photograph/function/architectural intent. Boundary census is inventory only; complete mounting/role evidence remains necessary.117 conditional connected bodies remain ungrounded because original cap45867 is below retained parent terrain. No solid/root/bridge/role approval or current acceptance.',evidenceRefs=refs,currentAcceptance=False,installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0,terrainChanges=0))
 spec=importlib.util.spec_from_file_location('block16_original_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.freeze(BATCH,'seven-original-roof-body-provider-context-only-v1',[ROOT/x['path']for x in refs],dict(uids=['landsd/256319:0'],sourceOnly=True,currentAcceptance=False,nativeReacceptance=False,noArchitecturalFunctionClaim=True,allSevenBodyRolesUnresolved=True,buriedCapNegativePreserved=True))
if __name__=='__main__':main()
