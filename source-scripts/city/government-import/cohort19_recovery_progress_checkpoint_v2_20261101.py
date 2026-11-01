"""Read back completed XL source recovery jobs and preserve actionable outcomes.

No approval, source editing, optimisation, publication or terminal classification.
"""
import sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-cohort19-recovery-progress-v2-20261101'
LOCAL=HERE/'local'/BATCH
PREFIX='government-xl-cohort19-'

def owned():
    assert reservations.owns(read(LOCAL/'reservation.json'))
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];records=[]
    for folder in sorted(BASE.glob(PREFIX+'*')):
        p=folder/'result.json'
        if folder.name==BATCH or not p.is_file():continue
        r=read(p);assert r['batch']==folder.name
        assert not r.get('installationApproved',False) and not r.get('publication',False)
        assert r.get('sourceGeometryChanges',0)==0
        records.append(dict(batch=folder.name,jobId=r['jobId'],result=r));refs.append(p)
    with connect()as db:
        db.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        rows={r[0]:(r[1],r[2])for r in db.execute('SELECT id,status,result FROM astra_modelling.jobs WHERE id=ANY(%s)',([r['jobId']for r in records],)).fetchall()}
        assert records and all(rows[r['jobId']]==('complete',r['result'])for r in records)
    def take(batch,name='summary.json'):
        folder=BASE/batch;receipt=read(folder/'result.json');p=folder/name
        assert any(r['jobId']==receipt['jobId']for r in records)
        assert dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))in receipt['evidenceRefs']
        refs.append(p);return read(p)
    runtime=PREFIX+'current-original-checks-v1-20261101-runtime'
    selection=take(runtime,'selection.json.gz');physical=take(runtime)
    identity=take(PREFIX+'current-original-checks-v1-20261101-identity')
    scope=take(PREFIX+'complete-source-scope-v1-20261101')
    current=ROOT/'3d-viewer/city/data/manifest.json';assert digest(current.read_bytes())==selection['manifestSHA256']==scope['currentManifestSHA256'];refs.append(current)
    sources={r['uid']:r for r in selection['rows']};assert len(sources)==19
    ids={r['uid']:r for r in identity['rows']};earth={r['uid']:r for r in physical['rows']};scopes={r['uid']:r for r in scope['rows']}
    assert set(sources)==set(ids)==set(earth)==set(scopes)
    outcomes=[]
    for uid,source in sources.items():
        assert ids[uid]['sourceSHA256']==scopes[uid]['sourceSHA256']==source['sourceSHA256']
        p=ROOT/source['candidate']['path'];assert digest(p.read_bytes())==source['sourceSHA256'];refs.append(p)
        native=[r['uid']for r in scopes[uid]['nearbyNativeActors']]
        reason=('identity and placement investigation' if not ids[uid]['passed'] else 'source terrain/foundation recovery' if earth[uid]['fullyBuriedTriangles'] else 'installed native joint qualification' if native else 'original companion/support acquisition and qualification')
        outcomes.append(dict(uid=uid,sourceSHA256=source['sourceSHA256'],identity=ids[uid],actualEarth=earth[uid],nativeCandidates=native,humanStatus='In process',requiredResource='Code and compute; no new human decision or AI geometry modelling requested',nextAction=reason,installed=False,permanentRejection=False))
    browser=PREFIX+'aqua-installed-supported-preview-v1-20261101'
    # Preview has a frozen result and per-width reports, not summary.json.
    assert any(r['batch']==browser for r in records)
    images=[]
    for width in [1280,390]:
        report=take(browser,str(width)+'/staged-browser.json');assert report['passed']and not report['errors']
        for field in ['views','retainedNativeOwnViews']:
            views=[r for r in report[field]if r.get('file')];assert len(views)==2
            for view in views:
                p=BASE/browser/str(width)/view['file'];receipt=read(BASE/browser/'result.json')
                assert dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))in receipt['evidenceRefs']
                assert view['fullyFramed']and view['active']and view['visible']and not view['fallbackFaces']
                refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),width=width,time=view['time'],uid=view['uid']))
    assert len(images)==8
    result=dict(uids=sorted(sources),rows=outcomes,completedProofJobs=len(records),allNeonResultsReadBack=True,identityPassed=sum(r['passed']for r in ids.values()),identityFailed=sum(not r['passed']for r in ids.values()),identityCleanWithoutEarthBurial=sum(ids[u]['passed']and not earth[u]['fullyBuriedTriangles']for u in sources),aquaDesktopMobilePreviewPassed=True,imagesActuallyOpenedByRoot=images,visualAcceptance=False,physicalAcceptance=False,installationApproved=False,publication=False,newlyInstalled=0,newlyTerminal=0,sourceGeometryChanges=0,sourcePoseChanges=0,scriptExternalAICalls=0,currentManifestSHA256=selection['manifestSHA256'],qualification=__doc__+' ROOT opened all eight exact Aqua source/retained day/night desktop/mobile exports. Diagnostic image inspection and positive contact paths do not grant installation acceptance. Whole fixed521XL goal, both NULL source keys and other unfinished sources remain unchanged.')
    save(out/'summary.json',result);save(out/'completed-proof-index.json',dict(rows=[dict(batch=r['batch'],jobId=r['jobId'])for r in records]));refs.append(out/'completed-proof-index.json')
    module('cohort19_progress_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-xl-original-recovery-progress-and-exact-diagnostic-image-inspection',list(dict.fromkeys(refs)),result)
    print(dict(completedProofJobs=len(records),identityPassed=result['identityPassed'],newlyInstalled=0),flush=True)

if __name__=='__main__':
    if '--owned'in sys.argv:owned()
    else:
        assert not LOCAL.exists();c=reservations.claim('cohort19-proof-checkpoint-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],c
        execute_reserved(c['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
