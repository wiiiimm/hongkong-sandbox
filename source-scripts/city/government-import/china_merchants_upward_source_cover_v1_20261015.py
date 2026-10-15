"""Diagnostic continuous projected cover by higher original source surfaces; no approval."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-merchants-upward-source-cover-v1-20261015';DOC=BASE/BATCH
SOURCE=BASE/'government-xl-china-merchants264206-saved-face-attribution-v1-20261013/source-face-attribution.json.gz'
def plane(t):
 n=np.cross(t[1]-t[0],t[2]-t[0]);return np.array([-n[0]/n[1],-n[2]/n[1],np.dot(n,t[0])/n[1]])
def clip(points,coeff):
 out=[]
 for a,b in zip(points,points[1:]+points[:1]):
  va=coeff[0]*a[0]+coeff[1]*a[1]+coeff[2];vb=coeff[0]*b[0]+coeff[1]*b[1]+coeff[2]
  if va>=0:out.append(a)
  if (va>=0)!=(vb>=0):out.append((a+(b-a)*(va/(va-vb))))
 return out

def main():
 assert not DOC.exists();saved=read(SOURCE);t=np.asarray(saved['completeOriginalSourceFaceVerticesInOrdinalOrder']);assert t.shape==(19551,3,3)
 polys=shapely.polygons(t[:,:,[0,2]]);area=shapely.area(polys);valid=np.where(area>1e-10)[0];tree=shapely.STRtree(polys[valid]);planes={int(i):plane(t[i])for i in valid};rows=[]
 groups=saved['failureGroupsInCanonicalDelegateOrder'];ids=sorted({i for g in groups for i in g['buriedUpwardSourceFaceIndices']});assert len(ids)==102
 for i in ids:
  p=polys[i];assert area[i]>1e-10;pieces=[];cover=[];fp=planes[i]
  for j in valid[tree.query(p,predicate='intersects')]:
   j=int(j)
   if i==j:continue
   difference=planes[j]-fp;difference[2]-=.01
   clipped=clip([x.copy()for x in t[j][:,[0,2]]],difference)
   if len(clipped)<3:continue
   q=shapely.Polygon(clipped).intersection(p)
   if q.area>1e-12:pieces.append(q);cover.append(j)
  union=shapely.union_all(pieces)if pieces else shapely.GeometryCollection();uncovered=p.difference(union)
  centroid=t[i].mean(axis=0);heights=[]
  for j in cover:
   if polys[j].covers(shapely.Point(centroid[[0,2]])):heights.append(float(np.dot(planes[j],np.r_[centroid[[0,2]],1])-centroid[1]))
  rows.append({'sourceFace':i,'groups':[g['delegateOrdinal']for g in groups if i in g['buriedUpwardSourceFaceIndices']],'projectedAreaM2':float(p.area),'coveredByHigherSourceAreaM2':float(union.area),'uncoveredAreaM2':float(uncovered.area),'uncoveredWKT':uncovered.wkt,'higherSourceFaceIndices':cover,'nearestHigherCentroidGapM':min(heights)if heights else None})
 summary=[]
 for g in groups:
  selected=[r for r in rows if g['delegateOrdinal']in r['groups']];summary.append({'group':g['delegateOrdinal'],'upwardFaces':len(selected),'uncoveredAreaM2':sum(r['uncoveredAreaM2']for r in selected),'uncoveredFaces':[r['sourceFace']for r in selected if r['uncoveredAreaM2']>1e-8]})
 DOC.mkdir();save(DOC/'source-cover.json',{'sourceSHA256':saved['sourceSHA256'],'completeSourceFaces':len(t),'upwardFacesExamined':len(ids),'higherSeparationDiagnosticM':.01,'rows':rows,'groups':summary,'qualification':'Continuous projected source-over-source cover in original Float64 decoded coordinates. This is only an upward visibility diagnostic, not enclosure, side-visibility, basement identity, physical acceptance or a runtime waiver. Every original face retained.','sourceGeometryChanges':0,'installationApproved':False})
 module('china_source_cover_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'all-102-buried-upward-original-source-cover-diagnostic',[Path(__file__),SOURCE],{'uids':['landsd/264206:0'],'groups':summary,'fullAcceptance':False,'newlyInstalled':0});print(summary,flush=True)
if __name__=='__main__':main()
