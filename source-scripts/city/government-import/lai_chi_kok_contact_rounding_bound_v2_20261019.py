"""Exact barycentric finite-contact correspondence across renderer coordinate modes."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_shell_intersections_20261009 import rational_face,intersection_points,sub,dot
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-contact-rounding-bound-v2-20261019';DOC=BASE/BATCH;PATHS=BASE/'government-xl-lai-chi-kok-rim-contact-paths-v2-20261019';REPLAY=BASE/'government-xl-lai-chi-kok-rim-contact-replay-v2-20261019';ATTR=BASE/'government-xl-lai-chi-kok-eight-render-attributes-v1-20261019';SRC=BASE/'government-xl-lai-chi-kok-original-component-checks-v2-20261019'
def bary(p,t):
 u=sub(t[1],t[0]);v=sub(t[2],t[0]);w=sub(p,t[0]);a=dot(u,u);b=dot(u,v);c=dot(v,v);d=dot(w,u);e=dot(w,v);den=a*c-b*b;assert den;beta=(c*d-b*e)/den;gamma=(a*e-b*d)/den;weights=(1-beta-gamma,beta,gamma);assert min(weights)>=0 and max(weights)<=1;assert tuple(sum(weights[i]*t[i][k]for i in range(3))for k in range(3))==p;return weights
def mapped(weights,t):return tuple(sum(weights[i]*t[i][k]for i in range(3))for k in range(3))
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'exact_original_shell_intersections_20261009.py'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');r=read(REPLAY/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(REPLAY/'result.json')
 for e in r['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p);pins[p]=e['sha256']
 data=read(SRC/'input.json.gz');oldSupport=np.asarray(data['podium']);ng=len(oldSupport)-37577;ground=oldSupport[:ng];old={r['uid']:np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in data['rows']};captures={r['uid']:r for r in read(ATTR/'attributes.json.gz')['rows']};summary=[]
 for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
  world={u:np.asarray(r[field],dtype='<f8').reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]for u,r in captures.items()};support=np.concatenate([ground,world['landsd/281463:0']])
  for uid,t in old.items():
   out=[]
   for row in read(PATHS/(uid.split('/')[1]+'.json'))['rows']:
    hit=row['finiteSupportContact'];assert hit;i=hit['sourceFace'];j=hit['supportFace'];a=rational_face(t[i]);b=rational_face(oldSupport[j]);points=sorted(intersection_points(a,b));assert len(points)>1;na=rational_face(world[uid][i]);nb=rational_face(support[j]);pairs=[];squares=[];mappedpoints=[]
    for point in points:
     wa=bary(point,a);wb=bary(point,b);pa=mapped(wa,na);pb=mapped(wb,nb);delta=sub(pa,pb);square=dot(delta,delta);squares.append(square);mappedpoints.append(pa);pairs.append(dict(sourceWeights=list(map(str,wa)),supportWeights=list(map(str,wb)),sourcePoint=list(map(float,pa)),supportPoint=list(map(float,pb)),exactSquaredSeparation=str(square)))
    assert len(set(mappedpoints))>1;bound=max(squares);out.append(dict(sample=row['sample'],sourceFace=i,supportFace=j,originalIntersectionVertices=len(points),mappedSourcePositiveDimension=True,maximumSquaredSeparation=str(bound),maximumSeparationMetres=float(bound)**.5,withinExistingPointOneMetreBand=bound<=F(1,100),vertexCorrespondences=pairs))
   s=dict(uid=uid,mode=mode,samples=len(out),withinExistingPointOneMetreBand=sum(r['withinExistingPointOneMetreBand']for r in out),maximumSeparationMetres=max(r['maximumSeparationMetres']for r in out));summary.append(s);save(DOC/(uid.split('/')[1]+'-'+mode+'.json'),dict(summary=s,rows=out));print(s,flush=True)
 save(DOC/'summary.json',dict(rows=summary,installationApproved=False,proof='Exact rational original intersection vertices have nonnegative barycentric coordinates in both finite facets. Reusing those weights in each rendered facet preserves containment. Convexity bounds separation everywhere on their corresponding convex contact region by the largest vertex-pair distance. This is a finite contact band, not an assertion of exact intersection or zero rim gap.'))
 module('rounding_bound_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-contact-renderer-rounding-bound',list(dict.fromkeys(refs)),dict(uids=list(old),rows=summary,installationApproved=False))
if __name__=='__main__':main()
