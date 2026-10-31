import json,gzip,hashlib
from pathlib import Path
from fractions import Fraction
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
base=Path('docs/astra-city/government-import');out=base/'government-xl-heritage165054-face187-context-v1-20261015';out.mkdir(exist_ok=True)
s=base/'government-xl-heritage165054-source-context-draft-v1-20261014/source-context-output-v1/complete-original-array.json.gz';d=json.loads(gzip.decompress(s.read_bytes()));faces=np.asarray(d['completeOrderedOriginalTriangles']);target=faces[187];lo=target.min(axis=0);hi=target.max(axis=0);centre=target.mean(axis=0);context=(faces[:,:,0].max(1)>=lo[0]-5)&(faces[:,:,0].min(1)<=hi[0]+5)&(faces[:,:,2].max(1)>=lo[2]-5)&(faces[:,:,2].min(1)<=hi[2]+5)
fig=plt.figure(figsize=(15,8));witness=[];refs=[s]
for mode in ['providerOriginal','literal','explicitLeftF32']:
 p=base/'government-xl-heritage165054-saved-full-actor-finite-v1-20261014/chunks/00'/mode/'00002.json.gz';refs.append(p);rows=json.loads(gzip.decompress(p.read_bytes()))['rows'];r=next(x for x in rows if x['sourceFace']==187);witness.append(dict(mode=mode,currentLowerM=r['current']['exactLowerM'],candidateLowerM=r['candidate']['exactLowerM'],candidateLowerDecimal=float(Fraction(r['candidate']['exactLowerM'])),projectionCovered=r['candidate']['projectionCovered'],sourceFaceSHA256=r['sourceFaceSHA256']))
for i,(subset,elev,azim)in enumerate([(faces,45,-70),(faces[context],25,-70)]):
 ax=fig.add_subplot(1,2,i+1,projection='3d');xyz=lambda a:(a-centre)[:,:,[0,2,1]]
 ax.add_collection3d(Poly3DCollection(xyz(subset),facecolors='#a8c8d0',edgecolors='#406775',linewidths=.1,alpha=.25));ax.add_collection3d(Poly3DCollection(xyz(faces[[187]]),facecolors='#d34535',edgecolors='#812215',linewidths=1,alpha=1));v=xyz(subset).reshape(-1,3);ax.auto_scale_xyz(v[:,0],v[:,1],v[:,2]);ax.set_box_aspect(np.maximum(np.ptp(v,axis=0),1));ax.view_init(elev=elev,azim=azim);ax.set_title('Full original source'if i==0 else'Local whole-face context (5m margin)')
fig.suptitle('Heritage Museum: original face187 in red\nSource context only; no geometry edits or automatic acceptance');fig.tight_layout();fig.savefig(out/'face187-original-context-1800x960.png',dpi=120)
(out/'evidence.json').write_text(json.dumps(dict(sourceOnly=True,installationApproved=False,sourceTriangle=target.tolist(),contextFaceIDs=np.flatnonzero(context).tolist(),modeWitnesses=witness,refs=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in refs]),indent=2)+'\n');print(witness)
