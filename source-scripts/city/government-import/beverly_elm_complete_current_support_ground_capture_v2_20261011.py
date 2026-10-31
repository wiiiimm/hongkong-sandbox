"""DRAFT read-only full actual drawn-ground capture for two exact original support actors.
Execution requires root stable manifest pin. No proposed terrain, installation or acceptance.
"""
import argparse,importlib.util,subprocess,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-beverly-elm-complete-current-support-ground-capture-v2-20261011';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH
EXPECTED={'landsd/255939:0':('8503f33cdfee1ab9730821c4024bd8a7ac8b807a05109971c61c06fed0e9d8bc',12640),'landsd/258892:0':('8a4ff3f17f25fbf7f974e38955e83b4ff078665e477b42b7b53a8c800aed9c6b',764)}
RANK=B/'xl-terrain-recovery-20261010-next-current-native-cap-source-only-ranking-v1/diagnostic.json.gz';ELM=B/'government-xl-elm-tree-podium-physical-20261007';NOM=B/'government-xl-fixed295-simple-source-support-nomination-census-v1-20261011';HISTORY=['government-xl-terrain-recovery-255543-original-physical-v1-20261009','government-xl-elm-tree-podium-physical-20261007','government-xl-elm-tree-podium-outside-parent-20261007']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(p):
 s=importlib.util.spec_from_file_location('reviewed_current_form_loader',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--manifest-sha256');parser.add_argument('--preflight-only',action='store_true');args=parser.parse_args()
 rank=next(r for r in read(RANK)['rows']if r['uid']=='landsd/255543:0');native=rank['completeCandidateNativeInventory'][0];cached=next(r for r in read(ELM/'selection.json.gz')['rows']if r['uid']=='landsd/258892:0');sources={'landsd/255939:0':ROOT/native['asset']['path'],'landsd/258892:0':ROOT/cached['candidate']['path']};triangles={}
 for uid,p in sources.items():
  sha,count=EXPECTED[uid];assert ref(p)['sha256']==sha;triangles[uid]=decode_original_world_triangles(p.read_bytes());assert triangles[uid].shape==(count,3,3)and np.isfinite(triangles[uid]).all()
 if args.preflight_only:print(json.dumps(dict(exactSourceUIDHashes=EXPECTED,wholeFaces={u:len(t)for u,t in triangles.items()},mutableCurrentRead=False,executionApproved=False)));return
 assert args.manifest_sha256 and len(args.manifest_sha256)==64;assert not DOC.exists()and not LOCAL.exists(),'Preserve any completed/partial capture; separate version required';manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==args.manifest_sha256;current=read(manifest);pins={};pin=lambda p:pins.setdefault(str(p.relative_to(ROOT)),digest(p.read_bytes()))
 pin(manifest);pin(ROOT/'3d-viewer/city/data/terrain.json');catalogues=[ROOT/'3d-viewer'/url for url in current['officialModelCatalogues']];terrain=[ROOT/'3d-viewer'/r['url']for r in current['terrainPatches']]
 for p in catalogues+terrain:pin(p)
 installed={};installedcat={}
 for cat in catalogues:
  for e in read(cat)['models']:assert e['uid']not in installed;installed[e['uid']]=e;installedcat[e['uid']]=cat
 assert 'landsd/255939:0'in installed and 'landsd/258892:0'not in installed,'Source publication state differs; separately reviewed capture needed'
 assert installed['landsd/255939:0']['sha256']==EXPECTED['landsd/255939:0'][0]
 for p in [Path(__file__),RANK,ELM/'selection.json.gz',NOM/'result.json',HERE/'beverly_elm_current_support_actual_render_attributes_v2_20261011.mjs',HERE/'beverly_elm_capture_module_closures_v2_20261011.mjs',HERE/'literal_production_module_dependency_closure_20261010.mjs',HERE/'actual_float32_model_matrix_bounds_20261011.mjs',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py']+list(sources.values()):pin(p)
 for name in ['government-xl-beverly-hill-k-original-carrier-bounded-grade-route-diagnostic-v1-20261011','government-xl-elm-tree-b-original-podium-complete-finite-contact-inventory-v1-20261011']:
  for filename in ['diagnostic.json.gz','result.json']:pin(B/name/filename)
 historical=[]
 for name in HISTORY:
  doc=B/name;one=dict(batch=name,rawReasons=read(doc/'result.json')['reasons'],evidenceRefs=[],savedForeignAndNativeRows=[])
  for name2 in ['result.json','neighbour-inputs.json.gz','neighbour-checks.json','native-neighbour-checks.json']:
   p=doc/name2
   if p.exists():pin(p);one['evidenceRefs'].append(ref(p));x=read(p);one['savedForeignAndNativeRows'].append(dict(file=name2,rows=x.get('rows',[]),blocked=x.get('blocked'),resolved=x.get('resolved')))
  historical.append(one)
 final=module(HERE/'xl-final-script-pass.py');rows=[];allforms={};bodybindings=[]
 for uid in EXPECTED:
  tri=triangles[uid];lo,hi=tri.min((0,1)),tri.max((0,1));forms=final.load_forms([float(lo[0]-30),float(lo[2]-30),float(hi[0]+30),float(hi[2]+30)]);form,_,tile=next(r for r in forms if r[0]['uid']==uid)
  for f,_,t in forms:allforms[f['uid']]=dict(building=f,tile=t,installedNative=f['uid']in installed);pin(ROOT/'3d-viewer'/t)
  entry=installed[uid]if uid in installed else cached['candidate']['entry'];assert entry['uid']==uid and entry['sha256']==EXPECTED[uid][0]and entry['triangles']==EXPECTED[uid][1];assert entry['buildingCSUID']==form['buildingCSUID'];bounds=np.asarray(entry['worldBounds']);assert np.all(lo>=bounds[0]-1)and np.all(hi<=bounds[1]+1),'Broadphase bounds fail to contain complete original source'
  asset=sources[uid]
  if uid in installed:
   liveasset=installedcat[uid].parent/entry['asset'];pin(liveasset);assert ref(liveasset)['sha256']==EXPECTED[uid][0]
  dest=LOCAL/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(asset.read_bytes());row=dict(uid=uid,sourceSHA256=EXPECTED[uid][0],candidate=dict(entry=entry,path=str(dest.relative_to(ROOT))),source=dict(building=form,tile=tile,tileSHA256=ref(ROOT/'3d-viewer'/tile)['sha256']));rows.append(row);bodybindings.append(dict(uid=uid,originalSource=ref(asset),completeOriginalFaces=len(tri),completeOriginalWorldSHA256=digest(tri.tobytes()),installedEntryPreserved=uid in installed,entry=entry,currentForm=form,currentTile=ref(ROOT/'3d-viewer'/tile)))
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=start['sha256']));save(DOC/'terrain-candidates.json',[]);save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='diagnostic-original-support-catalogue',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=[r['candidate']['entry']for r in rows],counts=dict(packedModels=2)));save(LOCAL/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']))
 save(DOC/'support-source-preflight.json',dict(currentManifest=start,bodySourceBindings=bodybindings,allCurrentCatalogueRefs=[ref(p)for p in catalogues],allCurrentTerrainRefs=[ref(p)for p in terrain],historicalObligations=historical,fullCurrentRelevantForeignBasicAndNativeFormInventory=list(allforms.values()),noForeignRegressionDischarged=True,noNativeReapproval=True,noTerrainProposal=True,currentAcceptance=False))
 def fence():
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 def call(command):fence();subprocess.run(command,cwd=ROOT,check=True);fence()
 rel=lambda p:str(p.relative_to(ROOT));call(['node',str(HERE/'beverly_elm_capture_module_closures_v2_20261011.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
 save(DOC/'literal-source-inputs.json.gz',dict(rows=[dict(uid=r['uid'],path=r['candidate']['path'],entry=r['candidate']['entry'],building=r['source']['building'])for r in rows],currentManifest=start,currentCatalogueRefs=[ref(p)for p in catalogues],evidenceRefs=[ref(DOC/'selection.json.gz')]+[ref(ROOT/r['candidate']['path'])for r in rows]));call(['node',str(HERE/'beverly_elm_current_support_actual_render_attributes_v2_20261011.mjs'),rel(DOC/'literal-source-inputs.json.gz'),rel(DOC/'actual-render-geometry.json.gz')]);call(['node',str(HERE/'beverly_elm_capture_module_closures_v2_20261011.mjs'),rel(DOC)+'/','--verify'])
 runtime=read(LOCAL/'runtime-geometry.json.gz');actual=read(DOC/'actual-render-geometry.json.gz');assert {r['uid']for r in runtime['rows']}==set(EXPECTED)
 for r in runtime['rows']:
  idx=np.asarray(r['index']).reshape(-1,3);world=np.asarray(r['position']).reshape(-1,3)[idx];ground=np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3);assert len(world)==EXPECTED[r['uid']][1]and len(ground)>0;source=next(r2 for r2 in actual['rows']if r2['uid']==r['uid']);assert source['completeOriginalIndex']==r['index']and source['completeLiteralWorldPosition']==r['position'];lo,hi=np.asarray(rows[[x['uid']for x in rows].index(r['uid'])]['candidate']['entry']['worldBounds']);
  for positions in [source['completeLiteralWorldPosition'],source['completeExplicitLeftAssociatedFloat32WorldPosition'],source['completeExplicitBalancedFloat32WorldPosition']]:
   points=np.asarray(positions).reshape(-1,3);assert np.all(points.min(0)>=lo-1)and np.all(points.max(0)<=hi+1),'Complete arithmetic source outside actual-ground broadphase'
 for x in [runtime,actual,read(DOC/'metrics.json')]:
  for p,h in x.get('inputHashes',{}).items():assert digest((ROOT/p).read_bytes())==h,p
 fence();save(DOC/'capture-scope.json',dict(currentManifest=start,startEndInputsVerified=True,inputHashes=pins,allCurrentTerrainPatchesPreserved=True,terrainCandidates=[],completeRelevantActualGround='Every actual makeTerrain indexed/nonindexed Float32 triangle whose closed XZ AABB intersects each complete source bounds expanded1m; includes complete intersecting triangles, no clipping or sampled surface. Actual literal/left/balanced F32 source bounds independently contained in same broadphase.',completeGroundRows=[dict(uid=r['uid'],faces=len(r['drawnGroundGeometry'])//9,worldSHA256=digest(np.asarray(r['drawnGroundGeometry'],dtype=float).reshape(-1,3,3).tobytes()))for r in runtime['rows']],noForeignRegressionDischarged=True,noGradeRootCredit=True,nativeReapproval=False,currentAcceptance=False,installationApproved=False,newlyInstalled=0))
 print(json.dumps(dict(completeSupportGroundCaptured=True,sourceOnly=True,currentAcceptance=False)))
if __name__=='__main__':main()
