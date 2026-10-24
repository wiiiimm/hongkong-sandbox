"""Private Folkland terrain constructor probe; retain failures, never publish."""
from pathlib import Path
import uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from rendered_patch_sampler import RenderedPatchSampler
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-folkland-native-parent-candidate-v1-20261020';DOC=BASE/BATCH
SCOPE=BASE/'government-xl-folkland-current-scope-v1-20261020'
GROUND=BASE/'government-xl-next-twenty-original-ground-v3-20261020'
def main():
 assert not DOC.exists()
 refs=[Path(__file__)];pins={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [SCOPE,GROUND]:
   receipt=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
   pins[folder.name]={e['path']:e['sha256'] for e in receipt['evidenceRefs']};refs.append(folder/'result.json')
 def consume(folder,path):
  assert digest(path.read_bytes())==pins[folder.name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 scope=consume(SCOPE,SCOPE/'scope.json');row=next(r for r in scope['rows'] if r['uid']=='landsd/225387:0')
 parentinfo=next(p for p in row['overlappingInstalledTerrain'] if p['url']=='city/data/terrain/unnamed147996-private-v1.json')
 parentpath=ROOT/'3d-viewer'/parentinfo['url'];parent=consume(SCOPE,parentpath);assert not parent.get('patches')
 sourcepath=HERE/'local'/GROUND.name/'264677:0-ground.json.gz';source=consume(GROUND,sourcepath)
 native=np.asarray(source['completeOriginalTerrain'])
 builder=module('folkland_private_builder',HERE/'resolve-pass-indexed-parent-clipping.py')
 # A contained replacement region avoids touching the adjoining native parent.
 # This is a construction proposal, with all acceptance checks still required.
 cells=list(parentinfo['nestedReplacementCells']);cells[1]=0;bb=builder.extent(cells,parent)
 assert bb==[372.5,-4027.5,462.5,-3937.5]
 selected=(native[:,:,0].max(1)>=bb[0])&(native[:,:,0].min(1)<=bb[2])&(native[:,:,2].max(1)>=bb[1])&(native[:,:,2].min(1)<=bb[3]);native=native[selected]
 oldsampler=builder.terrain.fine.DemSampler
 def actual_sampler(data,rendered=False):
  grid=oldsampler(data,rendered=rendered)
  return RenderedPatchSampler(data,grid,grid) if rendered and data.get('nativeMesh') else grid
 capture={};validate=builder.validate_patch
 def capture_validate(p,base):
  capture['patch']=p;save(DOC/'unapproved-local-surface.json',p);return validate(p,base)
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/264677:0','building:landsd/225387:0','private-terrain-proposal:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();builder.terrain.fine.DemSampler=actual_sampler;builder.validate_patch=capture_validate
  error=None
  try:
   builder.make_patch(dict(uids=['landsd/264677:0','landsd/225387:0'],cells=cells),parent,native,[dict(evidencePath=str(sourcepath.relative_to(ROOT)),sha256=digest(sourcepath.read_bytes()))],parent_url=parentinfo['url'],parent_sha256=parentinfo['sha256'],allow_native_below_clamp=bool((native[:,:,1]<1.2).any()))
  except Exception as e:error=dict(type=type(e).__name__,message=str(e))
  finally:builder.terrain.fine.DemSampler=oldsampler;builder.validate_patch=validate
  summary=dict(uids=['landsd/264677:0','landsd/225387:0'],replacementBounds=bb,selectedSourceFaces=int(selected.sum()),candidateReachedValidator=bool(capture),validatorFailure=error,installationApproved=False,liveChanges=False,sourceBuildingGeometryChanges=0,parentNativeUids=parentinfo['parentNativeUids'],nextStep='Flatten the local proposal into a complete replacement parent, preserve outside facets, then verify full packed domain, neighbour and runtime acceptance. Do not nest or publish this local surface.')
  if capture:summary['candidateFaces']=len(capture['patch']['nativeMesh']['index'])//3
  assert reservations.owns(lease)
  for p in refs:
   if p==parentpath:assert digest(p.read_bytes())==parentinfo['sha256']
  refs.extend([HERE/'rendered_patch_sampler.py',HERE/'native_patch_resolution.py',HERE/'resolve-pass-indexed-parent-clipping.py'])
  save(DOC/'summary.json',summary)
  module('folkland_candidate_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-native-parent-local-construction',refs,summary)
  print(summary,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
