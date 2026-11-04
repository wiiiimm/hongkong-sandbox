"""Private shared original terrain for both museums; no live replacement or acceptance."""
from pathlib import Path
import copy,shutil,subprocess,uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-science-history-combined-private-terrain-v1-20261016';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=BASE/'government-xl-science-museum-original-terrain-v2-20261016';INSTALLED=BASE/'government-xl-history-museum-original-installed-v1-20261016'
def main():
 assert not DOC.exists() and not LOCAL.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PRIOR,INSTALLED]:
   p=folder/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for q in r['evidenceRefs']:
    assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);manifestsha=digest(manifestpath.read_bytes());science=read(BASE/'government-xl-science-museum-current-ground-v1-20261016/selection.json.gz')['rows'][0];history=copy.deepcopy(read(BASE/'government-xl-history-museum-current-ground-v1-20261016/selection.json.gz')['rows'][0])
 caturl=next(u for u in manifest['officialModelCatalogues'] if any(e['uid']=='landsd/4759:0' for e in read(ROOT/'3d-viewer'/u)['models']));catpath=ROOT/'3d-viewer'/caturl;entry=next(e for e in read(catpath)['models'] if e['uid']=='landsd/4759:0');history['candidate']=dict(entry=entry,path=str((catpath.parent/entry['asset']).relative_to(ROOT)))
 rows=[science,history]
 for row in rows:
  p=ROOT/'3d-viewer'/row['source']['tile'];assert next(b for b in read(p)['buildings'] if b['uid']==row['uid'])==row['source']['building'];row['source']['tileSHA256']=digest(p.read_bytes());refs.append(p);assert digest((ROOT/row['candidate']['path']).read_bytes())==row['sourceSHA256']
 oldentry=next(t for t in manifest['terrainPatches'] if t['url']=='city/data/government-xl-history-museum-private-browser-v1-20261016-terrain.json');oldpath=ROOT/'3d-viewer'/oldentry['url'];old=read(oldpath);parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);helper=module('museum_combined_constructor',HERE/'resolve-pass.py');f=module('museum_combined_foundation',HERE/'xl-final-script-pass.py')
 allbounds=np.asarray([r['candidate']['entry']['worldBounds'] for r in rows]);bounds=[allbounds[:,0,:].min(axis=0).tolist(),allbounds[:,1,:].max(axis=0).tolist()];cells=helper.rectangle_for(bounds,parent);cells=[min(cells[0],old['coarseCells'][0]),min(cells[1],old['coarseCells'][1]),max(cells[2],old['coarseCells'][2]),max(cells[3],old['coarseCells'][3])];extent=helper.extent(cells,parent);parts=[];sources=[]
 for rel in read(PRIOR/'summary.json')['terrainPaths']:
  p=ROOT/rel;t=helper.context.triangles(p);mask=(t[:,:,0].max(1)>=extent[0])&(t[:,:,0].min(1)<=extent[2])&(t[:,:,2].max(1)>=extent[1])&(t[:,:,2].min(1)<=extent[3]);parts.append(t[mask]);sources.append(dict(path=rel,sha256=digest(p.read_bytes()),provenance=str((PRIOR/'summary.json').relative_to(ROOT))))
 claim=reservations.claim('museum-combined-private-'+str(uuid.uuid4()),['private-combined-museums-terrain'],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();LOCAL.mkdir();core=[bounds[0][0]-2,bounds[0][2]-2,bounds[1][0]+2,bounds[1][2]+2];patch=helper.make_patch(dict(uids=[r['uid'] for r in rows],cells=cells),parent,np.concatenate(parts),sources,native_core=core);patch['id']=BATCH;save(DOC/'private-terrain.json',patch)
  candidate=dict(path=str((DOC/'private-terrain.json').relative_to(ROOT)),sha256=digest((DOC/'private-terrain.json').read_bytes()),uids=[r['uid'] for r in rows],replaces=dict(url=oldentry['url'],sha256=digest(oldpath.read_bytes()),retainedUids=['landsd/4759:0']));save(DOC/'terrain-candidates.json',[candidate]);save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=manifestsha))
  for row in rows:
   dest=LOCAL/row['candidate']['entry']['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],dest)
  tool=HERE/'acceptance-metrics-retained-group-parent.mjs';rel=lambda p:str(p.relative_to(ROOT));cmd=['node',str(tool),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')]
  with (DOC/'worker.log').open('w') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
  metrics=read(DOC/'metrics.json');assert not any(r.get('error') for r in metrics['rows']);foundations=[]
  for g,row in zip(read(LOCAL/'runtime-geometry.json.gz')['rows'],rows):
   assert g['uid']==row['uid'];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=row['source']['building'];foundations.append(dict(uid=row['uid'],foundation=f.foundation_context(t,ground,Polygon(b['rings'][0],b['rings'][1:]))))
  summary=dict(metrics=metrics['rows'],foundations=foundations,changedParentExtent=extent,coarseCells=cells,originalCore=core,retainedHistoryModelChecked=True,allNeighbourChecksPending=True,liveTerrainChanged=False,fullAcceptance=False);save(DOC/'summary.json',summary)
  for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  refs += [oldpath,parentpath,catpath,LOCAL/'runtime-geometry.json.gz',Path(helper.__file__),Path(f.__file__)]
  r=module('museum_combined_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'combined-two-museum-original-private-terrain-v1',list(dict.fromkeys(refs)),dict(uids=[r['uid'] for r in rows],summary=summary,newlyInstalled=0,fullAcceptance=False));print(dict(jobId=r['jobId'],metrics=metrics['rows'],foundations=foundations),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
