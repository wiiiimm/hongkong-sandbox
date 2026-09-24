"""Write the source-accounted visual trial report and interactive screenshot comparison."""
import collections,datetime,gzip,html,json,pathlib,sqlite3
ROOT=pathlib.Path(__file__).resolve().parents[3];WORK=ROOT/'source-scripts/city/building-batch/local';DOC=ROOT/'docs/astra-city/building-batch/visual-trial'
def read(p):return json.loads(p.read_bytes())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
screen=read(WORK/'publication/screening.json');samples=read(WORK/'publication/samples.json');held=read(WORK/'publication/held.json')
for name in ['screening.json','samples.json','guard.json','plan.json']:(DOC/name).write_bytes((WORK/'publication'/name).read_bytes())
for src,name in [(WORK/'publication/held.json','held.json.gz'),(WORK/'candidates/validation.json','candidate-validation.json.gz')]: (DOC/name).write_bytes(gzip.compress(src.read_bytes(),mtime=0))
all_models=[m for a in read(WORK/'publication/plan.json')['areas'] for m in read(ROOT/a['catalogue'])['models']]
new={m['uid'] for m in all_models}
samples += [dict(m,reviewArea='mui-wo') for m in all_models if m['worldBounds'][1][0]<-15000]
db=sqlite3.connect(WORK/'buildings.sqlite');db.row_factory=sqlite3.Row;areas=collections.defaultdict(collections.Counter);names={}
for b in db.execute("SELECT b.*,s.reasons_json,EXISTS(SELECT 1 FROM models m WHERE m.uid=b.uid) AS progressive FROM buildings b JOIN selection_members s ON b.uid=s.uid WHERE s.name='tourist-trial-v1'"):
 names[b['uid']]=b['name']
 for reason in json.loads(b['reasons_json']):
  if reason.startswith('area:'):
   r=areas[reason[5:]];r['forms']+=1;r['beforeDetail']+=int(bool(b['embedded'] or b['progressive']) and b['uid'] not in new);r['added']+=int(b['uid'] in new)
db.close()
for row in areas.values():row['afterDetail']=row['beforeDetail']+row['added'];row['afterPercent']=round(row['afterDetail']/row['forms']*100,1)
save(DOC/'coverage.json',areas)
cards=[]
for m in samples:
 uid=m['uid'];name=html.escape(names.get(uid) or m['label']);area=m.get('reviewArea','central');suffix='-mui-wo' if area=='mui-wo' else '';slug=area+'-'+''.join(c if c.isalnum() else '-' for c in uid)+'-day.png'
 cards.append(f'''<section><h2>{name}</h2><p>{uid} · {m['triangles']:,} source triangles</p><div class="compare"><img src="browser/before{suffix}/{slug}" alt="Basic form of {name}"><img class="after" src="browser/after{suffix}/{slug}" alt="Detailed government form of {name}"></div><label>Basic form <input type="range" min="0" max="100" value="50" aria-label="Show detailed model for {name}" oninput="this.closest('section').style.setProperty('--reveal',this.value+'%')"> Detailed model</label><p><a href="browser/before{suffix}/{slug}">Open before</a> · <a href="browser/after{suffix}/{slug}">Open after</a></p></section>''')
page='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Tourist model trial — before and after</title><style>*{box-sizing:border-box}body{font:16px/1.55 system-ui;margin:0;background:#f4f5ef;color:#173b32}main{max-width:1200px;margin:auto;padding:32px 20px}h1{font-size:clamp(26px,4vw,42px)}h2{margin:0;font-size:23px}section{--reveal:50%;padding:24px 0;border-top:1px solid #c7d1c9}.compare{position:relative;aspect-ratio:1.44;background:#ddd}.compare img{display:block;width:100%}.compare .after{position:absolute;inset:0;clip-path:inset(0 calc(100% - var(--reveal)) 0 0)}label{display:flex;align-items:center;gap:16px;margin:16px 0}input{flex:1;min-width:40px;height:44px;accent-color:#245440}a{color:#21564a}small{display:block}p{max-width:900px}</style><main><h1>Central and Mui Wo: detailed model trial</h1><p>1,075 Central + 3 Mui Wo models added · 6.5 MB compressed · 1,797 candidates held for further review. Drag each comparison to reveal the government geometry. These are matching views in the actual viewer, with only the new model catalogues disabled for the baseline.</p><p>All source elevations and footprints are preserved. Ten representative Central models and all three Mui Wo additions received visual review; source names can identify one building part rather than the complete named landmark; this is not a claim that every building or region is architecturally complete.</p>'''+''.join(cards)+'''<section><h2>Night and mobile</h2><p><a href="browser/after/central-night.png">Desktop night</a> · <a href="browser/after/central-mobile-night.png">Central mobile night</a> · <a href="browser/after-mui-wo/mui-wo-mobile-night.png">Mui Wo mobile night</a></p><small>Mobile viewport emulation on desktop Chrome; physical-phone performance remains unverified.</small></section></main>'''
(DOC/'comparison.html').write_text(page)
print(json.dumps(areas))
