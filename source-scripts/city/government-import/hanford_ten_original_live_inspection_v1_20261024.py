"""Bind ROOT's actual forty-image Hanford live inspection."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from hanford_ten_original_catalogue_scope_v1_20261024 import SOURCES
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-hanford-ten-original-original-installed-v1-20261024'


def main():
    folder=BASE/BATCH
    result,pins=authenticate(folder)
    assert result['fullXLCurrentCounts']==dict(total=521,installedVerified=350,remaining=171)
    assert result['sourceSHA256ByUid']==SOURCES
    target=folder/'ROOT-LIVE-EXPORT-INSPECTION.json';assert not target.exists()
    images=[];retained=[];sheets=[]
    def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    for width in [390,1280]:
        report=read(folder/('viewport-'+str(width))/'live-browser.json')
        assert report['passed']and not report['errors']
        source=[v for v in report['views']if'time'in v]
        assert len(source)==20 and not report.get('retainedNativeOwnViews',[])
        for views,output in [(source,images),(report.get('retainedNativeOwnViews',[]),retained)]:
            for v in views:
                assert v['active']and v['visible']and v['fullyFramed']and not v['fallbackFaces']
                assert all(v['meshVisibility'])and not any(v['wireframeFlags'])
                if v['uid']in SOURCES:
                    assert v['sourceSHA256']==SOURCES[v['uid']]and v['solidAppearance']and v['pick']==v['collision']==v['uid']
                else:raise AssertionError('Unexpected retained actor')
                image=folder/('viewport-'+str(width))/v['file'];r=ref(image)
                assert r['sha256']==pins[r['path']]
                output.append(dict(**r,uid=v['uid'],width=width,time=v['time']))
        for time in ['1500','2200']:
            sheet=BASE/'government-xl-hanford-ten-original-root-live-inspection-v1-20261024'/str(width)/(str(width)+'-'+time+'.jpg')
            assert sheet.is_file();sheets.append(ref(sheet))
    assert len(images)==40 and not retained
    save(target,dict(reviewer='ROOT',visualAcceptance=True,imagesActuallyViewed=images,
        retainedImagesActuallyViewed=retained,inspectionSheetsActuallyViewed=sheets,
        visualFinding='ROOT inspected all40 live desktop/mobile day/night canvases through four full-frame sheets. All ten original Hanford components remain visibly inspectable, consistent with the accepted private V3images. The broader authored-yaw tower camera preserves complete framing. Natural partial tower/podium occlusion and dark original night appearance remain; no procedural window shader, source pose or geometry change was introduced. Exact two-podium original-TIN terrain bytes and complete current-neighbour evidence remain bound',
        sourceGeometryChanges=0,terrainEdits=True,aiGeometryModelling=False))
    print(dict(inspectedSourceExports=40,inspectedRetainedExports=0,installedJobId=result['jobId']))


if __name__=='__main__':main()
