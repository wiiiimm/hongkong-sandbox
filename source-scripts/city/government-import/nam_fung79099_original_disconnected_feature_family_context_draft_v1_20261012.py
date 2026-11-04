"""DRAFT exact original feature families and unchanged placed context, no role approval."""
import argparse,json,hashlib
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from nam_fung79099_source_bound_basic_mainbody_interbody_role_draft_v1_20261012 import ROOT,HERE,read,ref,SOURCE,CAP,DOC as GRAPH
BATCH='government-xl-nam-fung79099-original-disconnected-feature-family-context-v1-20261012';DOC=ROOT/'docs/astra-city/government-import'/BATCH;GRAPH_SHA='e115dc76bf126e2053c541f92c92f94cfd616e85b386e07badbbb8d73b3f9b7e'

def complete_shape_signature(faces):
 # Exact translation-invariant description only: never move vertices for rendering.
 a=np.asarray(faces,dtype='<f8');assert a.ndim==3 and a.shape[1:]==(3,3)and len(a)and np.isfinite(a).all()
 pts=[tuple(F(float(v))for v in p)for face in a for p in face];anchor=tuple(min(p[k]for p in pts)for k in range(3));rows=[]
 for face in a:
  local=[tuple(str(F(float(p[k]))-anchor[k])for k in range(3))for p in face];rows.append(min(tuple(local[i:]+local[:i])for i in range(3)))
 return hashlib.sha256(json.dumps(sorted(rows),separators=(',',':')).encode()).hexdigest(),[str(v)for v in anchor]

def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-graph-sha',required=True);args=p.parse_args();assert args.expected_graph_sha==GRAPH_SHA==ref(GRAPH/'result.json')['sha256']and not DOC.exists()
 receipt=read(GRAPH/'result.json');d=read(GRAPH/'diagnostic.json.gz');assert d['sourceSHA256']==SOURCE and d['completeFaces']==13061 and d['completeOriginalBodies']==569 and d['originalZeroFaces']==75
 refs=[ref(Path(__file__)),ref(GRAPH/'result.json'),ref(GRAPH/'diagnostic.json.gz'),ref(CAP/'original-full-source-root-context.json.gz'),ref(CAP/'actual-render-geometry.json.gz')]+receipt['evidenceRefs']
 for e in refs:assert ref(ROOT/e['path'])==e,e
 raw=read(CAP/'original-full-source-root-context.json.gz')['rows'][0];world=np.asarray(raw['completeOriginalBinary64WorldTriangles'],dtype='<f8');assert world.shape==(13061,3,3)and hashlib.sha256(world.tobytes()).hexdigest()=='5a3726aafe64e1410482327fd681f49ede03b47718d4180e0e24b5cd27078c38'
 bodysets=[g['all569BodyRoleCandidates']for g in d['distinctInterbodyRoleContexts'].values()];bodies=[r['completeOriginalFaceIds']for r in bodysets[0]];assert all([r['completeOriginalFaceIds']for r in rows]==bodies for rows in bodysets)
 misses=[g['typedGraph']['conditionalGraph']['unreachedNonvisualBodies']for g in d['distinctInterbodyRoleContexts'].values()];assert all(m==misses[0]for m in misses)and len(misses[0])==112;pending=misses[0];families={};records=[]
 for body in pending:
  faces=world[bodies[body]];sh,anchor=complete_shape_signature(faces);families.setdefault(sh,[]).append(body);records.append(dict(originalBody=body,completeSourceFaceIds=bodies[body],completeShapeTranslationInvariantSHA256=sh,exactOriginalAnchor=anchor,originalWorldBounds=[faces.min(axis=(0,1)).tolist(),faces.max(axis=(0,1)).tolist()],sourcePlacementPreserved=True,acceptedTerminalRole=False))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 from PIL import Image
 DOC.mkdir(parents=True);images=[];pending_ids=[j for i in pending for j in bodies[i]];selected=world[pending_ids];colors={34:'#e66101',18:'#5e3c99',14:'#018571'};limits=[world.min(axis=(0,1)),world.max(axis=(0,1))]
 for title,filename,axes in [('Original complete source plan; pending bodies','complete-source-pending-plan-1800x1500.png',(0,2)),('Original complete source X/Y elevation; pending bodies','complete-source-pending-x-y-1800x1500.png',(0,1)),('Original complete source Z/Y elevation; pending bodies','complete-source-pending-z-y-1800x1500.png',(2,1))]:
  fig,ax=plt.subplots(figsize=(12,10),dpi=150);ax.add_collection(PolyCollection(world[:,:,axes],facecolors='#cccccc',edgecolors='#999999',linewidth=.08,alpha=.15))
  for body in pending:ax.add_collection(PolyCollection(world[bodies[body]][:,:,axes],facecolors=colors[len(bodies[body])],edgecolors='black',linewidth=.15,alpha=.85))
  ax.autoscale();ax.set_aspect('equal');ax.set_title(title+'\nColour = face-count style only, not shape or architectural role');ax.set_xlabel('original world '+'XYZ'[axes[0]]+' (m)');ax.set_ylabel('original world '+'XYZ'[axes[1]]+' (m)');fig.tight_layout();path=DOC/filename;fig.savefig(path);plt.close(fig)
  with Image.open(path)as im:assert im.size==(1800,1500)
  images.append(dict(**ref(path),width=1800,height=1500,completeSourceFacesSubmitted=13061,pendingSourceFacesSubmitted=len(pending_ids),view='unwarped original coordinate projection; overlap/occlusion possible'))
 fig=plt.figure(figsize=(12,10),dpi=150);ax=fig.add_subplot(111,projection='3d');ax.add_collection3d(Poly3DCollection(world,facecolors='#bbbbbb',edgecolors='#777777',linewidth=.03,alpha=.10))
 for body in pending:ax.add_collection3d(Poly3DCollection(world[bodies[body]],facecolors=colors[len(bodies[body])],edgecolors='black',linewidth=.15,alpha=.85))
 lo,hi=limits;ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(lo[2],hi[2]);ax.set_box_aspect(hi-lo);ax.view_init(elev=20,azim=-60,vertical_axis='y');ax.set_title('Whole original source and all112 pending features\nTransparent layered context only; no GPU visibility/role proof');fig.tight_layout();path=DOC/'complete-source-pending-3d-1800x1500.png';fig.savefig(path);plt.close(fig)
 with Image.open(path)as im:assert im.size==(1800,1500)
 images.append(dict(**ref(path),width=1800,height=1500,completeSourceFacesSubmitted=13061,pendingSourceFacesSubmitted=len(pending_ids),view='display-only perspective; transparency/occlusion possible'))
 # Four explicit source-ID outlier candidates, not a claim of different function.
 panel_ids=[548,550,554,566];assert set(panel_ids)<=set(pending)
 fig,axs=plt.subplots(2,2,figsize=(12,10),dpi=150);panels=[]
 for ax,body in zip(axs.flat,panel_ids):
  faces=world[bodies[body]];lo=faces.min(axis=(0,1))-1;hi=faces.max(axis=(0,1))+1;mainids=np.asarray(bodies[0]);mainfaces=world[mainids];keep=np.all(mainfaces.max(axis=1)>=lo,axis=1)&np.all(mainfaces.min(axis=1)<=hi,axis=1);hostids=mainids[keep];context=world[hostids];spans=hi-lo;horizontal=0 if spans[0]>=spans[2]else 2;axes=(horizontal,1)
  if len(context):ax.add_collection(PolyCollection(context[:,:,axes],facecolors='#cccccc',edgecolors='#777777',linewidth=.15,alpha=.35))
  ax.add_collection(PolyCollection(faces[:,:,axes],facecolors=colors[len(bodies[body])],edgecolors='black',linewidth=.3,alpha=.85));ax.set_xlim(lo[horizontal],hi[horizontal]);ax.set_ylim(lo[1],hi[1]);ax.set_aspect('equal');ax.set_title('Complete source body '+str(body)+'; local body0 context');ax.set_xlabel('original '+'XYZ'[horizontal]+' (m)');ax.set_ylabel('original Y (m)');panels.append(dict(originalBody=body,completeSourceFaceIds=bodies[body],contextBody0SourceFaceIds=hostids.tolist(),bounds=[lo.tolist(),hi.tolist()],axes=list(axes),contextNotMountOrOwnershipProof=True))
 fig.suptitle('Explicit source outlier candidates; exact original placement\nFinite local AABB context only; no weld, role or support inference');fig.tight_layout(rect=(0,0,1,.95));path=DOC/'complete-source-outlier-candidate-panels-1800x1500.png';fig.savefig(path);plt.close(fig)
 with Image.open(path)as im:assert im.size==(1800,1500)
 images.append(dict(**ref(path),width=1800,height=1500,completeOutlierPanelBindings=panels,view='Exact full selected bodies; explicit subset local body0 context; overlap/occlusion possible'))
 outliers=[r for r in records if len(families[r['completeShapeTranslationInvariantSHA256']])==1]
 for e in refs:assert ref(ROOT/e['path'])==e,e
 context=dict(uid=d['uid'],sourceSHA256=SOURCE,sourceOnly=True,inputRefs=refs,all112CompleteFeatureRecords=records,completeExactShapeFamilies=[dict(completeShapeSHA256=sh,originalBodies=ids)for sh,ids in sorted(families.items())],exactSingletonShapeOutlierBodies=[r['originalBody']for r in outliers],completeWholeSourceFaces=13061,all569OriginalBodiesRemainExplicit=True,all75AuthoredZerosRemainIndependent=True,images=images,signatureMeans='Exact complete triangle coordinates relative to actual per-body minimum vertex anchor; face-order/cyclic winding invariant, original winding retained. Translation equivalence groups description only; no source coordinates moved, fitted, scaled or reflected.',rootAccepted=False,physicalAccepted=False,terminalRolesAccepted=False,sourceGeometryChanges=0)
 (DOC/'context.json').write_text(json.dumps(context,indent=2)+'\n');print(json.dumps(dict(context=ref(DOC/'context.json'),images=images,exactShapeFamilies=len(families),singletonBodies=context['exactSingletonShapeOutlierBodies'],noRoleApproval=True)))
if __name__=='__main__':main()
