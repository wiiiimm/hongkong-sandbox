"""Exact installed terrain hierarchy and complete native actor nominations; no publication."""
from pathlib import Path
from shapely.geometry import box
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-one-pacifica-parent-scope-v1-20261018';DOC=BASE/BATCH
UIDS=['landsd/72354:0','landsd/283036:0']
def extent(p):
 g=p['meta']['georef'];return[g['bE']-834500,816500-g['bN'],g['bE']-834500+(p['w']-1)*g['aE'],816500-g['bN']-(p['h']-1)*g['aN']]
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];prior=BASE/'government-xl-times-square-native-scope-v1-20261018'
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [prior,BASE/'government-xl-next-twenty-current-terrain-v1-20261018']:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 inventory=read(prior/'complete-bounds.json.gz')['rows'];manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);basepath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(basepath);builder=module('waterfront_scope_builder',HERE/'resolve-pass-indexed-parent-clipping.py');selection=read(BASE/'government-xl-next-twenty-current-terrain-v1-20261018/selection.json.gz')['rows'];summaries=[]
 for uid in UIDS:
  row=next(r for r in selection if r['uid']==uid);cells=builder.rectangle_for(row['candidate']['entry']['worldBounds'],parent);domain=builder.extent(cells,parent);overlaps=[]
  for entry in manifest['terrainPatches']:
   path=ROOT/'3d-viewer'/entry['url'];p=read(path);e=extent(p)
   if box(*domain).intersection(box(*e)).area<=1e-8:continue
   refs.append(path);nestedcells=builder.rectangle_for(row['candidate']['entry']['worldBounds'],p);nestedextent=builder.extent(nestedcells,p);children=[]
   for child in p.get('patches',[]):
    ce=extent(child)
    children.append(dict(id=child.get('id'),extent=ce,intersectsNewChild=box(*nestedextent).intersection(box(*ce)).area>1e-8))
   overlaps.append(dict(url=entry['url'],sha256=digest(path.read_bytes()),extent=e,nativeMesh=bool(p.get('nativeMesh')),nestedReplacementCells=nestedcells,nestedReplacementExtent=nestedextent,nestedContainedByParent=box(*e).covers(box(*nestedextent)),existingChildren=children,touchingNativeUids=[r['uid'] for r in inventory if not closed_disjoint(r['completeFourWorldBounds'],nestedextent)],parentNativeUids=[r['uid'] for r in inventory if not closed_disjoint(r['completeFourWorldBounds'],e)]))
  summaries.append(dict(uid=uid,baseReplacementCells=cells,baseReplacementExtent=domain,overlappingInstalledTerrain=overlaps,installationApproved=False))
 save(DOC/'scope.json',dict(rows=summaries,currentNativeActors=len(inventory),fullMeshRegressionStillRequired=True));print([{ 'uid':r['uid'],'parents':[{ 'url':p['url'],'nestedContained':p['nestedContainedByParent'],'touchingChildren':[c['id'] for c in p['existingChildren'] if c['intersectsNewChild']],'touchingNative':len(p['touchingNativeUids'])} for p in r['overlappingInstalledTerrain']]} for r in summaries],flush=True)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([manifestpath,basepath,HERE/'resolve-pass-indexed-parent-clipping.py',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py'])
 module('waterfront_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-one-pacifica-current-parent-native-scope',list(dict.fromkeys(refs)),dict(uids=UIDS,currentNativeActors=len(inventory),installationApproved=False))
if __name__=='__main__':main()
