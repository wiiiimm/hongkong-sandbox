"""Full current actor census for original Wave/Verdant complete-source terrain domain."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave-verdant-expanded-scope-v1-20261017';DOC=BASE/BATCH
NAMES=['government-xl-wave275510-current-native-scope-v1-20261017','government-xl-wave275510-pair-capture-v1-20261017','government-xl-wave-verdant-pair-source-tin-foundation-v1-20261017']
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 rows=read(BASE/NAMES[1]/'selection.json.gz')['rows']+read(BASE/NAMES[2]/'selection.json.gz')['rows'];assert len({r['uid']for r in rows})==4
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);second=module('wave_verdant_expanded_parent',HERE/'xl-second-pass.py');rects=[];sourceBounds=[]
 for r in rows:
  p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];b=packed_world_bounds(raw)['originalWholeSourceBounds'];sourceBounds.append(dict(uid=r['uid'],bounds=b));rects.append(second.resolution.rectangle_for([[b[0][0]-.1,b[0][1],b[0][2]-.1],[b[1][0]+.1,b[1][1],b[1][2]+.1]],parent));refs.append(p)
 cells=[min(r[0]for r in rects),min(r[1]for r in rects),max(r[2]for r in rects),max(r[3]for r in rects)];domain=second.resolution.extent(cells,parent)
 current=read(ROOT/'3d-viewer/city/data/manifest.json');installed={e['uid']:e for url in current['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']};bounds=read(BASE/NAMES[0]/'complete-bounds.json.gz')['rows'];assert set(installed)=={r['uid']for r in bounds};touch=[];boundrows=[]
 for r in bounds:
  assert installed[r['uid']]['sha256']==r['sourceSHA256'];disjoint=closed_disjoint(r['completeFourWorldBounds'],domain);boundrows.append(dict(r,disjoint=disjoint))
  if not disjoint:touch.append(r['uid'])
 final=module('wave_verdant_expanded_forms',HERE/'xl-final-script-pass.py');forms=final.load_forms(domain)
 scope=dict(parentCells=cells,parentExtent=domain,changedParentExtent=domain,currentNativeActors=len(bounds),touchingNativeUids=sorted(touch),basicAndNativeForms=[b['uid']for b,_,_ in forms],allCurrentActorsNominated=True,sourceBounds=sourceBounds,fullAcceptance=False)
 save(DOC/'scope.json',scope);save(DOC/'complete-bounds.json.gz',dict(rows=boundrows));save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())));save(DOC/'forms.json.gz',dict(rows=[dict(building=b,tile=t)for b,_,t in forms]));refs.extend([ROOT/'3d-viewer'/t for _,_,t in forms]);refs.extend([parentpath,HERE/'xl-second-pass.py',HERE/'resolve-pass.py',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_bounds_v3_20261010.py',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py'])
 summary=dict(parentCells=cells,parentExtent=domain,forms=len(forms),currentNativeActors=len(bounds),touchingNativeUids=touch,fullAcceptance=False);save(DOC/'summary.json',summary);out=module('expanded_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'wave-verdant-whole-source-expanded-parent-current-census-v1',list(set(refs)),dict(uids=[r['uid']for r in rows]+touch,summary=summary,newlyInstalled=0,fullAcceptance=False));print(summary,flush=True);print(out['jobId'],flush=True)
if __name__=='__main__':main()
