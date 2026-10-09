"""Fence complete current Garden evidence and explicit remaining blockers in Neon."""
from pathlib import Path
import json,uuid
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row,NATIVE_RUN
BATCH='government-xl-garden-terrace-complete-current-support-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-garden-terrace-complete-original-physical-v2-20261009'
WALLS=ROOT/'docs/astra-city/government-import/government-xl-garden-terrace-complete-current-walls-20261009'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
    assert not (DOC/'result.json').exists()
    selected=read(PHYSICAL/'selection.json.gz');manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes())==selected['manifestSHA256']
    physical=read(PHYSICAL/'result.json');assert read(PHYSICAL/'neon-sync.json')['resultVerified']
    for item in physical['evidenceRefs']:assert ref(ROOT/item['path'])==item
    support=read(DOC/'diagnostic.json.gz');contacts=read(DOC/'exact-original-component-contacts.json.gz');walls=read(WALLS/'diagnostic.json.gz')
    for p,h in support['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
    for d in [contacts,walls]:
        for item in d['evidenceRefs']:assert ref(ROOT/item['path'])==item
    assert support['completeFaceAccounting'] and len(support['rows'])==259
    assert contacts['completeOriginalFaceAccounting'] and contacts['sourceFaces']==10670
    assert walls['wholeSourceUncoveredFaces']==0 and walls['allAffectedWallsHaveRoles'] and not walls['otherAffectedFaces']
    main=support['rows'][0]['interface'];assert main['strictLowRim']['missing']==0
    source_uids={r['uid'] for r in selected['rows']};scope={b['building']['uid'] for b in read(PHYSICAL/'neighbour-inputs.json.gz')['rows']}|source_uids
    parent=read(PHYSICAL/'nested-parent-routing.json')['parentURL'];scope.update(u for child in read(ROOT/'3d-viewer'/parent)['patches'] for u in child['meta'].get('targetUids',[]))
    claim=reservations.claim('codex-garden-record-'+str(uuid.uuid4()),[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope)]+['terrain-surface:'+parent],batch=BATCH,ttl=3600);assert claim['ok'],claim
    lease=json.loads(json.dumps(claim['reservation'],default=str));job=None
    try:
        refs=[ref(p) for p in sorted(DOC.rglob('*')) if p.is_file()]+[ref(p) for p in [WALLS/'diagnostic.json.gz',PHYSICAL/'result.json',PHYSICAL/'selection.json.gz',manifest,Path(__file__),HERE/'xl-garden-terrace-complete-current-support-20261009.mjs',HERE/'xl-garden-terrace-complete-current-render-20261009.mjs',HERE/'xl-garden-terrace-complete-current-walls-20261009.py']]
        refs+=contacts['evidenceRefs']+walls['evidenceRefs']+[{'path':p,'sha256':h} for p,h in support['inputHashes'].items()]
        refs=list({r['path']:r for r in refs}.values())
        stage='garden-current-complete-ground-components-wall-role-blockers-v1';payload={'uids':sorted(source_uids),'manifestSHA256':selected['manifestSHA256'],'sourceSHA256s':{r['uid']:r['sourceSHA256'] for r in selected['rows']},'evidenceRefs':refs};jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
        result={**payload,'jobId':jid,'batch':BATCH,'humanStatus':'held-unknown','requiresHumanDecision':False,'requiresAI':False,'requiresAIModelGeometry':False,'requiresMoreComputeOrSourceEvidence':True,'newlyInstalled':0,'publication':False,'sourceGeometryChanges':0,'scriptExternalAICalls':0,'sourceEvidenceInterpretationUsedAI':True,'reasons':['tower-complete-original-support-unresolved-110-samples','podium-original-wall-role-complete-foreign-interaction-not-yet-certified'],'wholeSourceFoundationsPassed':2,'runtimeLoaderChecksPassed':2,'currentNeighboursCheckedAndResolved':14,'currentTowerGroundMissingSamples':0,'mainTowerSupportSamples':main['samples'],'mainTowerStrictContacts':main['strictContacts'],'mainTowerUnresolvedSamples':len(main['unresolved']),'strictCompleteOriginalComponentAnchors':sum(r['interface']['passed'] for r in support['rows']),'completeTowerComponents':259,'podiumAll1418FacesGroundCovered':True,'podiumRawFailingWallFaces':walls['affectedWallFaces'],'podiumUpwardMinimumGapM':walls['upwardContinuousMinimumGapM'],'mainToPodiumExactContacts':len(contacts['mainToPodiumContacts']['contacts']),'mainToPodiumLargestContactSpanM':max(c['maximumSpanM'] for c in contacts['mainToPodiumContacts']['contacts']),'otherComponentsDirectContactingMain':sum(any(c['dimension']>0 for c in r['originalContact']['contacts']) for r in contacts['rows']),'qualification':'Complete fresh physical and component evidence only. Exact contacts and original wall-to-roof paths do not approve incomplete strict support or omit foreign interactions. Remaining parts without direct main-body contact may have transitive contacts; this checkpoint does not claim those parts are corrupt or permanently impossible. No model edits or acceptance-limit changes.','nextStep':'Use new full-ground/contact witnesses for positive authored envelope/support and complete foreign wall evidence; retain current models until all independent gates pass. Do not repeat unchanged partial-ground or exact family checks.'}
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
            for item in refs:assert ref(ROOT/item['path'])==item
            for r in selected['rows']:assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,r['native']['cacheKey'])).fetchone()['result_sha']==r['native']['resultSha']
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()[0]==result
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print({'jobId':jid,'neonVerified':True,'unresolvedSupport':len(main['unresolved'])},flush=True)
    except Exception as e:
        if job:jobs.finish(job,error=str(e))
        raise
    finally:reservations.release(lease)
if __name__=='__main__':main()
