"""Read-only saved geometry display; no contact rerun or architecture qualification."""
import json
from fractions import Fraction
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image
from run import ROOT,HERE,read,save,digest
B=ROOT/'docs/astra-city/government-import'
CAP=B/'government-xl-nam-fung79099-actual-basic45779-current-capture-v2-20261012'
JOIN=B/'government-xl-nam-fung79099-actual-basic45779-lower-join-grade-cap-v2-20261012'
DOC=B/'government-xl-nam-fung79099-actual-basic45779-saved-source-lowerjoin-views-v1-20261012'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists()
 paths=[CAP/'original-full-source-root-context.json.gz',CAP/'actual-render-geometry.json.gz',CAP/'result.json',JOIN/'diagnostic.json.gz',JOIN/'result.json']
 pins=[ref(p)for p in paths]
 assert pins[2]['sha256']=='498c1512d084c0ed488993f2243523a14ba9589e05f396913bab83aeb1cd4c65'
 assert pins[4]['sha256']=='d3bdc58e7cfb9eafa617ee9fc25ec979b91b79c85ad3d6adf974749e14383933'
 d=read(JOIN/'diagnostic.json.gz');a=read(CAP/'actual-render-geometry.json.gz')
 t=np.asarray(read(paths[0])['rows'][0]['completeOriginalBinary64WorldTriangles'],dtype='<f8');assert t.shape==(13061,3,3)and digest(t.tobytes())==d['fourWorldBindings']['original']['wholeWorldSHA256']
 r=next(r for r in a['basicContextRows']if r['uid']=='landsd/45779:0');b=np.asarray(r['position'],dtype='<f8').reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]
 assert b.shape==(432,3,3)and digest(b.tobytes())==d['actualBasicWorldSHA256']
 q=d['distinctSourcePrismContactProofs'][d['fourWorldBindings']['original']['wholeWorldSHA256']];cs=q['completeSourceBasicFiniteContacts']['contacts'];assert len(cs)==202
 contactids=sorted({c['sourceFaceA']for c in cs});lowerids=sorted({c['sourceFace']for c in q['allPrismFragments']})
 colors=['#e56335'if i in contactids else'#ebb164'if i in lowerids else'#9ba7b1'for i in range(len(t))]
 pts=np.concatenate([t,b]).reshape(-1,3);lo=pts.min(0);hi=pts.max(0);DOC.mkdir(parents=True)
 exports=[]
 for name,kind,azim in [('whole-source-basic-plan','plan',0),('whole-source-basic-3d','whole',-60),('lower-interface-3d-minus60','lower',-60),('lower-interface-3d-plus120','lower',120)]:
  fig=plt.figure(figsize=(12,10))
  if kind=='plan':
   ax=fig.add_subplot(111);ax.add_collection(PolyCollection(b[:,:,[0,2]],facecolors='#64a3d3',alpha=.35,edgecolors='#416b8a',linewidths=.2));ax.add_collection(PolyCollection(t[:,:,[0,2]],facecolors=colors,alpha=.65,edgecolors='none'));ax.set_xlim(lo[0]-2,hi[0]+2);ax.set_ylim(lo[2]-2,hi[2]+2);ax.set_aspect('equal');ax.set_xlabel('Original world X (m)');ax.set_ylabel('Original world Z (m)')
  else:
   ax=fig.add_subplot(111,projection='3d');ax.add_collection3d(Poly3DCollection(b[:,:,[0,2,1]],facecolors='#64a3d3',alpha=.22,edgecolors='#416b8a',linewidths=.2));ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolors=colors,alpha=.7,edgecolors='none'))
   for c in cs:
    p=np.array([[float(Fraction(x))for x in z]for z in c['exactPoints']]);ax.plot(p[:,0],p[:,2],p[:,1],color='#b50029',linewidth=.7)
   yhi=hi[1]if kind=='whole' else 26;ax.set_xlim(lo[0]-2,hi[0]+2);ax.set_ylim(lo[2]-2,hi[2]+2);ax.set_zlim(lo[1]-1,yhi);ax.set_box_aspect([hi[0]-lo[0],hi[2]-lo[2],yhi-lo[1]+1]);ax.view_init(elev=25,azim=azim);ax.set_xlabel('World X');ax.set_ylabel('World Z');ax.set_zlabel('World Y')
  ax.set_title('Nam Fung original13061 + actual BASIC432; blue BASIC, orange saved prism/contact facets\nAll facets submitted unchanged; lower panels crop axes at Y26; transparency/occlusion context only',fontsize=10)
  p=DOC/(name+'-1800x1500.png');fig.savefig(p,dpi=150);plt.close(fig)
  with Image.open(p)as im:assert im.size==(1800,1500)
  exports.append({**ref(p),'width':1800,'height':1500,'completeSubmittedSourceFaces':13061,'completeSubmittedBasicFaces':432,'axisCropYMaximum':26 if kind=='lower'else None})
 assert [ref(p)for p in paths]==pins
 save(DOC/'context.json',{'sourceOnly':True,'identityAccepted':False,'physicalAccepted':False,'rootAccepted':False,'unchangedSourceCoordinates':True,'sourceBodies':569,'zeroSourceFaces':75,'savedContacts':202,'highlightedSourceContactFacetIds':contactids,'highlightedSourcePrismFacetIds':lowerids,'evidenceRefs':[ref(__import__('pathlib').Path(__file__))]+pins,'images':exports,'limits':'Matplotlib transparent layered diagnostic, not GPU visibility, intentional joint, collision, ownership, support or engineering proof. All source facets remain obligations; lower views are explicitly axis cropped.'})
 print(json.dumps({'images':exports}))
if __name__=='__main__':main()
