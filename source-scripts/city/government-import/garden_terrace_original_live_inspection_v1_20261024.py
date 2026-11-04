"""Bind ROOT's actual sixteen-image Garden Terrace live inspection."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from garden_terrace_original_catalogue_scope_v1_20261024 import SOURCES, RETAINED, RETAINED_SHA
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-garden-terrace-three-original-original-installed-v1-20261024'


def main():
    folder=BASE/BATCH
    result,pins=authenticate(folder)
    assert result['fullXLCurrentCounts']==dict(total=521,installedVerified=349,remaining=172)
    assert result['sourceSHA256ByUid']==SOURCES and result['terrainEdits']is False
    target=folder/'ROOT-LIVE-EXPORT-INSPECTION.json';assert not target.exists()
    images=[];retained=[];sheets=[]
    def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    for width in [390,1280]:
        report=read(folder/('viewport-'+str(width))/'live-browser.json')
        assert report['passed']and not report['errors']
        source=[v for v in report['views']if'time'in v]
        assert len(source)==6 and len(report['retainedNativeOwnViews'])==2
        for views,output in [(source,images),(report['retainedNativeOwnViews'],retained)]:
            for v in views:
                assert v['active']and v['visible']and v['fullyFramed']and not v['fallbackFaces']
                assert all(v['meshVisibility'])and not any(v['wireframeFlags'])
                if v['uid']in SOURCES:
                    assert v['sourceSHA256']==SOURCES[v['uid']]and v['solidAppearance']and v['pick']==v['collision']==v['uid']
                else:assert v['uid']in RETAINED and v['sourceSHA256']==RETAINED_SHA and v['originalTriangles']==821 and not v['overflow']
                image=folder/('viewport-'+str(width))/v['file'];r=ref(image)
                assert r['sha256']==pins[r['path']]
                output.append(dict(**r,uid=v['uid'],width=width,time=v['time']))
        for time in ['1500','2200']:
            sheet=BASE/'government-xl-garden-terrace-three-original-root-live-inspection-v1-20261024'/str(width)/(str(width)+'-'+time+'.jpg')
            assert sheet.is_file();sheets.append(ref(sheet))
    assert len(images)==12 and len(retained)==4
    save(target,dict(reviewer='ROOT',visualAcceptance=True,imagesActuallyViewed=images,
        retainedImagesActuallyViewed=retained,inspectionSheetsActuallyViewed=sheets,
        visualFinding='ROOT inspected all16 actual live exports through four full-frame desktop/mobile day/night sheets. Both unchanged original towers and the common podium are visibly inspectable and consistent with the accepted private V2 views; the retained No1GardenTerrace podium remains visible and unchanged. Natural partial foreground/own-tower occlusion and original darknightappearance remain. No procedural window shader, source/terrain edit or pose change was introduced.',
        sourceGeometryChanges=0,terrainEdits=False,aiGeometryModelling=False))
    print(dict(inspectedSourceExports=12,inspectedRetainedExports=4,installedJobId=result['jobId']))


if __name__=='__main__':main()
