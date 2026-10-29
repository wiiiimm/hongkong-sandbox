"""Bounded dated primary photographs to distinguish the entrance from the lighthouse."""
import urllib.request,urllib.parse,re,html,io
from pathlib import Path
from PIL import Image
from run import ROOT,HERE,save,digest
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-disneyland-piers-after-passenger-dated-photos-v1-20261030'
def fetch(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'HongKongSandbox-source-research/1.0'}),timeout=30).read()
def main():
 out=ROOT/'docs/astra-city/government-import'/BATCH;assert not out.exists();out.mkdir();refs=[Path(__file__)];rows=[]
 for index,title in enumerate(['Disneyland Resort Pier 2026.jpg','Disneyland Resort Pier (Hong Kong).jpg','HK Disneyland Ferry Pier n Park Promenade morning.JPG']):
  url='https://commons.wikimedia.org/wiki/File:'+urllib.parse.quote(title.replace(' ','_'));row=dict(sourcePage=url,title=title,qualification='Primary photographer metadata and unmodified image; no inferred exact dimensions or automatic source acceptance.')
  try:
   raw=fetch(url);page=raw.decode();match=re.search(r'class="fullImageLink"[^>]*>.*?<a href="([^"]+)"',page,re.S);assert match,'Original image link absent';imageurl=html.unescape(match[1]);data=fetch(imageurl);im=Image.open(io.BytesIO(data));assert im.width>500 and im.height>300
   p=out/('photo-'+str(index)+'.jpg');p.write_bytes(data);refs.append(p)
   # Preserve short exact source table cells and licensing URLs for audit.
   metadata={}
   for key in ['filedesc','Date','Source','Author']:
    m=re.search(r'id="'+key+r'"[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>',page,re.S|re.I)
    if m:metadata[key]=html.unescape(re.sub('<[^>]+>',' ',m[2])).strip()[:900]
   row.update(originalURL=imageurl,path=str(p.relative_to(ROOT)),sha256=digest(data),pageSHA256=digest(raw),dimensions=[im.width,im.height],metadata=metadata,licenceURLs=sorted(set(re.findall(r'https?://creativecommons.org/licenses/[^"<> ]+',page))))
   print(dict(title=title,metadata=metadata,dimensions=im.size),flush=True)
  except Exception as e:row['error']=str(e);print(dict(title=title,error=str(e)),flush=True)
  rows.append(row)
 save(out/'provenance.json',rows);refs.append(out/'provenance.json');module('pier_dated_photographs_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-dated-primary-photographic-entrance-context',refs,dict(uids=['landsd/75642:0','landsd/75643:0'],photographs=rows,sourceGeometryChanges=0,identityAccepted=False,physicalAcceptance=False,installationApproved=False))
if __name__=='__main__':main()
