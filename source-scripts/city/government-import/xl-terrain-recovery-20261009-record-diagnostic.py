"""Fenced durable Neon checkpoint for new diagnostic context; no approval changes."""
import json
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row

BATCH='xl-terrain-recovery-20261009-shell-cohort'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
STAGE='below-grade-shell-topology-diagnostic-v1'


def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}


def main():
    assert not (DOC/'result.json').exists(),'Fresh immutable checkpoint required'
    diagnostic=read(DOC/'diagnostic.json.gz')
    scope_path=ROOT/'docs/astra-city/government-import/government-xl-current-320-blocker-families-20261009/dispositions.json.gz'
    scope=read(scope_path)
    assert diagnostic['sourceScope']==173 and diagnostic['pairedHistoricalGeometry']==119
    assert diagnostic['nonzeroBuriedGeometry']==13 and diagnostic['geometricBelowGradeShellLeads']==2
    source_rows=[]
    for row in diagnostic['rows']:
        if not row['foundationSummary']['foundation']['fullyBuriedTriangles']:continue
        if row['uid']=='landsd/177604:0':
            next_step='Prove the 24-face original closed column shell has no self-intersections and only a downward underside is hidden by source terrain. Establish provider/source component context for a source-specific below-grade contract. Independently resolve Hoi Yu House177605 support regression. Preserve raw original failure and require complete fresh source/runtime/neighbour/browser/publication checks before acceptance.'
        elif row['uid']=='landsd/228547:0':
            next_step='Investigate the remaining original faces outside the25closed shells with clearance-1.0258539455m; closed downward shells alone cannot resolve this independent source penetration. Establish source component context before any below-grade contract.'
        else:
            next_step='Inspect the recorded original buried upward faces or nonclosed/nonoutward shell components. Resolve exact source/surface/component mismatch, not a general burial waiver; full acceptance remains required.'
        source_rows.append({'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],
            'classification':row['classification'],'geometricBelowGradeShellLead':row.get('geometricBelowGradeShellLead',False),
            'outsideShellMinimumGapM':row.get('outsideShellMinimumGapM'),
            'buriedTriangles':row['foundationSummary']['foundation']['fullyBuriedTriangles'],
            'buriedUpwardTriangles':row['foundationSummary']['foundation']['fullyBuriedUpwardTriangles'],
            'originalStrictFailures':row['currentReasons'],'nextStep':next_step,
            'historicalEvidenceRefs':row['historicalEvidenceRefs'],
            'installationApproved':False,'permanentRejection':False})
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes())==scope['manifestSHA256']
    refs=[ref(p) for p in [Path(__file__),HERE/'xl-terrain-recovery-20261009-shell-cohort.py',
        HERE/'original_shell_diagnostic_20261009.py',HERE/'test_original_shell_diagnostic_20261009.py',
        HERE/'exact_terrain_contact_20261009.py',HERE/'test_exact_terrain_contact_20261009.py',
        DOC/'diagnostic.json.gz',DOC/'README.md',scope_path,manifest]]
    for row in diagnostic['rows']:
        refs += row['historicalEvidenceRefs']
        refs += row.get('compoundOriginalSupport',{}).get('evidenceRefs',[])
    refs=list({r['path']:r for r in refs}.values())
    claim=reservations.claim('codex-xl-terrain-shell-context-'+str(uuid.uuid4()),
        ['source-context:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'],claim
    lease=claim['reservation'];job=None
    try:
        payload={'sourceScope':173,'evidenceRefs':refs,'sourceSHA256s':{r['uid']:r['sourceSHA256'] for r in source_rows}}
        jid=jobs.enqueue(BATCH,STAGE,payload);job=jobs.claim(BATCH,lease['owner'],[STAGE],lease_seconds=1800);assert job and job['id']==jid
        result={**payload,'jobId':jid,'batch':BATCH,'stage':STAGE,'rows':source_rows,
                'pairedHistoricalGeometry':119,'zeroWhollyBuriedInPairedGeometry':106,
                'newShellDiagnoses':13,'geometricBelowGradeShellLeads':2,'otherShellDiagnoses':11,
                'unpairedCachedDrawnGroundGeometry':54,'manifestSHA256':scope['manifestSHA256'],
                'snapshotId':scope['snapshotId'],'newlyInstalled':0,'publication':False,
                'modelGeometryChanges':0,'aiGeometryModelling':False,'scriptExternalAICalls':0,
                'sourceEvidenceInterpretationUsedAI':True,'supportsUndergroundAcceptance':False,
                'qualification':'Fresh exact source-shell topology context on historical terrain, not another unchanged physical retry. No model-review, source transform, suppression, tolerance, runtime or installation decision is changed. Closed shells are leads, not proof of underground authorisation or self-intersection freedom.'}
        with connect() as c:
            c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
            for item in refs:assert ref(ROOT/item['path'])==item
            assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True})
        print(json.dumps({'jobId':jid,'neonVerified':True,'newlyInstalled':0,'geometricLeads':2}),flush=True)
    except Exception as e:
        if job:jobs.finish(job,error=str(e))
        raise
    finally:assert reservations.release(lease)['ok']


if __name__=='__main__':main()
