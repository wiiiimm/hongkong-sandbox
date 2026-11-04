"""Construct a private nested original-ground candidate; no installation approval."""
import ast,json,sys,uuid,subprocess,traceback
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-nested-terrain-v2-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
INPUT=BASE/'government-xl-west-wing-terrain-inputs-v3-20261018';REVIEW=BASE/'government-xl-west-wing-identity-review-v1-20261018';GROUND=BASE/'government-xl-west-wing-original-ground-foundations-v1-20261018';UID='landsd/26195:0'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);pins={};refs=[Path(__file__)]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [INPUT,REVIEW,GROUND]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 scope=read(INPUT/'scope.json');assert scope['nestedParent'] and not scope['retainedParents']
 parent=ROOT/'3d-viewer'/scope['parentURL'];assert digest(parent.read_bytes())==scope['parentSHA256']
 path=HERE/'xl-routed-source-local-contact-resolution.py';code=path.read_text()
 start=code.index('        from routed_original_cell_identity import verify_files, POLICY');end=code.index("        for path, pinned in context[r['uid']]['neighbourTileHashes'].items():",start)
 code=code[:start]+'''        from exact_original_georef_cell_identity_20261009 import verify_files
        identity_context=read(ROOT/'docs/astra-city/government-import/government-xl-west-wing-current-identity-v1-20261018/identity-context.json')
        proof=verify_files(r,identity_context,LOCAL/'identity-recheck')
        review=read(ROOT/'docs/astra-city/government-import/government-xl-west-wing-identity-review-v1-20261018/ROOT-IDENTITY-REVIEW.json')
        assert review['identityAccepted'] and not review['installationApproved']
        for key in ['uid','sourceSHA256','worldTrianglesSHA256','sourceFormSHA256']:assert proof[key]==review[key],key
        assert proof['reasons']==review['rawAutomaticReasons']
        assert sha(ROOT/'3d-viewer/city/data/manifest.json')==review['manifestSHA256']
        for tile,h in review['tileHashes'].items():assert sha(ROOT/'3d-viewer'/tile)==h
        assembly=read(ROOT/'docs/astra-city/government-import/government-xl-west-wing-group-four-world-v1-20261018/selection.json.gz')['rows']
        for uid,h in review['requiredAssemblyOriginals'].items():
            required=next(q for q in assembly if q['uid']==uid)
            assert required['sourceSHA256']==h and sha(ROOT/required['candidate']['path'])==h
        save(DOC/'identity-recheck.json',proof)
        save(DOC/'required-assembly.json',{'sources':review['requiredAssemblyOriginals'],'installationApproved':False})
'''+code[end:]
 old='    assert len(RETAIN_NATIVE_URLS)>=2 and len(set(RETAIN_NATIVE_URLS))==len(RETAIN_NATIVE_URLS)\n    assert not NESTED_PARENT'
 assert old in code
 code=code.replace(old,"""    scope=read(BASE/'scope.json')
    assert NESTED_PARENT and RETAIN_NATIVE_URLS==[] and scope['retainedParents']==[]
    assert PARENT_URL==scope['parentURL'] and sha(parent_path)==scope['parentSHA256']
    assert cells==scope['replacementCells']
    assert [c.get('id') for c in parent.get('patches',[])]==scope['retainedChildIds']""")

 old_world="    world = [r['native']['model']['worldBounds'] for r in rows]"
 new_world="    assembly = read(ROOT/'docs/astra-city/government-import/government-xl-west-wing-group-four-world-v1-20261018/selection.json.gz')['rows']\n    world = [r['candidate']['entry']['worldBounds'] for r in assembly]"
 assert old_world in code;code=code.replace(old_world,new_world)
 old_models="    models = {r['uid']:second.glb_triangles(r) for r in rows}"
 new_models="""    from exact_packed_world_geometry_20261009 import decode_original_world_triangles
    models={}
    for actor in assembly:
        raw=(ROOT/actor['candidate']['path']).read_bytes()
        assert digest(raw)==actor['sourceSHA256']
        models[actor['uid']]=decode_original_world_triangles(raw)
    assert len(models)==4
"""
 assert old_models in code;code=code.replace(old_models,new_models)
 code=code.replace('    all_declared_uids=set(UIDS)','    all_declared_uids=set(models)')
 start=code.index("    proof = read(SOURCE / 'original/download.json')");end=code.index('    native = np.concatenate(fragments)',start)
 code=code[:start]+'''    sheet=read(ROOT/'docs/astra-city/government-import/government-xl-west-wing26195-missing-sheet-candidates-v2-20261017/sheet-result.json.gz')
    terrain=sheet['result']['terrain'][0];files=[];gltf=None
    for entry in terrain['preparedFiles']:
        if entry['path']=='manifest.json':continue
        p=HERE.parent/'central-completion/staged/11-SW-9C'/entry['path']
        assert sha(p)==entry['sha256'];files.append({'path':rel(p),'sha256':sha(p)})
        if p.suffix=='.gltf':gltf=p
    assert gltf is not None
    original=np.asarray(second.context.triangles(gltf),dtype='<f8')
    assert len(original)==97915 and digest(original.tobytes())=='25e82f091ff9ee5fbe00b353a9c4d1684ef0f471af90f224354bfd899aaa361e'
    used=[{'sheet':'11-SW-9C','nativeStageCacheKey':sheet['cacheKey'],'nativeStageResultSHA':sheet['resultSHA'],'sourceHashes':terrain['sourceHashes'],'sourceFiles':files}]
    fragments=[original]
'''+code[end:]
 old="    patch_row['replacesMany']=retained_replacements";assert old in code;code=code.replace(old,"    assert retained_replacements==[]")
 donor=HERE/'park_avenue239350_joint_terrain_v3_20261018.py';values={}
 for node in ast.walk(ast.parse(donor.read_text())):
  if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ['original_projection','complete_projection']:values[node.targets[0].id]=ast.literal_eval(node.value)
 assert values['original_projection'] in code;code=code.replace(values['original_projection'],values['complete_projection'])
 code=code.replace('terrain-central-with-sun-yat-sen.json','terrain-regional-with-west-wing.json')
 # Candidate construction only: full actor nomination must precede physical acceptance.
 marker="    live = {e['uid'] for url in manifest['officialModelCatalogues']"
 start=code.index(marker);end=code.index('\ndef ',start);code=code[:start]+'    return\n'+code[end:]
 DOC.mkdir();generated=LOCAL/'terrain-worker.py';generated.write_text(code);worker=module('west_nested_candidate',generated)
 worker.BATCH=BATCH;worker.BASE=INPUT;worker.DOC=DOC;worker.LOCAL=LOCAL;worker.UIDS=[UID];worker.RETAIN_NATIVE_URLS=[];worker.NESTED_PARENT=True;worker.PARENT_URL=scope['parentURL']
 error=None
 try:worker.owned()
 except Exception as exc:
  error=str(exc);save(DOC/'guard-failure.json',dict(error=error,traceback=traceback.format_exc(),publication=False))
 assert reservations.owns(lease)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins);refs.extend([path,donor,generated]);refs.extend(p for p in LOCAL.rglob('*') if p.is_file() and p.name!='reservation.json')
 out=module('west_nested_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'west-wing-full-assembly-private-nested-original-ground-v2',list(dict.fromkeys(refs)),dict(uids=[UID],guardFailure=error,fullAcceptance=False,installationApproved=False,publication=False,modelGeometryChanges=0,neighbourNominationPending=True))
 print(dict(jobId=out['jobId'],guardFailure=error),flush=True)
def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists();assert not (LOCAL/'reservation.json').exists() or not reservations.owns(read(LOCAL/'reservation.json'))
 scope=read(INPUT/'scope.json');final=module('west_scope_forms',HERE/'xl-final-script-pass.py');uids={b['uid'] for b,_,_ in final.load_forms(scope['fullParentBounds'])}|{UID}
 keys={('building:' if u.startswith('landsd/') else 'source-form:')+u for u in uids}|{'terrain:city/data/terrain.json'}
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
