"""Root publisher: correct two proven installed dependency records, never geometry.

Archive exact historical catalogue/test bytes, retain all existing review states,
and make fresh downstream captures mandatory even if the manifest stays unchanged.
"""
import copy
import importlib.util
import json
import subprocess
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from publication_lock import locked_publication
from retained_installed_dependency_metadata_plan_20261010 import EXPECTED,corrected,verify
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding

BATCH='government-xl-retained-installed-dependency-metadata-applied-v1-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PLAN=ROOT/'docs/astra-city/government-import/government-xl-one-peking-retained-installed-dependency-metadata-plan-v2-20261010'
MANIFEST='3a2f56f7980954ff3493aba5e8a015ca79153f81da55bb580e26bf5b2cdb2ee8'
SNAPSHOT='ee1a41d61d2de0fe'
OLD_TEST='eef0ec49d6211da4d4090aad31012f024a6491f3cc65d253c358e8ea2f3ea437'
PROPOSED=['f97028226f0c17153bf00166516ef68190859dd1104d8e551cbd162bd419f92c','435383c711b88fdecaec30bfd0dc77af2fced5f48b1c9a4bf23b0d401d2e14aa']

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def reviews(actors):
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for a in actors:
            assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(SNAPSHOT,a['uid'])).fetchone()==('installed-verified',a['entry']['sha256'])

def source_check(actors):
    for a in actors:
        raw=(ROOT/a['asset']['path']).read_bytes()
        assert digest(raw)==a['asset']['sha256']==a['entry']['sha256'] and len(raw)==a['entry']['bytes']
        world=decode_original_world_triangles(raw)
        assert len(world)==a['completeOriginalFaces']==a['entry']['triangles']
        assert digest(world.tobytes())==a['originalWorldSHA256']
        assert source_stream_binding(raw)==a['completeSourceStreams']
        assert ref(ROOT/a['currentViewer']['tile']['path'])==a['currentViewer']['tile']

def main():
    assert not DOC.exists(),'Fresh named mutation required; inspect prior receipt before retry'
    assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='codex/astra-hong-kong-city'
    manifest=ROOT/'3d-viewer/city/data/manifest.json';pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
    assert ref(manifest)['sha256']==MANIFEST and read(pointer)['snapshotId']==SNAPSHOT
    pointer_before=ref(pointer);plan=read(PLAN/'proposal.json.gz');receipt=read(PLAN/'result.json')
    assert plan['manifestSHA256']==MANIFEST and plan['snapshotId']==SNAPSHOT
    assert receipt['jobId']=='1dc77d87e92ced06618f2e84ab7fafc5df92ac65e261c9590784085a30316d38'
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    archive_test=HERE/'archived_retained_installed_dependency_pre_correction_tests_20261010.py'
    assert ref(archive_test)['sha256']==OLD_TEST
    aliases=[dict(path=str((HERE/'test_retained_installed_dependency_metadata_plan_20261010.py').relative_to(ROOT)),sha256=OLD_TEST,archivePath=str(archive_test.relative_to(ROOT)))]
    for r in receipt['evidenceRefs']:
        p=ROOT/r['path']
        if r['path']==aliases[0]['path'] and r['sha256']==OLD_TEST:assert ref(archive_test)['sha256']==r['sha256']
        else:assert ref(p)==r,r
    actors=plan['actors'];assert len(actors)==4
    assert {a['uid'] for a in actors}==set(EXPECTED)|{d[0] for d in EXPECTED.values()}
    source_check(actors);reviews(actors)
    catpaths=sorted({a['catalogue']['path'] for a in actors});assert len(catpaths)==2
    before={p:(ROOT/p).read_bytes() for p in catpaths};after={}
    by_uid={a['uid']:a['entry'] for a in actors}
    for i,p in enumerate(catpaths):
        proposed=PLAN/('proposed-'+str(i)+'.json');assert ref(proposed)['sha256']==PROPOSED[i]
        current=read(ROOT/p);expected=copy.deepcopy(current)
        for e in expected['models']:
            if e['uid'] in EXPECTED:
                support=by_uid[EXPECTED[e['uid']][0]];updated=corrected(e,support)
                assert verify(e,updated,support);e.clear();e.update(updated)
        assert expected==read(proposed),'Unexpected catalogue difference'
        after[p]=proposed.read_bytes()
    # Prove each actor is still uniquely installed in the live catalogue inventory.
    found={}
    for url in read(manifest)['officialModelCatalogues']:
        for e in read(ROOT/'3d-viewer'/url)['models']:
            if e['uid'] in by_uid:
                assert e['uid'] not in found and e==by_uid[e['uid']];found[e['uid']]=e
    assert set(found)==set(by_uid)
    claim=reservations.claim('codex-retained-metadata-'+str(uuid.uuid4()),['building:'+u for u in sorted(by_uid)],batch=BATCH,ttl=1800)
    assert claim['ok'],claim
    lease=claim['reservation'];committed=False
    try:
        with locked_publication(ROOT):
            assert reservations.owns(lease) and ref(manifest)['sha256']==MANIFEST and ref(pointer)==pointer_before
            source_check(actors);reviews(actors)
            for p in catpaths:
                assert (ROOT/p).read_bytes()==before[p]
                archive=DOC/'before'/p;archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(before[p])
                assert archive.read_bytes()==before[p]
                aliases.append(dict(path=p,sha256=digest(before[p]),archivePath=str(archive.relative_to(ROOT))))
            save(DOC/'plan-binding.json',dict(proposal=ref(PLAN/'proposal.json.gz'),proposalNeonJob=receipt['jobId'],aliases=aliases,manifestSHA256=MANIFEST,snapshotId=SNAPSHOT))
            try:
                for p in catpaths:
                    tmp=(ROOT/p).with_name('catalogue.metadata-tmp.json');tmp.write_bytes(after[p]);tmp.replace(ROOT/p)
                assert all((ROOT/p).read_bytes()==after[p] for p in catpaths)
                current={}
                for url in read(manifest)['officialModelCatalogues']:
                    for e in read(ROOT/'3d-viewer'/url)['models']:
                        if e['uid'] in by_uid:assert e['uid'] not in current;current[e['uid']]=e
                for uid,e in current.items():
                    if uid in EXPECTED:assert verify(by_uid[uid],e,current[EXPECTED[uid][0]])
                    else:assert e==by_uid[uid]
                for uid in EXPECTED:
                    dep=current[uid]['supportDependencies'][0];support=current[dep['uid']]
                    assert dep['state']=='installed' and dep['csuid']==support['buildingCSUID']
                    if 'sha256' in dep:assert dep['sha256']==support['sha256']
                source_check(actors);reviews(actors)
                assert ref(manifest)['sha256']==MANIFEST and ref(pointer)==pointer_before
                payload=dict(uids=sorted(by_uid),proposal=ref(PLAN/'proposal.json.gz'),aliases=aliases)
                stage='exact-two-already-installed-dependency-metadata-correction-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800)
                assert job and job['id']==jid
                result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'metadataCorrectionApplied':True,'catalogueChanges':2,'dependencyChanges':2,'sourceGeometryChanges':0,'modelGeometryChanges':0,'terrainGeometryChanges':0,'newlyInstalled':0,'nativeReacceptance':False,'physicalAccepted':False,'installationApproved':False,'publication':False,'runtimeMetadataPublished':True,'aiGeometryModelling':False,'scriptExternalAICalls':0,'snapshotId':SNAPSHOT,'manifestSHA256':MANIFEST,'currentCatalogueRefs':[ref(ROOT/p) for p in catpaths],'originalActorAssets':[a['asset'] for a in actors],'originalFullWorldStreamsUnchanged':True,'reviewsUnchanged':True,'freshDownstreamCapturesRequired':True,'qualification':'Metadata-only repair of already installed exact UID/CSUID dependencies. Strict dependency loader guard unchanged. No source/terrain/role/root/identity acceptance or new model installation credit.'}
                result['evidenceRefs']=[ref(p) for p in [Path(__file__),HERE/'retained_installed_dependency_metadata_plan_20261010.py',HERE/'test_retained_installed_dependency_metadata_plan_20261010.py',HERE/'test_retained_installed_dependency_metadata_plan_v2_20261010.py',archive_test,HERE/'check-native-neighbours-multi-retained.mjs',PLAN/'result.json',PLAN/'proposal.json.gz',DOC/'plan-binding.json',manifest,pointer,*[ROOT/p for p in catpaths],*[ROOT/a['asset']['path'] for a in actors],*[ROOT/a['archivePath'] for a in aliases]]]
                with connect() as c:
                    c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
                    for r in result['evidenceRefs']:assert ref(ROOT/r['path'])==r
                    assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
                committed=True
                with connect() as c:
                    c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
                save(DOC/'result.json',result);save(DOC/'neon-sync.json',dict(jobId=jid,resultVerified=True))
                print(dict(jobId=jid,metadataCorrectionApplied=True,newlyInstalled=0,manifestSHA256=MANIFEST),flush=True)
            except BaseException:
                if not committed:
                    for p in catpaths:(ROOT/p).write_bytes(before[p])
                    save(DOC/'failure-rollback.json',dict(manifestSHA256=MANIFEST,oldCataloguesRestored=all((ROOT/p).read_bytes()==before[p] for p in catpaths),newlyInstalled=0))
                raise
    finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()
