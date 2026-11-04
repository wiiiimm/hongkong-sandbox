"""Read current vendor-linked plan PDFs; no model geometry or approvals changed."""
import json,re,html,urllib.request,urllib.parse
from pathlib import Path
import pymupdf
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-fleur-live-primary-plans-v1-20261028';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
assert not DOC.exists()and not LOCAL.exists();refs=[Path(__file__)];captures=[]
def get(url,name,limit=2*1024**2):
 p=LOCAL/name
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=120)as response:
  raw=response.read(limit+1);assert len(raw)<=limit;final=response.url;headers={k:v for k,v in response.headers.items()if k.lower()in['content-length','content-type','etag','last-modified']}
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);refs.append(p);captures.append(dict(url=url,finalURL=final,path=str(p.relative_to(ROOT)),sha256=digest(raw),bytes=len(raw),headers=headers));return p
rows=[]
for category in['residential-property-sales-brochure','parking-space-sales-brochure']:
 try:
  vendor='https://www.fleurpavilia.com.hk/'+category;page=get(vendor,category+'/vendor.html');frames=[urllib.parse.urljoin(vendor,html.unescape(x))for x in re.findall(r'<iframe[^>]+src=["\']([^"\']+)',page.read_text(errors='replace'),re.I)if'cms.nwd.com.hk'in x];assert len(frames)==1;index=get(frames[0],category+'/publisher-index.html');links=[urllib.parse.urljoin(frames[0],html.unescape(x))for x in re.findall(r'href=["\']([^"\']+)',index.read_text(errors='replace'),re.I)if'.pdf'in x.lower()];assert links;url=urllib.parse.quote(links[0],safe=':/?&=%');pdf=get(url,category+'/original-primary-brochure.pdf',64*1024**2);assert pdf.read_bytes().startswith(b'%PDF');hits=[]
  with pymupdf.open(pdf)as doc:
   for i,page in enumerate(doc):
    text=page.get_text();terms=[k for k,pattern in{'layout-plan':r'layout\s+plan','basement':r'basement','lower-ground':r'lower\s+ground|LG\d?\s*/?F','ground-floor':r'ground\s+floor','podium':r'podium','elevation':r'elevation','HKPD':r'HKPD|principal\s+datum'}.items()if re.search(pattern,text,re.I)]
    if terms:hits.append(dict(pageIndex=i,pageNumber=i+1,terms=terms))
   count=len(doc)
  rows.append(dict(category=category,pdf=str(pdf.relative_to(ROOT)),pdfSHA256=digest(pdf.read_bytes()),pages=count,relevantPages=hits,sourceApproval=False))
 except Exception as error:rows.append(dict(category=category,errorType=type(error).__name__))
result=dict(uids=['landsd/23296:0','landsd/269972:0'],captures=captures,documents=rows,sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False,qualification='Current document links resolved from live designated vendor pages and live publisher indexes, not stale search-result PDF links. PDFs preserved unchanged; page keywords identify pages to render/inspect only. No surveyed registration, source role, basement, ownership, geometry, placement or installation approval inferred.')
save(DOC/'summary.json',result);module('fleur_live_primary_plans_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'live-designated-vendor-primary-plan-acquisition-no-approval',refs,result);print([(r['category'],r.get('pages'),r.get('errorType'),r.get('relevantPages',[])[:12])for r in rows],flush=True)
