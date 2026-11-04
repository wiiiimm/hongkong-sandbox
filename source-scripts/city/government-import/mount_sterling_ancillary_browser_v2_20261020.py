"""Private desktop/mobile review of eight unchanged originals, no publication."""
from pathlib import Path
import copy,json,os,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-mount-sterling-ancillary-browser-v2-20261020'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-mount-sterling-actual-render-attributes-v1-20261020'
TERRAIN=BASE/'government-xl-mount-sterling-terrain-validation-v2-20261020'
CURRENT=BASE/'government-xl-mount-sterling-neighbours-v2-20261020'
POD='landsd/289787:0'

def owned():
    lease=read(LOCAL/'reservation.json')
    assert reservations.owns(lease) and not DOC.exists()
    refs=[Path(__file__)];pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in [CAP,TERRAIN,CURRENT]:
            r=read(folder/'result.json')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
            refs.append(folder/'result.json')
            for e in r['evidenceRefs']:
                if folder==CAP and e['path']!=str((CAP/'input.json.gz').relative_to(ROOT)):continue
                assert e['path'] not in pins or pins[e['path']]==e['sha256']
                pins[e['path']]=e['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    source=read(CAP/'input.json.gz');rows=sorted(source['rows'],key=lambda r:r['uid']!=POD);uids=[r['uid'] for r in rows]
    assert len(set(uids))==8
    tile=ROOT/'3d-viewer/city/data/tiles/-2_-3.json';forms={b['uid']:b for b in read(tile)['buildings']};refs.append(tile)
    models=[];sha={r['uid']:r['entry']['sha256'] for r in rows}
    for r in rows:
        uid=r['uid'];e=copy.deepcopy(r['entry'])
        assert e['buildingCSUID']==forms[uid]['buildingCSUID'] and r['building']==forms[uid]
        p=ROOT/r['path'];raw=p.read_bytes();assert digest(raw)==sha[uid];refs.append(p)
        e.update(priority='landmark',proceduralWindows=False,publicationApproved=False,placementReviewed=False,
                 supportDependencies=[] if uid==POD else [dict(uid=POD,csuid=forms[POD]['buildingCSUID'],sha256=sha[POD],state='candidate')])
        e['asset']='assets/'+sha[uid]+'.glb.gz';dest=LOCAL/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);models.append(e)
    cat=dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',
             crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],
             models=models,counts=dict(packedModels=8))
    save(LOCAL/'catalogue.json',cat);save(LOCAL/'catalogue-index.json',dict(models=8,catalogues=['catalogue.json']))
    save(LOCAL/'source-forms.json',[forms[u] for u in uids])
    save(LOCAL/'validation-forms.json',{u:dict(building=forms[u],tile='city/data/tiles/-2_-3.json',tileSHA256=digest(tile.read_bytes())) for u in uids})
    candidates=read(TERRAIN/'terrain-candidates.json');save(DOC/'terrain-candidates.json',candidates)
    t=candidates[0]
    terrain=[dict(source=t['path'],destination='city/data/mount-sterling-private-v1.json',resolution=5,
                  area='Private Mount Sterling original source terrain',replaces=t['replaces'])]
    tool=HERE.parent/'building-batch/validate_candidates.mjs'
    cmd=['node',str(tool),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'validation-forms.json').relative_to(ROOT)),
         '--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))]
    with (DOC/'loader.log').open('w') as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=600)
    save(DOC/'loader-command.json',dict(command=cmd,exitCode=p.returncode))
    v=read(DOC/'validation.json');assert v['loaderAccepted']==8 and not v['exceptions'];refs.append(tool)
    config=dict(stage=str(LOCAL.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',
                terrain=terrain,browserUids=['landsd/163899:0'],failureTestUids=['landsd/163899:0'],
                jointUidsByModel={u:([POD] if u==POD else [POD,u]) for u in uids},
                fitBox=True,captureBoundsByModel={'landsd/163899:0':[[-2192.34,10,-5578.23],[-2133.28,75,-5526.77]]},captureDirectionByModel={'landsd/163899:0':[.2,1,-.2]})
    browser=HERE/'yoho_seven_acceptance_browser_v1_20261020.mjs';refs.append(browser)
    for width in [390,1280]:
        assert reservations.owns(lease)
        cfg={**config,'viewportWidths':[width],'doc':str((DOC/str(width)).relative_to(ROOT))+'/'}
        path=LOCAL/f'browser-config-{width}.json';save(path,cfg)
        cmd=['node',str(browser),'staged',str(path.relative_to(ROOT))]
        with (DOC/f'browser-{width}.log').open('w') as log:
            proc=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1800)
        save(DOC/f'command-{width}.json',dict(command=cmd,exitCode=proc.returncode));assert proc.returncode==0
        report=read(DOC/str(width)/'staged-browser.json')
        assert report['passed'] and len([v for v in report['views'] if 'time' in v])==2
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
    refs.extend(p for p in LOCAL.rglob('*') if p.is_file() and p.name!='reservation.json')
    assert reservations.owns(lease)
    module('mount_sterling_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'private-ancillary-unobstructed-mobile-desktop-runtime',list(dict.fromkeys(refs)),
        dict(uids=uids,installationApproved=False,visualAcceptance=False,privateSupportRelationsOnly=True))

def main():
    if '--owned' in sys.argv:return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600)
    assert claim['ok'];lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
    try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']

if __name__=='__main__':main()
