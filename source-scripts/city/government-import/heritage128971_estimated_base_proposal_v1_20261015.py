"""Read-only proposal: recompute an unsurveyed BASIC base from exact drawn ground."""
from pathlib import Path
from fractions import Fraction as F
import json,gzip,hashlib
import numpy as np
from actual_native_parent_transition_v3_20261010 import clip,cross,rational
from exact_original_polygon_triangle_partition_20261010 import exact_partition
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'docs/astra-city/government-import'
CAP=BASE/'government-xl-heritage165054-parent-basic-production-capture-v1-20261014'
OUT=BASE/'government-xl-heritage128971-estimated-base-proposal-v1-20261015'
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 assert not OUT.exists()
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']=='12971667a74b07de90ce5ee29999f44a6bf297de84ec7916a629bc42725cd82c'
 tile=ROOT/'3d-viewer/city/data/tiles/1_-6.json';building=next(b for b in read(tile)['buildings']if b['uid']=='landsd/128971:0')
 assert building['buildingCSUID']=='3707226513T20071207'and building['objectId']==128971 and building['base']==7.403 and building['height']==3
 assert building.get('baseHeightHKPD')is None and building.get('topHeightHKPD')is None and building['baseSource']=='terrain-estimated'and building['heightSource']=='estimated'and not building.get('modelGeometry')
 catalogue_refs=[]
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;catalogue_refs.append(ref(p));assert not any(m['uid']==building['uid']for m in read(p)['models'])
 certificate=read(CAP/'ROOT-VERIFIED.json');assert certificate['jobId']=='2f502f07dd1f57aab49e3e85f4bd2a4876162d5204fa1d2d43f84c425e402536'and certificate['allEvidenceHashesVerified']and certificate['leaseReleased']
 ground_path=CAP/'complete-candidate-ground.json.gz';ground=np.asarray(read(ground_path)['completeRelevantDrawnTriplets'],dtype='<f8').reshape(-1,3,3)
 assert len(building['rings'])==1;ring=[(F(x),F(0),F(z))for x,z in building['rings'][0][:-1]]
 area=sum(a[0]*b[2]-a[2]*b[0]for a,b in zip(ring,ring[1:]+ring[:1]));assert area
 if area<0:ring.reverse()
 assert all(cross(ring[i-1],ring[i],ring[(i+1)%len(ring)])>=0 for i in range(len(ring)))
 records=[];projected=[];heights=[];zeros=[]
 for i,face in enumerate(ground):
  if face[:,0].max()<min(p[0]for p in ring)or face[:,0].min()>max(p[0]for p in ring)or face[:,2].max()<min(p[2]for p in ring)or face[:,2].min()>max(p[2]for p in ring):continue
  poly=[rational(v)for v in face]
  for a,b in zip(ring,ring[1:]+ring[:1]):poly=clip(poly,lambda p,a=a,b=b:cross(a,b,p))
  if len(poly)<3 or all(cross(poly[0],poly[k],poly[k+1])==0 for k in range(1,len(poly)-1)):
   if poly:zeros.append(dict(groundFace=i,vertices=[list(map(str,p))for p in poly]))
   continue
  records.append(dict(groundFace=i,vertices=[list(map(str,p))for p in poly]));heights.extend(p[1]for p in poly)
  for k in range(1,len(poly)-1):
   tri=[poly[0],poly[k],poly[k+1]]
   if cross(*tri):projected.append([[p[0],p[2]]for p in tri])
 partition=exact_partition(building['rings'],projected)
 low,high=min(heights),max(heights);assert high-low<F(building['height'])-F('1.8')
 result=dict(uid=building['uid'],objectId=128971,buildingCSUID=building['buildingCSUID'],previousBase=building['base'],base=float(low),height=3,baseSource='terrain-estimated',heightSource='estimated',sourceBaseHeightHKPD=None,sourceTopHeightHKPD=None,exactTerrainMin=str(low),exactTerrainMax=str(high),fullFootprintExactSingleCoverage=partition,completeClippedGroundRecords=records,boundaryDegenerateRecords=zeros,sourceBuildingBefore=building,sourceFieldsChanged=False,governmentModelGeometryChanged=False,privateProposalOnly=True,published=False,newlyInstalled=0,requires='Apply only atomically with exact Museum terrain; recapture changed BASIC constructor, ordinary neighbour and runtime/browser checks before publication.',evidenceRefs=[ref(p)for p in [manifest,tile,ground_path,CAP/'ROOT-VERIFIED.json',Path(__file__)]]+catalogue_refs)
 OUT.mkdir();(OUT/'proposal.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['uid','previousBase','base','exactTerrainMin','exactTerrainMax','fullFootprintExactSingleCoverage','privateProposalOnly']}))
if __name__=='__main__':main()
