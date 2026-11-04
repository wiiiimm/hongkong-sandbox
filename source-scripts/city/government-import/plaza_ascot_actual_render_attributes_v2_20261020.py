"""Capture complete production-loader coordinates for eight unchanged originals."""
from pathlib import Path
import json,sys,uuid,subprocess
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-actual-render-attributes-v2-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-plaza-ascot-assembly-original-recovery-v1-20261020'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
    assert reservations.owns(read(LOCAL/'reservation.json')) and not DOC.exists();receipt=read(SRC/'result.json')
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']};p=SRC/'recovery.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
    rows=read(p)['rows'];assert len(rows)==19
    tile=ROOT/'3d-viewer/city/data/tiles/2_-7.json';forms={b['uid']:b for b in read(tile)['buildings']};inputs=[]
    for r in rows:
        assert digest((ROOT/r['assetPath']).read_bytes())==r['sourceSHA256']==pins[r['assetPath']]
        m=r['native']['model'];form=forms[r['uid']]
        if 'candidate' in m:entry=dict(m['candidate'])
        else:
            matches=[x for x in m['matching']['officialCandidates'] if x['objectId']==form['objectId'] and x['buildingCSUID']==form['buildingCSUID']];assert len(matches)==1
            entry=dict(m['asset'],uid=r['uid'],objectId=form['objectId'],buildingCSUID=form['buildingCSUID'],modelId=m['modelId'],triangles=m['triangles'],worldBounds=m['worldBounds'],label=form.get('name',''),placementReviewed=False,publicationApproved=False,identityReviewApproved=False,diagnosticOnly=True,sourceMatching=m['matching'])
        entry.update(rootTranslation=[-834500,0,816500],sourceTile=r['native']['sheet'],proceduralWindows=False)
        assert entry['uid']==r['uid'] and entry['sha256']==r['sourceSHA256'];inputs.append(dict(uid=r['uid'],entry=entry,building=forms[r['uid']],path=r['assetPath']))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';save(DOC/'input.json.gz',dict(currentManifest=ref(manifest),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/url) for url in read(manifest)['officialModelCatalogues']],evidenceRefs=[ref(p),ref(tile)],rows=inputs))
    tool=HERE/'plaza_ascot_actual_render_attributes_v1_20261020.mjs';subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
    output=read(DOC/'attributes.json.gz');assert output['startEndAllInputsVerified'];refs=[Path(__file__),tool,SRC/'result.json']
    for p,h in output['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    module('mount_sterling_attributes_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'nineteen-original-production-loader-coordinates',list(dict.fromkeys(refs)),dict(uids=[r['uid'] for r in rows],completeFaces=sum(r['native']['model']['triangles'] for r in rows),installationApproved=False,sourceGeometryChanges=0))
def main():
    if '--owned' in sys.argv:return owned()
    assert not DOC.exists() and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
    try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
