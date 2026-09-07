"""Reproducible source accounting, reviewed assets and byte-preservation checks."""
import gzip,hashlib,html,json,pathlib,sqlite3,subprocess
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/landmark-pass'
def read(p):return json.loads(p.read_bytes())
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 pub=read(DOC/'publication.json');assert pub['published'];before=read(DOC/'baseline.json')['manifest'];after=read(ROOT/'3d-viewer/city/data/manifest.json');assert before['counts']==after['counts']
 for p,h in pub['after'].items():assert sha(ROOT/p)==h,p
 previous=before['officialModelCatalogues'];assert after['officialModelCatalogues'][:len(previous)]==previous
 all_models={}
 for url in after['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for m in read(p)['models']:
   assert m['uid'] not in all_models;all_models[m['uid']]=m
 approved=read(HERE/'approved/catalogue.json')['models'];assert len(approved)==59
 for m in approved:
  p=ROOT/'3d-viewer/city/data/official-models/landmark-pass'/m['asset'];assert sha(p)==m['sha256'] and p.stat().st_size==m['bytes'];assert m['uid'] in all_models
 c=sqlite3.connect('file:'+str(HERE.parent/'building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
 # Inventory still represents the baseline until verification succeeds and it is refreshed.
 changed=[]
 for path,h in read(DOC/'baseline.json')['tileHashes'].items():
  p=ROOT/'3d-viewer'/path
  if sha(p)!=h:changed.append(p)
 expected={'landsd/240278:0'};adjusted=set()
 for p in changed:
  relative=str(p.relative_to(ROOT));old=json.loads(subprocess.check_output(['git','show',pub['beforeCommit']+':'+relative],cwd=ROOT));new=read(p)
  for b in new['buildings']:
   if b['uid'] in expected:
    assert b['baseHeightHKPD'] is None and b['topHeightHKPD'] is None and b['base']==4.184 and b['height']==3
    b['base']=11.617;adjusted.add(b['uid'])
  assert new==old,'Unexpected tile edit: '+relative
 assert adjusted==expected
 oldModels={m['uid'] for url in previous for m in read(ROOT/'3d-viewer'/url)['models']}
 groups=[]
 for g in read(HERE/'selection.json')['landmarks']:
  rows=[]
  for r in g['records']:
   b=c.execute('select * from buildings where uid=? and active=1',(r['uid'],)).fetchone();assert b
   rows.append({'uid':r['uid'],'name':b['name'],'kind':b['structure_type'],'beforeDetailed':bool(b['embedded'] or r['uid'] in oldModels),'afterDetailed':bool(b['embedded'] or r['uid'] in all_models),'added':any(m['uid']==r['uid'] for m in approved)})
  groups.append({'id':g['id'],'title':g['title'],'parts':len(rows),'beforeDetailed':sum(r['beforeDetailed'] for r in rows),'added':sum(r['added'] for r in rows),'afterDetailed':sum(r['afterDetailed'] for r in rows),'rows':rows})
 v={'passed':True,'addedModels':59,'compressedModelBytes':sum(m['bytes'] for m in approved),'progressiveModels':len(all_models),'unchangedBaseForms':after['counts'],'changedTileFiles':len(changed),'onlyEstimatedBaseChanged':sorted(adjusted),'groups':groups}
 write(DOC/'coverage.json',v)
 for name,source in [('context.json',HERE/'ngong-context.json'),('existing-audit.json',HERE/'existing-audit.json'),('source-plan.json',HERE/'acquisition-plan.json'),('terrain-replacement-audit.json',HERE/'taio-terrain-replacement-audit.json'),('approved-validation.json',HERE/'approved/validation.json')]:write(DOC/name,read(source))
 config=read(HERE/'final-browser-config.json');blocks=[]
 for g in config['groups']:
  for uid in g['uids']:
   b=c.execute('select name from buildings where uid=?',(uid,)).fetchone();name=g['area']+'-'+''.join(ch if ch.isalnum() else '-' for ch in uid)+'-day.png'
   for phase in ['before','after']:assert (DOC/'browser'/phase/name).exists()
   label=html.escape((b['name'] or uid)+' · '+uid)
   blocks.append(f'<section><h2>{label}</h2><div class="compare"><img src="browser/before/{name}" alt="Before {label}"><div class="after"><img src="browser/after/{name}" alt="After {label}"></div></div><label>Before / after <input type="range" min="0" max="100" value="50" aria-label="Compare {label}"></label></section>')
 text='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Astra landmark pass</title><style>body{font:16px system-ui;background:#f3f3ed;color:#253b32;max-width:1200px;margin:32px auto;padding:0 16px}section{background:white;padding:16px;margin:24px 0}h2{font-size:18px}.compare{position:relative;aspect-ratio:1.44;overflow:hidden}.compare>img,.after img{position:absolute;width:100%;height:100%;object-fit:cover}.after{position:absolute;inset:0;clip-path:inset(0 50% 0 0)}input{width:70%;vertical-align:middle}a{color:inherit}</style><h1>Named landmark upgrades</h1><p>59 new detailed source parts. Fixed 1× vertical scale; original model elevations preserved. Ngong Ping gains source-backed 5m terrain, and Tai O hotel terrain is corrected. One unsupported pagoda and 19 absent standalone source parts remain explicit gaps. These are non-textured government models with procedural materials.</p><p>Matching cameras show the original basic forms/terrain on the left and the reviewed candidates on the right. Slide to compare. Region-wide acceptance remains open.</p>'''+''.join(blocks)+'''<script>document.querySelectorAll('input').forEach(el=>el.addEventListener('input',()=>el.closest('section').querySelector('.after').style.clipPath=`inset(0 ${100-el.value}% 0 0)`))</script>'''
 (DOC/'comparison.html').write_text(text);print(json.dumps({k:v[k] for k in ['passed','addedModels','compressedModelBytes','progressiveModels','changedTileFiles']}));print(json.dumps([{k:g[k] for k in ['title','parts','beforeDetailed','added','afterDetailed']} for g in groups]))
if __name__=='__main__':main()
