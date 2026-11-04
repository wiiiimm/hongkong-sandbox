"""Plot unchanged original detached and attached access side faces, diagnostic crop."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest

DOC=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-panel-visual-20261009'
INPUT=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-pair-interface-20261009/exact-original-contact-inputs.json.gz'
CONTEXT=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-panel-context-20261009/original-panel-nearest-complete-sources.json.gz'
PRIOR=ROOT/'docs/astra-city/government-import/government-xl-popcorn-source-access-ownership-20261009/every-far-access-component-exact-attachments.json.gz'

def main():
 assert not (DOC/'render.json').exists(),'Fresh evidence captures only'
 row=next(r for r in read(INPUT)['rows'] if r['uid']=='landsd/295538:0');tri=np.array(row['position']).reshape(-1,3,3)
 context=read(CONTEXT);parts=read(PRIOR)['separateOriginalSourceComponents'];panel_ids=context['originalPanelFaces'];paired=next(p for p in parts if p['component']==13063)
 counterpart=paired['allOriginalFaceIndices'];panel=tri[panel_ids];lo=panel.min((0,1));hi=panel.max((0,1))
 mask=np.all(tri.max(1)>=lo-[4,4,4],axis=1)&np.all(tri.min(1)<=hi+[4,4,4],axis=1)
 crop_ids=np.flatnonzero(mask);crop_ids=np.setdiff1d(crop_ids,panel_ids+counterpart);origin=np.array([10195.,0.,-2210.])
 fig=plt.figure(figsize=(16,9),dpi=180);fig.suptitle('PopCorn original access side surfaces · complete 12-face panel',fontsize=16)
 for i,(azim,title) in enumerate([(-110,'Original mall crop · west view'),(30,'Original mall crop · reverse view')],1):
  ax=fig.add_subplot(1,2,i,projection='3d');ax.set_proj_type('ortho')
  for ids,color,alpha in [(crop_ids,'#afb7bd',.18),(counterpart,'#7352a6',1.),(panel_ids,'#e97022',1.)]:
   vertices=tri[ids]-origin;vertices=vertices[:,:,[0,2,1]];vertices[:,:,1]*=-1
   ax.add_collection3d(Poly3DCollection(vertices,facecolors=color,edgecolors=color,linewidth=.4,alpha=alpha))
  ax.set_xlim(lo[0]-origin[0]-3,hi[0]-origin[0]+3);ax.set_ylim(-(hi[2]-origin[2])-3,-(lo[2]-origin[2])+3);ax.set_zlim(lo[1]-2,hi[1]+2)
  ax.set_box_aspect((hi[0]-lo[0]+6,hi[2]-lo[2]+6,hi[1]-lo[1]+4));ax.view_init(elev=17,azim=azim)
  ax.set_title(title);ax.set_xlabel('East offset (m)');ax.set_ylabel('North offset (m)');ax.set_zlabel('HKPD (m)')
 fig.text(.5,.06,'Orange: all 12 detached original panel faces · purple: all original faces of attached component 13063\nGrey: surrounding original source crop. No geometry edits. 1 m vertical edge pairs; vertex-to-source gaps 4.16–5.52 cm.\nDiagnostic only: exact no-contact evidence remains; no architectural role, support or installation approval.',ha='center',fontsize=10)
 fig.subplots_adjust(bottom=.17,top=.87,wspace=.02);DOC.mkdir(parents=True,exist_ok=True);file=DOC/'original-panel-and-attached-source-2880x1620.png';fig.savefig(file,dpi=180);plt.close(fig)
 refs=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in [INPUT,CONTEXT,PRIOR,Path(__file__),file]]
 save(DOC/'render.json',{'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'originalPanelFaces':panel_ids,'originalCounterpartFaces':counterpart,'surroundingCropOriginalFaces':crop_ids.tolist(),'counterpartExactDirectMainBodyContact':paired['exactDirectMainBodyContact'],'width':2880,'height':1620,'evidenceRefs':refs,'sourceGeometryChanges':0,'installationApproved':False})
 print({'file':str(file.relative_to(ROOT)),'panelFaces':len(panel_ids),'counterpartFaces':len(counterpart),'surroundingOriginalFaces':len(crop_ids)},flush=True)

if __name__=='__main__':main()
