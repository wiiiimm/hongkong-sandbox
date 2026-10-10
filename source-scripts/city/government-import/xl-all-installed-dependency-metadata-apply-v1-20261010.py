"""Apply only frozen metadata corrections between already installed actors.

No geometry, root, review, identity, terrain or installation acceptance. Exact
historical bytes are archived. Uncommitted mutation failures restore all files.
"""
import copy
import subprocess
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from publication_lock import locked_publication
from verified_installed_dependency_metadata_20261010 import verify

BATCH='government-xl-all-installed-dependency-metadata-applied-v1-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PLAN=DOC.parent/'government-xl-all-installed-dependency-metadata-proposal-v2-20261010'
MANIFEST='3a2f56f7980954ff3493aba5e8a015ca79153f81da55bb580e26bf5b2cdb2ee8'
SNAPSHOT='ee1a41d61d2de0fe'

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def review_check(actors):
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  rows={u:(s,h) for u,s,h in c.execute('SELECT uid,review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(SNAPSHOT,[a['uid'] for a in actors])).fetchall()}
 assert rows=={a['uid']:('installed-verified',a['entry']['sha256']) for a in actors}
 return rows

def asset_check(actors):
 for a in actors:
  raw=(ROOT/a['asset']['path']).read_bytes()
  assert digest(raw)==a['entry']['sha256']==a['asset']['sha256']
  assert len(raw)==a['assetBytes']==a['entry']['bytes']

def inventory(manifest):
 cats={};entries={};forms={};tiles=[]
 for url in manifest['officialModelCatalogues']:
  path='3d-viewer/'+url;cat=read(ROOT/path);cats[path]=cat
  for e in cat['models']:
   assert e['uid'] not in entries;entries[e['uid']]=e
 for t in manifest['tiles']:
  p=ROOT/'3d-viewer'/t['url'];tiles.append(ref(p))
  for b in read(p)['buildings']:
   assert b['uid'] not in forms;forms[b['uid']]=b
 return cats,entries,forms,tiles

def main():
 assert not DOC.exists(),'Fresh named attempt required; inspect any earlier receipt'
 assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='codex/astra-hong-kong-city'
 mp=ROOT/'3d-viewer/city/data/manifest.json';pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
 assert ref(mp)['sha256']==MANIFEST and read(pointer)['snapshotId']==SNAPSHOT
 pointer_ref=ref(pointer);packet=read(PLAN/'proposal.json.gz');receipt=read(PLAN/'result.json')
 assert receipt['jobId']=='dbe9e4691c811d6924d7d8077bb9ceb8e62f24fd3f2ff34ae29c904e375fea6c'
 assert packet['manifestSHA256']==MANIFEST and packet['snapshotId']==SNAPSHOT
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 old_test=HERE/'test_verified_installed_dependency_metadata_20261010.py';archive_test=HERE/'archived_verified_installed_dependency_metadata_tests_v1_20261010.py'
 pins=[r for r in receipt['evidenceRefs'] if r['path']==str(old_test.relative_to(ROOT))];assert len(pins)==1 and ref(archive_test)['sha256']==pins[0]['sha256']
 aliases=[dict(path=pins[0]['path'],sha256=pins[0]['sha256'],archivePath=str(archive_test.relative_to(ROOT)))]
 for r in receipt['evidenceRefs']:
  p=archive_test if r==pins[0] else ROOT/r['path'];assert digest(p.read_bytes())==r['sha256'],r
 actors=packet['actors'];changed=packet['changedCatalogues'];assert len(actors)==254 and len(changed)==28
 cats,entries,forms,tiles=inventory(read(mp));before_cats=copy.deepcopy(cats)
 for a in actors:assert entries[a['uid']]==a['entry'] and forms[a['uid']]==a['currentViewer']
 assert {p:cats[p] for p in packet['beforeCatalogues']}==packet['beforeCatalogues']
 assets={a['uid']:dict(sha256=a['asset']['sha256'],bytes=a['assetBytes']) for a in actors};reviews=review_check(actors);asset_check(actors)
 proof=verify(packet['beforeCatalogues'],packet['afterCatalogues'],reviews,forms,assets)
 key=lambda r:(r['catalogue'],r['uid'],r['dependencyIndex'])
 assert sorted(proof['changes'],key=key)==sorted(packet['changes'],key=key) and len(proof['changes'])==210
 assert len({r['uid'] for r in proof['changes']})==206 and len(proof['retainedRelations'])==27
 before={p:(ROOT/p).read_bytes() for p in changed};after={}
 for i,p in enumerate(changed):
  path=PLAN/('proposed-'+str(i)+'.json');assert read(path)==packet['afterCatalogues'][p];after[p]=path.read_bytes()
 assert {p for p in packet['beforeCatalogues'] if packet['beforeCatalogues'][p]!=packet['afterCatalogues'][p]}==set(changed)
 # Independent tests are required before entering the publication lock.
 check=subprocess.run(['/tmp/astra-city-venv/bin/python','-m','unittest','test_verified_installed_dependency_metadata_v2_20261010'],cwd=HERE,capture_output=True,text=True)
 assert check.returncode==0,check.stdout+check.stderr
 claim=reservations.claim('codex-all-installed-metadata-'+str(uuid.uuid4()),['building:'+a['uid'] for a in sorted(actors,key=lambda a:a['uid'])],batch=BATCH,ttl=1800)
 assert claim['ok'],claim
 lease=claim['reservation'];committed=False
 try:
  with locked_publication(ROOT):
   assert reservations.owns(lease) and ref(mp)['sha256']==MANIFEST and ref(pointer)==pointer_ref
   current,_,current_forms,current_tiles=inventory(read(mp));assert current==before_cats and current_tiles==tiles
   for a in actors:assert current_forms[a['uid']]==a['currentViewer']
   assert review_check(actors)==reviews;asset_check(actors)
   for p in changed:
    assert (ROOT/p).read_bytes()==before[p];archive=DOC/'before'/p;archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(before[p]);assert archive.read_bytes()==before[p]
    aliases.append(dict(path=p,sha256=digest(before[p]),archivePath=str(archive.relative_to(ROOT))))
   save(DOC/'plan-binding.json',dict(proposal=ref(PLAN/'proposal.json.gz'),proposalNeonJob=receipt['jobId'],aliases=aliases,manifestSHA256=MANIFEST,snapshotId=SNAPSHOT))
   save(DOC/'tests-before.json',dict(passed=True,command=['python','-m','unittest','test_verified_installed_dependency_metadata_v2_20261010'],stdout=check.stdout,stderr=check.stderr,qualification='Original frozen v1 test had20pass/1failure from catalogue iteration order after JSON reload. Exact original test archived; v2 compares full records by catalogue/UID/index; no production logic changed.'))
   try:
    for p in changed:
     tmp=(ROOT/p).with_name('catalogue.metadata-tmp.json');tmp.write_bytes(after[p]);tmp.replace(ROOT/p)
    actual,now_entries,now_forms,now_tiles=inventory(read(mp));expected=copy.deepcopy(before_cats);expected.update(packet['afterCatalogues']);assert actual==expected and now_tiles==tiles
    for a in actors:assert now_forms[a['uid']]==a['currentViewer']
    verify({p:before_cats[p] for p in packet['beforeCatalogues']},{p:actual[p] for p in packet['afterCatalogues']},reviews,now_forms,assets)
    assert review_check(actors)==reviews;asset_check(actors)
    assert ref(mp)['sha256']==MANIFEST and ref(pointer)==pointer_ref and reservations.owns(lease)
    payload=dict(uids=sorted(a['uid'] for a in actors),proposal=ref(PLAN/'proposal.json.gz'),aliases=aliases)
    stage='exact-already-installed-support-dependency-metadata-correction-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
    result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'metadataCorrectionApplied':True,'catalogueChanges':28,'dependencyChanges':210,'ownerEntries':206,'missingStableCSUIDsAdded':108,'retainedFallbackOrLegacyRelations':27,'sourceGeometryChanges':0,'modelGeometryChanges':0,'terrainGeometryChanges':0,'newlyInstalled':0,'reviewStateChanges':0,'nativeReacceptance':False,'physicalAccepted':False,'installationApproved':False,'publication':False,'runtimeMetadataPublished':True,'aiGeometryModelling':False,'scriptExternalAICalls':0,'snapshotId':SNAPSHOT,'manifestSHA256':MANIFEST,'currentCatalogueRefs':[ref(ROOT/p) for p in changed],'originalActorAssets':[a['asset'] for a in actors],'completeAssetBytesUnchanged':True,'reviewsUnchanged':True,'freshDownstreamCapturesRequired':True,'qualification':'Only existing candidate-state dependencies between exact unique already installed current source actors repaired. All original source bytes, placement fields, edge directions, fallback/legacy relations and reviewed states retained. No new installation, identity or terrain acceptance.'}
    paths=[Path(__file__),HERE/'verified_installed_dependency_metadata_20261010.py',old_test,archive_test,HERE/'test_verified_installed_dependency_metadata_v2_20261010.py',PLAN/'result.json',PLAN/'proposal.json.gz',DOC/'plan-binding.json',DOC/'tests-before.json',mp,pointer,*[ROOT/p for p in changed],*[ROOT/a['asset']['path'] for a in actors],*[ROOT/a['archivePath'] for a in aliases]]
    result['evidenceRefs']=[ref(p) for p in sorted(set(paths))]
    with connect() as c:
     c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
     for r in result['evidenceRefs']:assert ref(ROOT/r['path'])==r
     assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
    committed=True
    with connect() as c:
     c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
    save(DOC/'result.json',result);save(DOC/'neon-sync.json',dict(jobId=jid,resultVerified=True));print(dict(jobId=jid,dependencyChanges=210,newlyInstalled=0),flush=True)
   except BaseException:
    if not committed:
     for p in changed:(ROOT/p).write_bytes(before[p])
     save(DOC/'failure-rollback.json',dict(oldCataloguesRestored=all((ROOT/p).read_bytes()==before[p] for p in changed),newlyInstalled=0))
    raise
 finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()
