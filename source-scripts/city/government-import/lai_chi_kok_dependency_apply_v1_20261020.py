"""Publish only seven proven installed-dependency labels; preserve source assets."""
from pathlib import Path
import subprocess, uuid
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from publication_lock import locked_publication
from verified_installed_dependency_metadata_20261010 import verify

BASE=ROOT/'docs/astra-city/government-import'
PLAN=BASE/'government-xl-lai-chi-kok-dependency-plan-v1-20261020'
BATCH='government-xl-lai-chi-kok-dependency-applied-v1-20261020'
DOC=BASE/BATCH

def ref(p):
    return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def main():
    assert not DOC.exists(), 'Inspect previous publication before retry'
    assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='codex/astra-hong-kong-city'
    plan=read(PLAN/'proposal.json');receipt=read(PLAN/'result.json')
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    for e in receipt['evidenceRefs']:
        assert ref(ROOT/e['path'])==e,e['path']
    cat=ROOT/plan['cataloguePath'];before=cat.read_bytes();after=(PLAN/'proposed-catalogue.json').read_bytes()
    assert digest(before)==plan['catalogueBeforeSHA256']
    assert read(cat)==plan['before'] and read(PLAN/'proposed-catalogue.json')==plan['after']
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
    pointer_ref=ref(pointer);uids=sorted(e['uid'] for e in plan['before']['models'])
    def validate():
        assert ref(manifest)['sha256']==plan['manifestSHA256']
        assert ref(pointer)==pointer_ref and read(pointer)['snapshotId']==plan['snapshotId']
        reviews={};assets={};forms={};asset_paths=[]
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            for e in plan['before']['models']:
                reviews[e['uid']]=db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(plan['snapshotId'],e['uid'])).fetchone()
                p=cat.parent/e['asset'];raw=p.read_bytes();asset_paths.append(p)
                assets[e['uid']]=dict(sha256=digest(raw),bytes=len(raw))
        for tile in read(manifest)['tiles']:
            for b in read(ROOT/'3d-viewer'/tile['url'])['buildings']:
                if b['uid'] in uids:
                    assert b['uid'] not in forms
                    forms[b['uid']]=b
            if len(forms)==len(uids):break
        assert forms=={b['uid']:b for b in plan['forms']}
        proof=verify({plan['cataloguePath']:plan['before']},{plan['cataloguePath']:plan['after']},reviews,forms,assets)
        assert proof['changes']==plan['changes'] and len(proof['changes'])==7
        found={}
        for url in read(manifest)['officialModelCatalogues']:
            for e in read(ROOT/'3d-viewer'/url)['models']:
                if e['uid'] in uids:
                    assert e['uid'] not in found
                    found[e['uid']]=e
        assert found=={e['uid']:e for e in read(cat)['models']}
        return asset_paths
    validate()
    claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=BATCH,ttl=1800)
    assert claim['ok'];lease=claim['reservation'];committed=False
    try:
        with locked_publication(ROOT):
            assert reservations.owns(lease) and cat.read_bytes()==before
            assets=validate()
            archive=DOC/'before'/plan['cataloguePath'];archive.parent.mkdir(parents=True,exist_ok=True);archive.write_bytes(before)
            aliases=[dict(path=plan['cataloguePath'],sha256=digest(before),archivePath=str(archive.relative_to(ROOT)))]
            save(DOC/'plan-binding.json',dict(proposal=ref(PLAN/'proposal.json'),proposalNeonJob=receipt['jobId'],aliases=aliases))
            try:
                temp=cat.with_name('catalogue.metadata-tmp.json');temp.write_bytes(after);temp.replace(cat)
                assert cat.read_bytes()==after;validate()
                payload=dict(uids=uids,proposal=ref(PLAN/'proposal.json'),aliases=aliases)
                stage='seven-already-installed-dependency-labels'
                jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800)
                assert job and job['id']==jid
                result=dict(**payload,jobId=jid,batch=BATCH,stage=stage,metadataCorrectionApplied=True,
                            dependencyChanges=7,catalogueChanges=1,newlyInstalled=0,sourceGeometryChanges=0,
                            modelGeometryChanges=0,terrainGeometryChanges=0,installationApproved=False,
                            publication=False,runtimeMetadataPublished=True,reviewsUnchanged=True,
                            freshDownstreamCapturesRequired=True,aiGeometryModelling=False,
                            snapshotId=plan['snapshotId'],manifestSHA256=plan['manifestSHA256'])
                paths=[Path(__file__),HERE/'verified_installed_dependency_metadata_20261010.py',
                       PLAN/'result.json',PLAN/'proposal.json',PLAN/'loader-check.json',
                       DOC/'plan-binding.json',archive,cat,manifest,pointer,*assets]
                result['evidenceRefs']=[ref(p) for p in paths]
                with connect() as db:
                    db.row_factory=dict_row
                    db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
                    assert reservations._current(db,lease)
                    for e in result['evidenceRefs']:assert ref(ROOT/e['path'])==e
                    assert db.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
                committed=True
                with connect() as db:
                    db.execute('SET TRANSACTION READ ONLY')
                    assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
                save(DOC/'result.json',result);save(DOC/'neon-sync.json',dict(jobId=jid,resultVerified=True))
                print(dict(jobId=jid,dependencyChanges=7,newlyInstalled=0),flush=True)
            except BaseException:
                if not committed:
                    cat.write_bytes(before)
                    save(DOC/'failure-rollback.json',dict(oldCatalogueRestored=cat.read_bytes()==before))
                raise
    finally:
        assert reservations.release(lease)['ok']

if __name__=='__main__':main()
