"""Measure exact original detached-component separation and export source context."""
from pathlib import Path
from fractions import Fraction
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_closed_components import components
from exact_original_triangle_distance_20261009 import triangle_distance
BASE=ROOT/'docs/astra-city/government-import'
def main():
 batch='government-xl-fu-tor-loy-detached-context-v1-20261023';out=BASE/batch;assert not out.exists();refs=[Path(__file__)]
 capture='government-xl-fu-tor-loy-five-originals-current-v1-20261023-runtime';_,pins=authenticate(BASE/capture)
 p=BASE/capture/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([p,BASE/capture/'result.json'])
 output=[]
 for r in read(p)['rows']:
  if r['uid']not in ['landsd/231442:0','landsd/232818:0']:continue
  asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
  t=decode_original_world_triangles(asset.read_bytes());groups=sorted(components(t)['components'],key=lambda c:-c['triangles']);main=groups[0]['faceIndices'];target=groups[1]if r['uid']=='landsd/231442:0'else next(c for c in groups if c['faceIndices']==[1079])
  a,b=t[target['faceIndices']],t[main];pairs=[]
  for i,f in zip(target['faceIndices'],a):
   gaps=np.maximum(np.maximum(f.min(0)-b.max(1),b.min(1)-f.max(0)),0);bounds=np.einsum('ij,ij->i',gaps,gaps)
   pairs.extend((float(v),i,j)for v,j in zip(bounds,main))
  best=None;tested=0
  for lower,i,j in sorted(pairs):
   if best and lower>float(Fraction(best['exactSquaredDistanceM2']))+1e-10:break
   proof=triangle_distance(t[i],t[j]);tested+=1
   if best is None or Fraction(proof['exactSquaredDistanceM2'])<Fraction(best['exactSquaredDistanceM2']):best=dict(**proof,sourceFace=i,mainFace=j)
  assert best and not best['exactOriginalContact']
  row=dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],worldSHA256=digest(t.tobytes()),completeMainFaces=len(main),secondaryFaces=target['faceIndices'],exactNearestPair=best,minimumDistanceM=float(Fraction(best['exactSquaredDistanceM2']))**.5,pairsConsidered=len(pairs),exactPairsTested=tested,sourceGeometryChanges=0,installationApproved=False)
  out.mkdir(parents=True,exist_ok=True);save(out/(r['uid'].split('/')[1]+'.json'),row);output.append(row)
  centre=a.reshape(-1,3).mean(0);span=max(np.ptp(a,axis=(0,1)).max()*1.5,2.)
  lo,hi=centre-span,centre+span;local=b[np.all(b.max(1)>=lo,axis=1)&np.all(b.min(1)<=hi,axis=1)]
  fig=plt.figure(figsize=(14,7));ax=fig.add_subplot(121,projection='3d');ax.add_collection3d(Poly3DCollection(local,facecolor='#bbc9d4',edgecolor='#7c8d99',linewidth=.15,alpha=.25));ax.add_collection3d(Poly3DCollection(a,facecolor='#f08b23',edgecolor='#9b4412',linewidth=.7,alpha=.9));ax.set(xlim=(lo[0],hi[0]),ylim=(lo[2],hi[2]),zlim=(lo[1],hi[1]))
  # Correct plotting convention: source coordinates X,Y(height),Z map to plot X,Y,Z.
  ax.set(xlim=(lo[0],hi[0]),ylim=(lo[1],hi[1]),zlim=(lo[2],hi[2]));ax.set_box_aspect((1,1,1));ax.view_init(elev=20,azim=-55);ax.set_xlabel('X m');ax.set_ylabel('height m');ax.set_zlabel('Z m')
  bx=fig.add_subplot(122)
  for f in local:bx.fill(f[:,0]-centre[0],f[:,1]-centre[1],facecolor='#bbc9d4',edgecolor='#7c8d99',alpha=.15,linewidth=.2)
  for f in a:bx.fill(f[:,0]-centre[0],f[:,1]-centre[1],facecolor='#f08b23',edgecolor='#9b4412',alpha=.7,linewidth=.7)
  q1=np.array([float(Fraction(v))for v in best['firstOriginalWitness']]);q2=np.array([float(Fraction(v))for v in best['secondOriginalWitness']]);bx.plot([q1[0]-centre[0],q2[0]-centre[0]],[q1[1]-centre[1],q2[1]-centre[1]],'r.-');bx.set_aspect('equal');bx.set_xlabel('X offset m');bx.set_ylabel('height offset m')
  fig.suptitle(r['uid']+' · unchanged original secondary component\nminimum finite separation %.9fm; contact/support not claimed'%row['minimumDistanceM']);fig.tight_layout();fig.savefig(out/(r['uid'].split('/')[1]+'.png'),dpi=160);plt.close(fig);print({k:v for k,v in row.items()if k not in ['exactNearestPair','secondaryFaces']},flush=True)
 result=dict(uids=[r['uid']for r in output],rows=output,installationApproved=False,qualification='Exact finite original facet separation, original body context. A near miss is not attachment or support. Geometry/pose remain unchanged; no semantic role inferred.')
 save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','source_closed_components.py','exact_original_triangle_distance_20261009.py','exact_original_shell_intersections_20261009.py'])
 module('detached_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-original-detached-component-context',refs,result)
if __name__=='__main__':main()
