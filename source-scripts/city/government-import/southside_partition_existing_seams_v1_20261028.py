"""Test private partition edges against unchanged finite-pair seam checks; no guard changes."""
import argparse,copy,sys,uuid
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
sys.path.insert(0,str(HERE.parent/'island-detail-integration'))
import coordinated_native_boundary as legacy
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-southside-partition-existing-seams-v1-20261028';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';PART='government-xl-southside-six-strip-partition-diagnostic-v1-20261028';PRIOR='government-xl-southside-unchanged-highest-surface-proof-v1-20261028';UID='landsd/315025:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__),Path(legacy.__file__),HERE/'coordinated_native_boundary_v1_20261023.py',HERE/'finite_native_boundary_strip_v1_20261023.py'];pins={}
 for name in [PART,PRIOR]:
  _,bound=authenticate(BASE/name);pins.update(bound);refs.append(BASE/name/'result.json')
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 part=take(BASE/PART/'summary.json');assert part['allNodeBudgetsPassed']and not part['missingParentFaces']and not part['heightDriftViolations'];master=take(BASE/PRIOR/'height-contract-only-terrain.json.gz');rootpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(rootpath);refs.append(rootpath);members={};nodes={}
 for entry in part['strips']:
  strip=take(ROOT/entry['asset']['path']);j=entry['strip'];node=copy.deepcopy(master);node['id']=BATCH+'-'+str(j);node['nativeMesh'].pop('sourceOverlap',None);node['nativeMesh']['position']=strip['position'];node['nativeMesh']['index']=strip['index'];node['coarseCells']=strip['coarseCells'];node['w']=15
  for key in ['elev','renderedElev','vegetation']:
   node[key]=[master[key][r*master['w']+c]for r in range(master['h'])for c in range(j*14,j*14+15)]
  node['meta']['georef']['bE']=834500+strip['bounds'][0];node['meta']['georef']['W']=15;assert legacy.bounds(node)==tuple(strip['bounds']);p=LOCAL/('strip-'+str(j)+'-unbound.json');save(p,node);refs.append(p);members[str(j)]=dict(before=ref(p),candidate=ref(p),canonicalSHA256=legacy.canonical_sha(node));nodes[str(j)]=node
 results=[]
 for j in range(5):
  names=[str(j),str(j+1)];bounds=[legacy.bounds(nodes[n])for n in names];x=bounds[0][2];z0,z1=bounds[0][1],bounds[0][3];edit=shapely.box(x-1,z0+1,x+1,z1-1);p=DOC/('pair-'+str(j)+'.json');save(p,dict(policy=legacy.POLICY,parent=ref(rootpath),members={n:members[n]for n in names},editRegionWKT=edit.wkt));refs.append(p);row=dict(pair=names,sourceGeometryChanges=0,sides=[])
  for name in names:
   temporary=copy.deepcopy(nodes[name]);temporary['nativeMesh']['source']['coordinatedBoundary']=dict(policy=legacy.POLICY,proof=ref(p),member=name)
   try:callback=legacy.coordinated_boundary(temporary,parent)
   except Exception as error:row['sides'].append(dict(member=name,finitePairConstructionPassed=False,errorType=type(error).__name__,reason=str(error)));continue
   tri=legacy.triangles(nodes[name]);points=np.unique(tri.reshape(-1,3),axis=0);points=points[(abs(points[:,0]-x)<.002)&(points[:,2]>=z0+1)&(points[:,2]<=z1-1)];allowed=0;ordinary=0;failures=[]
   for point in points:
    try:
     if callback(*map(float,point)):allowed+=1
     else:ordinary+=1
    except Exception as error:failures.append(dict(position=point.tolist(),errorType=type(error).__name__,reason=str(error)))
   row['sides'].append(dict(member=name,finitePairConstructionPassed=True,nominatedVertices=len(points),finiteMateAccepted=allowed,ordinaryBoundaryRemaining=ordinary,failedVertices=len(failures),failures=failures))
  results.append(row)
 result=dict(uids=[UID],pairs=results,sourceGeometryChanges=0,productionGuardChanges=False,terrainValidatorPassed=False,installationApproved=False,physicalAccepted=False,identityAccepted=False,qualification='Diagnostic only. Existing finite-pair kernel unchanged; every shared-edge band vertex nominated. before/candidate references are the same new private unbound proposal, not historical installed terrain or acceptance. Nodes have no inherited overlap approval. All source/height/coverage/shared-boundary/current-neighbour and publication gates remain required.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);module('southside_existing_partition_seams_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-finite-pair-kernel-on-private-partition-seams',refs,result);print([(r['pair'],[(s['member'],s['finitePairConstructionPassed'],s.get('failedVertices'))for s in r['sides']])for r in results],flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('southside-existing-partition-seams-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()
