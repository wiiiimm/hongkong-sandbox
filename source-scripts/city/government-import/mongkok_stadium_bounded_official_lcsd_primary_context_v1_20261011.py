"""DRAFT four exact official LCSD resources/two readers, source-only unwarped plan pages."""
from pathlib import Path
import json,datetime,requests,fitz
from run import ROOT,read,save,digest,connect
B=ROOT/'docs/astra-city/government-import';DOC=B/'government-xl-mongkok-stadium-bounded-official-lcsd-primary-context-v1-20261011';METHOD=B/'government-xl-mongkok-stadium-original-source-visual-primary-method-v2-20261011/METHOD.md';OLD=B/'government-xl-mongkok-stadium-complete-original-far-extent-body-attribution-v1-20261011';CAP=8*1024*1024
RESOURCES=[dict(name='facilities.html',url='https://www.lcsd.gov.hk/en/stadium/mks/facilities.html',kind='html'),dict(name='location-access.html',url='https://www.lcsd.gov.hk/en/stadium/mks/locations-directions.html',kind='html'),dict(name='original-official-location-map.pdf',url='https://www.lcsd.gov.hk/en/stadium/mks/common/pdf/mks_locmap.pdf',kind='pdf',pages=1,render=[0]),dict(name='original-official-2022-car-park-tender.pdf',url='https://www.lcsd.gov.hk/ls/tender/tc/list/forms/LC-LS-T-CP-HKS-MKS-2022.pdf',kind='pdf',pages=116,render=[110,111,112])]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def fetch(url):
 when=datetime.datetime.now(datetime.timezone.utc).isoformat();response=requests.get(url,stream=True,timeout=(15,45));chunks=[];total=0
 for block in response.iter_content(65536):
  total+=len(block);assert total<=CAP,'Bounded exact resource exceeded8MB cap';chunks.append(block)
 raw=b''.join(chunks);headers={k:response.headers.get(k)for k in ['Content-Type','Content-Length','ETag','Last-Modified','Date']};meta=dict(url=url,finalURL=response.url,httpStatus=response.status_code,headers=headers,sha256=digest(raw),bytes=len(raw),fetchedUTC=when);response.close();return raw,meta
def main():
 assert not DOC.exists();DOC.mkdir();old=read(OLD/'diagnostic.json.gz');assert old['completeOriginalFaces']==15456 and len(old['all62OriginalFarFaceAttributions'])==62;records=[];images=[]
 try:
  receipt=read(OLD/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e
  for resource in RESOURCES:
   readings=[];data=[]
   for number in [1,2]:
    raw,meta=fetch(resource['url']);save(DOC/(resource['name']+'.reader'+str(number)+'.json'),meta);readings.append(meta);data.append(raw);print(json.dumps(dict(resource=resource['name'],reader=number,status=meta['httpStatus'],bytes=len(raw))),flush=True)
   assert all(r['httpStatus']==200 and r['finalURL']==resource['url']for r in readings),'Actual HTTP/source URL failure';assert data[0]==data[1],'Official resource changed between readers'
   for key in ['ETag','Last-Modified']:assert readings[0]['headers'][key]==readings[1]['headers'][key],'Official source version headers changed'
   p=DOC/resource['name'];p.write_bytes(data[0]);records.append(dict(**resource,actualUnchangedReaders=readings,originalDownloadedResource=ref(p),exactBothReaderBytesEqual=True))
   if resource['kind']=='pdf':
    assert data[0].startswith(b'%PDF-');pdf=fitz.open(stream=data[0],filetype='pdf');assert len(pdf)==resource['pages'],'Exact observed PDF page count changed';texts={}
    for index in resource['render']:
     page=pdf[index];texts[str(index)]=page.get_text();out=DOC/(resource['name']+'.page-'+str(index+1)+'.png');pix=page.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False);pix.save(out);images.append(dict(**ref(out),parentOriginalPDF=ref(p),originalPDFZeroBasedPage=index,width=pix.width,height=pix.height,renderScale=2,originalPageUnwarped=True))
    save(DOC/(resource['name']+'.selected-original-page-text.json'),dict(parentOriginalPDF=ref(p),zeroBasedOriginalPages=resource['render'],originalExtractedPageText=texts))
   else:assert b'<html'in data[0].lower()
  save(DOC/'diagnostic.json',dict(uid='landsd/240332:0',completeExactOfficialResourceCount=4,readerCountPerResource=2,sourceCapBytes=CAP,actualHTTPAndVersionAccounting=records,originalUnwarpedPlanPageExports=images,siteContextOnly=True,primaryImagesViewedByAgent=False,sourceFeatureRegistrationPerformed=False,sourceComponentUIDOrElevationProven=False,sourceOnly=True,currentAcceptance=False,identityAccepted=False,architectureRoleAccepted=False,installationApproved=False,governmentGeometryChanges=0,terrainGeometryChanges=0,qualification='Four exact official LCSD venue/locations and original map/2022parking-tender resources, two actual readers and complete byte/header versions. Rendered original pages include location map and AnnexA/B/C parking location/layout. PDF images must actually be inspected; no feature/sourceUID/as-built geometry/elevation/ownership/support or current acceptance is inferred from the page index. Full source15,456/14body/15zero/62far-facet obligations and all raw identity/physical guards survive. Priorv1 cardinal wording is preserved and corrected by the separate southwest georef method.',evidenceRefs=[ref(p)for p in [Path(__file__),METHOD,OLD/'diagnostic.json.gz',OLD/'result.json',*[DOC/r['name']for r in RESOURCES],*[DOC/(r['name']+'.reader'+str(n)+'.json')for r in RESOURCES for n in [1,2]],*[DOC/(r['name']+'.selected-original-page-text.json')for r in RESOURCES if r['kind']=='pdf'],*[ROOT/i['path']for i in images]]]));print(json.dumps(dict(sourceOnly=True,originalResources=4,unwarpedPrimaryPages=len(images),identityAccepted=False)),flush=True)
 except Exception as error:
  save(DOC/'failure.json',dict(type=type(error).__name__,message=str(error),completedResourceRecords=records,renderedImages=images,sourceOnly=True,currentAcceptance=False,identityAccepted=False,rawFailurePreserved=True));raise
if __name__=='__main__':main()
