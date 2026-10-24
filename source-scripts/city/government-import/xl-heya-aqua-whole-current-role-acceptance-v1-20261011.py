"""DRAFT supervised unmocked Heya complete unchanged current source account.
Hermetic30 counterexamples are distinct from the production owned-identity replay.
All completed numerical/source receipts are independently read back; no live writes.
"""
import importlib.util,json,subprocess,sys,uuid,unittest
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from government_owned_identity import verify_files
from heya_aqua_complete_current_role_fixture_20261011 import BASE,FOLDERS,load
from heya_aqua_complete_current_role_policy_20261011 import compose,CURRENT,T,P
BATCH='government-xl-heya-aqua-whole-current-role-acceptance-v1-20261011'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
VALIDATION=BASE/'government-xl-heya-aqua-whole-current-role-validation-v1-20261011'
HELPERS=['heya_aqua_original_lower_assembly_join_20261011.py','heya_aqua_complete_current_role_policy_20261011.py',
 'heya_aqua_complete_current_role_fixture_20261011.py','test_heya_aqua_complete_current_role_policy_20261011.py',
 'heya_aqua_58_original_terminal_visual_placement_20261011.py','heya_aqua_current_exposed_grade_path_20261011.py',
 'government_owned_identity.py','original_source_ownership.py','exact_original_georef_cell_identity_20261009.py',
 'georef_projection_coverage.py','exact_packed_world_geometry_20261009.py',
 'xl-popcorn-source-investigations-checkpoints-20261009.py','run.py']
CODES=[Path(__file__)]+[HERE/h for h in HELPERS]+[HERE.parent/'shared-modelling/reservations.py']
def pin(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def codehashes():return {str(p.relative_to(ROOT)):digest(p.read_bytes())for p in CODES}
def validation():
 assert not VALIDATION.exists();VALIDATION.mkdir(parents=True)
 before=codehashes();log=VALIDATION/'unittest.log'
 suite=unittest.defaultTestLoader.loadTestsFromName('test_heya_aqua_complete_current_role_policy_20261011')
 assert suite.countTestCases()==30
 with log.open('w')as stream:result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
 assert codehashes()==before
 save(VALIDATION/'validation.json',dict(testsRun=result.testsRun,allPassed=result.wasSuccessful(),codeHashes=before,evidenceRefs=[pin(log)],hermeticActualSourceCounterexamples=True,separateUnmockedProductionReplayRequired=True))
 assert result.testsRun==30 and result.wasSuccessful(), 'Preserve negative validation unchanged'
 print(json.dumps(dict(validation=str(VALIDATION.relative_to(ROOT)),testsRun=30,allPassed=True)),flush=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
 v=read(VALIDATION/'validation.json');assert v['allPassed']and v['testsRun']==30 and v['codeHashes']==codehashes()
 refs=CODES+[VALIDATION/'validation.json'];pins=codehashes()
 for r in v['evidenceRefs']:
  assert pin(ROOT/r['path'])==r;refs.append(ROOT/r['path']);pins[r['path']]=r['sha256']
 # Read-only complete saved-job equality, not status-only or summary inference.
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for key,folder in FOLDERS.items():
   d=BASE/folder
   if key=='context':
    context=read(d/'context.json');extra=[d/'context.json']+[ROOT/r['path']for r in context['evidenceRefs']]
    for r in context['evidenceRefs']:assert pin(ROOT/r['path'])==r
   else:
    receipt=read(d/'result.json')
    assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    extra=[d/'result.json']
    for r in receipt['evidenceRefs']:
     assert pin(ROOT/r['path'])==r;extra.append(ROOT/r['path'])
   for p in extra:
    r=pin(p);assert r['path']not in pins or pins[r['path']]==r['sha256'];pins[r['path']]=r['sha256'];refs.append(p)
  memberships=read(BASE/FOLDERS['identity']/'complete-two-native-source-memberships.json')['rows']
  query=c.execute("SELECT r.cache_key,m,i.sheet,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_members membership USING(cache_key), LATERAL jsonb_array_elements(r.result->'models')m WHERE membership.run_id=%s AND m->>'modelId' IN ('B339682218601063C0','B339442219102063C0') ORDER BY m->>'modelId'",(NATIVE_RUN,)).fetchall()
  assert len(query)==len(memberships)==2
  assert [dict(cacheKey=k,model=m,sheet=s,resultSHA256=sha)for k,m,s,sha in query]==memberships
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==CURRENT
 data=load();identity_dir=BASE/FOLDERS['identity']
 row=read(identity_dir/'selection.json.gz')['rows'][0];context=read(identity_dir/'context.json.gz')['rows'][0]
 identity=verify_files(row,context,LOCAL/'unmocked-current-owned-identity')
 assert identity==data['identity'] and identity['passed']and identity['reasons']==[]
 support=read(identity_dir/'installed-support-entry.json');cats=read(identity_dir/'all-current-catalogues.json')['rows']
 current_catalogues=[ROOT/'3d-viewer'/url for url in read(manifest)['officialModelCatalogues']]
 assert [pin(p)for p in current_catalogues]==cats
 entries=[(p,e)for p in current_catalogues for e in read(p)['models']]
 assert len(entries)==len({e['uid']for p,e in entries})==6648
 assert not any(e['uid']==T for p,e in entries)
 matches=[(p,e)for p,e in entries if e['uid']==P];assert len(matches)==1
 p,e=matches[0];assert e==support['entry'] and pin(p)==support['catalogue'] and pin(p.parent/e['asset'])==support['asset']
 assert sorted(e['uid']for p,e in entries)==sorted(data['native_uids'])
 # Every current module, tile, source, asset and catalogue in the complete
 # fresh receipts was verified above and is rechecked after composition.
 role=compose(**data)
 entry=json.loads(json.dumps(row['candidate']['entry']))
 assert entry['uid']==T and entry['sha256']==role['sourceSHA256']
 assert 'supportDependencies'not in entry
 entry['supportDependencies']=[dict(uid=P,buildingCSUID=support['entry']['buildingCSUID'],state='installed',sourceSHA256=support['entry']['sha256'])]
 entry.update(placementReviewed=True,publicationApproved=False,priority='approved-private-stage-only')
 save(DOC/'complete-current-role.json.gz',role)
 save(DOC/'private-stage-entry.json',entry)
 save(DOC/'preserved-negative-history.json',dict(rawTwoResidualRimFailures=data['source']['rawTwoResidualRimFailuresRetained'],ordinaryNumericReasons=data['physical']['ordinaryNumericReasons'],runtimeConcerns=data['physical']['rawRuntimeConcerns'],complete85ProperCrossingContext=data['native']['completeCoupledOriginalPrimitiveContext'],sourceOwnedLowerJoinInterpretation=role['completeSourceOwnedLowerAssemblyJoin'],installedPodiumReapproved=False))
 assert manifest.read_bytes()==before and reservations.owns(lease)
 for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
 refs += [p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json']
 refs += [DOC/'complete-current-role.json.gz',DOC/'private-stage-entry.json',DOC/'preserved-negative-history.json']
 spec=importlib.util.spec_from_file_location('heya_complete_current_account_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.freeze(BATCH,'heya-unchanged-complete-current-typed-original-account-private-staging-ready-v1',refs,
  dict(uids=[T,P],scriptChecksPassed=True,stagingReady=True,installationApproved=False,newlyInstalled=0,completeOriginalTowerFaces=17910,completeAttachedTowerComponents=516,completeTerminalVisualComponents=58,sourceGeometryChanges=0,terrainGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,engineeredSupportClaim=False,installedPodiumReapproved=False))
 print(json.dumps(dict(jobId=result['jobId'],stagingReady=True,installationApproved=False)),flush=True)
def main():
 if '--validate'in sys.argv:return validation()
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists()
 data=read(BASE/FOLDERS['actual']/'capture-inputs.json.gz')
 resources=['building:'+f['uid']for f in data['completeCurrentForms']];assert len(resources)==14 and len(set(resources))==14
 claim=reservations.claim('heya-whole-current-role-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
 save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
