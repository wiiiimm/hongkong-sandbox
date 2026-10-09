"""Attribute every original runtime sample; ordinary limits/anchors stay strict.

No new tolerance. Requires independently replayed drawn-ground gaps and a verified
whole-source exterior wall role; it does not grant installation credit.
"""
import math,numpy as np

def original_samples(position,index,bottom):
 p=np.asarray(position,float).reshape(-1,3);idx=np.asarray(index).reshape(-1,3)
 assert np.isfinite(p).all() and np.isfinite(bottom) and np.issubdtype(idx.dtype,np.integer)
 assert (idx>=0).all() and (idx<len(p)).all()
 incidence={i:[] for i in range(len(p))}
 for i,face in enumerate(idx):
  for v in set(face):incidence[int(v)].append(i)
 records=[]
 for i,point in enumerate(p):records.append({'point':point.tolist(),'kind':'vertex','originalIncidentFaces':incidence[i],'vertex':i})
 for i,ids in enumerate(idx):
  v=p[ids];centre=[]
  for k in range(3):
   total=0.0
   for x in v:total+=float(x[k])
   centre.append(total/3)
  records.append({'point':centre,'kind':'centre','originalIncidentFaces':[i],'vertex':None})
  for e in range(3):
   a,b=v[e],v[(e+1)%3]
   if max(a[1],b[1])>bottom+.35:continue
   n=math.ceil(math.hypot(float(a[0]-b[0]),float(a[2]-b[2])))
   for j in range(1,n):records.append({'point':[float(a[k])+float(b[k]-a[k])*j/n for k in range(3)],'kind':'lowEdge','originalIncidentFaces':[i],'vertex':None})
 return records

def verify(position,index,bottom,all_samples,*,wall_faces,verified_wall_role,expected_metric):
 assert verified_wall_role is True and wall_faces and len(set(wall_faces))==len(wall_faces)
 expected=original_samples(position,index,bottom);assert len(all_samples)==len(expected)==expected_metric['checks'],'Incomplete original sample inventory'
 walls=set(wall_faces);assert all(type(f)is int and 0<=f<len(np.asarray(index).reshape(-1,3)) for f in walls)
 low=[];ordinary=[];failed=[];clearance=[]
 for actual,source in zip(all_samples,expected):
  assert all(actual[k]==v for k,v in source.items()),'Misattributed original sample'
  assert source['originalIncidentFaces'],'Unreferenced original vertex'
  assert np.isfinite([actual['ground'],actual['gap']]).all() and actual['gap']==actual['point'][1]-actual['ground'],'Missing or changed drawn ground'
  exclusively_wall=all(f in walls for f in source['originalIncidentFaces'])
  if actual['gap']<-.5:
   clearance.append(actual);assert exclusively_wall,'Ordinary original clearance failure'
  if actual['point'][1]<=bottom+.35:
   low.append(actual)
   if not exclusively_wall:
    ordinary.append(actual);assert -.5<=actual['gap']<=1,'Ordinary original rim failure'
   if actual['gap']<-.5 or actual['gap']>1:
    failed.append(actual);assert exclusively_wall and actual['gap']<-.5,'Unclassified original rim failure'
 assert low and ordinary and len(low)==expected_metric['lowRimChecks']
 assert min(r['gap'] for r in all_samples)==expected_metric['minSurfaceGap'] and min(r['gap'] for r in low)==expected_metric['minLowGap'] and max(r['gap'] for r in low)==expected_metric['maxLowGap']
 anchors=[r for r in ordinary if -.1<=r['gap']<=.1];assert anchors,'Missing genuine strict original anchor'
 assert min(r['gap'] for r in ordinary)<=.1 and max(r['gap'] for r in low)<=1
 return {'contract':'unchanged-original-wall-rim-accounting-v1','verified':True,'wholeOriginalRuntimeSamples':len(all_samples),'originalLowRimSamples':len(low),'ordinaryRimSamples':len(ordinary),'strictOrdinaryAnchorSamples':len(anchors),'ordinaryMinimumGapM':min(r['gap'] for r in ordinary),'ordinaryMaximumGapM':max(r['gap'] for r in ordinary),'rawWallRimFailuresRetained':len(failed),'rawWallClearanceFailuresRetained':len(clearance),'creditedWallFaces':sorted(walls),'ordinaryClearanceMinimumLimitM':-.5,'contactMinimumUpperLimitM':.1,'rimMaximumLimitM':1,'strictAnchorBandM':[-.1,.1],'installationApproved':False}
