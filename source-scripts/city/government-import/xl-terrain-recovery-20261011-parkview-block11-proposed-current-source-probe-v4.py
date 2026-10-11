"""Read-only complete current Parkview Block11 and original installed carrier probe.

Explicit terrain candidate only; no identity acceptance, native reapproval or installation.
Candidate computation retains canonical source leases and manifest/input fences.
"""
import importlib.util,json,os,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BASE=ROOT/'docs/astra-city/government-import';SCOUT=BASE/'xl-terrain-recovery-20261010-next-current-native-cap-source-only-ranking-v1'
BATCH='government-xl-terrain-recovery-parkview-block11-complete-original-proposed-current-probe-v4-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/254491:0','landsd/255647:0']
PROPOSAL=BASE/'xl-terrain-recovery-20261011-parkview-authentic-foreign-preserved-terrain-proposal-v4'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);current=read(manifest);originals={};forms={};matches=[];refs=[ref(Path(__file__)),ref(SCOUT/'diagnostic.json.gz'),start]
 for uid in UIDS[1:]:
  rank=next(r for r in read(SCOUT/'diagnostic.json.gz')['rows']if r['uid']==uid);selection=ROOT/rank['cachedSelection']['path'];original=next(r for r in read(selection)['rows']if r['uid']==uid);assert original['sourceSHA256']==rank['sourceSHA256'];originals[uid]=original;refs.append(ref(selection))
 for tile in current['tiles']:
  p=ROOT/'3d-viewer'/tile['url']
  for b in read(p)['buildings']:
   if b['uid']in UIDS:assert b['uid']not in forms;forms[b['uid']]=dict(building=b,tile=tile['url'],tileSHA256=digest(p.read_bytes()))
 assert set(forms)==set(UIDS)
 for url in current['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url
  for e in read(path)['models']:
   if e['uid']in UIDS:matches.append((path,e))
 assert len(matches)==1 and matches[0][1]['uid']==UIDS[0];cat,native=matches[0];catalogue=read(cat);native=dict(native,rootTranslation=catalogue['rootTranslation'],coordinatePolicy=catalogue.get('coordinatePolicy'),datasetId=catalogue.get('datasetId'));native_asset=cat.parent/native['asset'];proof=packed_world_bounds(native_asset.read_bytes());assert proof['sourceSHA256']==native['sha256']=='8d1de7a507bedd3b321786220569d5ff4ee279496220bd1e5c93580411c7ad77';assert native['buildingCSUID']==forms[UIDS[0]]['building']['buildingCSUID']
 catalogue_start={url:ref(ROOT/'3d-viewer'/url)for url in current['officialModelCatalogues']};refs.extend(catalogue_start.values());refs.append(ref(BASE/'government-xl-all-installed-dependency-metadata-applied-v1-20261010/result.json'))
 rows=[]
 for uid in UIDS:
  if uid==UIDS[0]:
   row=dict(uid=uid,modelId=native['modelId'],name=forms[uid]['building'].get('name'),sourceSHA256=native['sha256'],triangles=proof['completeOriginalTriangles'],native=dict(model=dict(triangles=proof['completeOriginalTriangles'],worldBounds=proof['originalWholeSourceBounds'])),candidate=dict(path=str(native_asset.relative_to(ROOT)),entry=native),source=forms[uid]);assert row['triangles']==63133
  else:
   row=dict(originals[uid]);assert row['source']['building']['buildingCSUID']==forms[uid]['building']['buildingCSUID'] and row['source']['building']['objectId']==forms[uid]['building']['objectId'];row['source']=forms[uid]
  raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']==row['candidate']['entry']['sha256'];dest=LOCAL/row['candidate']['entry']['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);row['candidate']=dict(row['candidate'],path=str(dest.relative_to(ROOT)));rows.append(row);refs.extend([ref(dest),ref(ROOT/'3d-viewer'/forms[uid]['tile'])])
 refs.extend([ref(cat),ref(native_asset),ref(HERE/'exact_packed_world_bounds_v3_20261010.py')]);save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=start['sha256'],alreadyInstalledActorIncludedOnlyForOriginalSupportGeometry=UIDS[0],diagnosticOnly=True,sourceGeometryChanges=0,publication=False,newlyInstalled=0));save(LOCAL/'catalogue.json',dict(models=[r['candidate']['entry']for r in rows]));receipt=read(PROPOSAL/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 assert ref(PROPOSAL/'diagnostic.json.gz')in receipt['evidenceRefs']
 candidates=read(PROPOSAL/'terrain-candidates.json');assert len(candidates)==1 and candidates[0]['uids']==[UIDS[1]]
 assert digest((ROOT/candidates[0]['path']).read_bytes())==candidates[0]['sha256'];save(DOC/'terrain-candidates.json',candidates)
 refs.extend([ref(PROPOSAL/'result.json'),ref(PROPOSAL/'diagnostic.json.gz'),ref(PROPOSAL/'terrain.json'),ref(PROPOSAL/'terrain-candidates.json'),ref(ROOT/candidates[0]['path'])])
 module_snapshot=DOC/'production-module-closure.json'
 js="import{writeFileSync}from'node:fs';import{snapshotModuleClosure}from'./source-scripts/city/government-import/literal_production_module_dependency_closure_20261010.mjs';const root=new URL('./',import.meta.url);writeFileSync(process.argv[1],JSON.stringify(snapshotModuleClosure(new URL('source-scripts/city/government-import/acceptance-metrics-multi-retained.mjs',root),root)));"
 subprocess.run(['node','--input-type=module','-e',js,str(module_snapshot)],cwd=ROOT,check=True)
 closure=read(module_snapshot);assert closure['completeAuditedLiteralImportClosure']is True and closure['unsupportedDynamicImports']==0
 for path,sha in closure['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ref(ROOT/path))
 refs.extend([ref(module_snapshot),ref(HERE/'literal_production_module_dependency_closure_20261010.mjs')])
 subprocess.run(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 for path,sha in closure['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 assert ref(manifest)==start and reservations.owns(lease)
 for url,r in catalogue_start.items():assert ref(ROOT/'3d-viewer'/url)==r
 metrics=read(DOC/'metrics.json');assert [r['uid']for r in metrics['rows']]==UIDS and not any(r.get('error')for r in metrics['rows']);geometry=read(LOCAL/'runtime-geometry.json.gz');assert [r['uid']for r in geometry['rows']]==UIDS
 for path,sha in geometry['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ref(ROOT/path))
 refs.extend([ref(DOC/'selection.json.gz'),ref(DOC/'metrics.json'),ref(LOCAL/'runtime-geometry.json.gz')]);s=importlib.util.spec_from_file_location('parkview-block11-two_source_probe_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'read-only-proposed-authentic-current-two-original-parkview-block11-carrier-runtime-source-geometry-v4',[ROOT/r['path']for r in {r['path']:r for r in refs}.values()],dict(uids=UIDS,completeProductionModuleDependencyClosure=ref(module_snapshot),productionModules=len(closure['modules']),sourceGeometryChanges=0,alreadyInstalledOriginalSupportActor=UIDS[0],noTerrainProposal=False,terrainProposalGeometryChanged=True,diagnosticOnly=True,currentIdentityAcceptance=False,fullAcceptance=False,nativeReacceptance=False,publication=False,newlyInstalled=0,metrics=[dict(uid=r['uid'],minSurfaceGap=r['minSurfaceGap'],minLowGap=r['minLowGap'],maxLowGap=r['maxLowGap'],maxSamplerDelta=r['maxSamplerDelta'],missingTerrain=r['missingTerrain'])for r in metrics['rows']]));print(dict(sourceProbePassed=True,publication=False),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('parkview-block11-current-source-probe-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
