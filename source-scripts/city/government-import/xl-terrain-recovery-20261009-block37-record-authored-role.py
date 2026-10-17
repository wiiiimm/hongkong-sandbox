"""Fence complete authored source role and failed current identity preflight."""
from pathlib import Path
import json
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row

BATCH='xl-terrain-recovery-20261009-block37-authored-role'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
CURRENT=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-block37-current-inputs-20261009'
LEASE='/tmp/xl-terrain-recovery-20261009-block37-authored-role-lease.json'

def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}

def main():
    assert not (DOC/'result.json').exists()
    lease=read(LEASE);assert reservations.heartbeat(lease)['ok']
    inventory=read(DOC/'inventory.json.gz');role=read(DOC/'role-context.json.gz');preflight=read(CURRENT/'indexed-preflight.json')
    assert inventory['allOriginalFacesAndComponentsPartitionedExactlyOnce'] and inventory['wholeSourceFaces']==13914
    assert inventory['allShaftInterfacesPass'] and inventory['allTerminalHighestVertexMembershipsPass']
    assert not preflight['canStartTerrainWork']
    refs=inventory['evidenceRefs']+role['evidenceRefs']+preflight['evidenceRefs']
    paths=[Path(__file__),DOC/'README.md',DOC/'role-context.json.gz',DOC/'inventory.json.gz',
        CURRENT/'check-selection.json.gz',CURRENT/'context.json.gz',CURRENT/'indexed-preflight.json',CURRENT/'block-j-excess-context.json.gz',
        HERE/'xl-terrain-recovery-20261009-block37-authored-role.py',HERE/'xl-terrain-recovery-20261009-block37-role-inventory.py',
        HERE/'xl-terrain-recovery-20261009-block37-current-preflight.py',
        *[HERE/(p+'.py') for p in ['authored_wall_roof_paths_20261009','test_authored_wall_roof_paths_20261009',
            'unchanged_open_exterior_paths_20261009','test_unchanged_open_exterior_paths_20261009',
            'exact_shell_context_accelerated_20261009','test_exact_shell_context_accelerated_20261009',
            'exact_closed_shell_point_20261009','test_exact_closed_shell_point_20261009']]]
    refs.extend(ref(p) for p in paths);refs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path'])
    stage='original-authored-open-exterior-shaft-context-v1'
    payload={'uid':inventory['uid'],'sourceSHA256':inventory['sourceSHA256'],'evidenceRefs':refs}
    jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
    result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'wholeSourceFaces':13914,'roleCounts':inventory['roleCounts'],
        'originalTriangleAttributesAndHierarchyPreserved':True,'originalOpenBodyOrientationConflictsPreserved':2,
        'allAffectedOpenWallsHaveRoofPaths':True,'all25ShaftsHaveOriginalRoofAndEmbeddedTerminalInterfaces':True,
        'currentIdentityPassed':False,'currentIdentityReasons':preflight['identity']['reasons'],
        'sourceExcessCoveredByUnrelatedFormsM2':preflight['identity']['freshCurrentIdentity']['sourceExcessCoveredByUnrelatedFormsM2'],
        'humanStatus':'held-unknown','heldReason':'Original source excess overlaps Block J; exact provider ownership/context investigation pending.',
        'sourceGeometryChanges':0,'newlyInstalled':0,'publication':False,'installationApproved':False,
        'requiresAI':False,'requiresHumanDecision':False,'sourceEvidenceInterpretationUsedAI':True,'modelGeometryAI':False,
        'nextStep':'Resolve exact Block J source ownership/context; then compose source-specific open-wall and closed-shaft contracts with fresh independent physical/runtime/neighbour/browser checks.'}
    try:
        with connect() as c:
            c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
            for item in refs:assert ref(ROOT/item['path'])==item
            assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True})
        print(json.dumps({'jobId':jid,'currentIdentityPassed':False,'neonVerified':True,'newlyInstalled':0}),flush=True)
    finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()
