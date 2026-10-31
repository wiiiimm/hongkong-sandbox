"""Acquire dated primary developer context; no geometry or acceptance changes."""
from pathlib import Path
import urllib.request,re
import pymupdf
from run import ROOT,HERE,save,digest
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-la-marina-primary-brochure-context-v1-20261028';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
URL='https://www.lamarina.com.hk/upload/LaMarina%20Sales%20brochure_20220329_web_part_A.pdf'
def main():
 assert not DOC.exists()and not LOCAL.exists()
 with urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':'Mozilla/5.0'}),timeout=120)as response:
  raw=response.read(64*1024**2+1);assert len(raw)<=64*1024**2 and raw.startswith(b'%PDF');final=response.url;headers={k:v for k,v in response.headers.items()if k.lower()in ['etag','last-modified','content-type','content-length']}
 pdf=LOCAL/'original-dated-primary-brochure.pdf';pdf.parent.mkdir(parents=True);pdf.write_bytes(raw);relevant=[]
 with pymupdf.open(pdf)as document:
  pages=len(document)
  for i,page in enumerate(document):
   text=page.get_text();terms=[name for name,pattern in [('tower2-compound',r'Tower\s*2\s*\(\s*2A\s*(?:and|&)\s*2B\s*\)'),('layout',r'layout\s+plan'),('cross-section',r'cross[ -]section'),('HKPD',r'(?:mPD|HKPD|principal\s+datum)')]if re.search(pattern,text,re.I)]
   if terms:relevant.append(dict(pageIndex=i,pageNumber=i+1,terms=terms))
 result=dict(uids=['landsd/311761:0','landsd/311762:0','landsd/315025:0'],primaryURL=URL,finalURL=final,headers=headers,sourcePDF=dict(path=str(pdf.relative_to(ROOT)),sha256=digest(raw),bytes=len(raw)),filenameDate='2022-03-29',pages=pages,relevantPages=relevant,sourceGeometryChanges=0,identityAccepted=False,placementAccepted=False,installationApproved=False,qualification='Dated primary developer sales brochure, part A. Keyword page index is navigation only. No rendered plan inspected by this script, no map/geometry registration, no claim that this is the latest brochure, no source identity/support/placement or publication approval.')
 save(DOC/'summary.json',result);module('la_marina_primary_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'dated-primary-developer-context-no-model-acceptance',[Path(__file__),pdf],result);print(dict(pages=pages,relevantPages=len(relevant),bytes=len(raw)),flush=True)
if __name__=='__main__':main()
