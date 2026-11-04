"""Rebind saved sources to the current map; nominate the complete expanded parent."""
from pathlib import Path
import json,subprocess,re
from shapely.geometry import box
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-pacifica-current-scope-v1-20261018';DOC=BASE/BATCH
UID='landsd/283036:0';PRIOR=BASE/'government-xl-times-square-native-scope-v1-20261018';INSTALL=BASE/'government-xl-olympian-one-original-installed-v1-20261018'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];aliases=[]
 folders=[BASE/'government-xl-next-twenty-original-ground-v1-20261018',BASE/'government-xl-next-twenty-current-terrain-v1-20261018',BASE/'government-xl-olympian-one-pacifica-parent-scope-v1-20261018',INSTALL]
 history=read(INSTALL/'historical-input-context.json')['mutableCurrentByteSnapshots']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in folders:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    p=ROOT/e['path']
    if digest(p.read_bytes())!=e['sha256']:
     assert e['path']=='3d-viewer/city/data/manifest.json'
     h=next(h for h in history if h['originalPath']==e['path']and h['originalSHA256']==e['sha256'])
     p=ROOT/h['savedHistoricalBytes']['path'];assert digest(p.read_bytes())==e['sha256'];aliases.append(dict(original=e,historical=h['savedHistoricalBytes']))
    key=str(p.relative_to(ROOT));assert key not in pins or pins[key]==e['sha256'];pins[key]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 oldpath=ROOT/next(h for h in history if h['originalPath']=='3d-viewer/city/data/manifest.json')['savedHistoricalBytes']['path'];old=read(oldpath);manifestpath=ROOT/'3d-viewer/city/data/manifest.json';current=read(manifestpath)
 assert current['tiles']==old['tiles'];added=[u for u in current['officialModelCatalogues']if u not in old['officialModelCatalogues']];assert len(added)==1 and current['officialModelCatalogues']==old['officialModelCatalogues']+added
 assert current['terrainPatches'][:-1]==old['terrainPatches'];newpatch=read(ROOT/'3d-viewer'/current['terrainPatches'][-1]['url'])
 inventory=read(PRIOR/'complete-bounds.json.gz');rows=inventory['rows'];models={};assets={};roots={}
 for url in current['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;cat=read(p);refs.append(p)
  for e in cat['models']:
   assert e['uid']not in models;models[e['uid']]=e;assets[e['uid']]=p.parent/e['asset'];roots[e['uid']]=cat['rootTranslation']
 oldids={r['uid']for r in rows};new=sorted(set(models)-oldids);assert new==['landsd/256927:0','landsd/72354:0']and oldids<=set(models)
 for r in rows:assert r['sourceSHA256']==models[r['uid']]['sha256']==digest(assets[r['uid']].read_bytes())
 for p,h in inventory['currentFormTileHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 forms={}
 for t in current['tiles']:
  p=ROOT/'3d-viewer'/t['url']
  for b in read(p)['buildings']:
   if b['uid']in new:forms[b['uid']]=b;refs.append(p)
 DOC.mkdir();save(DOC/'input.json.gz',dict(currentManifest=ref(manifestpath),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/u)for u in current['officialModelCatalogues']],evidenceRefs=[ref(PRIOR/'complete-bounds.json.gz')],rows=[dict(uid=u,entry={**models[u],'rootTranslation':roots[u]},building=forms[u],path=str(assets[u].relative_to(ROOT)))for u in new]))
 template=(HERE/'oi_sin_new_native_attributes_v3_20261017.mjs').read_text().replace('oi_sin_new_native_attributes_v3_20261017.mjs','pacifica_current_new_native_attributes_v1_20261018.mjs')
 template=re.sub(r'assert.deepEqual\(input.rows.map\(r=>r.uid\),\[.*?\]\);','assert.deepEqual(input.rows.map(r=>r.uid),'+json.dumps(new)+');',template)
 expected={u:[models[u]['sha256'],models[u]['triangles']]for u in new};template=re.sub(r'rows=\[\],expected=\{.*?\};','rows=[],expected='+json.dumps(expected)+';',template).replace('completeOriginalFaces:121955','completeOriginalFaces:'+str(sum(v[1]for v in expected.values())))
 tool=HERE/'pacifica_current_new_native_attributes_v1_20261018.mjs';assert not tool.exists();tool.write_text(template)
 with(DOC/'capture.log').open('w')as log:subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
 actual=read(DOC/'attributes.json.gz');assert actual['startEndAllInputsVerified']
 for p,h in actual['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 for r in actual['rows']:
  proof=packed_world_bounds(assets[r['uid']].read_bytes());assert proof['sourceSHA256']==r['sourceSHA256'];rows.append(dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],completeFourWorldBounds=[proof['originalWholeSourceBounds'],r['completeLiteralWorldBounds'],r['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'],r['completeExplicitBalancedFloat32ModelMatrixWorldBounds']],completeOriginalPOSITIONProof=proof))
 builder=module('pacifica_scope_builder',HERE/'resolve-pass-indexed-parent-clipping.py');parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);saved=read(BASE/'government-xl-olympian-one-pacifica-parent-scope-v1-20261018/scope.json');s=next(r for r in saved['rows']if r['uid']==UID);retained=s['overlappingInstalledTerrain'][0];retainedpath=ROOT/'3d-viewer'/retained['url'];assert ref(retainedpath)['sha256']==retained['sha256'];patch=read(retainedpath)
 cells=s['baseReplacementCells'];oc=patch['coarseCells'];cells=[min(cells[0],oc[0]),min(cells[1],oc[1]),max(cells[2],oc[2]),max(cells[3],oc[3])];domain=builder.extent(cells,parent)
 overlaps=[]
 for e in current['terrainPatches']:
  p=read(ROOT/'3d-viewer'/e['url']);g=p['meta']['georef'];bounds=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(p['w']-1)*g['aE'],816500-g['bN']-(p['h']-1)*g['aN']]
  if box(*domain).intersection(box(*bounds)).area>1e-8:overlaps.append(e['url'])
 assert overlaps==[retained['url']]
 touch=[]
 for r in rows:
  r['disjoint']=closed_disjoint(r['completeFourWorldBounds'],domain)
  if not r['disjoint']:touch.append(r['uid'])
 assert len(rows)==len(models)==6719 and set(touch)=={'landsd/283034:0','landsd/265478:0'}
 summary=dict(uid=UID,currentNativeActors=len(rows),reusedActors=6717,freshInstalledCaptures=new,coarseCells=cells,changedParentExtent=domain,retainedTerrain=retained,touchingNativeUids=touch,overlappingTerrainURLs=overlaps,historicalInputAliases=aliases,fullMeshRegressionStillRequired=True,installationApproved=False)
 save(DOC/'scope.json',summary);save(DOC/'complete-bounds.json.gz',dict(rows=rows,currentFormTileHashes=inventory['currentFormTileHashes']));save(DOC/'selection.json.gz',dict(rows=[r for r in read(BASE/'government-xl-next-twenty-current-terrain-v1-20261018/selection.json.gz')['rows']if r['uid']==UID]))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([manifestpath,parentpath,retainedpath,tool,HERE/'rendered_patch_sampler.py',HERE/'exact_packed_world_bounds_v3_20261010.py',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py']);refs.extend(assets.values())
 module('pacifica_scope_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-expanded-parent-complete-native-scope',list(dict.fromkeys(refs)),dict(uids=[UID]+touch,currentNativeActors=len(rows),installationApproved=False))
 print({k:summary[k]for k in ['currentNativeActors','changedParentExtent','touchingNativeUids']},flush=True)
if __name__=='__main__':main()
