"""Joint two-original authentic-TIN candidate and complete raw physical gates.

No publication flock, source geometry change, invented support bridge, visual-role
approval or installation. Exact current cell identity AND legacy pipeline cell
identity both replay. All complete foreign current forms/native checks stay raw.
"""
from pathlib import Path
from types import SimpleNamespace
import importlib.util,json,subprocess,sys,uuid,traceback
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files as exact_identity
from routed_original_cell_identity import verify_files as pipeline_identity
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BASE=ROOT/'docs/astra-city/government-import';PROBE=BASE/'government-xl-terrain-recovery-sparkle-tower-podium-current-probe-v1-20261011';INPUT=BASE/'xl-terrain-recovery-20261011-sparkle-tower-podium-pair-current-inputs-v1'
BATCH='government-xl-terrain-recovery-sparkle-tower-podium-pair-authentic-current-v1-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';SOURCES={'landsd/242198:0':'5dcc709e25d0801ae3e2cef4a59c214babfa2adc4de42ce5fd956e649315c3f3','landsd/228000:0':'7429ad91552966b7e5ab6717626cb8e84d195da698140bcaf0b57ce890b89800'};UIDS=list(SOURCES);MANIFEST='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def region(rows):
 second=module('sparkle_region','xl-second-pass.py');parent=read(ROOT/'3d-viewer/city/data/terrain.json');positions={};rects=[]
 for row in rows:
  raw=(ROOT/row['candidate']['path']).read_bytes();position=packed_world_bounds(raw);assert position==row['completeOriginalPOSITIONProof'];actual=position['originalWholeSourceBounds'];assert actual==row['native']['model']['worldBounds'],'Original POSITION extent differs; broaden reviewed proposal before execution';rects.append(second.resolution.rectangle_for(actual,parent));positions[row['uid']]=position
 cells=[min(r[0]for r in rects),min(r[1]for r in rects),max(r[2]for r in rects),max(r[3]for r in rects)];return second.resolution.extent(cells,parent),positions

def owned():
 lease=read(LEASE);assert reservations.owns(lease);receipt=read(INPUT/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for pin in receipt['evidenceRefs']:
  path=ROOT/pin['path'];assert path.is_file() and digest(path.read_bytes())==pin['sha256']
 for name in ['check-selection.json.gz','context.json.gz','indexed-preflight.json']:assert ref(INPUT/name)in receipt['evidenceRefs']
 selected=read(INPUT/'check-selection.json.gz');assert selected['manifestSHA256']==MANIFEST and [r['uid']for r in selected['rows']]==UIDS;rows=selected['rows'];contexts={r['uid']:r for r in read(INPUT/'context.json.gz')['rows']};assert set(contexts)==set(UIDS)
 closure_path=PROBE/'production-module-closure.json';closure=read(closure_path);assert closure['completeAuditedLiteralImportClosure'] is True and closure['unsupportedDynamicImports']==0
 module_pins=[ref(closure_path)]
 for path,sha in closure['inputHashes'].items():
  assert digest((ROOT/path).read_bytes())==sha;module_pins.append(ref(ROOT/path))
 routing=read(INPUT/'indexed-preflight.json')['rows'];assert [r['uid'] for r in routing]==UIDS
 assert all(r['canStartTerrainWork'] and r['primarySheetIntersects'] and r['indexedSheetsCoverCompleteOriginalXZBounds'] and set(r['requiredOriginalSheets']) <= {'11-NW-13A','11-NW-13B'} for r in routing)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST;current=read(manifest);cats=[ref(ROOT/'3d-viewer'/u)for u in current['officialModelCatalogues']];assert not any(e['uid']in UIDS for r in cats for e in read(ROOT/r['path'])['models'])
 bounds,positions=region(rows);DOC.mkdir(parents=True);(DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes());exact={};identitypaths={}
 for row in rows:
  uid=row['uid'];assert row['sourceSHA256']==SOURCES[uid]==digest((ROOT/row['candidate']['path']).read_bytes())
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
  suffix=uid.split('/')[1].replace(':','-');exact[uid]=exact_identity(row,contexts[uid],LOCAL/('exact-current-cell-replay-'+suffix));assert exact[uid]['passed']and exact[uid]['proof']['identityAccepted'];save(DOC/('exact-current-identity-'+suffix+'.json'),exact[uid]);legacy=pipeline_identity(row,contexts[uid],LOCAL/('pipeline-current-cell-replay-'+suffix));assert legacy['passed'];identitypaths[uid]=DOC/('owned-source-identity-'+suffix+'.json');save(identitypaths[uid],legacy)
 index=module('sparkle_authentic_indexed','xl-owned-indexed-terrain-continuation.py');folder,terrainreceipt=index.terrain_sheet('11-NW-13A',LOCAL);adjacent,adjacentreceipt=index.terrain_sheet('11-NW-13B',LOCAL);save(DOC/'source-recovery.json',dict(uids=UIDS,sheets=[terrainreceipt,adjacentreceipt],publication=False,sourceGeometryChanges=0))
 pipeline=module('sparkle_current_physical_pipeline','xl-routed-cell-contact-resolution.py');pipeline.BATCH=BATCH;pipeline.BASE=INPUT;pipeline.DOC=DOC;pipeline.LOCAL=LOCAL;pipeline.UIDS=UIDS;pipeline.SOURCE=folder;pipeline.ADJACENT_SOURCES=[adjacent];pipeline.OWNED_IDENTITY_PATHS=identitypaths
 pins=[ref(Path(__file__)),ref(HERE/'xl-routed-cell-contact-resolution.py'),ref(HERE/'xl-owned-indexed-terrain-continuation.py'),ref(HERE/'exact_original_georef_cell_identity_20261009.py'),ref(HERE/'routed_original_cell_identity.py'),ref(HERE/'exact_packed_world_bounds_v3_20261010.py'),ref(INPUT/'check-selection.json.gz'),ref(INPUT/'context.json.gz'),ref(INPUT/'result.json'),start,*cats,*[ref(ROOT/r['candidate']['path'])for r in rows]]
 pins.extend(ref(ROOT/'3d-viewer'/tile)for context in contexts.values()for tile in context['neighbourTileHashes'])
 pins.extend(module_pins)
 original_call=pipeline.call
 def fenced_call(*args,**kwargs):
  original_call(*args,**kwargs);assert ref(manifest)==start and all(ref(ROOT/r['path'])==r for r in pins),'Current inputs changed during candidate-only physical run'
 pipeline.call=fenced_call
 try:pipeline.owned()
 except AssertionError as error:
  save(DOC/'guard-failure.json',dict(error=str(error),traceback=traceback.format_exc(),currentAcceptance=False,publication=False,sourceGeometryChanges=0));reasons=['raw-terrain-or-physical-guard:'+str(error)]
 else:
  metrics=read(DOC/'metrics.json');found=read(DOC/'foundation.json');validation=read(DOC/'validation.json');policy=module('sparkle_raw_acceptance_policy','acceptance-policy.py');assert [r['uid']for r in metrics['rows']]==[r['uid']for r in found['rows']]==[r['uid']for r in validation['results']]==UIDS;assert all(r['sourceSHA256']==SOURCES[r['uid']]for r in found['rows']);reasons=[]
  for row,metric,foundation,result in zip(rows,metrics['rows'],found['rows'],validation['results']):
   uid=row['uid'];reasons.extend(uid+':'+r for r in policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCES[uid],identityProof=exact[uid]['proof']),metric,metrics['profiles']['mobile']))
   if not foundation['strictFoundationAccepted']:reasons.append(uid+':whole-source-foundation')
   reasons.extend(uid+':'+r for r in result.get('concerns',[]))
  native=read(DOC/'native-neighbour-checks.json');resolved=set(native['resolved']);reasons.extend('native-neighbour-regression:'+u for u in set(native['blocked'])-resolved);reasons.extend('terrain-regresses-neighbour:'+r['uid']for r in read(DOC/'neighbour-checks.json')['rows']if r['reasons']and r['uid']not in resolved)
 assert ref(manifest)==start and reservations.owns(lease)and all(ref(ROOT/r['path'])==r for r in pins);save(DOC/'current-pair-physical-diagnostic.json',dict(uids=UIDS,sourceSHA256ByUID=SOURCES,completeOriginalPOSITIONProofByUID=positions,proposedTerrainRegion=bounds,rawReasons=sorted(set(reasons)),noSourceRolesOrRootExceptionsApplied=True,exactCurrentIdentityRefs=[ref(DOC/('exact-current-identity-'+uid.split('/')[1].replace(':','-')+'.json'))for uid in UIDS],legacyRawPipelineIdentityRefs=[ref(identitypaths[uid])for uid in UIDS],currentManifest=start,completeCurrentCatalogueRefs=cats,sourceGeometryChanges=0,terrainProposalCreated=True,terrainGeometryProposalMustBeReviewed=True,currentAcceptance=False,newlyInstalled=0,evidenceRefs=pins))
 freeze=module('sparkle_physical_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');paths=[ROOT/r['path']for r in pins]+[p for p in DOC.rglob('*')if p.is_file()]+[p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json'];freeze.freeze(BATCH,'sparkle-pair-complete-current-original-tin-all-raw-physical-gates-diagnostic-v1',paths,dict(uids=UIDS,rawReasons=sorted(set(reasons)),sourceGeometryChanges=0,terrainProposalCreated=True,wholeCurrent6648NativeAlteredDomainCheckStillRequired=True,currentAcceptance=False,newlyInstalled=0))

def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();selected=read(INPUT/'check-selection.json.gz');assert [r['uid']for r in selected['rows']]==UIDS;bounds,_=region(selected['rows']);forms=module('sparkle_lease_all_current_forms','xl-final-script-pass.py').load_forms(bounds);uids=sorted({b['uid']for b,_,_ in forms}|set(UIDS))
 claim=reservations.claim('sparkle-pair-authentic-current-'+str(uuid.uuid4()),[('building:' if u.startswith('landsd/') else 'foreign-form:')+u for u in uids]+['terrain-patch:'+uid for uid in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
