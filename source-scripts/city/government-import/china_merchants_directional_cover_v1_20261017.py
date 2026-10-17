"""Directional original-source occlusion diagnostic; never an acceptance waiver."""
import numpy as np
import shapely
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from require_remaining_xl import require_remaining
from china_merchants_upward_source_cover_v1_20261015 import clip
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-china-merchants-directional-cover-v1-20261017';DOC=BASE/BATCH
SOURCE=BASE/'government-xl-china-merchants264206-saved-face-attribution-v1-20261013/source-face-attribution.json.gz'
PRIOR=BASE/'government-xl-china-merchants-upward-source-cover-v1-20261015/result.json'
COUNT=BASE/'government-xl-citic-original-installed-v1-20261017/full-xl-current-count.json'
def inspect_direction(t,ids,axis,sign):
 uv=[i for i in range(3) if i!=axis];p=shapely.polygons(t[:,:,uv]);areas=shapely.area(p);valid=np.flatnonzero(areas>1e-10)
 n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);coeff=np.zeros((len(t),3));coeff[valid,:2]=-n[valid][:,uv]/n[valid,axis,None];coeff[valid,2]=np.einsum('ij,ij->i',n[valid],t[valid,0])/n[valid,axis]
 tree=shapely.STRtree(p[valid]);rows=[]
 for i in ids:
  if areas[i]<=1e-10:continue
  pieces=[];cover=[]
  for j in valid[tree.query(p[i],predicate='intersects')]:
   j=int(j)
   if j==i:continue
   delta=sign*(coeff[j]-coeff[i]);delta[2]-=.01
   points=clip([x.copy() for x in t[j][:,uv]],delta)
   if len(points)<3:continue
   q=shapely.Polygon(points).intersection(p[i])
   if q.area>1e-12:pieces.append(q);cover.append(j)
  missing=p[i].difference(shapely.union_all(pieces) if pieces else shapely.GeometryCollection())
  rows.append(dict(sourceFace=int(i),projectedAreaM2=float(areas[i]),uncoveredAreaM2=float(missing.area),uncoveredWKT=missing.wkt,occludingSourceFaceIndices=cover))
 return rows

def main():
 assert not DOC.exists();saved=read(SOURCE);require_remaining(COUNT,saved['uid'],saved['sourceSHA256'])
 prior=read(PRIOR)
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 for q in prior['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 t=np.asarray(saved['completeOriginalSourceFaceVerticesInOrdinalOrder'],dtype=float);assert t.shape==(19551,3,3)
 ids=sorted(set(saved['fullyBuriedSourceFaceIndices']));assert len(ids)==582
 # Synthetic coverage exercises both direction signs and a genuinely exposed face.
 synthetic=np.array([[[0,0,0],[1,0,0],[0,0,1]],[[0,1,0],[1,1,0],[0,1,1]]],float)
 assert inspect_direction(synthetic,[0],1,1)[0]['uncoveredAreaM2']==0
 assert inspect_direction(synthetic,[0],1,-1)[0]['uncoveredAreaM2']==.5
 assert inspect_direction(synthetic,[1],1,-1)[0]['uncoveredAreaM2']==0
 rows=[];summary=[]
 for axis in range(3):
  for sign in [-1,1]:
   found=inspect_direction(t,ids,axis,sign);rows.append(dict(axis=axis,sign=sign,faces=found));exposed=[r for r in found if r['uncoveredAreaM2']>1e-8]
   summary.append(dict(axis=axis,sign=sign,nonzeroProjectedFaces=len(found),uncoveredFaces=len(exposed),uncoveredProjectedAreaM2=sum(r['uncoveredAreaM2'] for r in found),groups=[dict(group=g['delegateOrdinal'],uncoveredFaces=[r['sourceFace'] for r in exposed if r['sourceFace'] in g['sourceFaceIndices']]) for g in saved['failureGroupsInCanonicalDelegateOrder']]))
   print(summary[-1],flush=True)
 save(DOC/'directional-cover.json.gz',dict(uid=saved['uid'],sourceSHA256=saved['sourceSHA256'],completeSourceFaces=len(t),examinedFaces=len(ids),minimumOccluderSeparationM=.01,rows=rows,summary=summary,qualification='Six axis-direction continuous projection diagnostics only. Does not prove full enclosure, camera visibility, terrain occlusion, basement roles, collision acceptance or permission to discard any face.',installationApproved=False))
 out=module('china_directional_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-buried-original-six-direction-visibility-diagnostic-v1',[Path(__file__),SOURCE,PRIOR,COUNT,HERE/'china_merchants_upward_source_cover_v1_20261015.py',HERE/'require_remaining_xl.py'],dict(uids=[saved['uid']],summary=summary,fullAcceptance=False,nextStep='Use exposed-face groups to focus source-role and runtime visibility review. Axis coverage is not an enclosure or acceptance certificate.'))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()
