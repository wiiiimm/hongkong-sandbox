"""Preserve a separate official 2026 bridge progress document for source review."""
import gzip
import sys
from pathlib import Path
import fitz
from run import ROOT,HERE,save,digest
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request
BATCH='government-xl-nam-cheong-bridge-primary-progress-v1-20261023'
URL='https://www.districtcouncils.gov.hk/ssp/doc/2024_2027/en/dc_meetings_doc/31835/SSP_DC_2026_15_tc_annex.pdf'

def main():
    doc=ROOT/'docs/astra-city/government-import'/BATCH
    assert not doc.exists()
    raw,meta=request(URL,json_expected=False)
    decoded=gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
    assert decoded.startswith(b'%PDF')
    doc.mkdir();path=doc/'cedd-2026-bridge-progress.pdf';path.write_bytes(decoded)
    save(doc/'request.json',dict(meta,decodedSHA256=digest(decoded)))
    pdf=fitz.open(stream=decoded,filetype='pdf');assert 0<len(pdf)<=12
    pages=[]
    for n,page in enumerate(pdf):
        text=page.get_text();stem='page-'+str(n+1);(doc/(stem+'.txt')).write_text(text)
        image=doc/(stem+'.png');page.get_pixmap(matrix=fitz.Matrix(1.7,1.7),alpha=False).save(str(image))
        pages.append(dict(page=n+1,image=dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()))))
    summary=dict(uids=['landsd/268867:0'],sourceURL=URL,sourceSHA256=digest(decoded),pages=pages,bridgeIdentityAccepted=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Separate2026officialprogresssource only. No inference that proposed2021works,2009bridgeoranysourceextensionareidentical; actualpageinspection/spatialcomparison stillrequired. NormalTLSverificationkeptenabled.')
    save(doc/'summary.json',summary)
    module('nam_bridge_primary_progress_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'official-cedd-2026-bridge-progress-primary-capture',[Path(__file__),HERE.parent/'landsd-territory/source.py'],summary)

if __name__=='__main__':main()
