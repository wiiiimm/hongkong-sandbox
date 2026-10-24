"""Exact parent/retained-child comparison; no legacy-support reclassification."""
from pathlib import Path
from copy import deepcopy
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ifc-mall-retained-parent-equivalence-v1-20261019';DOC=BASE/BATCH
SCOPE=BASE/'government-xl-next-two-current-scope-v1-20261019';CAP=BASE/'government-xl-ifc-mall-private-ground-v2-20261019'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [SCOPE,CAP]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 plan=read(CAP/'terrain-candidates.json')[0];oldpath=ROOT/'3d-viewer'/plan['replaces']['url'];newpath=ROOT/plan['path'];assert digest(oldpath.read_bytes())==plan['replaces']['sha256'];assert digest(newpath.read_bytes())==plan['sha256'];old,new=read(oldpath),read(newpath)
 assert {k:v for k,v in old.items()if k!='patches'}=={k:v for k,v in new.items()if k!='patches'}
 assert len(new['patches'])==len(old['patches'])+1;aliases=[]
 for a,b in zip(old['patches'],new['patches']):
  normalized=deepcopy(b)
  if a!=b:
   x=a['nativeMesh']['sourceOverlap'];y=b['nativeMesh']['sourceOverlap'];assert {k:v for k,v in x.items()if k!='evidencePath'}=={k:v for k,v in y.items()if k!='evidencePath'}
   for p in [ROOT/x['evidencePath'],ROOT/y['evidencePath']]:assert digest(p.read_bytes())==x['evidenceSHA256'];refs.append(p)
   normalized['nativeMesh']['sourceOverlap']['evidencePath']=x['evidencePath'];aliases.append(dict(childId=a['id'],before=x['evidencePath'],after=y['evidencePath'],sha256=x['evidenceSHA256']))
  assert a==normalized,a.get('id')
 child=new['patches'][-1];g=child['meta']['georef'];domain=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(child['w']-1)*g['aE'],816500-g['bN']-(child['h']-1)*g['aN']]
 scope=next(r for r in read(SCOPE/'scope.json')['rows']if r['uid']=='landsd/64856:0')['overlappingInstalledTerrain'][0];assert domain==scope['nestedReplacementExtent'];pos=np.asarray(child['nativeMesh']['position']).reshape(-1,3)
 # Native positions are in viewer world coordinates for this packed child.
 assert pos[:,0].min()>=domain[0]-1e-6 and pos[:,0].max()<=domain[2]+1e-6
 assert pos[:,2].min()>=domain[1]-1e-6 and pos[:,2].max()<=domain[3]+1e-6
 actors=read(SCOPE/'complete-bounds.json.gz')['rows'];assert len(actors)==6752
 retained=set(scope['parentNativeUids']);unchanged=[a['uid']for a in actors if a['uid']in retained and closed_disjoint(a['completeFourWorldBounds'],domain)];affected=sorted(retained-set(unchanged));assert affected==sorted(scope['touchingNativeUids'])
 assert len(unchanged)==1189 and len(affected)==15
 summary=dict(uids=['landsd/64856:0'],unchangedParentExceptAddedChild=True,retainedChildren=len(old['patches']),allRetainedChildrenIdenticalExceptByteIdenticalEvidenceAliases=True,evidenceAliases=aliases,changedChildExtent=domain,allCurrentSourceBoundsDisjoint=False,currentNativeActors=len(actors),unchangedNativeUids=sorted(unchanged),requiresFullNativeChecks=affected,parentNativeUids=sorted(retained),installationApproved=False,qualification='Structural equivalence of regional parent and existing children plus complete four-world source-domain disjointness for explicitly listed 1189 actors only. All 15 intersecting actors retain full physical checks. No legacy support reclassification. Root patch ordering/render routing and final runtime/browser/publication acceptance remain separate.')
 save(DOC/'equivalence.json',summary);refs.extend([oldpath,newpath,CAP/'terrain-candidates.json',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py',ROOT/'3d-viewer/city/geo.js',ROOT/'3d-viewer/city/terrain-patch-index.js'])
 module('ocean_parent_equivalence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'ifc-mall-exact-retained-parent-structure',list(dict.fromkeys(refs)),summary);print(summary,flush=True)
if __name__=='__main__':main()
