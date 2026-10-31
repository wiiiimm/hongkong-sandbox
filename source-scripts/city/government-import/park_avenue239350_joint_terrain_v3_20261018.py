"""Private three-source terrain candidate; joint installed actors remain unapproved."""
from pathlib import Path
import json,sys,uuid,subprocess,traceback
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-park-avenue239350-joint-terrain-v3-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/239350:0','landsd/240161:0','landsd/227455:0']
INPUT=BASE/'government-xl-park-avenue239350-terrain-inputs-v1-20261018'
MAIN=BASE/'government-xl-park-avenue239350-current-identity-runtime-v3-20261018'
COMP=BASE/'government-xl-park-avenue239350-companion-identity-runtime-v1-20261018'
REVIEW=BASE/'government-xl-park-avenue239350-identity-review-v1-20261018'
JOINT=BASE/'government-xl-park-avenue239350-joint-scope-v1-20261018'
PRIOR=BASE/'government-xl-olympian-two-current-retained-terrain-v1-20261018'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 pins={};refs=[Path(__file__)];sources=[INPUT,MAIN,COMP,REVIEW,JOINT,PRIOR,BASE/'government-xl-park-avenue239350-native-scope-v1-20261018']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in sources:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(INPUT/'check-selection.json.gz')['rows']+read(COMP/'selection.json.gz')['rows']
 contexts=[]
 final=module('park_joint_context',HERE/'xl-final-script-pass.py')
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 near=final.load_forms(read(INPUT/'scope.json')['fullParentBounds'])
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for row in rows:
   review=db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE uid=%s ORDER BY updated_at DESC LIMIT 1',(row['uid'],)).fetchone()
   assert review is None, ('existing-review-needs-resolution',row['uid'],review)
   row['currentReview']=None
   resultsha,stage=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone()
   assert row['native']['model'] in stage['models'];row['native']['resultSha']=resultsha
   tri=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes())
   contexts.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,near),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in near}))
 fresh=LOCAL/'inputs';save(fresh/'check-selection.json.gz',dict(rows=rows,manifestSHA256=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())));save(fresh/'context.json.gz',dict(rows=contexts))
 # Keep the unmodified terrain algorithm; substitute only the previously reviewed, exact-source identity route.
 path=HERE/'xl-routed-source-local-contact-resolution.py';code=path.read_text()
 start=code.index('        from routed_original_cell_identity import verify_files, POLICY')
 end=code.index("        for path, pinned in context[r['uid']]['neighbourTileHashes'].items():",start)
 replacement="""        from exact_original_georef_cell_identity_20261009 import verify_files
        identity_base=ROOT/'docs/astra-city/government-import/government-xl-park-avenue239350-current-identity-runtime-v3-20261018'
        if r['uid']!='landsd/239350:0':identity_base=ROOT/'docs/astra-city/government-import/government-xl-park-avenue239350-companion-identity-runtime-v1-20261018'
        identity_context=read(identity_base/(r['uid'].split('/')[1]+'-identity.json'))['context']
        proof=verify_files(r,identity_context,LOCAL/'identity-recheck'/r['uid'].split('/')[1])
        if r['uid']=='landsd/239350:0':
            review=read(ROOT/'docs/astra-city/government-import/government-xl-park-avenue239350-identity-review-v1-20261018/239350:0-review.json')
            assert review['identityOnlyApproved'] and review['identityReviewApproved']
            for key in ['uid','sourceSHA256','sourceFormSHA256','worldTrianglesSHA256']:assert proof[key]==review[key],key
            assert proof['reasons']==review['rawReasonsRetained']
        else:assert proof['passed'],proof['reasons']
        save(DOC/(r['uid'].split('/')[1]+'-identity-recheck.json'),proof)
"""
 code=code[:start]+replacement+code[end:]
 # Polygon union alone drops zero-area vertical walls. Preserve their edges too.
 original_projection="    projection = shapely.union_all([shapely.union_all(shapely.polygons(t[:,:,[0,2]])) for t in models.values()])"
 complete_projection="""    projected_parts=[]
    for triangles in models.values():
        xz=triangles[:,:,[0,2]]
        projected_parts.extend(shapely.polygons(xz))
        for i in range(3):projected_parts.extend(shapely.linestrings(xz[:,[i,(i+1)%3],:]))
    projection=shapely.union_all(projected_parts)
    # Existing .1m/1m preservation margins stay unchanged.
    for triangles in models.values():
        for i in range(3):
            edges=shapely.linestrings(triangles[:,[i,(i+1)%3],:][:,:,[0,2]])
            # Tiny buffers of mixed polygon/line unions can erase narrow spikes.
            # Prove complete edges directly and test both actual preservation margins.
            exact=shapely.is_empty(shapely.difference(edges,projection))
            numerical=shapely.covers(projection.buffer(1e-8),edges)
            assert (exact|numerical).all(), 'incomplete-source-projection'
            save(DOC/('projection-proof-'+str(len(triangles))+'-'+str(i)+'.json'),dict(edges=len(edges),exactDifferenceEmpty=int(exact.sum()),coveredByExistingNumericalBuffer=int(numerical.sum()),uncovered=int((~(exact|numerical)).sum()),numericalToleranceM=1e-8,terrainMarginsM=[.1,1],modelGeometryChanges=0))
            for margin in (.1,1):
                assert shapely.covers(projection.buffer(margin,join_style='mitre'),edges).all(), 'incomplete-terrain-margin'
            endpoints=shapely.points(triangles[:,[i,(i+1)%3],:][:,:,[0,2]].reshape(-1,2))
            assert shapely.covers(projection.buffer(.1,join_style='mitre'),endpoints).all(), 'incomplete-projected-endpoints'
"""
 assert original_projection in code;code=code.replace(original_projection,complete_projection)

 # Inject complete previously nominated native scope into the existing generated checker input.
 old="    call(['node',str(HERE/'check-native-neighbours-multi-retained.mjs'),rel(DOC)+'/'])"
 new="""    ni=read(DOC/'neighbour-inputs.json.gz');ni['requiredNativeUids']=read(ROOT/'docs/astra-city/government-import/government-xl-park-avenue239350-native-scope-v1-20261018/scope.json')['touchingNativeUids'];save(DOC/'neighbour-inputs.json.gz',ni)
    call(['node',str(HERE/'check-native-neighbours-multi-retained-scoped-v3.mjs'),rel(DOC)+'/'])"""
 assert old in code;code=code.replace(old,new)
 # Private candidate: explicitly distinguish joint-rechecked actors from unchanged terrain.
 old="assert len(RETAIN_NATIVE_URLS)>=2 and len(set(RETAIN_NATIVE_URLS))==len(RETAIN_NATIVE_URLS)"
 new="assert RETAIN_NATIVE_URLS==['city/data/government-olympian-original-v1-20261018.json']"
 assert old in code;code=code.replace(old,new)
 old="            lo,hi=entry['worldBounds'];assert protected.buffer(1e-6).covers(box(lo[0],lo[2],hi[0],hi[2])), 'Retained model intersects new source projection'"
 new="""            joint=read(ROOT/'docs/astra-city/government-import/government-xl-park-avenue239350-joint-scope-v1-20261018/scope.json')
            joint_rows={e['uid']:e for e in joint['jointReviewRequired']}
            lo,hi=entry['worldBounds']
            if entry['uid'] in joint_rows:
                assert entry['sha256']==joint_rows[entry['uid']]['sourceSHA256']
                assert entry['uid'] in joint['requiredNativeUids']
            else:assert protected.buffer(1e-6).covers(box(lo[0],lo[2],hi[0],hi[2])), 'Unscoped retained model intersects new source projection'"""
 assert old in code;code=code.replace(old,new)
 old='boundsOfEveryRetainedModelInsideProtectedProjection=True)'
 new="boundsOfEveryRetainedModelInsideProtectedProjection=False, jointReviewRequired=sorted(joint_rows), jointReviewComplete=False, publication=False)"
 assert old in code;code=code.replace(old,new)
 generated=LOCAL/'pair-terrain-worker.py';generated.parent.mkdir(parents=True,exist_ok=True);generated.write_text(code);worker=module('olympian_pair_private_worker',generated)
 worker.BATCH=BATCH;worker.BASE=fresh;worker.DOC=DOC;worker.LOCAL=LOCAL;worker.UIDS=UIDS;worker.ALLOW_BASIC_TERRAIN_TARGETS=True
 worker.RETAIN_NATIVE_URLS=[x['url']for x in read(INPUT/'scope.json')['retainedParents']]
 recovery=read(PRIOR/'source-recovery.json')['sheets'];worker.SOURCE=ROOT/recovery[0]['cache'];worker.ADJACENT_SOURCES=[ROOT/r['cache']for r in recovery[1:]]
 error=None
 try:worker.owned()
 except AssertionError as exc:
  error=str(exc);save(DOC/'guard-failure.json',dict(error=error,traceback=traceback.format_exc(),publication=False,modelGeometryChanges=0))
 assert reservations.owns(lease)
 refs.extend(ROOT/p for p in pins);refs.extend([path,generated]);refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 summary=dict(uids=UIDS,guardFailure=error,fullAcceptance=False,newlyInstalled=0,publication=False,modelGeometryChanges=0)
 out=module('olympian_pair_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'park-avenue-private-joint-original-terrain-v3',list(set(refs)),summary);print(dict(jobId=out['jobId'],**summary),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();scope=read(INPUT/'scope.json');final=module('pair_scope_forms',HERE/'xl-final-script-pass.py');uids={b['uid']for b,_,_ in final.load_forms(scope['fullParentBounds'])}|set(UIDS)
 keys={('building:'if u.startswith('landsd/')else'source-form:')+u for u in uids}|{'terrain:city/data/terrain.json'}|{'terrain:'+r['url']for r in scope['retainedParents']}
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
