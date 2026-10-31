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
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'xl-terrain-recovery-20261011-mount-verdant-pair-current-inputs-v1'
BATCH='government-xl-terrain-recovery-mount-verdant-pair-authentic-current-v1-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';SOURCES={'landsd/261717:0':'c8e54f42cd1f52ce94d1112a5c51bd58674fdbe38d8af6ac0de2b9498fbddec1','landsd/75782:0':'4d3d6e5e5b08c6f33b1ce710161edc3554998f7afc7ee15ce29577f9e4c2f781'};UIDS=list(SOURCES);MANIFEST='b61c0bc2d706793c7d436ef3334ccb41e93675d3d50c29818a2dca3b56f8830e'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def region(rows):
 second=module('mount_region','xl-second-pass.py');parent=read(ROOT/'3d-viewer/city/data/terrain.json');positions={};rects=[]
 for row in rows:
  raw=(ROOT/row['candidate']['path']).read_bytes();position=packed_world_bounds(raw);assert position==row['completeOriginalPOSITIONProof'];actual=position['originalWholeSourceBounds'];assert actual==row['native']['model']['worldBounds'],'Original POSITION extent differs; broaden reviewed proposal before execution';rects.append(second.resolution.rectangle_for(actual,parent));positions[row['uid']]=position
 cells=[min(r[0]for r in rects),min(r[1]for r in rects),max(r[2]for r in rects),max(r[3]for r in rects)];return second.resolution.extent(cells,parent),positions

def owned():
 lease=read(LEASE);assert reservations.owns(lease);receipt=read(INPUT/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for name in ['check-selection.json.gz','context.json.gz']:assert ref(INPUT/name)in receipt['evidenceRefs']
 selected=read(INPUT/'check-selection.json.gz');assert selected['manifestSHA256']==MANIFEST and [r['uid']for r in selected['rows']]==UIDS;rows=selected['rows'];contexts={r['uid']:r for r in read(INPUT/'context.json.gz')['rows']};assert set(contexts)==set(UIDS)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST;current=read(manifest);cats=[ref(ROOT/'3d-viewer'/u)for u in current['officialModelCatalogues']];assert not any(e['uid']in UIDS for r in cats for e in read(ROOT/r['path'])['models'])
 bounds,positions=region(rows);DOC.mkdir(parents=True);(DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes());exact={};identitypaths={}
 for row in rows:
  uid=row['uid'];assert row['sourceSHA256']==SOURCES[uid]==digest((ROOT/row['candidate']['path']).read_bytes())
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
  suffix=uid.split('/')[1].replace(':','-');exact[uid]=exact_identity(row,contexts[uid],LOCAL/('exact-current-cell-replay-'+suffix));assert exact[uid]['passed']and exact[uid]['proof']['identityAccepted'];save(DOC/('exact-current-identity-'+suffix+'.json'),exact[uid]);legacy=pipeline_identity(row,contexts[uid],LOCAL/('pipeline-current-cell-replay-'+suffix));assert legacy['passed'];identitypaths[uid]=DOC/('owned-source-identity-'+suffix+'.json');save(identitypaths[uid],legacy)
 index=module('mount_authentic_indexed','xl-owned-indexed-terrain-continuation.py');folder,terrainreceipt=index.terrain_sheet('11-NE-25A',LOCAL);save(DOC/'source-recovery.json',dict(uids=UIDS,sheets=[terrainreceipt],publication=False,sourceGeometryChanges=0))
 pipeline=module('mount_current_physical_pipeline','xl-routed-cell-contact-resolution.py');pipeline.BATCH=BATCH;pipeline.BASE=INPUT;pipeline.DOC=DOC;pipeline.LOCAL=LOCAL;pipeline.UIDS=UIDS;pipeline.SOURCE=folder;pipeline.ADJACENT_SOURCES=[];pipeline.OWNED_IDENTITY_PATHS=identitypaths
 pins=[ref(Path(__file__)),ref(HERE/'xl-routed-cell-contact-resolution.py'),ref(HERE/'xl-owned-indexed-terrain-continuation.py'),ref(HERE/'exact_original_georef_cell_identity_20261009.py'),ref(HERE/'routed_original_cell_identity.py'),ref(HERE/'exact_packed_world_bounds_v3_20261010.py'),ref(INPUT/'check-selection.json.gz'),ref(INPUT/'context.json.gz'),ref(INPUT/'result.json'),start,*cats,*[ref(ROOT/r['candidate']['path'])for r in rows]]
 pins.extend(ref(ROOT/'3d-viewer'/tile)for context in contexts.values()for tile in context['neighbourTileHashes'])
 original_call=pipeline.call
 def fenced_call(*args,**kwargs):
  original_call(*args,**kwargs);assert ref(manifest)==start and all(ref(ROOT/r['path'])==r for r in pins),'Current inputs changed during candidate-only physical run'
 pipeline.call=fenced_call
 try:pipeline.owned()
 except AssertionError as error:
  save(DOC/'guard-failure.json',dict(error=str(error),traceback=traceback.format_exc(),currentAcceptance=False,publication=False,sourceGeometryChanges=0));reasons=['raw-terrain-or-physical-guard:'+str(error)]
 else:
  metrics=read(DOC/'metrics.json');found=read(DOC/'foundation.json');validation=read(DOC/'validation.json');policy=module('mount_raw_acceptance_policy','acceptance-policy.py');assert [r['uid']for r in metrics['rows']]==[r['uid']for r in found['rows']]==[r['uid']for r in validation['results']]==UIDS;assert all(r['sourceSHA256']==SOURCES[r['uid']]for r in found['rows']);reasons=[]
  for row,metric,foundation,result in zip(rows,metrics['rows'],found['rows'],validation['results']):
   uid=row['uid'];reasons.extend(uid+':'+r for r in policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCES[uid],identityProof=exact[uid]['proof']),metric,metrics['profiles']['mobile']))
   if not foundation['strictFoundationAccepted']:reasons.append(uid+':whole-source-foundation')
   reasons.extend(uid+':'+r for r in result.get('concerns',[]))
  native=read(DOC/'native-neighbour-checks.json');resolved=set(native['resolved']);reasons.extend('native-neighbour-regression:'+u for u in set(native['blocked'])-resolved);reasons.extend('terrain-regresses-neighbour:'+r['uid']for r in read(DOC/'neighbour-checks.json')['rows']if r['reasons']and r['uid']not in resolved)
 assert ref(manifest)==start and reservations.owns(lease)and all(ref(ROOT/r['path'])==r for r in pins);save(DOC/'current-pair-physical-diagnostic.json',dict(uids=UIDS,sourceSHA256ByUID=SOURCES,completeOriginalPOSITIONProofByUID=positions,proposedTerrainRegion=bounds,rawReasons=sorted(set(reasons)),noSourceRolesOrRootExceptionsApplied=True,exactCurrentIdentityRefs=[ref(DOC/('exact-current-identity-'+uid.split('/')[1].replace(':','-')+'.json'))for uid in UIDS],legacyRawPipelineIdentityRefs=[ref(identitypaths[uid])for uid in UIDS],currentManifest=start,completeCurrentCatalogueRefs=cats,sourceGeometryChanges=0,terrainProposalCreated=True,terrainGeometryProposalMustBeReviewed=True,currentAcceptance=False,newlyInstalled=0,evidenceRefs=pins))
 freeze=module('mount_physical_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');paths=[ROOT/r['path']for r in pins]+[p for p in DOC.rglob('*')if p.is_file()]+[p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json'];freeze.freeze(BATCH,'mount-pair-complete-current-original-tin-all-raw-physical-gates-diagnostic-v1',paths,dict(uids=UIDS,rawReasons=sorted(set(reasons)),sourceGeometryChanges=0,terrainProposalCreated=True,currentAcceptance=False,newlyInstalled=0))

def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();selected=read(INPUT/'check-selection.json.gz');assert [r['uid']for r in selected['rows']]==UIDS;bounds,_=region(selected['rows']);forms=module('mount_lease_all_current_forms','xl-final-script-pass.py').load_forms(bounds);uids=sorted({b['uid']for b,_,_ in forms}|set(UIDS))
 claim=reservations.claim('mount-pair-authentic-current-'+str(uuid.uuid4()),['building:'+u for u in uids]+['terrain-patch:'+uid for uid in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
