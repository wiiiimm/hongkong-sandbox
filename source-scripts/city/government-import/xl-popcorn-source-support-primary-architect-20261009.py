"""Retain architect's original project photographs for source role investigation."""
import re,sys,html,json
from run import ROOT,HERE,save
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request
DOC=ROOT/'docs/astra-city/government-import/government-xl-popcorn-source-support-roles-20261009/primary'
s=(DOC/'architect-the-wings.html').read_text()
s=re.sub(r'<script\b[^>]*>.*?</script>','',s,flags=re.S|re.I)
s=re.sub(r'<style\b[^>]*>.*?</style>','',s,flags=re.S|re.I)
text=html.unescape(re.sub('<[^>]+>',' ',s))
save(DOC/'architect-readable-project.json',{'text':re.sub(r'\s+',' ',text),'url':'https://www.wongtung.com/en/projects/the-wings/','qualification':'Architect first-party project text. No exact source-component ownership follows from generic project descriptions.'})
urls=sorted(set('https:'+u if u.startswith('//') else u for u in re.findall(r'<img[^>]+src=["\x27]([^"\x27]+)',s) if '030070_180423-WT-web-project-page' in u))
records=[]
for i,u in enumerate(urls):
 p=DOC/('architect-project-'+str(i+1)+'.jpg');meta=p.with_suffix('.jpg.request.json')
 if not p.exists():
  raw,r=request(u,json_expected=False);p.write_bytes(raw);save(meta,r)
 records.append({'url':u,'path':str(p.relative_to(ROOT)),'request':str(meta.relative_to(ROOT))})
save(DOC/'architect-original-photographs.json',{'originalPhotos':records,'qualification':'Unchanged first-party photos, not geometry replacements or support acceptance.'})
print({'photos':len(records)},flush=True)
