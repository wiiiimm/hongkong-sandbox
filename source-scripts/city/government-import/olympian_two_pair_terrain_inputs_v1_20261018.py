"""Fresh terrain replacement closure and source context; no terrain mutation."""
from pathlib import Path
from shapely.geometry import box
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-two-pair-terrain-inputs-v1-20261018';DOC=BASE/BATCH;UID='landsd/239351:0'
def main():
 assert not DOC.exists();prior=BASE/'government-xl-olympian-two-remaining-identity-review-v1-20261018/result.json';r=read(prior);pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),prior]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);second=module('olympian_current_terrain_scope',HERE/'xl-second-pass.py');final=module('olympian_current_terrain_context',HERE/'xl-final-script-pass.py')
 row=next(r for r in read(BASE/'government-xl-olympian-two-current-identity-runtime-v1-20261018/selection.json.gz')['rows']if r['uid']==UID);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);mainrow=next(r for r in read(BASE/'government-xl-olympian-two-current-identity-runtime-v1-20261018/selection.json.gz')['rows']if r['uid']=='landsd/265851:0');maintri=decode_original_world_triangles((ROOT/mainrow['candidate']['path']).read_bytes());import numpy as np;both=np.concatenate([tri,maintri]);bounds=[both.min((0,1)).tolist(),both.max((0,1)).tolist()];cells=second.resolution.rectangle_for(bounds,parent);initial=list(cells);patches=[]
 for entry in manifest['terrainPatches']:
  path=ROOT/'3d-viewer'/entry['url'];p=read(path);g=p['meta']['georef'];extent=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(p['w']-1)*g['aE'],816500-g['bN']-(p['h']-1)*g['aN']];patches.append((entry,path,p,extent))
 selected={};changed=True
 while changed:
  changed=False;domain=second.resolution.extent(cells,parent)
  for entry,path,p,extent in patches:
   if entry['url']in selected or box(*domain).intersection(box(*extent)).area<=1e-8:continue
   assert p.get('nativeMesh')and not p.get('patches'),entry['url'];c=p['coarseCells'];selected[entry['url']]=dict(url=entry['url'],sha256=digest(path.read_bytes()),coarseCells=c,targetUids=p['meta']['targetUids'],bounds=extent);cells=[min(cells[0],c[0]),min(cells[1],c[1]),max(cells[2],c[2]),max(cells[3],c[3])];changed=True;refs.append(path)
 domain=second.resolution.extent(cells,parent);near=final.load_forms(domain);tile=ROOT/'3d-viewer'/row['source']['tile'];form=next(b for b in read(tile)['buildings']if b['uid']==UID);row['source']=dict(building=form,tile=row['source']['tile'],tileSHA256=digest(tile.read_bytes()));row['currentReview']=None
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');review=c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE uid=%s ORDER BY updated_at DESC LIMIT 1',(UID,)).fetchone();assert review is None,review
  resultsha,stage=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone();assert row['native']['model']in stage['models'];row['native']['resultSha']=resultsha
 context=dict(uid=UID,sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,near),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in near});save(DOC/'check-selection.json.gz',dict(rows=[row],manifestSHA256=digest(manifestpath.read_bytes())));save(DOC/'context.json.gz',dict(rows=[context]));save(DOC/'scope.json',dict(initialCells=initial,replacementCells=cells,fullParentBounds=domain,retainedParents=list(selected.values()),nearbyForms=len(near),allCurrentNativeFourWorldNominationComplete=False,qualification='Whole intersecting-parent closure only. Complete actual installed actor nomination and final regressions still required. No installation or terrain publication.'))
 refs.extend([manifestpath,parentpath,HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py']);refs.extend(ROOT/'3d-viewer'/t for t in context['neighbourTileHashes']);refs.extend(ROOT/p for p in pins)
 out=module('olympian_current_inputs_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-current-terrain-parent-closure-and-inputs-v1',list(set(refs)),dict(uids=[UID],retainedParents=sorted(selected),nearbyForms=len(near),fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],cells=cells,retained=list(selected),nearbyForms=len(near)),flush=True)
if __name__=='__main__':main()
