"""Inspect complete immutable source geometry against exact current BASIC footprints."""
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['batch','runtime','scope']:p.add_argument('--'+key,required=True)
 a=p.parse_args();assert all(v.startswith('government-xl-')and'/'not in v for v in vars(a).values())
 base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();pins={};refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py']
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
  path=base/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(a.runtime,'selection.json.gz');scope=take(a.scope,'summary.json');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==scope['currentManifestSHA256']==selection['manifestSHA256'];refs.append(manifest);out.mkdir();rows=[]
 for row in selection['rows']:
  uid=row['uid'];source=ROOT/row['candidate']['path'];assert digest(source.read_bytes())==row['sourceSHA256'];refs.append(source);tri=decode_original_world_triangles(source.read_bytes());assert len(tri)==row['triangles']
  forms=take(a.scope,uid.split('/')[1]+'-forms.json.gz');model=tri.copy();model[:,:,2]*=-1;box=np.array([model.min((0,1)),model.max((0,1))]);colours=plt.get_cmap('viridis')((tri[:,:,1].mean(1)-box[0,1])/max(box[1,1]-box[0,1],1));files=[]
  fig,ax=plt.subplots(figsize=(15,10),layout='constrained');order=np.argsort(tri[:,:,1].mean(1));ax.add_collection(PolyCollection(model[order][:,:,[0,2]],facecolors=colours[order],edgecolors='none',rasterized=True))
  for item in forms:
   b=item['building'];own=b['uid']==uid
   for ring in b['rings']:
    ring=np.asarray(ring);ax.plot(ring[:,0],-ring[:,1],color='#e946ef'if own else '#e88722',lw=2 if own else .9)
   centre=np.mean(np.asarray(b['rings'][0])[:-1],axis=0);ax.text(centre[0],-centre[1],b['uid'].split('/')[1],fontsize=6,color='#98149e'if own else '#783c00',ha='center')
  ax.set_xlim(box[0,0]-15,box[1,0]+15);ax.set_ylim(box[0,2]-15,box[1,2]+15);ax.set_aspect('equal');ax.set_xlabel('Original render east X (m)');ax.set_ylabel('North = −render Z (m)');ax.set_title(uid+' · complete original '+str(len(tri))+' faces\nHeight-coloured source; magenta own / orange other exact BASIC footprints')
  f=out/(uid.split('/')[1].replace(':','-')+'-plan.png');fig.savefig(f,dpi=160);plt.close(fig);files.append(f)
  for azimuth in [35,215]:
   fig=plt.figure(figsize=(15,10),layout='constrained');ax=fig.add_subplot(111,projection='3d');ax.add_collection3d(Poly3DCollection(model[:,:,[0,2,1]],facecolors=colours,edgecolors='none',rasterized=True))
   for item in forms:
    b=item['building'];colour='#e946ef'if b['uid']==uid else '#b64a11'
    for ring in b['rings']:
     ring=np.asarray(ring);ax.plot(ring[:,0],-ring[:,1],np.full(len(ring),b['base']+b['height']),color=colour,lw=.8)
   ax.set_xlim(box[0,0],box[1,0]);ax.set_ylim(box[0,2],box[1,2]);ax.set_zlim(box[0,1]-5,box[1,1]+5);ax.set_box_aspect(np.maximum((box[1]-box[0])[[0,2,1]],1));ax.view_init(elev=35,azim=azimuth);ax.set_title(uid+' · original source / surveyed BASIC roof outlines\nDiagnostic only; no identity, support or installation approval');ax.set_xlabel('East X');ax.set_ylabel('North −Z');ax.set_zlabel('HKPD Y')
   f=out/(uid.split('/')[1].replace(':','-')+'-oblique-'+str(azimuth)+'.png');fig.savefig(f,dpi=160);plt.close(fig);files.append(f)
  rows.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],completeOriginalFaces=len(tri),exactCurrentBasicForms=len(forms),sourcePoseChanges=0,images=[dict(path=str(f.relative_to(ROOT)),sha256=digest(f.read_bytes()))for f in files]));print(uid,'3 complete-source views written',flush=True)
 result=dict(uids=[r['uid']for r in rows],rows=rows,sourceGeometryChanges=0,publication=False,installationApproved=False,visualAcceptance=False,qualification='All original triangles rendered at fixed source coordinates; no decimation, source edits, fitted imagery or role acceptance. Each PNG is2400x1600. BASIC roof outlines retain exact recorded heights; primary maps must be reviewed separately.')
 save(out/'summary.json',result);module('selected_original_scope_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-source-and-current-basic-scope-investigation-views',refs,result)
if __name__=='__main__':main()
