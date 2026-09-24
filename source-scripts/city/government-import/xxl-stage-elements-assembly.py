"""Stage the exact Elements estate assembly, restored native terrain and dependency migration; never AI."""
import importlib.util,json,shutil,subprocess,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xxl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE=s.ROOT,s.HERE;DOC=s.DOC/'elements';LOCAL=s.LOCAL/'elements-assembly';SUPPORT=s.LOCAL/'elements-supports';CULLINAN=s.LOCAL/'elements-cullinan/packed/assets';STAGE=HERE/'accepted/government-xxl-elements-assembly-20260912'
UID='landsd/273061:0';HARBOURSIDE='landsd/204153:0';CULLINANS={'landsd/203724:0','landsd/203728:0'};BATCH='government-xxl-elements-assembly-20260912';read,save,h,rel=s.read,s.save,s.h,s.rel

def assembly_rows():
 frozen=read(s.DOC/'runtime-selection.json.gz');primary=next(r for r in frozen['rows'] if r['uid']==UID);approved=read(HERE.parent/'identity-four-native/approved/catalogue.json');pe=next(e for e in approved['models'] if e['uid']==UID);primary['candidate']={'path':str(s.LOCAL/'assets'/(pe['sha256']+'.glb.gz')),'entry':{**pe,'rootTranslation':approved['rootTranslation']}}
 inputs=read(SUPPORT/'inputs.json.gz');recovered=[]
 for row in read(SUPPORT/'geometry-inputs.json')['rows']:
  if row['uid']!=HARBOURSIDE:recovered.append({'uid':row['uid'],'source':inputs['sources'][row['uid']],'candidate':row['candidate']})
 for uid in sorted(CULLINANS):
  e=next(x for x in approved['models'] if x['uid']==uid);recovered.append({'uid':uid,'source':inputs['sources'][uid],'candidate':{'path':str(CULLINAN/(e['sha256']+'.glb.gz')),'entry':{**e,'rootTranslation':approved['rootTranslation']}}})
 rows=[primary,*recovered];assert len(rows)==len({r['uid'] for r in rows})==38 and HARBOURSIDE not in {r['uid'] for r in rows};return frozen,rows

def start():
 frozen,rows=assembly_rows();neighbour=read(DOC/'neighbour-inputs.json.gz');ids={r['uid'] for r in rows};assert set(read(SUPPORT/'inputs.json.gz')['requestedUids'])==(ids-{UID})|{HARBOURSIDE};save(DOC/'assembly-selection.json.gz',{**frozen,'manifestSHA256':h(ROOT/'3d-viewer/city/data/manifest.json'),'rows':rows})
 resources={'building:'+u for u in ids|{HARBOURSIDE}}|{('building:' if r['building']['uid'].startswith('landsd/') else 'source-form:')+r['building']['uid'] for r in neighbour['rows']};claim=s.reservations.claim('codex-elements-assembly-'+str(uuid.uuid4()),sorted(resources),batch=BATCH);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));s.call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])

def owned():
 assert s.reservations.owns(read(LOCAL/'reservation.json'));selection=read(DOC/'assembly-selection.json.gz');rows=selection['rows'];ids={r['uid'] for r in rows};restoration=read(DOC/'restoration.json');terrain_source=ROOT/restoration['path'];assert restoration['exactApprovedTerrainMatch'] and h(terrain_source)==restoration['approvedSHA256']
 catalogue=read(HERE/'accepted/government-xxl-20260911/catalogue.json');entries=[];forms={};browser_forms=[];landmarks={UID,*CULLINANS,'landsd/201351:0','landsd/203737:0','landsd/80649:0','landsd/270607:0'}
 for row in rows:
  e=dict(row['candidate']['entry']);e['asset']='assets/'+e['sha256']+'.glb.gz';e.update(label=row['source']['building'].get('name') or e['modelId'],priority='landmark' if row['uid'] in landmarks else 'detail',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,placementReview='Exact UID/CSUID-matched unchanged government source in the Elements estate assembly; native podium dependencies and terrain are scripted with no AI modelling or geometry edits.')
  if row['uid']!=UID and row['uid']!='landsd/268080:0':e['supportDependencies']=[{'uid':UID,'state':'candidate'}]
  src=Path(row['candidate']['path']);assert h(src)==e['sha256'];dst=STAGE/e['asset'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);row['candidate']={'path':str(dst),'entry':e};entries.append(e);forms[row['uid']]=row['source'];b=dict(row['source']['building']);b['tile']=Path(row['source']['tile']).stem;browser_forms.append(b)
 save(DOC/'assembly-selection.json.gz',selection);catalogue.update(area='Elements estate original government source assembly',counts={'packedModels':len(entries)},models=entries);save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':len(entries),'catalogues':['catalogue.json']});save(STAGE/'source-forms.json',browser_forms);save(LOCAL/'source-forms.json',forms)
 terrain_target=STAGE/'terrain-elements-native.json';shutil.copyfile(terrain_source,terrain_target);terrain={'source':rel(terrain_target),'sha256':h(terrain_target),'destination':'city/data/terrain-elements-native.json','resolution':1,'area':'Elements original native terrain'}
 neighbour=read(DOC/'neighbour-inputs.json.gz');neighbour['candidateIds']=sorted(ids);neighbour['patches']=[{'path':rel(terrain_target),'sha256':h(terrain_target),'uids':sorted(ids),'bounds':neighbour['patches'][0]['bounds']}];save(DOC/'assembly-neighbour-inputs.json.gz',neighbour)
 original=DOC/'neighbour-inputs.json.gz';checks_path=DOC/'neighbour-checks.json';backup=original.read_bytes();checks_backup=checks_path.read_bytes();original.write_bytes((DOC/'assembly-neighbour-inputs.json.gz').read_bytes())
 try:s.call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);shutil.copyfile(DOC/'neighbour-checks.json',DOC/'assembly-neighbour-checks.json')
 finally:original.write_bytes(backup);checks_path.write_bytes(checks_backup)
 save(DOC/'terrain-candidates.json',[{'path':rel(terrain_target),'sha256':h(terrain_target),'uids':sorted(ids)}]);s.call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'assembly-selection.json.gz'),'--candidates',rel(STAGE),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'assembly-metrics.json')])
 v=subprocess.run(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(STAGE),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'assembly-validation.json')],cwd=ROOT);assert v.returncode in (0,1)
 dep=read(HERE.parent/'identity-four-native/dependency-replacements.json');assert dep['changes'][0]['uid']==HARBOURSIDE and dep['changes'][0]['supportDependencies']==[{'uid':UID,'state':'candidate'}];assert h(ROOT/dep['catalogues'][0]['source'])==dep['catalogues'][0]['oldSHA256'];support=read(ROOT/dep['contactReport']);sr={r['uid']:r for r in support['rows']};assert sr[HARBOURSIDE]['contacts']==sr[HARBOURSIDE]['rimSamples'] and all(sr[u]['contacts']==sr[u]['rimSamples'] for u in CULLINANS)
 metrics=read(DOC/'assembly-metrics.json');reasons=[]
 for row in metrics['rows']:
  if row.get('error') or not row.get('sourcePreserved') or row.get('missingTerrain'):reasons.append('source-integrity-or-terrain-coverage')
  if row.get('maxSamplerDelta',0)>.004:reasons.append('rendered-terrain-disagreement')
  if row.get('budget') and any(row['budget'][k]>metrics['profiles']['mobile'][k] for k in ('triangles','geometryBytes','residentBytes')):reasons.append('mobile-runtime-budget')
 for vr in read(DOC/'assembly-validation.json')['results']:
  if vr['outcome']=='validation-exception':reasons.append('runtime-validation-exception')
  e=next(x for x in entries if x['uid']==vr['uid']);allowed={'sampled-ground-gap-below-model-bottom','sampled-terrain-above-model-bottom'} if e.get('supportDependencies') or e['uid']==UID else set();reasons.extend(x for x in vr.get('concerns',[]) if x not in allowed)
 blocked=read(DOC/'assembly-neighbour-checks.json')['patches'][0]['blockedBy'];unresolved=[u for u in blocked if u not in ids and u!=HARBOURSIDE]
 if unresolved:reasons.append('terrain-correction-regresses-unresolved-neighbours')
 result={'uid':UID,'newModels':len(entries),'existingDependencyMigrations':[HARBOURSIDE],'policy':'original-government-elements-assembly-v1','passed':not reasons,'reasons':sorted(set(reasons)),'blockedNeighbours':blocked,'unresolvedNeighbours':unresolved,'terrainSHA256':terrain['sha256'],'aiCalls':0,'modelGeometryChanges':0,'publication':False};save(DOC/'assembly-result.json',result)
 if result['passed']:
  destination='city/data/official-models/'+BATCH+'/catalogue.json';plan={'areas':[{'area':catalogue['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':destination}],'topLevelTerrainPatches':[terrain],'dependencyReviews':[{'path':rel(HERE.parent/'identity-four-native/dependency-replacements.json'),'sha256':h(HERE.parent/'identity-four-native/dependency-replacements.json'),'visualApproval':{'path':rel(HERE.parent/'identity-four-native/migration-approval.json'),'sha256':h(HERE.parent/'identity-four-native/migration-approval.json')}}]};save(STAGE/'plan.json',plan);save(STAGE/'browser-config.json',{'stage':rel(STAGE)+'/','doc':rel(DOC)+'/','catalogueURL':destination,'terrain':[terrain],'fitBox':True,'browserUids':[UID,*sorted(CULLINANS),'landsd/201351:0'],'failureTestUids':[UID],'catalogueReplacements':[{'url':dep['catalogues'][0]['url'],'source':rel(HERE.parent/'identity-four-native/harbourside-migrated-catalogue.json')}]})
 print(json.dumps(result))

if __name__=='__main__':owned() if len(sys.argv)>1 else start()
