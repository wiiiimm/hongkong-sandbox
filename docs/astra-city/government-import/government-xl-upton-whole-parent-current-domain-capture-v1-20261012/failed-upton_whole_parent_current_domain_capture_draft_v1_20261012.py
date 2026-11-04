"""UNEXECUTED: full current parent-domain terrain/actor attribution only.

No source/pose/candidate/terrain/review/acceptance changes. No make_patch.
Completed fresh6649 scalar tuples nominate native loads, never physical credit.
"""
from pathlib import Path
from fractions import Fraction as F
import ast,importlib.util,json,subprocess,sys,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-whole-parent-current-domain-capture-v1-20261012'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
DOMAIN=BASE/'government-xl-upton-whole-parent-routing-domain-proposal-v1-20261012/domain.json'
PRIOR=BASE/'government-xl-upton-three-original-complete-current-runtime-capture-v4-20261012'
CENSUS=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v4-20261012'
METHOD=BASE/(BATCH+'-proposal')/'METHOD.md';PREFLIGHT=METHOD.parent/'unexecuted-schema-pin-check.json'
ACTOR=HERE/'upton_whole_parent_current_domain_actors_draft_v1_20261012.mjs'
GROUND=HERE/'upton_whole_parent_current_domain_ground_draft_v1_20261012.mjs'
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
UIDS=['landsd/338946:0','landsd/12728:0','landsd/12662:0'];RETAINED='landsd/79882:0';FOREIGN='landsd/254809:0'
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(pin):
 p=ROOT/pin['path'];assert p.is_file()and ref(p)==pin,pin;return p
def intersects(bounds,box):
 lo,hi=bounds;return hi[0]>=box[0]and lo[0]<=box[2]and hi[2]>=box[1]and lo[2]<=box[3]
def closure():
 todo=[Path(__file__),FREEZER];out={}
 while todo:
  p=todo.pop().resolve()
  if str(p)in out:continue
  out[str(p)]=ref(p)
  for n in ast.walk(ast.parse(p.read_text())):
   names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
   for name in names:
    for folder in[HERE,HERE.parent/'shared-modelling']:
     q=folder/(name.replace('.','/')+'.py')
     if q.is_file():todo.append(q)
 return list(out.values())
def prepare(refs,pulse):
 domain=read(DOMAIN);assert ref(DOMAIN)['sha256']=='20fbb1692b81b3807c82222ad796723f216403083e59e9440fd5990b6e15bbb9'
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifestpath)==domain['currentManifest']and ref(manifestpath)['sha256']==CURRENT
 for folder in[PRIOR,CENSUS]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.append(ref(folder/'result.json'))
  for pin in receipt['evidenceRefs']:check(pin);refs.append(pin);pulse()
 assert ref(CENSUS/'result.json')==domain['freshCurrentNativeCensusResult']
 census=read(CENSUS/'inventory.json.gz');cin=read(CENSUS/'input.json.gz')
 assert census['completeNativeActors']==census['successfullyCapturedActors']==6649 and not census['errors']and census['startAndEndInputHashesVerified']
 for p,h in census['inputHashes'].items():pin=dict(path=p,sha256=h);check(pin);refs.append(pin)
 manifest=read(manifestpath);basepath=ROOT/'3d-viewer/city/data/terrain.json';base=read(basepath);parentpath=check(domain['retainedParent']);parent=read(parentpath)
 assert parent['coarseCells']==domain['oldCoarseCells']==[457,449,459,451]
 assert parent['meta']['targetUids']==[RETAINED],'Exact actual meta.targetUids required'
 for native in parent['meta']['source']['nativeSources']:
  for pin in native['sourceFiles']:check(pin);refs.append(pin)
 g=base['meta']['georef'];boxes=[b for a in domain['owned']for b in a['completeUnusedBounds'].values()]
 low=[min(b[0][k]for b in boxes)for k in range(3)];high=[max(b[1][k]for b in boxes)for k in range(3)]
 floor=lambda x:x.numerator//x.denominator;ceil=lambda x:-floor(-x)
 xn=lambda x:(F(float(x))+F(834500)-F(g['bE']))/F(g['aE']);zn=lambda z:(F(816500)-F(float(z))-F(g['bN']))/F(g['aN'])
 nominated=[floor(xn(low[0])),floor(zn(low[2])),ceil(xn(high[0])),ceil(zn(high[2]))];old=parent['coarseCells']
 cells=[min(old[0],nominated[0]),min(old[1],nominated[1]),max(old[2],nominated[2]),max(old[3],nominated[3])]
 extent=[g['bE']+cells[0]*g['aE']-834500,816500-(g['bN']+cells[1]*g['aN']),g['bE']+cells[2]*g['aE']-834500,816500-(g['bN']+cells[3]*g['aN'])]
 assert cells==domain['rederivedWholeDomainCells']==[457,449,460,451]and extent==domain['wholeDomainXZ']==[-2477.5,-37.5,-2267.5,102.5]
 pg=parent['meta']['georef'];parentextent=[pg['bE']-834500,816500-pg['bN'],pg['bE']+pg['aE']*(pg['W']-1)-834500,816500-(pg['bN']+pg['aN']*(pg['H']-1))]
 oldextent=[g['bE']+old[0]*g['aE']-834500,816500-(g['bN']+old[1]*g['aN']),g['bE']+old[2]*g['aE']-834500,816500-(g['bN']+old[3]*g['aN'])]
 assert parentextent==oldextent==[-2477.5,-37.5,-2337.5,102.5]
 for p in[manifestpath,basepath,parentpath,DOMAIN]:refs.append(ref(p))
 installed={};cats=[]
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;cats.append(ref(p));refs.append(ref(p))
  for e in read(p)['models']:assert e['uid']not in installed;installed[e['uid']]=(p,e)
 assert len(installed)==6649 and not set(UIDS)&set(installed)
 forms={};tiles={};basic_scope=[];omitted=[]
 # Read every tile, not just metadata-selected cells: distant rings can extend.
 for tile in manifest['tiles']:
  p=ROOT/'3d-viewer'/tile['url'];data=read(p);pin=ref(p);refs.append(pin)
  for f in data['buildings']:
   assert f['uid']not in forms;forms[f['uid']]=f;tiles[f['uid']]=dict(tile=tile['url'],tileRef=pin)
   if f['uid']in installed or f['uid']in UIDS:continue
   coords=[v for ring in f.get('rings',[])for v in ring]
   # Raw embedded modelGeometry cannot be excluded using footprint bounds.
   if not coords or f.get('modelGeometry'):basic_scope.append(f['uid']);continue
   a=np.asarray(coords,float);assert a.ndim==2 and a.shape[1]==2 and np.isfinite(a).all()
   # Current BASIC extrusion uses sourced rings; illustrative posts stay inside.
   # Include raw and outward Float32 extrema; no near-boundary FP exclusion.
   af=a.astype(np.float32);lo=np.minimum(a.min(0),np.nextafter(af.min(0),np.float32(-np.inf)).astype(float));hi=np.maximum(a.max(0),np.nextafter(af.max(0),np.float32(np.inf)).astype(float))
   bounds=[[float(lo[0]),0,float(lo[1])],[float(hi[0]),0,float(hi[1])]]
   if intersects(bounds,extent):basic_scope.append(f['uid'])
   else:omitted.append(dict(uid=f['uid'],completeRingAndOutwardFloat32Bounds=bounds,tileRef=pin,strictlyDisjointFromWholeDomain=True))
 assert set(UIDS+[RETAINED,FOREIGN])<=set(forms)
 # Exact fresh tuple rebind: full raw entry, source, current form, all modules.
 cm={r['uid']:r for r in census['rows']};im={r['uid']:r for r in cin['rows']};assert len(cm)==len(im)==6649
 nominees=[];excluded=[]
 for uid,(cat,e)in installed.items():
  r=cm[uid];q=im[uid];assert q['rawCurrentEntry']==e and q['currentBuilding']==forms[uid]and q['source']['sha256']==r['sourceSHA256']==e['sha256'];check(q['source']);refs.append(q['source'])
  boxes=[r['completeOriginalPOSITIONProof']['originalWholeSourceBounds'],r['completeLiteralBounds'],r['completeLeftAssociatedF32Bounds'],r['completeBalancedF32Bounds']]
  hits=[i for i,b in enumerate(boxes)if intersects(b,extent)]
  if hits:nominees.append(dict(uid=uid,path=q['source']['path'],entry=e,building=forms[uid],role='installed-native-context',freshScalarTuple=r,catalogue=ref(cat),**tiles[uid]))
  else:excluded.append(dict(uid=uid,sourceSHA256=e['sha256'],allFourCompleteUnusedBounds=boxes,strictlyDisjointFromWholeDomain=True))
 assert [r['uid']for r in nominees]==[RETAINED]
 priorrows=read(PRIOR/'selection.json.gz')['rows'];actorrows=[]
 for d,r in zip(domain['owned'],priorrows):
  uid=d['uid'];assert r['uid']==uid and r['candidate']['entry']['uid']==uid and r['sourceSHA256']==d['source']['sha256']
  path=check(d['source']);refs.append(d['source']);proof=packed_world_bounds(path.read_bytes());assert proof['allOriginalPositionVerticesAccounted']and proof['originalWholeSourceBounds']==d['completeUnusedBounds']['original']
  assert r['candidate']['entry']['buildingCSUID']==forms[uid]['buildingCSUID']
  actorrows.append(dict(uid=uid,path=d['source']['path'],entry=r['candidate']['entry'],building=forms[uid],role='owned-original',completeOriginalPOSITIONProof=proof,previousWholeUnusedBounds=d['completeUnusedBounds'],**tiles[uid]))
 # Preserve foreign254809 even if geometry is outside the domain nomination.
 assert FOREIGN not in installed
 if FOREIGN not in basic_scope:basic_scope.append(FOREIGN)
 basics=[dict(uid=u,building=forms[u],**tiles[u])for u in sorted(basic_scope)]
 requested=set(cin['currentAllNativeSourceForms'])|set(UIDS)|set(basic_scope)
 for uid,f in cin['currentAllNativeSourceForms'].items():assert forms[uid]==f
 supplied=[forms[u]for u in sorted(requested)]
 terrainrefs=[ref(ROOT/'3d-viewer'/p['url'])for p in manifest['terrainPatches']];refs+=terrainrefs
 return dict(currentManifest=ref(manifestpath),expectedNativeCount=6649,domain=extent,rederivedCoarseCells=cells,retainedParent=ref(parentpath),retainedParentExactCurrentData=parent,retainedParentEntry=[p for p in manifest['terrainPatches']if '3d-viewer/'+p['url']==domain['retainedParent']['path']],ownedRows=actorrows,nativeRows=nominees,basicRows=basics,completeCurrentForms=supplied,currentCatalogueRefs=cats,currentTerrainRefs=terrainrefs,completeFreshNativeNomination=dict(receipt=ref(CENSUS/'result.json'),inventory=ref(CENSUS/'inventory.json.gz'),nomineeUIDs=[r['uid']for r in nominees],excludedRows=excluded,wholeUnusedFourWorldScope=True),completeBasicOmissionInventory=omitted,noTerrainProposal=True,currentAcceptance=False)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pre=read(PREFLIGHT);assert pre['passed']and pre['caller']==ref(Path(__file__))and pre['actorExporter']==ref(ACTOR)and pre['groundExporter']==ref(GROUND)and pre['method']==ref(METHOD)
 refs=closure()+[ref(METHOD),ref(PREFLIGHT),ref(ACTOR),ref(GROUND)];input=prepare(refs,pulse)
 DOC.mkdir(parents=True);save(DOC/'input.json.gz',dict(**input,evidenceRefs=list({(p['path'],p['sha256']):p for p in refs}.values())));refs.append(ref(DOC/'input.json.gz'))
 def fence():
  for pin in refs:check(pin)
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT; pulse(True)
 for script in[ACTOR,GROUND]:
  fence();p=subprocess.run(['node',str(script),str(DOC.relative_to(ROOT))],cwd=ROOT,capture_output=True,text=True);save(DOC/(script.stem+'-actual-log.json'),dict(exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr;fence()
 for name in['whole-domain-current-actors.json.gz','whole-domain-actual-parent-attribution.json.gz']:
  p=DOC/name;out=read(p);refs.append(ref(p))
  for path,h in out['inputHashes'].items():pin=dict(path=path,sha256=h);check(pin);refs.append(pin)
 fence();s=importlib.util.spec_from_file_location('upton_domain_freezer',FREEZER);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'whole-parent-domain-current-drawn-terrain-and-bounded-actual-actor-attribution',list({p['path']:check(p)for p in refs}.values()),dict(uids=UIDS+[RETAINED],currentManifest=input['currentManifest'],completeNativeNominationCount=6649,currentAcceptance=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0,noTerrainProposal=True))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();uids=UIDS+[RETAINED,FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-whole-parent-capture-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
