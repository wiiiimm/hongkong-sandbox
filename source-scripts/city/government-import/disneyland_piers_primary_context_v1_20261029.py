"""Archive primary pier-location context; never approve source identity or placement."""
import subprocess,urllib.request
from pathlib import Path
from pyproj import Transformer
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-disneyland-piers-primary-context-v1-20261029'
SELECT='government-xl-disneyland-piers-current-selection-v1-20261029'
BASE=ROOT/'docs/astra-city/government-import'
SOURCES=[('landsd-sunny-bay-disney-map.pdf','https://www.landsd.gov.hk/doc/en/mapping/ehkg/MapPages/GeoPDF/IS11_SunnyBay_Disney.pdf'),('td-disneyland-transport-2005.html','https://www.td.gov.hk/en/publications_and_press_releases/press_releases/transport_department/index_id_872.html')]


def main():
    out=BASE/BATCH;local=HERE/'local'/BATCH;assert not out.exists();refs=[Path(__file__)]
    _,pins=authenticate(BASE/SELECT);path=BASE/SELECT/'selection.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.extend([BASE/SELECT/'result.json',path]);selection=read(path)
    local.mkdir(parents=True,exist_ok=True);sources=[]
    for filename,url in SOURCES:
        path=local/filename;assert not path.exists()
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HongKongSandbox source-context research'}),timeout=60)as response:
            raw=response.read();assert response.status==200 and raw;sources.append(dict(url=url,path=str(path.relative_to(ROOT)),sha256=digest(raw),contentType=response.headers.get('Content-Type'),retrievedUTC=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()))
        path.write_bytes(raw);refs.append(path)
    out.mkdir();pdf=local/SOURCES[0][0];assert pdf.read_bytes().startswith(b'%PDF')
    info=subprocess.run(['pdfinfo',str(pdf)],check=True,capture_output=True,text=True);(out/'map-pdfinfo.txt').write_text(info.stdout)
    subprocess.run(['pdftoppm','-f','1','-singlefile','-r','150','-png',str(pdf),str(out/'landsd-map-page1')],check=True)
    image=out/'landsd-map-page1.png';refs.append(image)
    tr=Transformer.from_crs(2326,4326,always_xy=True);rows=[]
    for row in selection['rows']:
        x,z=row['source']['building']['centre'];lon,lat=tr.transform(x+834500,816500-z)
        rows.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],currentFormCentre=[x,z],currentFormCentreWGS84=dict(latitude=lat,longitude=lon),qualification='Coordinate transform of the viewer BASIC centre; approximate site context, not a new source placement or map-derived measurement.'))
    result=dict(uids=[r['uid']for r in rows],rows=rows,primarySources=sources,mapImage=dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes())),mapPage=1,mapRenderDPI=150,sourceGeometryChanges=0,identityAccepted=False,placementApproved=False,installationApproved=False,publication=False,qualification='Official LandsD Sunny Bay/Disney geographic map and archived2005 Transport Department transport notice. Location/name context only: neither proves correspondence of individual3D components, their full extents, support, current physical condition or publication eligibility. No historical Lantau reference set used.')
    save(out/'summary.json',result);module('disneyland_primary_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-pier-primary-geographic-context-without-identity-admission',refs,result)
    print(dict(batch=BATCH,primarySources=len(sources),identityAccepted=False),flush=True)

if __name__=='__main__':main()
