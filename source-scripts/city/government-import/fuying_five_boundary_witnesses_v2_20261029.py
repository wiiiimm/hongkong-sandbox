"""Explain every rejected parent-height witness without changing a candidate."""
from pathlib import Path
import math
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
import fuying_whole_parent_five_boundary_v1_20261029 as boundary
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying181489-five-boundary-witnesses-v2-20261029';PRIOR='government-xl-fuying181489-five-member-boundary-contract-v1-20261029'
def root_sample(parent,x,z):
 pg=parent['meta']['georef'];w=parent['w'];h=parent['h'];c=(x+834500-pg['bE'])/pg['aE'];r=(816500-z-pg['bN'])/pg['aN'];i=max(0,min(w-2,math.floor(c)));j=max(0,min(h-2,math.floor(r)));u=c-i;v=r-j
 def at(k):
  rendered=parent.get('renderedElev',[]);a=rendered[k]if rendered else None
  return a if a is not None else max(1.2,parent['elev'][k])if parent['elev'][k]>0 else -4
 a=at(j*w+i);b=at(j*w+i+1);d=at((j+1)*w+i);e=at((j+1)*w+i+1)
 return a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v)
def edge_points(node):
 x,z,X,Z=boundary.legacy.bounds(node)
 return [tuple(map(float,p))for p in np.asarray(node['nativeMesh']['position'],dtype='float32').astype('float64').reshape(-1,3)if min(abs(p[0]-x),abs(p[0]-X),abs(p[2]-z),abs(p[2]-Z))<.002]
def main():
 out=BASE/BATCH;assert not out.exists();_,pins=authenticate(BASE/PRIOR);refs=[Path(__file__),HERE/'fuying_five_boundary_witnesses_v1_20261029.py',BASE/'government-xl-fuying181489-five-boundary-witnesses-v1-20261029'/'failed-run.log',HERE/'fuying_whole_parent_five_boundary_v1_20261029.py',BASE/PRIOR/'result.json']
 def take(p):assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 summary=take(BASE/PRIOR/'summary.json');proofpath=BASE/PRIOR/'whole-parent-contract.json';proof=take(proofpath);root=take(ROOT/proof['parent']['path']);old=take(ROOT/proof['oldNative']['path']);oldpoints=set(tuple(p)for p in np.asarray(old['nativeMesh']['position'],dtype='float32').astype('float64').reshape(-1,3));oldbounds=boundary.legacy.bounds(old)
 oldbad=[dict(point=p,rootY=root_sample(root,p[0],p[2]),gap=p[1]-root_sample(root,p[0],p[2]))for p in set(edge_points(old))if abs(p[1]-root_sample(root,p[0],p[2]))>=.01]
 rows=[]
 for item in summary['members']:
  node=take(ROOT/item['candidate']['path']);callback=boundary.coordinated_boundary(node,root);points=set(edge_points(node));bad=[];allowed=0
  for p in points:
   if callback(*p):allowed+=1;continue
   expected=root_sample(root,p[0],p[2]);gap=p[1]-expected
   if abs(gap)>=.01:
    x,z,X,Z=oldbounds;outer=min(abs(p[0]-x),abs(p[0]-X),abs(p[2]-z),abs(p[2]-Z))<.002
    bad.append(dict(point=p,rootY=expected,gap=gap,onWholeOldOuterBoundary=outer,exactOldParentVertex=p in oldpoints))
  save(out/(item['member']+'-witnesses.json'),dict(witnesses=bad));rows.append(dict(member=item['member'],uniqueBoundaryVertices=len(points),finiteMateAccepted=allowed,rejectedRootWitnesses=len(bad),oldOuterBoundaryWitnesses=sum(q['onWholeOldOuterBoundary']for q in bad),exactOldParentVertices=sum(q['exactOldParentVertex']for q in bad),maximumGapM=max([abs(q['gap'])for q in bad],default=0)));print(rows[-1],flush=True)
 result=dict(uids=summary['uids'],sourceSHA256ByUid=summary['sourceSHA256ByUid'],members=rows,oldParentRootBoundaryFailures=oldbad,oldParentRootBoundaryFailureCount=len(oldbad),sourceGeometryChanges=0,sourcePoseChanges=0,candidateChanges=False,terrainValidatorPassed=False,physicalAcceptance=False,publication=False,installationApproved=False)
 save(out/'summary.json',result);module('fuying_boundary_witness_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'read-only-complete-rejected-boundary-witness-account',refs,result)
if __name__=='__main__':main()
