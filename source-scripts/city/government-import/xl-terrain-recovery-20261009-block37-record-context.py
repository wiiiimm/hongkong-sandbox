"""Fence complete original wall context in Neon, retaining strict failures."""
import json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row

BATCH='xl-terrain-recovery-20261009-block37-wall-context'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LEASE=Path('/tmp/xl-terrain-recovery-20261009-228547-lease.json')


def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}


def main():
    assert not (DOC/'result.json').exists(),'Fresh immutable result required'
    lease=read(LEASE);assert reservations.owns(lease)
    row=read(DOC/'diagnostic.json.gz');coverage=read(DOC/'coverage-v2.json.gz')
    shells=read(DOC/'shell-self-intersections.json.gz');separation=read(DOC/'buried-face-separation.json')
    assert row['uid']=='landsd/228547:0' and row['sourceFaces']==13914
    assert coverage['wholeSourceUncoveredFaces']==coverage['affectedUncoveredFaces']==0
    assert shells['allSelfIntersectionFree'] and len(shells['shells'])==25
    assert separation['sampledBuriedFacesExamined']==224 and separation['noOtherComponentIntersections']
    paths=[Path(__file__),HERE/'original_face_ground_crossing_20261009.py',
        HERE/'original_face_ground_crossing_v2_20261009.py',HERE/'test_original_face_ground_crossing_20261009.py',
        HERE/'test_original_face_ground_crossing_v2_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',
        HERE/'test_exact_original_shell_intersections_20261009.py',
        *[HERE/('xl-terrain-recovery-20261009-block37-'+suffix+'.py') for suffix in
          ['wall-context','coverage-v2','shell-context','buried-separation']],
        *[DOC/name for name in ['diagnostic.json.gz','coverage-v2.json.gz','shell-self-intersections.json.gz',
          'buried-face-separation.json','README.md','coverage-fixture.json','render-inputs.json',
          'captures/render.json','captures/228547-0.png']]]
    refs=[ref(p) for p in paths]+row['evidenceRefs']
    refs=list({r['path']:r for r in refs}.values())
    stage='original-whole-face-wall-terrain-context-v1'
    payload={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'evidenceRefs':refs}
    jid=jobs.enqueue(BATCH,stage,payload)
    job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
    result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'wholeSourceFaces':13914,
        'wholeOriginalTerrainProjectionCovered':True,'wholeSourceUpwardMinimumGapM':row['wholeSourceUpwardMinimumGapM'],
        'continuousOutsideWallMinimumGapM':row['outsideMinimumGapM'],'outsideAffectedWallFaces':857,
        'outsideAffectedExactlyVerticalFaces':829,'affectedUpwardFaces':0,'allAffectedWallsExposedWitness':True,
        'closedCrossingComponents':25,'closedComponentFaces':2300,
        'withinComponentExactPairsChecked':sum(s['trianglePairsChecked'] for s in shells['shells']),
        'allClosedComponentsSelfIntersectionFree':True,'sampledBuriedFacesWithNoOtherOriginalComponentOverlap':224,
        'foreignSceneInteractionsCertified':False,'continuousBurialMembershipCertified':False,
        'providerOpenBottomWallRoleEstablished':False,'sourceGeometryChanges':0,'newlyInstalled':0,
        'publication':False,'installationApproved':False,'modelGeometryAI':False,
        'sourceEvidenceInterpretationUsedAI':True,'originalStrictFailures':row['rawStrictFailures'],
        'nextStep':'Inspect unchanged original source hierarchy/materials and provider modelling specifications to establish authored exterior wall/common-base semantics; then review a source-specific typed contract preserving every independent identity, support, roof, neighbour and runtime gate.',
        'qualification':'New whole-source geometry and native-pose capture context only. Raw strict failures and historical terrain bindings retained; no burial waiver or installation credit.'}
    try:
        with connect() as c:
            c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
            assert reservations._current(c,lease)
            for item in refs:assert ref(ROOT/item['path'])==item
            assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True})
        print(json.dumps({'jobId':jid,'wholeFaces':13914,'neonVerified':True,'newlyInstalled':0}),flush=True)
    except Exception as exc:
        jobs.finish(job,error=str(exc));raise
    finally:assert reservations.release(lease)['ok']


if __name__=='__main__':main()
