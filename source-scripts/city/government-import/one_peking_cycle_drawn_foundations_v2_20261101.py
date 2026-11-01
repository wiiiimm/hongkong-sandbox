"""Complete four-world source foundation diagnostics on PRIVATE candidate members.
Uses production terrain/model constructors on the private successor. No browser, neighbour, support or publication acceptance.
"""
from pathlib import Path
import numpy as np
import subprocess
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from rectangular_native_fragments_v1_20261101 import drawn
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-one-peking-after-twin-';BATCH=P+'cycle-drawn-foundations-v2-20261101'
def main():
 out=BASE/BATCH;assert not out.exists();pins={};refs=[Path(__file__)]
 def take(batch,path):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 batch=P+'three-member-original-return-v2-20261101';summary=take(batch,BASE/batch/'summary.json');assert summary['allFiniteSeamsPassed'];ground=np.concatenate([drawn(take(batch,ROOT/m['candidate']['path']))for m in summary['members'].values()]);selection=take(P+'runtime-v1-20261101',BASE/(P+'runtime-v1-20261101')/'selection.json.gz');attrs=take(P+'attributes-v1-20261101',BASE/(P+'attributes-v1-20261101')/'attributes.json.gz');assert attrs['startEndAllInputsVerified'];results=[];final=module('one_peking_private_foundation',HERE/'xl-final-script-pass.py')
 for path,sha in attrs['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 retention=P+'cycle-preparation-v3-20261101';retained=take(retention,BASE/retention/'summary.json');assert retained['terrainValidatorPassed'];candidate=retained['candidate'];patch=take(retention,ROOT/candidate['path']);parentpath=ROOT/'3d-viewer'/retained['replacedNativeTerrain'][0]['url'];assert digest(parentpath.read_bytes())==retained['replacedNativeTerrain'][0]['sha256'];refs.append(parentpath)
 def targets(n):return set(n['meta'].get('targetUids',[]))|set().union(*(targets(c)for c in n.get('patches',[])))
 out.mkdir();candidates=out/'terrain-candidates.json';save(candidates,[dict(path=candidate['path'],sha256=candidate['sha256'],uids=summary['uids'],replaces=dict(url=retained['replacedNativeTerrain'][0]['url'],sha256=retained['replacedNativeTerrain'][0]['sha256'],retainedUids=sorted(targets(read(parentpath)))))]);sp=out/'selection.json.gz';save(sp,selection);runtimepath=HERE/'local'/BATCH/'runtime-geometry.json.gz';metrics_path=out/'metrics.json';tool=HERE/'acceptance-metrics-multi-retained.mjs'
 with(out/'worker.log').open('w')as log:subprocess.run(['node',str(tool),'--selection',str(sp.relative_to(ROOT)),'--candidates',str((HERE/'local'/(P+'runtime-v1-20261101')).relative_to(ROOT)),'--terrain-candidates',str(candidates.relative_to(ROOT)),'--out',str(metrics_path.relative_to(ROOT)),'--geometry-out',str(runtimepath.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 metrics=read(metrics_path);assert len(metrics['rows'])==2 and all(not r.get('error')for r in metrics['rows']);runtime={r['uid']:r for r in read(runtimepath)['rows']};assert set(runtime)==set(summary['uids'])
 for path,sha in metrics['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 refs.extend([tool,HERE/'terrain-replacements.mjs',runtimepath])
 for row in selection['rows']:
  uid=row['uid'];attr=next(r for r in attrs['rows']if r['uid']==uid);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==attr['sourceSHA256'];refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);worlds=dict(original=decode_original_world_triangles(asset.read_bytes()),**{mode:np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix]for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]})
  actual=runtime[uid];assert actual['sourceSHA256']==row['sourceSHA256'];assert np.array_equal(worlds['literal'],np.asarray(actual['position']).reshape(-1,3)[np.asarray(actual['index']).reshape(-1,3)]);ground=np.asarray(actual['drawnGroundGeometry']).reshape(-1,3,3)
  for mode,tri in worlds.items():
   lo,hi=tri.min((0,1)),tri.max((0,1));keep=(ground[:,:,0].max(1)>=lo[0]-10)&(ground[:,:,0].min(1)<=hi[0]+10)&(ground[:,:,2].max(1)>=lo[2]-10)&(ground[:,:,2].min(1)<=hi[2]+10);f=final.foundation_context(tri,ground[keep],Polygon(row['source']['building']['rings'][0],row['source']['building']['rings'][1:]));save(out/(uid.split('/')[1]+'--'+mode+'.json'),dict(uid=uid,mode=mode,foundation=f));r=dict(uid=uid,mode=mode,triangles=f['triangles'],covered=f['completeTerrainTriangles'],buried=f['fullyBuriedTriangles'],buriedUpward=f['fullyBuriedUpwardTriangles'],buriedAreaFraction=f['fullyBuriedAreaFraction'],minimumGapM=f['minimumGapM']);results.append(r);print(r,flush=True)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==summary['currentManifestSHA256'];refs.append(manifest);result=dict(uids=summary['uids'],currentManifestSHA256=selection['manifestSHA256'],rows=results,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,actualProductionTerrainConstructorsChecked=True,browserChecked=False)
 save(out/'summary.json',result);refs.extend([HERE/'rectangular_native_fragments_v1_20261101.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py']);module('one_peking_candidate_foundations_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-successor-actual-drawn-terrain-four-world-foundation-diagnostic',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
