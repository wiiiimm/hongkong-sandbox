"""Nominate actual native terrain leaves for complete current original sources.

Metadata-only source-bounds+4m domain study; no patch construction or approval.
"""
import argparse,math,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','runtime','attributes']:p.add_argument('--'+k,required=True)
 p.add_argument('--owned',action='store_true');a=p.parse_args();assert all(x.startswith('government-xl-')and '/'not in x for x in [a.batch,a.runtime,a.attributes]);pins={};refs=[Path(__file__)]
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(a.runtime,'selection.json.gz');attributes=take(a.attributes,'attributes.json.gz');assert attributes['startEndAllInputsVerified'];attrs={r['uid']:r for r in attributes['rows']};uids=[r['uid']for r in selection['rows']];local=HERE/'local'/a.batch;lease=local/'reservation.json'
 if not a.owned:
  assert not local.exists()and not(BASE/a.batch).exists();c=reservations.claim('original-native-leaf-nominations-'+str(uuid.uuid4()),['building:'+u for u in uids]+['immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert c['ok'],c
  execute_reserved(c['reservation'],lease,[sys.executable,__file__,*sys.argv[1:],'--owned']);return
 assert reservations.owns(read(lease));manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);assert digest(manifestpath.read_bytes())==selection['manifestSHA256'];refs.append(manifestpath);leaves=[]
 def visit(node,url,hierarchy,file_sha):
  if node.get('nativeMesh'):
   g=node['meta']['georef'];bounds=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(node['w']-1)*g['aE'],816500-g['bN']-(node['h']-1)*g['aN']];m=node['nativeMesh'];pos=np.asarray(m['position'],dtype='<f4').reshape(-1,3);idx=np.asarray(m['index'],dtype='<u4');lo,hi=pos.min(0),pos.max(0)
   leaves.append(dict(url=url,fileSHA256=file_sha,hierarchy=hierarchy,id=node.get('id'),coarseCells=node['coarseCells'],georef=g,w=node['w'],h=node['h'],cell=node['cell'],gridBounds=bounds,packedBounds=[[float(lo[0]),float(lo[2])],[float(hi[0]),float(hi[2])]],targetUids=node['meta'].get('targetUids',[]),triangles=len(idx)//3,renderedPositionSHA256=digest(pos.tobytes()),indexSHA256=digest(idx.tobytes()),descendantCount=len(node.get('patches',[])),exclusionCount=len(node.get('patchExclusions',[]))))
  for i,c in enumerate(node.get('patches',[])):visit(c,url,hierarchy+[i],file_sha)
 for entry in manifest['terrainPatches']:
  path=ROOT/'3d-viewer'/entry['url'];sha=digest(path.read_bytes());visit(read(path),entry['url'],[],sha);refs.append(path)
 outcomes=[]
 for row in selection['rows']:
  uid=row['uid'];attr=attrs[uid];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
  points=[decode_original_world_triangles(asset.read_bytes()).reshape(-1,3)]
  points.extend(np.asarray(attr[k],float).reshape(-1,3)for k in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']);v=np.concatenate(points);lo,hi=v.min(0),v.max(0);bounds=[float(lo[0]-4),float(lo[2]-4),float(hi[0]+4),float(hi[2]+4)];touch=[]
  for leaf in leaves:
   b=leaf['gridBounds']
   if min(bounds[2],b[2])<=max(bounds[0],b[0])or min(bounds[3],b[3])<=max(bounds[1],b[1]):continue
   g=leaf['georef'];s=leaf['cell'];assert s==g['aE']==-g['aN']and s>0
   cells=[math.floor((bounds[0]-.001+834500-g['bE'])/s),math.floor((bounds[1]-.001-816500+g['bN'])/s),math.ceil((bounds[2]+.001+834500-g['bE'])/s),math.ceil((bounds[3]+.001-816500+g['bN'])/s)]
   inside=0<cells[0]<cells[2]<leaf['w']-1 and 0<cells[1]<cells[3]<leaf['h']-1
   touch.append(dict(**leaf,nominatedLocalCells=cells,strictlyInsideLeaf=inside,existingLeafInMemoryContractEligible=inside and not leaf['descendantCount']and not leaf['exclusionCount'],manifestRootNativeLeaf=not leaf['hierarchy']))
  outcomes.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],completeFourWorldBounds=[lo.tolist(),hi.tolist()],proposedSourceBoundsPlus4m=bounds,touchingNativeLeaves=touch,wholeSourceNativeChildCandidates=[r for r in touch if r['existingLeafInMemoryContractEligible']],identityAccepted=False,physicalAcceptance=False,installationApproved=False))
 result=dict(uids=uids,rows=outcomes,currentManifestSHA256=selection['manifestSHA256'],nativeLeavesChecked=len(leaves),sourceGeometryChanges=0,terrainEdits=False,installationApproved=False,publication=False,qualification='Nominations only, for an explicit proposed source-bounds+4m edit domain using all four source representations. A nested leaf is not a manifest-native parent URL; no alias or guard bypass is authorised. Complete parent/child preservation, physical/neighbour checks and runtime integration remain mandatory.')
 save(BASE/a.batch/'summary.json',result);assert reservations.owns(read(lease))and digest(manifestpath.read_bytes())==selection['manifestSHA256'];refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('native_leaf_nomination_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-source-native-leaf-nominations',refs,result);print([dict(uid=r['uid'],touching=len(r['touchingNativeLeaves']),insideLeaf=[(v['url'],v['hierarchy'])for v in r['wholeSourceNativeChildCandidates']])for r in outcomes],flush=True)
if __name__=='__main__':main()
