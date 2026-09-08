"""Guarded publication of reviewed source assets; no whole-territory rebuild.
Run with a reviewed plan JSON and --apply. Retains rollback byte hashes and source fields.
"""
import argparse,copy,hashlib,json,pathlib,os,subprocess,tempfile,math,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from native_terrain_validation import validate_native_mesh
from reviewed_terrain_changes import reviewed_changes
from model_dependencies import stage_dependencies
from model_priorities import stage_priorities
ROOT=pathlib.Path(__file__).resolve().parents[3]
DOC=ROOT/'docs/astra-city/island-detail-integration'
def load(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(d):return (json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n').encode()
def validate_grid(data):
 # The renderer indexes arrays by w/h and uses georef for sampling; both must agree.
 assert all(type(data[k]) is int and data[k]>1 for k in ('w','h')),'Invalid terrain grid dimensions'
 g=data['meta']['georef']
 assert g['W']==data['w'] and g['H']==data['h'],'Terrain georef dimensions mismatch'
 assert all(isinstance(g[k],(int,float)) and math.isfinite(g[k]) for k in ('aE','aN','bE','bN')),'Invalid terrain georef'
 assert g['aE']>0 and g['aN']<0 and abs(g['aE']+g['aN'])<1e-8,'Unsupported terrain grid orientation'
 assert math.isfinite(data['cell']) and abs(data['cell']-g['aE'])<1e-8,'Terrain cell size mismatch'
 assert len(data['elev'])==len(data['vegetation'])==data['w']*data['h'],'Terrain array lengths mismatch'
 assert all(isinstance(v,(int,float)) and math.isfinite(v) for k in ('elev','vegetation') for v in data[k]),'Non-finite terrain values'
 if 'renderedElev' in data:
  assert len(data['renderedElev'])==data['w']*data['h'],'Rendered terrain array length mismatch'
  assert all(v is None or isinstance(v,(int,float)) and math.isfinite(v) for v in data['renderedElev']),'Invalid rendered terrain values'
def validate_patch(p,parent):
 validate_grid(p)
 validate_native_mesh(p,parent)
 cells=p['coarseCells'];assert len(cells)==4 and all(type(v) is int for v in cells),'Invalid terrain coarseCells'
 x0,z0,x1,z1=cells
 assert 0<=x0<x1<parent['w'] and 0<=z0<z1<parent['h'],'Terrain patch outside parent grid'
 g=parent['meta']['georef'];f=p['meta']['georef']
 assert abs(g['bE']+x0*g['aE']-f['bE'])<1e-5 and abs(g['bN']+z0*g['aN']-f['bN'])<1e-5,'Terrain patch origin misaligned'
 assert abs((x1-x0)*g['aE']-(p['w']-1)*f['aE'])<1e-5 and abs((z1-z0)*g['aN']-(p['h']-1)*f['aN'])<1e-5,'Terrain patch extent misaligned'
 assert f['aE']<g['aE'],'Terrain patch must refine the parent grid'
 children=[]
 for child in p.get('patches',[]):
  validate_patch(child,p);check_patch_overlap(child,children);children.append(child)
def check_patch_overlap(p,others):
 x0,z0,x1,z1=p['coarseCells']
 for q in others:
  a,b,c,d=q['coarseCells']
  assert x1<=a or x0>=c or z1<=b or z0>=d,'Overlapping terrain patches require review'
def stage_top_level_terrain(plan,original,manifest,edits,report):
 entries=plan.get('topLevelTerrainPatches',[])
 if not entries:return
 parent=load(ROOT/'3d-viewer/city/data/terrain.json');validate_grid(parent)
 replacements={}
 for entry in entries:
  replacement=entry.get('replaces')
  if not replacement:continue
  url=replacement['url'];assert url not in replacements,'Duplicate terrain replacement'
  matches=[m for m in original.get('terrainPatches',[]) if m['url']==url];assert len(matches)==1,'Terrain replacement must identify one installed patch'
  path=ROOT/'3d-viewer'/url;assert sha(path)==replacement['sha256'],'Installed terrain patch changed since review'
  old=load(path);new=load(ROOT/entry['source']);validate_patch(new,parent)
  assert not old.get('nativeMesh') and not new.get('nativeMesh'),'Native surface replacement needs a separate source review'
  a,b,c,d=old['coarseCells'];x0,z0,x1,z1=new['coarseCells'];assert x0<=a and z0<=b and x1>=c and z1>=d,'Replacement must contain installed extent'
  og=old['meta']['georef'];ng=new['meta']['georef'];assert og['aE']==ng['aE'] and og['aN']==ng['aN'],'Replacement must retain installed grid resolution'
  dx=(og['bE']-ng['bE'])/ng['aE'];dz=(og['bN']-ng['bN'])/ng['aN'];assert dx==int(dx) and dz==int(dz),'Replacement grids must align'
  assert old.get('hydro')==new.get('hydro'),'Replacement cannot alter water metadata'
  allowed=reviewed_changes(ROOT,entry,old,new)
  for row in range(old['h']):
   for col in range(old['w']):
    i=row*old['w']+col;j=(row+int(dz))*new['w']+col+int(dx)
    assert old['vegetation'][i]==new['vegetation'][j],'Replacement changed installed vegetation'
    if i in allowed:assert allowed[i]==j,'Correction changed grid identity'
    else:
     assert old['elev'][i]==new['elev'][j],'Replacement changed installed terrain nodes'
     assert old.get('renderedElev',old['elev'])[i]==new.get('renderedElev',new['elev'])[j],'Replacement changed rendered terrain nodes'
  replacements[url]=replacement['sha256']
 existing=list(parent.get('patches',[]))+[load(ROOT/'3d-viewer'/entry['url']) for entry in original.get('terrainPatches',[]) if entry['url'] not in replacements]
 if replacements:
  manifest['terrainPatches']=[m for m in manifest.get('terrainPatches',[]) if m['url'] not in replacements]
  report['replacedTerrainPatches']=[{'url':url,'sha256':digest,'oldAssetRetained':True} for url,digest in replacements.items()]
 for entry in entries:
  destrel=pathlib.Path(entry['destination'])
  assert not destrel.is_absolute() and '..' not in destrel.parts,'Terrain destination must be a viewer-relative path'
  dest=ROOT/'3d-viewer'/destrel
  assert dest.resolve().is_relative_to((ROOT/'3d-viewer').resolve()),'Terrain destination escapes viewer'
  assert not dest.exists() and not dest.is_symlink() and dest not in edits,'Do not overwrite an existing terrain asset'
  raw=(ROOT/entry['source']).read_bytes();digest=hashlib.sha256(raw).hexdigest()
  assert digest==entry['sha256'],'Terrain source hash changed since review'
  data=json.loads(raw);validate_patch(data,parent);check_patch_overlap(data,existing)
  assert entry['resolution']==data['cell'],'Terrain manifest resolution mismatch'
  assert isinstance(entry['area'],str) and entry['area'].strip(),'Terrain area is required'
  edits[dest]=raw;existing.append(data)
  metadata={'url':entry['destination'],'resolution':entry['resolution'],'area':entry['area'],'source':data['meta'].get('source'),'sha256':digest,'bytes':len(raw)}
  manifest.setdefault('terrainPatches',[]).append(metadata)
  report.setdefault('topLevelTerrainPatches',[]).append(metadata)
def stage_terrain_replacement(entry,edits):
 bundlePath=ROOT/entry['bundle'];bundle=load(bundlePath);parent=ROOT/'3d-viewer'/bundle['parentTerrainURL']
 assert sha(parent)==bundle['parentSha256'],'Parent terrain changed since replacement review'
 data=json.loads(edits[parent]) if parent in edits else load(parent);validate_grid(data);children=data.get('patches',[])
 matches=[i for i,p in enumerate(children) if p.get('id')==entry['oldChildId']]
 assert len(matches)==1,'Replacement child ID must identify exactly one existing child'
 i=matches[0];old=children[i]
 assert hashlib.sha256(encoded(old)).hexdigest()==entry['oldChildSha256'],'Terrain child hash changed since replacement review'
 assert len(bundle['patches'])==1,'Terrain replacement must contain exactly one child'
 replacement=bundle['patches'][0];assert replacement['id']==old['id'],'Terrain replacement must retain the child ID'
 validate_patch(replacement,data);check_patch_overlap(replacement,children[:i]+children[i+1:])
 x0,z0,x1,z1=old['coarseCells'];a,b,c,d=replacement['coarseCells']
 assert a<=x0 and b<=z0 and c>=x1 and d>=z1,'Replacement must retain the old child extent'
 assert set(old['meta'].get('targetUids',[]))<=set(replacement['meta'].get('targetUids',[])),'Replacement must retain original target UIDs'
 children[i]=replacement;edits[parent]=encoded(data)
 return bundle['parentSha256'],sha(bundlePath)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan');ap.add_argument('--apply',action='store_true');args=ap.parse_args();plan=load(ROOT/args.plan)
 manifestPath=ROOT/'3d-viewer/city/data/manifest.json';original=load(manifestPath);manifest=copy.deepcopy(original);edits={};assets=[];allUids=set();report={'published':False,'plan':args.plan,'areas':[],'before':{},'after':{},'counts':original['counts'],'beforeCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
 for url in original.get('officialModelCatalogues',[]):allUids.update(m['uid'] for m in load(ROOT/'3d-viewer'/url)['models'])
 stage_top_level_terrain(plan,original,manifest,edits,report)
 # Top-level refinements were hash-checked and staged above. Estimated bases
 # may reference only one of these exact parent/refinement pairs.
 topLevelBundles=[(sha(ROOT/'3d-viewer/city/data/terrain.json'),entry['sha256']) for entry in plan.get('topLevelTerrainPatches',[])]
 estimateByUid={};diagnostics={};estimatesFound=set()
 for area in plan['areas']:
  cataloguePath=ROOT/area['catalogue'];c=load(cataloguePath);dest=ROOT/'3d-viewer'/area['destination'];assert not dest.exists() and dest not in edits,'Do not overwrite a prior published catalogue or planned asset'
  assert c['counts']['packedModels']==len(c['models']);assert len({m['uid'] for m in c['models']})==len(c['models'])
  for m in c['models']:
   assert m['uid'] not in allUids,'Duplicate progressive source UID';allUids.add(m['uid']);p=cataloguePath.parent/m['asset'];assert sha(p)==m['sha256'] and p.stat().st_size==m['bytes'];assert '..' not in pathlib.Path(m['asset']).parts;assets.append((p,dest.parent/m['asset']))
  edits[dest]=encoded(c);manifest.setdefault('officialModelCatalogues',[]).append(area['destination'])
  includedBundles=[]
  for bundleName in area.get('terrain',[]):
   bundlePath=ROOT/bundleName;bundle=load(bundlePath);includedBundles.append((bundle['parentSha256'],sha(bundlePath)));parent=ROOT/'3d-viewer'/bundle['parentTerrainURL'];assert sha(parent)==bundle['parentSha256'],'Parent terrain changed since source review';data=json.loads(edits[parent]) if parent in edits else load(parent);children=data.setdefault('patches',[])
   for p in bundle['patches']:
    validate_patch(p,data)
    x0,z0,x1,z1=p['coarseCells'];assert 0<=x0<x1<data['w'] and 0<=z0<z1<data['h'];g=data['meta']['georef'];f=p['meta']['georef'];assert abs(g['bE']+x0*g['aE']-f['bE'])<1e-5 and abs(g['bN']+z0*g['aN']-f['bN'])<1e-5
    assert abs((x1-x0)*g['aE']-(p['w']-1)*f['aE'])<1e-5 and abs((z1-z0)*g['aN']-(p['h']-1)*f['aN'])<1e-5
    assert len(p['elev'])==len(p['vegetation'])==p['w']*p['h']
    for q in children:
     a,b,cx,d=q['coarseCells'];assert x1<=a or x0>=cx or z1<=b or z0>=d,'Overlapping nested patches require review'
    children.append(p)
   edits[parent]=encoded(data)
  for replacement in area.get('terrainReplacements',[]):
   includedBundles.append(stage_terrain_replacement(replacement,edits))
  for estimateName in area.get('estimates',[]):
   estimate=load(ROOT/estimateName);assert (estimate['parentSha256'],estimate['refinementSha256']) in includedBundles+topLevelBundles,'Estimated base requires its exact terrain bundle'
   for u in estimate['buildings']:
    assert u['uid'] not in estimateByUid;estimateByUid[u['uid']]=u
  for diagnosticName in area.get('diagnostics',[]):
   for uid,flags in load(ROOT/diagnosticName)['byBuildingUid'].items():
    assert uid not in diagnostics;diagnostics[uid]=flags
  report['areas'].append({'area':area['area'],'models':len(c['models']),'catalogue':area['destination'],'terrainBundles':area.get('terrain',[]),'terrainReplacements':area.get('terrainReplacements',[])})
 stage_priorities(ROOT,plan,manifest,edits,report)
 stage_dependencies(ROOT,plan,manifest,edits,{m['uid']:m for area in plan['areas'] for m in load(ROOT/area['catalogue'])['models']},report)
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
    assert b['heightSource']=='estimated' and b.get('baseSource')==u['baseSource']=='terrain-estimated';assert math.isfinite(u['base']);assert b['base']==u['previousBase'] and b['height']==u['height'];assert not b.get('modelGeometry');b['base']=u['base'];changed=True
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
