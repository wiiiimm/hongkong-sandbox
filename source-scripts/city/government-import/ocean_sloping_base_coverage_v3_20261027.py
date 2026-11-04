"""Complete finite-area clearance for five original slopes; correct V2's zero-gap scope."""
from fractions import Fraction as F
from pathlib import Path
import math
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_triangle_pair_column_gap_20261010 import verify
from ocean_sloping_base_coverage_v2_20261027 import source_polygon,fraction_area,FACES,P
BATCH='government-xl-ocean-five-sloping-base-coverage-v3-20261027'
def main():
 base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not out.exists();refs=[Path(__file__),HERE/'ocean_sloping_base_coverage_v2_20261027.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py'];records=[]
 runtime=P+'runtime-v1-20261027';_,rpins=authenticate(base/runtime);refs.append(base/runtime/'result.json');path=HERE/'local'/runtime/'runtime-geometry.json.gz';assert digest(path.read_bytes())==rpins[str(path.relative_to(ROOT))];refs.append(path)
 g=next(r for r in read(path)['rows']if r['uid']=='landsd/234188:0');ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);gh=digest(ground.tobytes());lo=ground[:,:,[0,2]].min(1);hi=ground[:,:,[0,2]].max(1)
 old=base/(P+'234188-low-faces-v1-20261027');_,pins=authenticate(old);refs.append(old/'result.json')
 for mode in ['original','literal','left','balanced']:
  path=old/(mode+'.json.gz');assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);data=read(path);assert data['groundSHA256']==gh
  for row in data['rows']:
   if row['sourceFace']not in FACES:continue
   tri=np.asarray(row['vertices'],dtype='<f8');xz=tri[:,[0,2]];ids=np.flatnonzero(np.all(hi>=xz.min(0),axis=1)&np.all(lo<=xz.max(0),axis=1));proofs=[]
   for j in ids:
    proof=verify(tri,ground[j])
    if proof['exactClosedHorizontalProjectionsMeet']and F(proof['exactMinimumFiniteColumnGapM'])<0:proofs.append(dict(groundFace=int(j),proof=proof))
   assert sorted(p['groundFace']for p in proofs if F(p['proof']['exactMinimumFiniteColumnGapM'])<F(-1,2))==sorted(p['groundFace']for p in row['negativeGroundPairProofs'])
   severe=[]
   for p in proofs:
    if F(p['proof']['exactMinimumFiniteColumnGapM'])>=F(-1,2):continue
    q=[[F(float(x))for x in v]for v in ground[p['groundFace']]];a=[q[1][i]-q[0][i]for i in range(3)];b=[q[2][i]-q[0][i]for i in range(3)];normal_y=a[2]*b[0]-a[0]*b[2]
    area=fraction_area(source_polygon(p['proof'],F(-1,2)));assert normal_y==area==0
    severe.append(dict(groundFace=p['groundFace'],groundFaceSHA256=digest(ground[p['groundFace']].tobytes()),exactNormalY=str(normal_y),exactSevereSourceBarycentricArea=str(area),groundYSpanM=float(np.ptp(ground[p['groundFace'],:,1]))))
   coverage=[];sourcearea=float(np.linalg.norm(np.cross(tri[1]-tri[0],tri[2]-tri[0]))/2)
   for threshold in [F(0),F(-1,2)]:
    polygons=[];exact_sum=F(0)
    for p in proofs:
     polygon=source_polygon(p['proof'],threshold);area=fraction_area(polygon);exact_sum+=area
     if area:polygons.append(shapely.Polygon([(float(v[0]),float(v[1]))for v in polygon]))
    ratio=float(shapely.area(shapely.union_all(polygons)))*2;assert -1e-12<=ratio<=1+1e-12
    coverage.append(dict(strictGapThresholdM=str(threshold),exactSumBarycentricArea=str(exact_sum),numericalUnionSourceAreaFraction=ratio,numericalUnionAreaM2=ratio*sourcearea))
   records.append(dict(mode=mode,sourceFace=row['sourceFace'],sourceVertices=tri.tolist(),sourceWorldSHA256=data['sourceWorldSHA256'],groundSHA256=gh,sourceAreaM2=sourcearea,finiteGroundPairsTested=len(ids),allGroundFacesConsidered=len(ground),negativePairCount=len(proofs),severePairs=severe,coverage=coverage,rawMinimumFiniteGapM=row['minimumFiniteGapM']))
 correction=dict(supersededReceipt=str((base/'government-xl-ocean-five-sloping-base-coverage-v2-20261027/result.json').relative_to(ROOT)),reason='V2 incorrectly treated the saved below-minus-half-metre pair partition as the complete below-zero partition. Its below-zero area claim is withdrawn. Its severe-area calculation remains valid. V3 recomputes every inclusive source/ground pair and includes all below-zero witnesses. V1 failed before any receipt because it assumed a single ground height at every source barycentric point. No prior receipt grants acceptance.')
 result=dict(uids=['landsd/234188:0'],sourceFaces=FACES,rows=records,correction=correction,severePairsAllZeroHorizontalProjectionAndZeroSourceArea=True,sourceTerrainClearanceDecision='five-severe-warnings-are-vertical-seam-column-contacts-not-positive-area-deep-burial',physicalAcceptance=False,installationApproved=False,publication=False,geometryChanges=0,qualification='All actual drawn-ground triangles considered for each of five original faces in all four coordinate streams. Severe threshold remains minus0.5m. Every severe pair is exactly vertical with zero severe source-surface area. Ordinary shallower below-grade area retained. This resolves the five deep-area burial interpretation only; it grants no cap/support/native-interface/source-appearance or installation approval.')
 save(out/'summary.json',result);refs.append(base/'government-xl-ocean-five-sloping-base-coverage-v2-20261027/result.json')
 module('ocean_base_complete_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'five-original-sloping-base-complete-finite-coverage-correction-v1',refs,result)
 print([dict(face=r['sourceFace'],belowZeroFraction=r['coverage'][0]['numericalUnionSourceAreaFraction'],belowHalfMetreFraction=r['coverage'][1]['numericalUnionSourceAreaFraction'],severeVerticalPairs=len(r['severePairs']))for r in records if r['mode']=='original'])
if __name__=='__main__':main()
