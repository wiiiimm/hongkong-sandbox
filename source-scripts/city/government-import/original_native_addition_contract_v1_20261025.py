"""Additive terrain obligations with complete, unchanged retained native actors.

Separate positive contract; the existing no-native and replacement guards stay
unchanged. Existing native-neighbour acceptance remains the authority.
"""
def verify(model_forms,terrain_forms,scope,model_scope,regression,retained_entries,*,sources,terrain_targets,native_count,expected_count):
 assert scope['currentNativeActors']==native_count and scope['uids']==terrain_targets
 assert not scope['terrainContacts']and scope['positiveAreaTerrainOverlaps']==0
 required=set(scope['touchingNativeUids']);assert required and required==set(retained_entries)and not required&set(sources)
 assert set(model_scope['uids'])==set(sources)
 assert {r['uid']for r in model_scope['rows']}==set(sources)
 for row in model_scope['rows']:assert row['currentNativeActorsChecked']==native_count and not row['nearbyNativeActors']
 assert set(regression['uids'])==set(sources)and not regression['basicFlags']
 assert required==set(regression['requiredNativeUids'])==set(regression['nativeResolved'])
 rows=regression['nativeRows'];assert len(rows)==len({r['uid']for r in rows})==len(required)and{r['uid']for r in rows}==required
 for row in rows:
  assert row['passed']and row['triangles']==retained_entries[row['uid']]['triangles']
  assert row['terrain']['newlyWhollyBuried']==row['terrain']['newlyUpwardWhollyBuried']==0
 assert len(terrain_forms)==len({f['uid']for f in terrain_forms})==scope['intersectingForms']
 result=dict(model_forms);assert all(k==v['uid']for k,v in result.items())
 for f in terrain_forms:
  assert f['uid']not in result or result[f['uid']]==f
  result[f['uid']]=f
 assert len(result)==expected_count and required|set(sources)<=set(result)
 return result
