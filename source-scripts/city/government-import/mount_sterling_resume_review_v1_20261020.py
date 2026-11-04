"""Resume checkpoint: verified diagnostics and inspected night exports; no acceptance waiver."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-mount-sterling-resume-review-v1-20261020'
DOC=BASE/BATCH

def main():
    assert not DOC.exists()
    refs=[Path(__file__)]; receipts=[]; pins={}
    names=['ancillary-paths-v1','compound-foundations-v1','private-browser-v3','ancillary-browser-v2']
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for name in names:
            folder=BASE/f'government-xl-mount-sterling-{name}-20261020'
            receipt=read(folder/'result.json')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
            refs.append(folder/'result.json');receipts.append(dict(batch=name,jobId=receipt['jobId']))
            pins.update({e['path']:e['sha256'] for e in receipt['evidenceRefs']})
    images=[]
    folder=BASE/'government-xl-mount-sterling-private-browser-v3-20261020'
    for width,ids in [(1280,['272927','258775','272554']),(390,['289787','273905','103465','239797','272927','258775','272554'])]:
        for uid in ids:
            p=folder/str(width)/f'staged-landsd-{uid}-0-{width}-2200.png'
            key=str(p.relative_to(ROOT));sha=digest(p.read_bytes());assert pins[key]==sha
            refs.append(p);images.append(dict(path=key,sha256=sha,actuallyInspected=True))
    save(DOC/'review.json',dict(reviewer='Codex ROOT',receipts=receipts,imagesActuallyInspected=images,
        observations=['Night tower silhouettes and stepped roofs are visible, with dark untextured original facades. These images cannot establish every lower contact or buried surface.',
        'The mobile mall view is distant; other mobile views have UI and foreground occlusion. Intentional download-failure tests leave retry banners in several images. These are not clean final installation captures.',
        'Completed ancillary shared-edge paths are diagnostic evidence, not a substitute for physical placement acceptance. All six tower foundation checks pass; mall and ancillary findings still require source-specific interpretation.'],
        placementReviewed=False,publicationApproved=False,installationApproved=False,aiGeometryModelling=False,sourceGeometryChanges=0))
    module('mount_sterling_resume_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'resumed-original-diagnostics-and-night-export-inspection',refs,dict(uids=['landsd/289787:0','landsd/273905:0','landsd/103465:0','landsd/239797:0','landsd/163899:0','landsd/272927:0','landsd/258775:0','landsd/272554:0'],installationApproved=False,imagesInspected=10))
if __name__=='__main__':main()
