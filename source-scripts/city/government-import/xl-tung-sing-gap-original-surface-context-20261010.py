"""Exact witness original parent/TIN heights and unchanged neighbouring facets."""
from fractions import Fraction
from pathlib import Path
import numpy as np,shapely
from run import ROOT,read,save,digest
from native_parent_child_flat_composition_20261010 import faces
from exact_original_projection_coverage_20261009 import point,cross,signed_area
BATCH='government-xl-tung-sing-gap-original-surface-context-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
GAP=DOC.parent/'government-xl-tung-sing-exact-gap-source-facets-20261010/diagnostic.json.gz';CAND=DOC.parent/'government-xl-tung-sing-actual-parent-interior-composition-v3-20261010/candidate-single-native-original-surface.json';TIN=DOC.parent/'government-xl-tung-sing-original-pair-source-tin-context-20261010/complete-original-source-tin.json.gz';PARENT=ROOT/'3d-viewer/city/data/government-native-163705-0.json'
def exact_height(t,q):
 p=[point(v) for v in t[:,[0,2]]];area=signed_area(p)
 if area==0:return None
 sign=1 if area>0 else -1
 if not all(sign*cross(a,b,q)>=0 for a,b in zip(p,p[1:]+p[:1])):return None
 y=[Fraction(float(v)) for v in t[:,1]];return y[0]+(y[1]-y[0])*cross(p[0],q,p[2])/cross(p[0],p[1],p[2])+(y[2]-y[0])*cross(p[0],p[1],q)/cross(p[0],p[1],p[2])
assert not DOC.exists();q=[Fraction(v) for v in next(r['proof']['exactUncoveredInteriorWitnessXZ'] for r in read(GAP)['rows'] if r['originalFace']==423)];source=np.asarray(next(r['originalTriangle'] for r in read(GAP)['rows'] if r['originalFace']==423));x,z=map(float,q);tin=read(TIN);tf=np.asarray(tin['position'],float).reshape(-1,3)[np.asarray(tin['index']).reshape(-1,3)];records=[]
for label,g in [('parent',faces(read(PARENT))),('sourceTIN',tf),('candidate',faces(read(CAND)))]:
 lo=g[:,:,[0,2]].min(1);hi=g[:,:,[0,2]].max(1);ids=np.flatnonzero((lo[:,0]<=x+.001)&(hi[:,0]>=x-.001)&(lo[:,1]<=z+.001)&(hi[:,1]>=z-.001));hit=[]
 for i in ids:
  y=exact_height(g[i],q);hit.append({'originalFace':int(i),'vertices':g[i].tolist(),'coversExactWitness':y is not None,'exactWitnessY':None if y is None else str(y),'floatWitnessY':None if y is None else float(y)})
 records.append({'surface':label,'completeFacets':len(g),'allNearbyOriginalFacets':hit,'exactCoveringFacets':sum(r['coversExactWitness'] for r in hit)})
save(DOC/'diagnostic.json.gz',{'exactWitnessXZ':[str(v) for v in q],'runtimeFloat32WitnessXZ':np.asarray([x,z],np.float32).astype(float).tolist(),'floatWitnessXZ':[x,z],'originalPodiumFace423':source.tolist(),'originalPodiumWitnessY':str(exact_height(source,q)),'completeSurfaceRows':records,'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [GAP,CAND,TIN,PARENT,Path(__file__)]},'physicalAccepted':False,'modelGeometryChanges':0});print([(r['surface'],[(x['originalFace'],x['floatWitnessY']) for x in r['allNearbyOriginalFacets'] if x['coversExactWitness']]) for r in records],flush=True)
