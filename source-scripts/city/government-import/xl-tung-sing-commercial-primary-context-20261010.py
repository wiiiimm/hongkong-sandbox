"""Primary commercial-complex/PhaseII context, not a cadastral or support proof."""
import datetime,json,urllib.request
from pathlib import Path
from run import ROOT,save,digest
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-commercial-primary-context-20261010'
URLS=[('current-operator-lei-tung.html','https://www.peoplesplace.com.hk/information-en/lei-tung/'),('hkex-2018-commercial-complex.pdf','https://www1.hkexnews.hk/listedco/listconews/sehk/2018/1212/ltn20181212803.pdf'),('housing-authority-lei-tung-estate.pdf','https://www.housingauthority.gov.hk/hdw/content/static/file/b5/residential/plans/estate/Lei%20Tung%20Estate.pdf')]
def main():
 assert not DOC.exists();DOC.mkdir(parents=True);records=[]
 for name,url in URLS:
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'HongKongSandbox-original-source-provenance/1.0'})
   with urllib.request.urlopen(req,timeout=45) as response:data=response.read();headers=dict(response.headers);actual=response.url
   assert data.startswith(b'%PDF-') if name.endswith('.pdf') else len(data)>1000
   (DOC/name).write_bytes(data);r={'filename':name,'url':url,'resolvedURL':actual,'retrievedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':digest(data),'bytes':len(data),'responseHeaders':headers,'qualification':'Primary descriptive source; not exact registered property boundary, surveyed height or source geometry correspondence proof.'};save(DOC/(name+'.request.json'),r);records.append(r)
  except Exception as e:records.append({'filename':name,'url':url,'retrievalFailure':str(e),'qualification':'Failed retrieval is no building absence or permanent rejection evidence.'})
 save(DOC/'primary-context.json',{'sources':records,'identityAccepted':False,'physicalAccepted':False,'qualification':'Current operator PhaseII directory,2018 issuer complex description,HA estate plan are independent naming/layout context only. No legal/commonOP, source support or95% acceptance exemption.'});print(json.dumps([{'file':r['filename'],'bytes':r.get('bytes'),'failure':r.get('retrievalFailure')} for r in records]),flush=True)
if __name__=='__main__':main()
