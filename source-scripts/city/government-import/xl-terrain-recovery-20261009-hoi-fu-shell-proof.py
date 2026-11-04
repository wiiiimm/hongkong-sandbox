"""Fenced exact rational self-intersection context for one original source shell."""
import json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from exact_original_shell_intersections_20261009 import shell_self_intersections

BATCH='xl-terrain-recovery-20261009-hoi-fu-shell-proof'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
SCOPE=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-shell-cohort/diagnostic.json.gz'
LEASE=Path('/tmp/xl-terrain-recovery-20261009-hoi-fu-lease.json')
UID='landsd/177604:0'


def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}


def main():
    assert not (DOC/'result.json').exists(),'Fresh immutable source proof required'
    lease=read(LEASE);assert reservations.owns(lease)
    row=next(r for r in read(SCOPE)['rows'] if r['uid']==UID)
    assert row['sourceSHA256']=='bf710f3c82832b8b82b85571bbda7904416ea8743a081e6aa3de321915a21122'
    assert row['geometricBelowGradeShellLead'] and len(row['shells'])==1
    shell=row['shells'][0];assert shell['triangles']==24 and shell['outwardPositiveVolume']
    geometry_path=ROOT/row['runtimeGeometry'];geometry=next(r for r in read(geometry_path)['rows'] if r['uid']==UID)
    assert geometry['sourceSHA256']==row['sourceSHA256']
    tri=np.asarray(geometry['position']).reshape(-1,3)[np.asarray(geometry['index']).reshape(-1,3)]
    assert len(tri)==14627 and len(shell['componentFaces'])==24
    proof=shell_self_intersections(tri[shell['componentFaces']].tolist())
    assert proof['trianglePairsChecked']==276 and proof['selfIntersectionFree']
    proof.update(uid=UID,sourceSHA256=row['sourceSHA256'],originalFaceIndices=shell['componentFaces'],
                 inputGeometry=ref(geometry_path),topologyDiagnostic=ref(SCOPE),originalSourcePreserved=True)
    assert proof==read(DOC/'self-intersection.json'),'Exact original proof differs'
    refs=[ref(p) for p in [Path(__file__),HERE/'exact_original_shell_intersections_20261009.py',
         HERE/'test_exact_original_shell_intersections_20261009.py',DOC/'self-intersection.json',
         DOC/'README.md',SCOPE,geometry_path]]
    refs+=row['historicalEvidenceRefs'];refs=list({r['path']:r for r in refs}.values())
    stage='exact-original-closed-shell-self-intersection-context-v1'
    payload={'uid':UID,'sourceSHA256':row['sourceSHA256'],'evidenceRefs':refs}
    jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
    result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'sourceFaces':24,
        'wholeSourceFaces':14627,'otherSourceMinimumClearanceM':row['outsideShellMinimumGapM'],
        'trianglePairsChecked':276,'legalSharedContacts':proof['legalSharedContacts'],
        'selfIntersectionFree':True,'originalShellClosedOutward':True,
        'buriedFaces':row['buriedFaces'],'buriedUpwardFaces':[],
        'sourceSamplesCrossGround':True,'providerBelowGradeClassification':None,
        'originalStrictFailures':row['currentReasons'],'sourceGeometryChanges':0,
        'newlyInstalled':0,'publication':False,'installationApproved':False,
        'modelGeometryAI':False,'sourceEvidenceInterpretationUsedAI':True,
        'nextStep':'Original Hoi Yu177605 interface and source-specific below-grade policy interpretation; complete fresh acceptance and source byte/pose/neighbour/browser checks remain required.',
        'qualification':'Exact geometric proof for one original24-face closed outward column-like shell only. It does not authorise a burial exception or establish provider basement semantics. All raw strict failures remain recorded.'}
    try:
        with connect() as c:
            c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
            for item in refs:assert ref(ROOT/item['path'])==item
            assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True})
        print(json.dumps({'jobId':jid,'selfIntersectionFree':True,'neonVerified':True,'newlyInstalled':0}),flush=True)
    except Exception as e:
        jobs.finish(job,error=str(e));raise
    finally:assert reservations.release(lease)['ok']


if __name__=='__main__':main()
