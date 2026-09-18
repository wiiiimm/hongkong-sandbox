"""Generate a compact, source-accounted review from the installed cultural run."""
import html,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=ROOT/'source-scripts/city/cultural-landmarks';DOC=ROOT/'docs/astra-city/cultural-landmarks'
def read(p):return json.loads(p.read_bytes())
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 cat=read(ROOT/'3d-viewer/city/data/official-models/cultural-landmarks/catalogue.json');report=read(HERE/'report.json');pub=read(DOC/'publication.json');assert pub['published']
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');assert manifest['counts']==pub['counts']
 after=read(DOC/'browser/after/verification.json');before=read(DOC/'browser/before/verification.json');assert before['result']==after['result']=='passed'
 assert read(HERE/'browser-config-live.json')['live']
 progressive=sum(len(read(ROOT/'3d-viewer'/u)['models']) for u in manifest['officialModelCatalogues'])
 d={'sourceParts':16,'detailedBefore':0,'detailedAfter':len(cat['models']),'spaceMuseum':{'sourceParts':3,'detailed':3},'culturalCentreAndPodium':{'sourceParts':13,'detailed':7},'heldSeparateCanopies':6,'bytes':sum(m['bytes'] for m in cat['models']),'triangles':sum(m['triangles'] for m in cat['models']),'terrainChanged':False,'verticalScale':1,'territoryForms':manifest['counts']['buildings'],'progressiveModels':progressive,'limits':['Six canopy identities remain basic; projected roof overlap is not verified source identity equivalence.','Studio Theatre retains a small foundation-edge terrain depression.','Non-textured source geometry; not a photorealistic or whole-Kowloon sign-off.','Mobile performance is Chrome viewport emulation, not physical-phone certification.']}
 write(DOC/'coverage.json',d)
 cards=[]
 for area in after['areas']:
  for row,name in zip(area['models'],area['views']):
   label=row['uid'];files=['browser/'+p+'/'+name+'.png' for p in ['before','after']]
   assert all((DOC/f).exists() for f in files)
   cards.append(f'<article><h2>{html.escape(label)}</h2><div class="pair"><img src="{files[0]}" alt="Before {label}"><img class="after" src="{files[1]}" alt="After {label}"></div><label>Before / After <input aria-label="Compare {label}" type="range" min="0" max="100" value="50"></label></article>')
 text='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Space Museum and Cultural Centre — HKS-207</title><style>body{font:16px system-ui;margin:24px auto;padding:0 16px;max-width:1080px;background:#f5f5ee;color:#263e36}h1{font-size:28px}article{margin:32px 0}h2{font-size:17px}.pair{position:relative}.pair img{width:100%;display:block}.after{position:absolute;inset:0;clip-path:inset(0 0 0 50%)}label{display:flex;gap:12px;align-items:center}input{flex:1;min-width:0}</style><h1>Space Museum and Cultural Centre</h1><p>Ten detailed government model parts; 16 source parts accounted for. Six canopies retain their basic forms. Fixed 1× elevations. Drag each slider to compare the same viewpoint.</p><p>The original trial did not select these two landmarks. This explicit HKS-207 pass reuses cached government data. <a href="coverage.json">Counts and limitations</a> · <a href="browser/after/verification.json">Installed browser checks</a></p>'''+''.join(cards)+'''<script>document.querySelectorAll('input').forEach(i=>i.addEventListener('input',()=>i.closest('article').querySelector('.after').style.clipPath='inset(0 0 0 '+i.value+'%)'));</script></html>'''
 (DOC/'comparison.html').write_text(text);print(json.dumps(d))
if __name__=='__main__':main()
