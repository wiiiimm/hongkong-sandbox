"""Private expanded terrain proposal, not a complete current-neighbour nomination."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-expanded-raw-terrain-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-plaza-ascot-actual-render-attributes-v4-20261020';NEW=BASE/'government-xl-plaza-ascot-three-neighbour-render-attributes-v2-20261020';GROUND=BASE/'government-xl-plaza-ascot-domain-ground-v1-20261020'
UIDS=['landsd/258411:0','landsd/228446:0','landsd/164322:0']
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,NEW,GROUND]:
   receipt=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
   refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
 def take(folder,p):
  assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 points=[];source_hashes={}
 for folder in [CAP,NEW]:
  inputs=take(folder,folder/'input.json.gz');capture=take(folder,folder/'attributes.json.gz')
  for r in capture['rows']:
   if r['uid'] not in UIDS:continue
   entry=next(v['entry'] for v in inputs['rows'] if v['uid']==r['uid']);source_hashes[r['uid']]=entry['sha256']
   for key in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
    points.append(np.asarray(r[key]).reshape(-1,3))
   points.append(np.asarray(entry['worldBounds']))
 assert set(source_hashes)==set(UIDS)
 xyz=np.concatenate(points);bounds=[xyz.min(0).tolist(),xyz.max(0).tolist()]
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);refs.append(parentpath)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';manifestsha=digest(manifest.read_bytes());refs.append(manifest)
 builder=module('ascot_expanded_builder',HERE/'resolve-pass-indexed-parent-clipping.py');refs.append(HERE/'resolve-pass-indexed-parent-clipping.py')
 cells=builder.rectangle_for(bounds,parent);domain=builder.extent(cells,parent)
 save(DOC/'scope.json',dict(uids=UIDS,sourceHashes=source_hashes,completeCandidateRenderBounds=bounds,baseReplacementCells=cells,baseReplacementExtent=domain,allCurrentActorsNominated=False,installationApproved=False,qualification='Candidate terrain construction scope only; fresh complete current actor nomination is required before any installation.'))
 sourcepath=HERE/'local'/GROUND.name/'258411:0-ground.json.gz';data=take(GROUND,sourcepath);ground=np.asarray(data['completeAdjoiningTerrain'])
 keep=(ground[:,:,0].max(1)>=domain[0])&(ground[:,:,0].min(1)<=domain[2])&(ground[:,:,2].max(1)>=domain[1])&(ground[:,:,2].min(1)<=domain[3]);native=ground[keep]
 captured=[];validate=builder.validate_patch
 def capture(p,parent):captured.append(p);return validate(p,parent)
 builder.validate_patch=capture
 source=dict(provider='Lands Department / HKSAR',crs='EPSG:2326',verticalDatum='HKPD',sourceFiles=[dict(path=str(sourcepath.relative_to(ROOT)),sha256=digest(sourcepath.read_bytes()))],sheets=data['sheets'])
 error=None
 try:patch=builder.make_patch(dict(uids=UIDS,cells=cells),parent,native,[source])
 except AssertionError as ex:
  assert str(ex)=='Native terrain contains overlapping height surfaces';assert len(captured)==1;patch=captured[0];error=str(ex)
 out=LOCAL/'unvalidated-terrain.json';save(out,patch);refs.append(out);assert digest(manifest.read_bytes())==manifestsha
 result=dict(uids=UIDS,baseReplacementExtent=domain,faces=len(patch['nativeMesh']['index'])//3,validationFailure=error,installationApproved=False,productionTerrainChanges=0,allCurrentActorsNominated=False)
 save(DOC/'summary.json',result)
 module('ascot_expanded_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-expanded-three-original-terrain-construction',refs,result)
 print(result,flush=True)
if __name__=='__main__':main()
