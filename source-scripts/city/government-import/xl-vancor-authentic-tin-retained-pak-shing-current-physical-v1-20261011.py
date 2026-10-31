"""Fresh Vancor-only original-TIN terrain candidate and complete raw physical gates.

No publication flock, source geometry change, cross-actor support bridge, visual-role
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
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'government-xl-vancor-authentic-tin-retained-pak-shing-current-inputs-v1-20261011'
BATCH='government-xl-vancor-authentic-tin-retained-pak-shing-current-physical-v1-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';UID='landsd/147956:0';PARENT='city/data/government-native-186864-0.json';SOURCE='acf35402e274ec2010d4a96d63cf6ca74c7a689615a48c47d7be7798063e8b58';MANIFEST='b61c0bc2d706793c7d436ef3334ccb41e93675d3d50c29818a2dca3b56f8830e'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def region(row):
 second=module('vancor_region','xl-second-pass.py');parent=read(ROOT/'3d-viewer/city/data/terrain.json');raw=(ROOT/row['candidate']['path']).read_bytes();position=packed_world_bounds(raw);assert position==row['completeOriginalPOSITIONProof'];actual=position['originalWholeSourceBounds'];assert actual==row['native']['model']['worldBounds'],'Original POSITION extent differs; broaden reviewed proposal before execution';cells=second.resolution.rectangle_for(actual,parent);old=read(ROOT/'3d-viewer'/PARENT)['coarseCells'];cells=[min(cells[0],old[0]),min(cells[1],old[1]),max(cells[2],old[2]),max(cells[3],old[3])];bounds=second.resolution.extent(cells,parent);inp=read(INPUT/'proposal-input.json');assert cells==inp['proposedCoarseCells']and bounds==inp['proposedRegionBounds']and position==inp['wholeOwnedPOSITIONProof']and ref(ROOT/'3d-viewer'/PARENT)==inp['retainedParent'];return bounds,position

def owned():
 lease=read(LEASE);assert reservations.owns(lease);receipt=read(INPUT/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for name in ['check-selection.json.gz','context.json.gz','proposal-input.json','complete-proposed-region-current-forms.json.gz']:assert ref(INPUT/name)in receipt['evidenceRefs']
 selected=read(INPUT/'check-selection.json.gz');assert selected['manifestSHA256']==MANIFEST and len(selected['rows'])==1;row=selected['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SOURCE;context=read(INPUT/'context.json.gz')['rows'][0]
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST;current=read(manifest);cats=[ref(ROOT/'3d-viewer'/u)for u in current['officialModelCatalogues']];assert not any(e['uid']==UID for r in cats for e in read(ROOT/r['path'])['models'])
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==SOURCE;bounds,position=region(row);DOC.mkdir(parents=True);(DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes())
 exact=exact_identity(row,context,LOCAL/'exact-current-cell-replay');assert exact['passed']and exact['proof']['identityAccepted'];save(DOC/'exact-current-identity.json',exact)
 legacy=pipeline_identity(row,context,LOCAL/'pipeline-current-cell-replay');assert legacy['passed'];save(DOC/'owned-source-identity.json',legacy)
 index=module('vancor_authentic_indexed','xl-owned-indexed-terrain-continuation.py');folder,terrainreceipt=index.terrain_sheet('11-NW-24D',LOCAL);save(DOC/'source-recovery.json',dict(uid=UID,sheets=[terrainreceipt],publication=False,sourceGeometryChanges=0))
 pipeline=module('vancor_current_physical_pipeline','xl-routed-cell-contact-resolution.py');pipeline.BATCH=BATCH;pipeline.BASE=INPUT;pipeline.DOC=DOC;pipeline.LOCAL=LOCAL;pipeline.UIDS=[UID];pipeline.SOURCE=folder;pipeline.ADJACENT_SOURCES=[];pipeline.RETAIN_NATIVE_URL=PARENT;pipeline.NESTED_PARENT=False;pipeline.ALLOW_BASIC_TERRAIN_TARGETS=False;pipeline.RETAIN_NATIVE_MODEL_REGIONS_ONLY=False
 pins=[ref(Path(__file__)),ref(HERE/'xl-routed-cell-contact-resolution.py'),ref(HERE/'xl-owned-indexed-terrain-continuation.py'),ref(HERE/'exact_original_georef_cell_identity_20261009.py'),ref(HERE/'routed_original_cell_identity.py'),ref(HERE/'exact_packed_world_bounds_v3_20261010.py'),ref(INPUT/'check-selection.json.gz'),ref(INPUT/'context.json.gz'),ref(INPUT/'result.json'),ref(INPUT/'proposal-input.json'),ref(INPUT/'complete-proposed-region-current-forms.json.gz'),ref(ROOT/'3d-viewer'/PARENT),ref(ROOT/read(INPUT/'proposal-input.json')['retainedAsset']['path']),ref(ROOT/row['candidate']['path']),start,*cats]
 original_call=pipeline.call
 def fenced_call(*args,**kwargs):
  original_call(*args,**kwargs);assert ref(manifest)==start and all(ref(ROOT/r['path'])==r for r in pins),'Current inputs changed during candidate-only physical run'
 pipeline.call=fenced_call
 try:pipeline.owned()
 except AssertionError as error:
  save(DOC/'guard-failure.json',dict(error=str(error),traceback=traceback.format_exc(),currentAcceptance=False,publication=False,sourceGeometryChanges=0));reasons=['raw-terrain-or-physical-guard:'+str(error)]
 else:
  metrics=read(DOC/'metrics.json');found=read(DOC/'foundation.json');validation=read(DOC/'validation.json');policy=module('vancor_raw_acceptance_policy','acceptance-policy.py');reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCE,identityProof=exact['proof']),metrics['rows'][0],metrics['profiles']['mobile'])
  if not found['rows'][0]['strictFoundationAccepted']:reasons.append('whole-source-foundation')
  reasons.extend(validation['results'][0].get('concerns',[]));native=read(DOC/'native-neighbour-checks.json');resolved=set(native['resolved']);reasons.extend('native-neighbour-regression:'+u for u in set(native['blocked'])-resolved);reasons.extend('terrain-regresses-neighbour:'+r['uid']for r in read(DOC/'neighbour-checks.json')['rows']if r['reasons']and r['uid']not in resolved)
 assert ref(manifest)==start and reservations.owns(lease)and all(ref(ROOT/r['path'])==r for r in pins);save(DOC/'current-podium-only-physical-diagnostic.json',dict(uid=UID,sourceSHA256=SOURCE,completeOriginalPOSITIONProof=position,proposedTerrainRegion=bounds,rawReasons=sorted(set(reasons)),distinctLeeKongPodiumAnd145527RemainFullForeignActors=True,exactCurrentIdentity=ref(DOC/'exact-current-identity.json'),legacyRawPipelineIdentity=ref(DOC/'owned-source-identity.json'),currentManifest=start,completeCurrentCatalogueRefs=cats,sourceGeometryChanges=0,terrainProposalCreated=True,terrainGeometryProposalMustBeReviewed=True,currentAcceptance=False,newlyInstalled=0,evidenceRefs=pins))
 freeze=module('vancor_physical_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');paths=[ROOT/r['path']for r in pins]+[p for p in DOC.rglob('*')if p.is_file()]+[p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json'];freeze.freeze(BATCH,'vancor-podium-only-complete-current-original-tin-raw-physical-diagnostic-v1',paths,dict(uids=[UID],rawReasons=sorted(set(reasons)),sourceGeometryChanges=0,terrainProposalCreated=True,currentAcceptance=False,newlyInstalled=0))

def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();selected=read(INPUT/'check-selection.json.gz');row=selected['rows'][0];bounds,_=region(row);forms=module('vancor_lease_all_current_forms','xl-final-script-pass.py').load_forms(bounds);uids=sorted({b['uid']for b,_,_ in forms}|{UID});assert {'landsd/186864:0','landsd/145527:0','landsd/72296:0'}<=set(uids),'All current Pak Shing and Lee Kong actors remain fully accounted'
 claim=reservations.claim('vancor-podium-authentic-current-'+str(uuid.uuid4()),['building:'+u for u in uids]+['terrain-patch:'+UID,'terrain-surface:'+PARENT],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
