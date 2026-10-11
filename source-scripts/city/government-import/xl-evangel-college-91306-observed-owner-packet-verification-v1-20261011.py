"""Replay exact saved official owner-page/image extraction, no image registration.

The original raw network captures/headers are retained unchanged. This method
independently reproduces observed image URLs and first-frame pixels from the
saved bytes. It makes no new live-page, ownership, physical or acceptance claim.
"""
import importlib.util,json,io
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,urlparse
import numpy as np
from PIL import Image
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'government-xl-evangel-college-91306-official-campus-packet-v1-20261011'
BATCH='government-xl-evangel-college-91306-observed-owner-packet-verification-v1-20261011';DOC=BASE/BATCH
URLS=['https://www.evangel.edu.hk/about_schdesign.php','https://www.evangel.edu.hk/about_contact.php','https://www.edb.gov.hk/en/student-parents/sch-info/sch-search/schlist-by-district/school-list-sk.html']
class Images(HTMLParser):
 def __init__(self):super().__init__();self.src=[]
 def handle_starttag(self,tag,attrs):
  if tag.lower()=='img':
   a=dict(attrs)
   if a.get('src'):self.src.append(urljoin(URLS[0],a['src']))
def main():
 assert not DOC.exists();pages=read(INPUT/'raw-page-provenance.json');images=read(INPUT/'raw-image-provenance.json');observed=read(INPUT/'observed-image-urls.json');refs=[Path(__file__)]
 assert pages['uids']==images['uids']==['landsd/91306:0']and [r['url']for r in pages['records']]==URLS
 for r in pages['records']:
  p=ROOT/r['path'];assert p.is_relative_to(INPUT)and r['status']==200 and digest(p.read_bytes())==r['sha256'];refs.append(p)
 parser=Images();html=(ROOT/pages['records'][0]['path']).read_bytes();parser.feed(html.decode('utf-8'));assert observed['sourceHTMLSHA256']==digest(html)and observed['observedURLs']==list(dict.fromkeys(parser.src))
 selected=[u for u in observed['observedURLs']if urlparse(u).netloc=='www.evangel.edu.hk'and urlparse(u).path.startswith('/images/about/school_design/')];assert [r['url']for r in images['records']]==selected and len(selected)==9
 checked=[]
 for r in images['records']:
  raw=ROOT/r['path'];png=ROOT/r['firstOriginalImageFramePNG']['path'];assert raw.is_relative_to(INPUT)and png.is_relative_to(INPUT)and r['status']==200
  assert digest(raw.read_bytes())==r['sha256']and digest(png.read_bytes())==r['firstOriginalImageFramePNG']['sha256']
  original=Image.open(io.BytesIO(raw.read_bytes()));assert list(original.size)==r['originalDimensions']and getattr(original,'n_frames',1)==r['originalFrameCount'];original.seek(0)
  saved=Image.open(png);assert np.array_equal(np.asarray(original.convert('RGBA')),np.asarray(saved.convert('RGBA')))
  checked.append(dict(url=r['url'],sourceSHA256=r['sha256'],firstFramePNG=r['firstOriginalImageFramePNG'],dimensions=r['originalDimensions'],firstFramePixelsExactlyReproduced=True));refs.extend([raw,png])
 refs.extend([INPUT/'raw-page-provenance.json',INPUT/'observed-image-urls.json',INPUT/'raw-image-provenance.json'])
 save(DOC/'diagnostic.json',dict(uids=['landsd/91306:0'],observedOwnerImages=checked,originalNetworkHeaderRecordsRetained=True,noLivePageRevalidationClaim=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,precisePlanRegistration=False,architecturalFunctionAccepted=False,propertyOwnershipAccepted=False,currentAcceptance=False,installationApproved=False))
 s=importlib.util.spec_from_file_location('evangel_owner_packet_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'saved-official-owner-network-packet-and-exact-image-extraction-replay-no-registration',refs,dict(uids=['landsd/91306:0'],pages=3,observedOwnerImages=9,currentAcceptance=False,newlyInstalled=0))
if __name__=='__main__':main()
