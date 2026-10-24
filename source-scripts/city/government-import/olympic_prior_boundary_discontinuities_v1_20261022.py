"""Measure exact prior native boundary jumps without changing the rejected guard."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from southside_selective13_certified_width_parent_restoration_draft_v2_20261013 import whole_edge_max_envelope
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympic-prior-boundary-discontinuities-v1-20261022'
def clean(v):
 if isinstance(v,F):return str(v)
 if isinstance(v,dict):return {str(k):clean(x)for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [clean(x)for x in v]
 if isinstance(v,np.generic):return v.item()
 return v
def main():
 doc=BASE/BATCH;assert not doc.exists();prior=BASE/'government-xl-olympic-narrow-retained-candidate-v1-20261022';r,pins=authenticate(prior);p=ROOT/'3d-viewer'/r['candidate']['replaces']['url'];assert digest(p.read_bytes())==r['candidate']['replaces']['sha256'];d=read(p);v=np.asarray(d['nativeMesh']['position'],dtype='<f4').astype('<f8').reshape(-1,3);faces=v[np.asarray(d['nativeMesh']['index']).reshape(-1,3)];box=read(prior/'input.json')['cut'];x,z,X,Z=map(F,box);corners=[(x,z),(X,z),(X,Z),(x,Z)];out=[]
 for side in range(4):
  a,b=corners[side],corners[(side+1)%4];lo=np.minimum(a,b).astype(float);hi=np.maximum(a,b).astype(float);q=faces[:,:,[0,2]];ids=np.flatnonzero((q.max(1)>=lo).all(1)&(q.min(1)<=hi).all(1));selected=[(int(i),faces[i])for i in ids];report=whole_edge_max_envelope((a[0],0,a[1]),(b[0],0,b[1]),selected);assert report['allClosedEdgeCovered'];planes={r['facet']:r for r in report['completeProjectedFiniteFacetIntervals']};points={r['parameter']:r for r in report['allOriginalClosedEndpointAndPlaneCrossoverKnots']};jumps=[]
  for interval in report['allCompleteOpenIntervalMaximumBranches']:
   owner=interval['interiorWitness']['completeHighestFacetTies'][0];plane=planes[owner]
   for t in interval['closedInterval']:
    limit=plane['height0']+plane['slope']*t;gap=points[t]['exactHighestHeightM']-limit
    if gap>0:jumps.append(dict(parameter=t,endpointUpperExcessM=gap,openIntervalOwner=owner,closedEndpointOwners=points[t]['completeHighestFacetTies']))
  row=dict(side=side,closedCandidateFaces=len(ids),positiveEndpointJumps=jumps,maximumEndpointExcessM=max([r['endpointUpperExcessM']for r in jumps],default=F(0)));out.append(row);save(doc/f'side-{side}.json.gz',clean(report));print(clean(row),flush=True)
 result=dict(uids=['landsd/81242:0'],rows=clean(out),installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0,qualification='Existing packed native upper-boundary discontinuities; no guard relaxation, geometry change or source acceptance.')
 save(doc/'summary.json',result);refs=[Path(__file__),prior/'result.json',prior/'input.json',p,HERE/'southside_selective13_certified_width_parent_restoration_draft_v2_20261013.py'];module('prior_boundary_jump_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-prior-native-boundary-discontinuity-diagnostic',refs,result)
if __name__=='__main__':main()
