"""Persist completed Tuen Mun evidence and ROOT's actual private-image inspection.

This checkpoint grants no source/physical/publication approval and installs zero.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-tuen-mun-five-progress-checkpoint-v1-20261025'
BROWSER='government-xl-tuen-mun-five-private-browser-v2-20261025'


def main():
    out=BASE/BATCH
    assert not out.exists()
    refs=[Path(__file__)]
    completed=[]
    for folder in sorted(BASE.glob('government-xl-tuen-mun-*-20261025')):
        if not folder.is_dir() or not (folder/'result.json').exists():continue
        result,_=authenticate(folder)
        completed.append(dict(batch=folder.name,jobId=result['jobId']))
        refs.append(folder/'result.json')
    assert len(completed)>=35
    receipt,pins=authenticate(BASE/BROWSER)
    assert not receipt['installationApproved'] and receipt['newlyInstalled']==0
    images=[];retained=[];reports=[]
    for width in [390,1280]:
        report_path=BASE/BROWSER/str(width)/'staged-browser.json'
        assert digest(report_path.read_bytes())==pins[str(report_path.relative_to(ROOT))]
        report=read(report_path)
        assert report['passed'] and not report['errors']
        reports.append(dict(path=str(report_path.relative_to(ROOT)),sha256=digest(report_path.read_bytes())))
        for collection,target in [('views',images),('retainedNativeOwnViews',retained)]:
            for view in report[collection]:
                if 'time' not in view:continue
                path=report_path.parent/view['file']
                assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
                assert view['active'] and view['visible'] and view['fullyFramed'] and not view['fallbackFaces']
                target.append(dict(uid=view['uid'],width=width,time=view['time'],path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
                refs.append(path)
        refs.append(report_path)
    assert len(images)==20 and len(retained)==4
    diagrams=[]
    for uid in [290803,196123,200057,200059,34417]:
        folder=BASE/f'government-xl-tuen-mun-{uid}-source-views-v1-20261025'
        _,diagram_pins=authenticate(folder)
        for name in ['whole-source-plan.png','whole-source-perspectives.png']:
            path=folder/name
            assert digest(path.read_bytes())==diagram_pins[str(path.relative_to(ROOT))]
            diagrams.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
            refs.append(path)
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes())==pins[str(manifest.relative_to(ROOT))]
    refs.append(manifest)
    state=dict(uids=receipt['uids'] if 'uids' in receipt else list(receipt['sourceSHA256ByUid']),
        sourceSHA256ByUid=receipt['sourceSHA256ByUid'],installedXL=377,unfinishedXL=144,totalFixedXL=521,
        currentNativeActors=6949,newlyInstalled=0,completed=completed,
        imagesActuallyViewed=images,retainedImagesActuallyViewed=retained,sourceDiagramsActuallyViewed=diagrams,
        browserReports=reports,privateVisualInspectionCompleted=True,installationApproved=False,
        physicalAcceptance=False,identityAccepted=False,publication=False,
        sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,
        humanDecisionRequired=False,aiGeometryModellingRequired=False,state='held-for-compute',
        observations=[
          'ROOT opened all24 V1 exports and10 original-source diagrams. V1 small200057 framing was partially obscured; do not reuse that framing as final visual approval.',
          'ROOT opened all24 V2 exports individually. Opposite camera exposes200057 roof/return. Podium/library/three small parts and retained229481 are readable in both widths; original grey/dark-night materials and existing BASIC window lighting remain.',
          'Final6335face derived terrain has complete18216sourceface coverage, unchanged existing foundation policy passes for all5 originals, and all26 neighbour forms/native31087face regression pass. Existing native publicationApproved:false remains unchanged.',
          'Raw extent/foreign projection/low-wall-cap failures and native legacy burial remain explicit. Diagnostic grade/overhead evidence does not itself grant physical approval.'
        ],remainingWork=[
          'Bind source-specific identity and physical interpretation to final exact source/ground/current-neighbour evidence, including downward50nonwall source roles and three exposed-grade-crossing walls.',
          'Finish native-aware additive publisher and installer path; retain all old no-native/replacement guards, full native proofs, exact metadata and actual retained own-view checks.',
          'Prepare-only and qualification commit/push before guarded installation.',
          'After install inspect fresh20source+4retained exports; full6949old-assets/full521/globalBASIC/native readback and refresh inventory; commit/push.'
        ])
    save(out/'remaining-work.json',state)
    module('tuen_mun_progress_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-tuen-mun-compute-and-private-image-inspection-checkpoint',list(dict.fromkeys(refs)),state)
    print(dict(completed=len(completed),imagesActuallyViewed=24,newlyInstalled=0),flush=True)


if __name__=='__main__':main()
