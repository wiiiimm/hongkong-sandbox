"""Standard-library saved metadata/hash packaging only, no model computation."""
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
B=ROOT/'docs/astra-city/government-import'
IDS={'landsd/281463:0','landsd/236418:0','landsd/232240:0'}
PINS={}
def pin(path):
 path=path.resolve();assert path.is_relative_to(ROOT);raw=path.read_bytes();key=str(path.relative_to(ROOT));value=hashlib.sha256(raw).hexdigest()
 if key in PINS:assert PINS[key]==value
 PINS[key]=value;return raw
def load(path):
 raw=pin(path);return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
def write(name,data):
 with (HERE/name).open('x',encoding='utf-8') as stream:json.dump(data,stream,ensure_ascii=False,indent=2);stream.write('\n')
def main():
 assert not (HERE/'source-bound-findings.json').exists()
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert hashlib.sha256(pin(manifest)).hexdigest()=='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
 audit=B/'government-xl287-readonly-neon-frontier-audit-20261013'
 cohort=load(audit/'cohort.json');latest=load(audit/'latest-exact-source-job-readback.json');findings=load(audit/'findings.json');load(audit/'HANDOFF.json')
 ledger=load(B/'government-xl-identity-190-actionable-ledger-20261010/result.json')
 cases=[]
 for uid in sorted(IDS):
  row=next(r for r in ledger['rows'] if r['uid']==uid);co=next(r for r in cohort['sources'] if r['uid']==uid);la=next(r for r in latest['rows'] if r['expected_uid']==uid)
  assert co['indexedSourceSHA256']==row['sourceSHA256']==la['expected_source_sha256'];assert co['installedVerified'] is False
  role=load(B/'government-xl-spatial-surface-roles-20261009'/f"{uid.split('/')[1].replace(':','-')}.json.gz")
  assert role['sourceSHA256']==row['sourceSHA256'] and role['modelId']==row['modelId']
  assert hashlib.sha256(pin(ROOT/role['originalPath'])).hexdigest()==row['sourceSHA256']
  own=[r for v in role['variants'].values() for r in v['groupForms'] if r['uid']==uid];assert len(own)==1
  tile_rel=next(iter(role['sourceTileHashes']));tile=load(ROOT/'3d-viewer'/tile_rel);forms=[r for r in tile['buildings'] if r['uid']==uid];assert len(forms)==1
  assert forms[0]==own[0]
  cases.append({'uid':uid,'modelId':row['modelId'],'sourceSHA256':row['sourceSHA256'],'sourceKey':row['sourceKey'],'CSUID':own[0]['buildingCSUID'],'cohortRowVerbatim':co,'latestExactSourceRowVerbatim':la,'identityLedgerRowVerbatim':row,'currentFormVerbatim':forms[0],'currentFormEqualsSavedForm':True,'historicalSourceRoles':{'path':str((B/'government-xl-spatial-surface-roles-20261009'/f"{uid.split('/')[1].replace(':','-')}.json.gz").relative_to(ROOT)),'qualification':role['qualification'],'worldTrianglesSHA256':role['worldTrianglesSHA256'],'variants':{k:{'diagnosticFamilies':v['diagnosticFamilies'],'statsVerbatim':v['stats'],'groupUIDs':[r['uid'] for r in v['groupForms']]} for k,v in role['variants'].items()}}})
 pool_old=load(B/'government-xl-sustained-100-20261006-236418-0/result.json')
 retrieval=load(HERE/'retrieval.json');supp=load(HERE/'observed-images-retrieval.json');pages=load(HERE/'primary-document-page-lineage.json')
 allowed={'date','etag','last-modified','content-type','content-length','content-disposition'}
 for directory,receipt in (('primary-documents',retrieval),('primary-observed-images',supp)):
  for r in receipt['sources']:
   assert {k.lower() for k in r.get('provenanceHeaders',{})}<=allowed
   if r['saved']:assert hashlib.sha256(pin(HERE/directory/r['filename'])).hexdigest()==r['sha256']
 for page in pages['pages']:assert hashlib.sha256(pin(HERE/page['png'])).hexdigest()==page['sha256']
 annual=(HERE/'primary-documents/pool-completion-lcsd-2012-13.html').read_text();assert 'June 2012' in annual
 queries=['site.lcsd.gov.hk "Lai Chi Kok Park" "floor plan"','site:hkpl.gov.hk "Hong Kong Central Library" "floor plan"','site:lcsd.gov.hk "Lai Chi Kok Park Swimming Pool" layout','site:lcsd.gov.hk "Lai Chi Kok Park Sports Centre" "floor"','site:lcsd.gov.hk "Lai Chi Kok Park Swimming Pool" "plan" pdf','site:legco.gov.hk "Lai Chi Kok Park" "secondary pool" conversion','site:lcsd.gov.hk "Lai Chi Kok Park Sports Centre" "layout"','site:hkpl.gov.hk "Hong Kong Central Library" "Ground Floor" "Exhibition"']
 write('bounded-search-and-failures.json',{'queriesIssued':queries,'individualQueryTimesNotSaved':True,'LegCoBrowserTextURL':'https://www.legco.gov.hk/yr08-09/english/fc/pwsc/papers/p09-36e.pdf','LegCoFullPDFSaved':False,'LegCoDrawingActuallyViewed':False,'webDrawingScreenshotCacheMisses':{'p09-36e.pdf':[10,11],'hacb2-1304-1-e.pdf':[4]},'curlExactURLNormalTLSExit':60,'missingPDFMetadataInspection':{'toolChunk':'7572dc','actualExit':1,'exception':'pymupdf.FileNotFoundError','scope':'primary document inspection only; no model failure'},'caseSelectionAvoidedRecentChinaMerchantsYouthSquareGardenTerraceAndProviderSchemaCases':True,'stoppedAfterBoundedUsefulLeads':True})
 write('source-bound-findings.json',{'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'currentManifestSHA256':findings['currentManifestSHA256'],'currentSnapshotId':findings['currentSnapshotId'],'scope':{'fixedXL':521,'installed':234,'remaining':287,'selected':3},'cases':cases,'priorPoolResultVerbatim':pool_old,'newEvidenceAndNextActionsDefinedIn':'HANDOFF.md','actualPrimaryImagesViewed':['primary-document-pages/park-lcsd-permit-physical-page-103-2400px.png','primary-document-pages/park-lcsd-permit-physical-page-104-2400px.png','primary-observed-images/sports-centre-official-photo1.jpg','primary-observed-images/pool-official-photo.jpg','primary-documents/library-ground-floor-original.jpg','primary-documents/library-first-floor-original.JPG'],'documentTextLeadOnlyNoRawPDF':'PWSC(2009-10)36,245RS cover/retractable-sidewalls/covered-changing-room-walkway project; exact Enclosure1 still required','noModelDecode':True,'noModelExports':True,'noActualSourceNumericalWorkers':True,'noDBQueriesOrWrites':True,'noLeasesOrReceiptRecovery':True,'geometryChanges':0,'identityAccepted':False,'physicalAccepted':False,'currentAcceptance':False,'permanentRejection':False,'noOptimisationOrPublication':True})
 out=HERE/'closed-execution-logs';out.mkdir(exist_ok=False)
 for src,name in [('/tmp/lcsd-three-source-primary-retrieval-20261013.log','retrieval.log'),('/tmp/lcsd-three-source-primary-document-inspection-20261013.log','primary-document-render.log'),('/tmp/lcsd-pool-p09-36e-verified-curl.log','legco-normal-tls-curl-failure.log')]:shutil.copyfile(src,out/name)
 for path in sorted(HERE.rglob('*')):
  if path.is_file():pin(path)
 for rel,value in PINS.items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==value
 write('review-file-pins.json',{'allInputHashes':PINS,'allLiteralInputsUnchanged':True,'primaryOnlyNoNumericalClosureClaim':True})
 validation={'allPassed':True,'literalInputCount':len(PINS),'resultSHA256':hashlib.sha256((HERE/'source-bound-findings.json').read_bytes()).hexdigest(),'reviewPinsSHA256':hashlib.sha256((HERE/'review-file-pins.json').read_bytes()).hexdigest(),'actualOriginalSourceBytesVerified':3,'currentSavedFormsExactlyEqual':3,'actualViewedPrimaryImages':6,'retrievalsSaved':sum(r['saved'] for r in retrieval['sources'])+sum(r['saved'] for r in supp['sources']),'failedRawRetrievalsPreserved':sum(not r['saved'] for r in retrieval['sources'])+sum(not r['saved'] for r in supp['sources']),'headerAllowlistVerified':True,'noDBOrLeasesOrNumericalModelWorker':True,'identityAccepted':False,'physicalAccepted':False,'currentAcceptance':False}
 write('actual-closure-validation.json',validation);print(json.dumps(validation))
if __name__=='__main__':main()
