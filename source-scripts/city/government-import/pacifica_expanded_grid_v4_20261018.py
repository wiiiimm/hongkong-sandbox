"""Reuse completed private facets; preserve the installed one-metre fallback grid."""
from pathlib import Path
import copy,subprocess,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-pacifica-expanded-grid-v4-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=BASE/'government-xl-pacifica-expanded-parent-v1-20261018';UID='landsd/283036:0'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 refs=[Path(__file__),PRIOR/'result.json'];pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 original=HERE/'local'/PRIOR.name/'terrain-pacifica-mall.json';patch=read(original);native_before=copy.deepcopy(patch['nativeMesh']);retained_path=ROOT/'3d-viewer/city/data/terrain-residual-265478-0.json';retained=read(retained_path)
 builder=module('pacifica_grid_builder',HERE/'resolve-pass-indexed-parent-clipping.py');parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);g=patch['meta']['georef'];og=retained['meta']['georef'];bounds=builder.extent(patch['coarseCells'],parent)
 assert g['aE']==5 and g['aN']==-5 and og['aE']==1 and og['aN']==-1
 w=round(bounds[2]-bounds[0])+1;h=round(bounds[3]-bounds[1])+1;newgrids={}
 # DemSampler follows the existing two-triangle grid interpolation, avoiding bilinear resampling.
 for key,rendered in [('elev',False),('renderedElev',True)]:
  sampler=builder.terrain.fine.DemSampler(patch,rendered=rendered)
  grid=np.asarray([[sampler.ground(bounds[0]+x,bounds[1]+z)for x in range(w)]for z in range(h)])
  xoff=og['bE']-(bounds[0]+834500);zoff=(816500-og['bN'])-bounds[1];assert xoff==int(xoff)and zoff==int(zoff);xoff,zoff=int(xoff),int(zoff)
  old=np.asarray(retained.get(key,retained['elev'])).reshape(retained['h'],retained['w']);grid[zoff:zoff+retained['h'],xoff:xoff+retained['w']]=old
  assert np.array_equal(grid[zoff:zoff+retained['h'],xoff:xoff+retained['w']],old);newgrids[key]=grid.reshape(-1).tolist()
 # Match the producer's nearest parent vegetation sampling, then preserve every installed node.
 pg=parent['meta']['georef'];vegetation=[]
 for z in range(h):
  for x in range(w):
   c=min(parent['w']-1,max(0,round((bounds[0]+x+834500-pg['bE'])/pg['aE'])))
   r=min(parent['h']-1,max(0,round((bounds[1]+z-816500+pg['bN'])/pg['aE'])))
   vegetation.append(parent['vegetation'][r*parent['w']+c])
 vegetation=np.asarray(vegetation).reshape(h,w);oldvegetation=np.asarray(retained['vegetation']).reshape(retained['h'],retained['w'])
 vegetation[zoff:zoff+retained['h'],xoff:xoff+retained['w']]=oldvegetation
 assert np.array_equal(vegetation[zoff:zoff+retained['h'],xoff:xoff+retained['w']],oldvegetation)
 newgrids['vegetation']=vegetation.reshape(-1).tolist()
 patch.update(w=w,h=h,cell=1,**newgrids);patch['meta']['georef'].update(aE=1,aN=-1,W=w,H=h)
 assert patch['nativeMesh']==native_before
 # V1 saved its mesh before adding the independently measured overlap evidence.
 # Recompute and bind that evidence to this final grid payload, without editing facets.
 repair=module('pacifica_grid_resolution',HERE/'native_patch_resolution.py')
 prior_audit=PRIOR/'native-overlap.json';files=read(prior_audit)['source']['files'];refs.append(prior_audit)
 for item in files:
  q=ROOT/item['path'];assert digest(q.read_bytes())==item['sha256'];refs.append(q)
 path=LOCAL/'terrain-pacifica-mall.json';save(path,patch)
 repair.approve_original_overlap(patch,path,DOC/'native-overlap.json',files)
 repair.finalize_overlap_evidence(patch,DOC/'native-overlap.json')
 refs.append(HERE/'native_patch_resolution.py')
 builder.validate_patch(patch,parent)
 path=LOCAL/'terrain-pacifica-mall.json';save(path,patch)
 scope=read(BASE/'government-xl-pacifica-current-scope-v1-20261018/scope.json');row=read(BASE/'government-xl-pacifica-current-scope-v1-20261018/selection.json.gz')['rows'][0]
 save(DOC/'grid-preservation.json',dict(previousFailedProducer=str(original.relative_to(ROOT)),nativeFacetsByteEquivalent=True,retainedVegetationExact=True,retainedRawGridExact=True,retainedRenderedGridExact=True,newGrid=[w,h],offset=[xoff,zoff],sourceGeometryChanges=0,installationApproved=False))
 candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uids=[UID],coarseCells=patch['coarseCells'],replaces=dict(url=scope['retainedTerrain']['url'],sha256=scope['retainedTerrain']['sha256'],retainedUids=scope['retainedTerrain']['parentNativeUids']))
 save(DOC/'terrain-candidates.json',[candidate]);asset=LOCAL/row['candidate']['entry']['asset'];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(raw);row['candidate']['path']=str(asset.relative_to(ROOT));save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())))
 cmd=['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
 with(DOC/'metrics.log').open('w')as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 metrics=read(DOC/'metrics.json');assert len(metrics['rows'])==1 and not metrics['rows'][0].get('error')
 for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([original,retained_path,parentpath,HERE/'resolve-pass-indexed-parent-clipping.py']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file())
 module('pacifica_grid_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'expanded-original-terrain-existing-grid-preserved',list(dict.fromkeys(refs)),dict(uids=[UID,'landsd/283034:0','landsd/265478:0'],terrainValidationPassed=True,installationApproved=False))
 print(metrics['rows'][0],flush=True)
if __name__=='__main__':main()
