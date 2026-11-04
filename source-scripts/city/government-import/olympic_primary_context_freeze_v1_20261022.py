"""Archive primary MTR plan context, without source-face or placement approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-olympic-station-primary-context-v1-20261022';DOC=ROOT/'docs/astra-city/government-import'/BATCH
def main():
 assert not(DOC/'result.json').exists();p=DOC/'mtr-ap-110.pdf';assert digest(p.read_bytes())=='e1adf1fc458e6d437347d720231c3747d9c407c83c9e128eef6f8ab3c1b73335';assert p.read_bytes().startswith(b'%PDF')
 result=dict(uids=['landsd/81242:0'],sourcePage='https://www.mtr.com.hk/en/corporate/operations/station_tc_olympic.html',sourceURL='https://www.mtr.com.hk/archive/corporate/en/operations/AEL%20or%20TCL_RPAP/Mtr_Ap_110.pdf',document='MTR/AP/110 revision B, Olympic Station railway protection area plan',drawingDate='December 2023',pdfCreationDate='2024-11-13',page=1,rootViewedExport=True,observation='Plan identifies the elongated station, parallel rail alignments and connecting footbridges. This is contextual comparison with complete-source diagrams, not exact registration, face ownership, source date equivalence, clearance or whole-source identity approval.',installationApproved=False,newlyInstalled=0,publication=False,sourceGeometryChanges=0)
 save(DOC/'provenance.json',result);module('olympic_primary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'primary-station-plan-context',[Path(__file__),*DOC.glob('mtr-ap-110.*')],result)
if __name__=='__main__':main()
