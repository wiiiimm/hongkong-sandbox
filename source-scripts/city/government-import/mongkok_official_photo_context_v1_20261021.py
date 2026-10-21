"""Archive primary government stadium context; no identity acceptance by download."""
from pathlib import Path
import urllib.request
from run import ROOT,HERE,save,digest
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-mongkok-official-photo-context-v1-20261021';DOC=ROOT/'docs/astra-city/government-import'/BATCH
SOURCES=[('location-page.html','https://fpf.ccidahk.gov.hk/en/location/detail.php?id=1704')]+[(f'01704{c}.jpg',f'https://fpf.ccidahk.gov.hk/common/images/location/01704/01704{c}.jpg') for c in 'abcdefghij']
def main():
    assert not DOC.exists();DOC.mkdir(parents=True);sources=[]
    for name,url in SOURCES:
        with urllib.request.urlopen(url,timeout=25)as response:
            raw=response.read();content_type=response.headers.get('Content-Type');final=response.url
        (DOC/name).write_bytes(raw);sources.append(dict(path=str((DOC/name).relative_to(ROOT)),url=url,finalURL=final,sha256=digest(raw),contentType=content_type,bytes=len(raw)))
    result=dict(uids=['landsd/240332:0'],sources=sources,identityReviewApproved=False,installationApproved=False,sourceGeometryChanges=0)
    save(DOC/'sources.json',result);module('mongkok_official_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'primary-government-stadium-photo-context',[Path(__file__)],result)
if __name__=='__main__':main()
