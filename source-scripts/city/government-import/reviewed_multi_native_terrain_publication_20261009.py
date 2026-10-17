"""Explicit reviewed plural native replacement, delegating existing publication gates."""
import copy
def stage_top_level(module,plan,original,manifest,edits,report,delegate):
 entries=plan.get('topLevelTerrainPatches',[]);plural=[e for e in entries if e.get('replacesMany')]
 if not plural:return delegate(plan,original,manifest,edits,report)
 assert len(entries)==len(plural)==1,'Bounded one-patch plural replacement only'
 entry=plural[0];assert not entry.get('replaces') and len(entry['replacesMany'])==2
 rows=entry['replacesMany'];assert len({r['url'] for r in rows})==2
 assert len({u for row in rows for u in row['retainedUids']})==sum(len(r['retainedUids']) for r in rows),'Repeated retained native actor'
 parent=module.load(module.ROOT/'3d-viewer/city/data/terrain.json');new=module.load(module.ROOT/entry['source']);module.validate_patch(new,parent)
 old_patches=[]
 for r in rows:
  matches=[e for e in original.get('terrainPatches',[]) if e['url']==r['url']];assert len(matches)==1
  path=module.ROOT/'3d-viewer'/r['url'];assert module.sha(path)==r['sha256'];old=module.load(path)
  assert old.get('nativeMesh') and new.get('nativeMesh') and not old.get('patches') and not new.get('patches')
  synthetic={**entry,'replaces':r,'nativeReview':r['nativeReview']};synthetic.pop('replacesMany')
  decision=module.review_native_top_level_replacement(synthetic,old,new)
  assert set(r['retainedUids'])==set(decision['retainedUids'])==set(old['meta']['targetUids']),'Plural replacement must retain every original native actor'
  a,b,c,d=old['coarseCells'];x0,z0,x1,z1=new['coarseCells'];assert x0<=a and z0<=b and x1>=c and z1>=d
  assert old.get('hydro')==new.get('hydro')
  old_patches.append(old)
 module.check_patch_overlap(old_patches[0],[old_patches[1]])
 # Both removed originals have independently passed every unchanged native
 # source review above. Existing delegate validates the one new complete patch,
 # all remaining parent/installed overlap, destination, grid, build and edits.
 first,second=rows;delegated_entry={**entry,'replaces':first,'nativeReview':first['nativeReview']};delegated_entry.pop('replacesMany')
 delegated_plan={**plan,'topLevelTerrainPatches':[delegated_entry]}
 delegated_original=copy.deepcopy(original);delegated_original['terrainPatches']=[e for e in original['terrainPatches'] if e['url']!=second['url']]
 manifest['terrainPatches']=[e for e in manifest['terrainPatches'] if e['url']!=second['url']]
 delegate(delegated_plan,delegated_original,manifest,edits,report)
 assert report['replacedTerrainPatches']==[{'url':first['url'],'sha256':first['sha256'],'oldAssetRetained':True}]
 report['replacedTerrainPatches'].append({'url':second['url'],'sha256':second['sha256'],'oldAssetRetained':True})
 report['explicitPluralNativeReplacementReviews']=[r['nativeReview'] for r in rows]
