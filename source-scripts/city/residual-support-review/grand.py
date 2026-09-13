"""Stage the exact native Grand Promenade support closure, including existing tower metadata."""
import pathlib,json,sys,uuid,copy,hashlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DEST=HERE/'grand';DOC=ROOT/'docs/astra-city/residual-support-review/grand';DEST.mkdir(exist_ok=True);DOC.mkdir(exist_ok=True);read=lambda p:json.loads(p.read_bytes());write=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n');sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
uids={f'landsd/{i}:0'for i in [229653,93772,95937,14699,96089,96788]};receipt=pathlib.Path('/tmp/astra-grand-lease.json');r=reservations.claim('residual-grand-'+str(uuid.uuid4()),['building:'+u for u in uids],batch='HKS-214-grand-promenade');assert r['ok'],r;receipt.write_text(json.dumps(r['reservation'],default=str))
input=read(HERE/'input.json');parts={p['uid']:p for p in input['parts']if p['uid']in uids};mf=read(ROOT/'3d-viewer/city/data/manifest.json');installed={};buildings={}
for t in mf['tiles']:
 for b in read(ROOT/'3d-viewer'/t['url'])['buildings']:
  if b['uid']in uids:buildings[b['uid']]=b
for url in mf['officialModelCatalogues']:
 for m in read(ROOT/'3d-viewer'/url)['models']:
  if m['uid']in uids:
   installed[m['uid']]={'catalogue':url,'catalogueSHA256':hashlib.sha256((ROOT/'3d-viewer'/url).read_bytes()).hexdigest(),'model':m};b=buildings[m['uid']];parts[m['uid']]={'uid':m['uid'],'objectId':m['objectId'],'csuid':m['buildingCSUID'],'name':b['name']or m['label'],'candidate':m,'landmarkIds':[],'knownHold':None,'sourceProgress':'installed-context','sourceState':'installed','classification':['elevated-component-support-context'],'assemblyHints':[],'identityProposalGroups':[]}
assert len(parts)==6 and len(installed)==3;write(DEST/'input.json',{'snapshotId':input['snapshotId'],'parts':list(parts.values())});write(DEST/'uids.json',sorted(uids));write(DOC/'installed-context.json',installed)
source=(HERE/'review-adapter.generated.mjs').read_text().replace("read('source-scripts/city/residual-support-review/input.json')","read('source-scripts/city/residual-support-review/grand/input.json')");(HERE/'grand-review.generated.mjs').write_text(source)
audit=next(r for r in read(ROOT/'docs/astra-city/residual-support-review/native-audit-adjacent.json')['rows']if r['uid']=='landsd/229653:0');write(DOC/'native-terrain.json',{'sources':audit['sources'],'sourceGridProposals':[{'uid':'landsd/229653:0'}]});write(DOC/'report.json',read(ROOT/'docs/astra-city/residual-support-review/support.json'))
sys.path.insert(0,str(ROOT/'source-scripts/city/assembly-support-review'));import terrain_patches as t;t.HERE=DEST;t.OUT=DOC;t.main()
