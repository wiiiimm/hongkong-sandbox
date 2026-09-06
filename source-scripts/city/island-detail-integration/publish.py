"""Guarded publication of reviewed source assets; no whole-territory rebuild.
Run with a reviewed plan JSON and --apply. Retains rollback byte hashes and source fields.
"""
import argparse,copy,hashlib,json,pathlib,os,subprocess,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[3]
DOC=ROOT/'docs/astra-city/island-detail-integration'
def load(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(d):return (json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n').encode()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan');ap.add_argument('--apply',action='store_true');args=ap.parse_args();plan=load(ROOT/args.plan)
 manifestPath=ROOT/'3d-viewer/city/data/manifest.json';original=load(manifestPath);manifest=copy.deepcopy(original);edits={};assets=[];allUids=set();report={'published':False,'plan':args.plan,'areas':[],'before':{},'after':{},'counts':original['counts'],'beforeCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
 for url in original.get('officialModelCatalogues',[]):allUids.update(m['uid'] for m in load(ROOT/'3d-viewer'/url)['models'])
 estimateByUid={};diagnostics={};estimatesFound=set()
 for area in plan['areas']:
  cataloguePath=ROOT/area['catalogue'];c=load(cataloguePath);dest=ROOT/'3d-viewer'/area['destination'];assert not dest.exists(),'Do not overwrite a prior published catalogue'
  assert c['counts']['packedModels']==len(c['models']);assert len({m['uid'] for m in c['models']})==len(c['models'])
  for m in c['models']:
   assert m['uid'] not in allUids,'Duplicate progressive source UID';allUids.add(m['uid']);p=cataloguePath.parent/m['asset'];assert sha(p)==m['sha256'] and p.stat().st_size==m['bytes'];assert '..' not in pathlib.Path(m['asset']).parts;assets.append((p,dest.parent/m['asset']))
  edits[dest]=encoded(c);manifest.setdefault('officialModelCatalogues',[]).append(area['destination'])
  includedBundles=[]
  for bundleName in area.get('terrain',[]):
   bundlePath=ROOT/bundleName;bundle=load(bundlePath);includedBundles.append((bundle['parentSha256'],sha(bundlePath)));parent=ROOT/'3d-viewer'/bundle['parentTerrainURL'];assert sha(parent)==bundle['parentSha256'],'Parent terrain changed since source review';data=json.loads(edits[parent]) if parent in edits else load(parent);children=data.setdefault('patches',[])
   for p in bundle['patches']:
    x0,z0,x1,z1=p['coarseCells'];assert 0<=x0<x1<data['w'] and 0<=z0<z1<data['h'];g=data['meta']['georef'];f=p['meta']['georef'];assert abs(g['bE']+x0*g['aE']-f['bE'])<1e-5 and abs(g['bN']+z0*g['aN']-f['bN'])<1e-5
    assert abs((x1-x0)*g['aE']-(p['w']-1)*f['aE'])<1e-5 and abs((z1-z0)*g['aN']-(p['h']-1)*f['aN'])<1e-5
    assert len(p['elev'])==len(p['vegetation'])==p['w']*p['h']
    for q in children:
     a,b,cx,d=q['coarseCells'];assert x1<=a or x0>=cx or z1<=b or z0>=d,'Overlapping nested patches require review'
    children.append(p)
   edits[parent]=encoded(data)
  for estimateName in area.get('estimates',[]):
   estimate=load(ROOT/estimateName);assert (estimate['parentSha256'],estimate['refinementSha256']) in includedBundles,'Estimated base requires its exact terrain bundle'
   for u in estimate['buildings']:
    assert u['uid'] not in estimateByUid;estimateByUid[u['uid']]=u
  for diagnosticName in area.get('diagnostics',[]):
   for uid,flags in load(ROOT/diagnosticName)['byBuildingUid'].items():
    assert uid not in diagnostics;diagnostics[uid]=flags
  report['areas'].append({'area':area['area'],'models':len(c['models']),'catalogue':area['destination'],'terrainBundles':area.get('terrain',[])})
 # Validate all new IDs and preserve every footprint, source field, existing model
 # and unrelated record. Only explicitly guarded null-source base estimates change.
 newModels={m['uid']:m for area in plan['areas'] for m in load(ROOT/area['catalogue'])['models']};newIds=set(newModels);found=set()
 for t in manifest['tiles']:
  p=ROOT/'3d-viewer'/t['url'];d=load(p);changed=False
  for b in d['buildings']:
   if b['uid'] in newIds:
    m=newModels[b['uid']];assert not b.get('modelGeometry'),'Embedded model already takes precedence';found.add(b['uid'])
    assert b.get('objectId')==m['objectId'] and b.get('buildingCSUID')==m['buildingCSUID'],'Model identity mismatch'
    assert b.get('baseHeightHKPD')==m['recordedBaseHeight'] and b.get('topHeightHKPD')==m['recordedTopHeight'],'Recorded source elevation mismatch'
   if b['uid'] in estimateByUid:
    u=estimateByUid[b['uid']];estimatesFound.add(b['uid']);assert b['objectId']==u['objectId'] and b['buildingCSUID']==u['buildingCSUID'];assert b.get('baseHeightHKPD') is None and b.get('topHeightHKPD') is None
    assert b['heightSource']=='estimated' and b.get('baseSource')==u['baseSource'];assert b['base']==u['previousBase'] and b['height']==u['height'];assert not b.get('modelGeometry');b['base']=u['base'];changed=True
   if b['uid'] in diagnostics:b.setdefault('terrainAudit',{}).update(diagnostics[b['uid']]);changed=True
  if changed:edits[p]=encoded(d);t['bytes']=len(edits[p])
 assert estimatesFound==set(estimateByUid),'Missing estimate update UID'
 assert found==newIds,'Source UID missing from current tiles';assert original['counts']==manifest['counts'];edits[manifestPath]=encoded(manifest)
 report['estimatedBases']=[{'uid':u['uid'],'before':u['previousBase'],'after':u['base']} for u in estimateByUid.values()]
 for p,value in edits.items():report['before'][str(p.relative_to(ROOT))]=sha(p) if p.exists() else None;report['after'][str(p.relative_to(ROOT))]=hashlib.sha256(value).hexdigest()
 # Index used by search stores base, so update only the same guarded estimates.
 for rel in ['3d-viewer/city/data/catalogue.json','3d-viewer/city/data/overview.json']:
  p=ROOT/rel;d=load(p);changed=[0]
  def walk(obj):
   if isinstance(obj,list):
    for v in obj:walk(v)
   elif isinstance(obj,dict):
    u=estimateByUid.get(obj.get('uid'))
    if u and obj.get('base')==u['previousBase']:obj['base']=u['base'];changed[0]+=1
    flags=diagnostics.get(obj.get('uid'))
    if flags and 'terrainAudit' in obj:obj['terrainAudit'].update(flags);changed[0]+=1
    for v in obj.values():
     if isinstance(v,(dict,list)):walk(v)
  walk(d)
  if changed[0]:edits[p]=encoded(d);report['before'][rel]=sha(p);report['after'][rel]=hashlib.sha256(edits[p]).hexdigest()
 if args.apply:
  # Prepare every byte before changing live data. New assets cannot overwrite a
  # different package. Manifest is installed last; any error restores old bytes.
  prepared=dict(edits)
  for src,dest in assets:
   assert dest not in prepared and not dest.exists(),'Asset destination collision'
   prepared[dest]=src.read_bytes()
  beforeBytes={p:p.read_bytes() if p.exists() else None for p in prepared}
  def atomic_write(p,value):
   p.parent.mkdir(parents=True,exist_ok=True)
   fd,name=tempfile.mkstemp(prefix='.island-publish-',dir=p.parent)
   try:
    with os.fdopen(fd,'wb') as f:f.write(value)
    os.replace(name,p)
   finally:
    if os.path.exists(name):os.unlink(name)
  installed=[]
  try:
   order=[dest for _,dest in assets]+[p for p in edits if p!=manifestPath]+[manifestPath]
   for p in order:atomic_write(p,prepared[p]);installed.append(p)
  except BaseException:
   for p in reversed(installed):
    if beforeBytes[p] is None:p.unlink(missing_ok=True)
    else:atomic_write(p,beforeBytes[p])
   raise
  report['published']=True
 DOC.mkdir(parents=True,exist_ok=True);(DOC/('publication.json' if args.apply else 'publication-plan.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'published':report['published'],'areas':report['areas'],'estimatedBases':report['estimatedBases']},indent=2))
if __name__=='__main__':main()
