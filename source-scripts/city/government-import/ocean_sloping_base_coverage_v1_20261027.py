"""Quantify only saved finite-column witnesses; no source-role or tolerance waiver."""
from fractions import Fraction as F
from pathlib import Path
import math
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
FACES=[225,226,227,1436,1437]
P='government-xl-after-waterfront-ocean-four-corrected-'
BATCH='government-xl-ocean-five-sloping-base-coverage-v1-20261027'
def hull(points):
 points=sorted(set(points))
 if len(points)<3:return points
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[];hi=[]
 for p in points:
  while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
  lo.append(p)
 for p in reversed(points):
  while len(hi)>=2 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
  hi.append(p)
 return lo[:-1]+hi[:-1]
def clip(poly,threshold):
 # q=(source barycentric1,source barycentric2,gap); affine interpolation.
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  inside_a=a[2]<threshold;inside_b=b[2]<threshold
  if inside_a:out.append(a)
  if inside_a!=inside_b:
   t=(threshold-a[2])/(b[2]-a[2]);out.append(tuple(a[k]+t*(b[k]-a[k])for k in range(3)))
 return out
def source_polygon(proof,threshold):
 points={}
 for v in proof['allExactBasicFeasibleColumnVertices']:
  w=list(map(F,v['exactSourceBarycentricWeights']));assert sum(w)==1 and min(w)>=0
  key=(w[1],w[2]);gap=F(v['exactGapM']);assert key not in points or points[key]==gap
  points[key]=gap
 boundary=hull(list(points));poly=[(*p,points[p])for p in boundary]
 return clip(poly,threshold) if len(poly)>=3 else []
def fraction_area(poly):
 if len(poly)<3:return F(0)
 return abs(sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(poly,poly[1:]+poly[:1])))/2

def main():
 base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not out.exists();old=base/(P+'234188-low-faces-v1-20261027');_,pins=authenticate(old)
 refs=[Path(__file__),old/'result.json'];records=[]
 for mode in ['original','literal','left','balanced']:
  path=old/(mode+'.json.gz');assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);data=read(path)
  assert data['completeSourceFaces']==10353 and sorted(r['sourceFace']for r in data['rows'])==[17,225,226,227,611,1436,1437,3059,3060,7525,7526,7527,7528,10150,10151]
  for row in data['rows']:
   if row['sourceFace']not in FACES:continue
   vertices=row['vertices'];a=[vertices[1][i]-vertices[0][i]for i in range(3)];b=[vertices[2][i]-vertices[0][i]for i in range(3)];normal=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];area=math.sqrt(sum(x*x for x in normal))/2
   coverage=[]
   for threshold in [F(0),F(-1,2)]:
    polygons=[];rational_sum=F(0)
    for witness in row['negativeGroundPairProofs']:
     proof=witness['proof'];assert proof['noGroundOrSourceFaceOmitted'] and proof['exactClosedHorizontalProjectionsMeet']
     polygon=source_polygon(proof,threshold);rational_sum+=fraction_area(polygon)
     if fraction_area(polygon)>0:polygons.append(shapely.Polygon([(float(p[0]),float(p[1]))for p in polygon]))
    union=shapely.union_all(polygons);ratio=float(shapely.area(union))*2
    assert -1e-12<=ratio<=1+1e-12
    coverage.append(dict(strictGapThresholdM=str(threshold),finiteNegativePairCount=len(polygons),exactSumBarycentricArea=str(rational_sum),numericalUnionSourceAreaFraction=ratio,numericalUnionAreaM2=ratio*area,numericalUnionAvoidsDoubleCounting=True))
   records.append(dict(mode=mode,sourceFace=row['sourceFace'],sourceWorldSHA256=data['sourceWorldSHA256'],groundSHA256=data['groundSHA256'],sourceAreaM2=area,rawMinimumFiniteGapM=row['minimumFiniteGapM'],rawHighestVertexAboveEveryGroundFace=row['highestVertexAboveEveryOverlappingGroundFace'],coverage=coverage))
 result=dict(uids=['landsd/234188:0'],sourceFaces=FACES,rows=records,physicalAcceptance=False,installationApproved=False,publication=False,geometryChanges=0,qualification='Strict finite saved triangle-column witnesses clipped in original source barycentric space with rational arithmetic. Polygon union and physical surface areas are numerical diagnostics, never exact acceptance, source-role approval, threshold changes or terrain edits. Missing nonnegative ground pairs cannot contribute to negative thresholds.')
 save(out/'summary.json',result)
 module('ocean_base_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'five-original-sloping-base-finite-coverage-diagnostic-v1',refs,result)
 print([dict(face=r['sourceFace'],belowGradeFraction=r['coverage'][0]['numericalUnionSourceAreaFraction'],belowHalfMetreFraction=r['coverage'][1]['numericalUnionSourceAreaFraction'])for r in records if r['mode']=='original'])
if __name__=='__main__':main()
