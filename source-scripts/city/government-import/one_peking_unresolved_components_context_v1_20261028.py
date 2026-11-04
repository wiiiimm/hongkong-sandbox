"""Complete original component context for a bounded non-modelling role review.

No support inference, tolerance change, source/terrain edit or approval.
"""
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-one-peking-ten-components-context-v1-20261028';GRAPH='government-xl-one-peking-original-ordinary-ground-graph-diagnostic-v2-20261010';PRIMARY='government-xl-one-peking-original-horizontal-assembly-primary-visuals-v1-20261010'
def main():
 p=argparse.ArgumentParser();p.add_argument('--lease',required=True);a=p.parse_args();lease=read(Path(a.lease));assert reservations.owns(lease)and{'building:landsd/233985:0','building:landsd/240487:0'}<=set(lease['resources']);out=BASE/BATCH;assert not out.exists();receipt,pins=authenticate(BASE/GRAPH);path=BASE/GRAPH/'diagnostic.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];g=read(path);refs=[Path(__file__),BASE/GRAPH/'result.json',path];meshes=[]
 for actor in g['actors']:
  paths=[ROOT/r['path']for r in receipt['evidenceRefs']if r['sha256']==actor['sourceSHA256']and r['path'].endswith('.glb.gz')];assert paths;asset=next(p for p in paths if p.exists());assert digest(asset.read_bytes())==actor['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==actor['completeOriginalFaceCount']and digest(tri.astype('<f8').tobytes())==actor['originalWorldTrianglesSHA256'];meshes.append(tri);refs.append(asset)
 alltri=np.concatenate(meshes);assert digest(alltri.astype('<f8').tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256'];parts=g['components'];ids=[i for p in parts for i in p['globalOriginalFaces']];assert len(ids)==len(set(ids))==len(alltri)and set(ids)==set(range(len(alltri)));unresolved=[int(r.rsplit(':',1)[1])for r in g['reasons']];assert unresolved==[8,12,13,15,21,23,27,34,46,49];rows=[]
 fig=plt.figure(figsize=(12,25),dpi=160);lo,hi=alltri.min((0,1)),alltri.max((0,1));span=(hi-lo)[[0,2,1]]
 for k,index in enumerate(unresolved):
  component=parts[index];tri=alltri[component['globalOriginalFaces']];low,high=tri.min((0,1)),tri.max((0,1));normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normals,axis=1);good=length>0;up=np.abs(normals[good,1])/length[good];area=length[good]/2
  row=dict(component=index,uid=component['actorUID'],completeOriginalFaceIDs=component['globalOriginalFaces'],completeFaces=len(tri),worldBounds=[low.tolist(),high.tolist()],axisSpans=(high-low).tolist(),surfaceAreaM2=float(area.sum()),nearHorizontalAreaFraction=float(area[up>=.9].sum()/area.sum())if area.sum()else None,nearVerticalAreaFraction=float(area[up<=.1].sum()/area.sum())if area.sum()else None,roleAccepted=False,physicalAccepted=False);rows.append(row)
  ax=fig.add_subplot(5,2,k+1,projection='3d');ax.add_collection3d(Poly3DCollection(alltri[:,:,[0,2,1]],facecolors='#9fa8ad',edgecolors='none',alpha=.07));ax.add_collection3d(Poly3DCollection(tri[:,:,[0,2,1]],facecolors='#e35317',edgecolors='#7b2008',linewidths=.6,alpha=1));ax.set(xlim=(lo[0],hi[0]),ylim=(lo[2],hi[2]),zlim=(lo[1],hi[1]));ax.set_box_aspect(span.copy());ax.view_init(elev=15,azim=-65);ax.set_title('Component '+str(index)+' | '+str(len(tri))+' faces\nXYZ spans '+', '.join(format(v,'.3f')for v in high-low)+'m',fontsize=9);ax.tick_params(labelsize=6)
 out.mkdir();fig.suptitle('Every original source facet retained; exact unresolved components highlighted individually\nSource-only context, no host/ground/role acceptance',fontsize=12);fig.tight_layout(rect=(0,0,1,.97));fig.savefig(out/'ten-complete-components-1920x4000.png');plt.close(fig)
 primary,pp=authenticate(BASE/PRIMARY);refs.append(BASE/PRIMARY/'result.json')
 for name in['owner-exterior.jpg','owner-facade.jpg','primary-and-source-context.json']:
  p=BASE/PRIMARY/name;assert digest(p.read_bytes())==pp[str(p.relative_to(ROOT))];refs.append(p)
 result=dict(uids=[a['uid']for a in g['actors']],completeOriginalFaces=len(alltri),completeOriginalComponents=len(parts),unresolvedComponents=rows,rawGroundGraphReasons=g['reasons'],sourceGeometryChanges=0,allSourceFacetsRetained=True,installationApproved=False,qualification='All58 original connected components partition every15784source facet. All10 unresolved components retained and highlighted. Raw historical support failures unchanged. Axis spans, normal-area fractions and owner photographs provide context only; thinness or appearance alone grants no source role, exact mounting, current support, ground or installation acceptance. No repeat of failed .1m association tests.')
 save(out/'summary.json',result);assert reservations.owns(lease);refs.extend([HERE/'exact_packed_world_geometry_20261009.py']);module('one_peking_component_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-ten-component-role-context-no-acceptance',refs,result);print([(r['component'],r['completeFaces'],r['axisSpans'])for r in rows],flush=True)
if __name__=='__main__':main()
