"""Explicit reviewed landmark publication; wraps the existing guarded publisher.
No bulk threshold relaxation. Unsupported pagoda and absent components stay basic.
"""
import argparse,hashlib,importlib.util,json,pathlib,shutil,sqlite3,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/landmark-pass'
def read(p):return json.loads(p.read_bytes())
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
HELD={'landsd/211847:0':'Unsupported pagoda: native geometry floats at least 3.23 m above source terrain, with no supporting neighbour. Keep fallback pending source revision/placement resolution.'}
CONTEXT={
 'landsd/232441:0':'Exact GeoRefNo, unique podium model; overlap 84.65%, centroid 18.56 m for irregular podium. Explicit source match exception, unchanged source geometry. Variable terrain around podium, roof clear; browser inspected.',
 'landsd/257115:0':'Exact GeoRefNo, unique podium model; overlap 94.16%, centroid 11.17 m for irregular podium. Explicit source match exception, unchanged source geometry. Podium spans variable ground levels, roof clear; browser inspected.',
 'landsd/238276:0':'Raised Hall of Great Hero supported by native podium238483: all348 rays at platform446.896, within0.167 m of hall base. Do not lower to bare terrain.',
 'landsd/238482:0':'Grand Hall supported by podium238483:1062 rays hit448.545HKPD platform, source base448.4; native bottom overlaps platform0.616m. Original tower/podium geometry retained.',
 'landsd/238483:0':'Podium supports both halls. Native lower/sloped portions intersect terrain locally; preserve full platform/stair geometry. Per-vertex intersection evidence and browser views retained.',
 'landsd/84455:0':'Native base3.56m below separately surveyed footprint base; native model follows retained terrain with no sampled ground gap. Per-vertex check only3/88 vertices >0.5m buried and none>2m. Native coordinates and surveyed metadata both preserved.',
 'landsd/170271:0':'Thin surveyed hotel source component; native roof clear of current fine terrain. Retain actual form, not artificial tower height.',
 'landsd/170357:0':'Hotel lower native vertices extend below hillside terrain; source roof clears fine terrain. Existing main building and attached components remain distinct.',
 'landsd/67478:0':'Hotel roof burial removed by guarded enlargement of existing native-TIN child2. Original native elevation retained.',
 'landsd/239278:0':'Source terrain replacement reveals low hotel outbuilding. A native corner reaches8.396m against highest roof8.213m; small remaining source intersection explicitly retained, no invented excavation.',
}
for uid in ['186841','6435','58870','67732','68108','94482']:
 CONTEXT['landsd/'+uid+':0']='Native lower vertices on stepped/sloping terrain, rather than wholly buried roofs. Retained per-vertex diagnostics and inspected browser view; no terrain or source-height adjustment for this model.'
def prepare():
 out=HERE/'approved';out.mkdir(exist_ok=True);models=[];guard={};screen=[]
 for folder,validation in [('compact','validation-fine.json'),('compact-existing','validation-final.json'),('compact-grandhall','validation.json')]:
  source=HERE/folder;cat=read(source/'catalogue.json');v=read(source/validation);rs={r['uid']:r for r in v['results']};guard[str((source/validation).relative_to(ROOT))]=sha(source/validation)
  for m in cat['models']:
   r=rs[m['uid']];assert r['outcome']=='runtime-accepted-placement-unreviewed',r
   if m['uid'] in HELD:continue
   if r['concerns']:assert m['uid'] in CONTEXT,'Unreviewed terrain exception: '+m['uid']
   if m.get('sourceMatchReview')=='explicit-landmark-match-review-required':assert m['uid'] in CONTEXT
   asset=source/m['asset'];assert sha(asset)==m['sha256'];dest=out/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,dest)
   models.append(dict(m,priority='landmark',placementReviewed=False,placementScreening='named-landmark-source-context-v1',contextReview=CONTEXT.get(m['uid'],'Existing exact source match and shared CPU placement screen; browser samples cover the group.')))
   screen.append({'uid':m['uid'],'concerns':r['concerns'],'contextReview':CONTEXT.get(m['uid'])})
  for path,h in v['hashes'].items():
   if path.startswith('3d-viewer/'):
    if path in guard:assert guard[path]==h
    guard[path]=h
 assert len(models)==59 and len({m['uid'] for m in models})==59
 cat=dict(cat,kind='official-model-catalogue',area='Named Hong Kong landmarks',counts={'packedModels':len(models)},models=models)
 write(out/'catalogue.json',cat);write(out/'catalogue-index.json',{'models':len(models),'catalogues':['catalogue.json']})
 plan={'areas':[{'area':'Named landmark upgrades','catalogue':str((out/'catalogue.json').relative_to(ROOT)),'destination':'city/data/official-models/landmark-pass/catalogue.json','terrainReplacements':[read(HERE/'taio-terrain-replacement-plan.json')],'estimates':[str((HERE/'taio-terrain-estimates.json').relative_to(ROOT))]}],'topLevelTerrainPatches':[{'source':str((HERE/'terrain-ngong-ping.json').relative_to(ROOT)),'destination':'city/data/terrain-ngong-ping.json','sha256':sha(HERE/'terrain-ngong-ping.json'),'area':'Ngong Ping landmarks','resolution':5}]}
 write(HERE/'publication-plan.json',plan)
 for p in [out/'catalogue.json',HERE/'publication-plan.json',HERE/'taio-terrain-replacement.json',HERE/'taio-terrain-estimates.json',HERE/'terrain-ngong-ping.json',HERE/'ngong-context.json',HERE/'existing-audit.json']:
  guard[str(p.relative_to(ROOT))]=sha(p)
 write(HERE/'guard.json',guard);write(DOC/'screening.json',{'accepted':len(models),'held':HELD,'context':CONTEXT,'compressedBytes':sum(m['bytes'] for m in models),'rows':screen,'limits':['Named parts are not whole-region sign-off.','Non-textured source geometry with procedural material; no claim of photorealistic textures.','Contextual exceptions are tied to these model/source hashes, not a global matcher change.']})
 # Staged full Tai O file used only for read-only CPU/browser review.
 print(json.dumps({'accepted':len(models),'compressedBytes':sum(m['bytes'] for m in models),'held':HELD}))
def publish(apply):
 for p,h in read(HERE/'guard.json').items():assert sha(ROOT/p)==h,'Reviewed input changed: '+p
 s=importlib.util.spec_from_file_location('shared_landmark_publisher',HERE.parent/'island-detail-integration/publish.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.ROOT=ROOT;m.DOC=DOC;sys.argv=['publish.py',str((HERE/'publication-plan.json').relative_to(ROOT))]+(['--apply'] if apply else []);m.main()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('step',choices=['prepare','publish']);p.add_argument('--apply',action='store_true');a=p.parse_args();prepare() if a.step=='prepare' else publish(a.apply)
