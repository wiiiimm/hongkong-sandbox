"""Construct a private HKUST native-terrain proposal; preserve unchanged validator failures."""
from pathlib import Path
import uuid
import numpy as np
from shapely.geometry import box
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-hkust-private-native-candidate-v1-20261015';DOC=BASE/BATCH;OLD=BASE/'government-xl-hkust-adjoining-native-terrain-v1-20261015';ARRAYS=BASE/'government-xl-hkust309822-232155-target-provenance-draft-v1-20261014/cached-complete-original-arrays-v1'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();old=read(OLD/'result.json');pins={r['path']:r['sha256'] for r in old['evidenceRefs']};gp=OLD/'native-ground.json.gz';assert ref(gp)['sha256']==pins[str(gp.relative_to(ROOT))];ground=np.array(read(gp)['completeOriginalTerrainTriangles']);parentp=ROOT/'3d-viewer/city/data/terrain.json';mp=ROOT/'3d-viewer/city/data/manifest.json';parent=read(parentp);manifest=read(mp);constructor=module('hkust_private_constructor',HERE/'resolve-pass.py');uids=['landsd/309822:0','landsd/232155:0'];world=[];paths=[Path(__file__),gp,OLD/'result.json',parentp,mp,HERE/'resolve-pass.py']
 for uid in uids:
  p=ARRAYS/(uid.replace('/','-').replace(':','-')+'.json.gz');assert ref(p)['sha256']==pins[str(p.relative_to(ROOT))];t=np.array(read(p)['completeOrderedOriginalTriangles']);world.append([t.min((0,1)).tolist(),t.max((0,1)).tolist()]);paths.append(p)
 rects=[constructor.rectangle_for(w,parent) for w in world];cells=[min(r[0] for r in rects),min(r[1] for r in rects),max(r[2] for r in rects),max(r[3] for r in rects)];bounds=constructor.extent(cells,parent);core=[min(w[0][0] for w in world)-1,min(w[0][2] for w in world)-1,max(w[1][0] for w in world)+1,max(w[1][2] for w in world)+1];overlaps=[]
 for e in manifest['terrainPatches']:
  p=ROOT/'3d-viewer'/e['url'];d=read(p);g=d['meta']['georef'];bb=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(d['w']-1)*g['aE'],816500-g['bN']-(d['h']-1)*g['aN']]
  if box(*bounds).intersection(box(*bb)).area>0:overlaps.append({'url':e['url'],'sha256':ref(p)['sha256'],'bounds':bb});paths.append(p)
 selected=(ground[:,:,0].max(1)>=bounds[0])&(ground[:,:,0].min(1)<=bounds[2])&(ground[:,:,2].max(1)>=bounds[1])&(ground[:,:,2].min(1)<=bounds[3]);native=ground[selected];sources=[]
 for name in ['government-xl-hkust-native-terrain-foundation-v1-20261015','government-xl-hkust-adjoining-native-terrain-v1-20261015']:
  for ap in (BASE/name).glob('*acquisition.json'):
   a=read(ap);sources.append({'sheet':a['sheet'],'revision':a['revisionDate'],'sourceETag':a['sourceETag'],'directorySHA256':a['directorySHA256'],'sourceFiles':[{'name':e['name'],'sha256':e['sha256']} for e in a['entries'] if e['name'].startswith('TERRAIN')]});paths.append(ap)
 assert len(sources)==2
 claim=reservations.claim('hkust-private-'+str(uuid.uuid4()),['private-terrain-proposal:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();original=constructor.validate_patch;captured={}
  def capture_then_validate(p,parent):
   captured['patch']=p;save(DOC/'unapproved-native-patch.json',p);return original(p,parent)
  constructor.validate_patch=capture_then_validate;error=None
  try:patch=constructor.make_patch({'uids':uids,'cells':cells},parent,native,sources,native_core=core,terrain_triangle_budget=100000,parent_sha256=ref(parentp)['sha256'])
  except Exception as e:error={'type':type(e).__name__,'message':str(e)}
  finally:constructor.validate_patch=original
  assert captured,'Construction stopped before producing candidate';p=captured['patch'];save(DOC/'proposal.json',{'uids':uids,'parent':ref(parentp),'manifest':ref(mp),'bounds':bounds,'core':core,'coarseCells':cells,'selectedOriginalTerrainFaces':np.flatnonzero(selected).tolist(),'candidate':ref(DOC/'unapproved-native-patch.json'),'validatorPassed':error is None,'validatorFailure':error,'existingTerrainOverlaps':overlaps,'publication':False,'installationApproved':False,'sourceBuildingGeometryChanges':0})
  module('hkust_private_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'hkust-private-original-terrain-proposal-v1',paths,{'uids':uids,'validatorPassed':error is None,'validatorFailure':error,'existingTerrainOverlaps':overlaps,'candidateTerrainFaces':len(p['nativeMesh']['index'])//3,'nextStep':'Resolve exact validator failures, then nominate all current actors from entire parent extent/packed positions and run actual runtime/neighbour/four-world checks. Private proposal is not accepted or published.'});print({'validatorFailure':error,'overlaps':overlaps,'candidateFaces':len(p['nativeMesh']['index'])//3},flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
