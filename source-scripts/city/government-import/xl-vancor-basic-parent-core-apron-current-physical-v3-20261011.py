"""Complete current unchanged ordinary physical replay of a changed terrain proposal.

No installation, source/actor omission or support/foreign/numeric waiver. The
terrain proposal's surface diagnostics remain distinct from full physical gates.
"""
import importlib.util,json,shutil,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_original_georef_cell_identity_20261009 import verify_files
from dependency_preflight import from_catalogues
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-vancor-authentic-tin-retained-pak-shing-current-physical-v1-20261011';PROPOSAL=BASE/'government-xl-vancor-basic-parent-core-apron-terrain-proposal-v4-20261011';INPUT=BASE/'government-xl-vancor-authentic-tin-retained-pak-shing-current-inputs-v2-20261011'
ACTUAL=BASE/'government-xl-vancor-own-retained-actual-render-capture-v2-20261011';BASIC=BASE/'government-xl-vancor-basic-253697-whole-projection-diagnostic-v2-20261011';INTERFACES=BASE/'government-xl-vancor-basic-parent-core-apron-packed-interfaces-diagnostic-v3-20261011'
BATCH='government-xl-vancor-basic-parent-core-apron-current-physical-v3-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;OLD=HERE/'local'/PRIOR.name;LEASE=LOCAL/'reservation.json';UID='landsd/147956:0';MANIFEST='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def owned():
 lease=read(LEASE);assert reservations.owns(lease);assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST
 prior=read(PRIOR/'result.json');proposal=read(PROPOSAL/'result.json');inputs=read(INPUT/'result.json');actual_receipt=read(ACTUAL/'result.json');basic_receipt=read(BASIC/'result.json');interface_receipt=read(INTERFACES/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in [prior,proposal,inputs,actual_receipt,basic_receipt,interface_receipt]:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  assert not c.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=%s',(UID,)).fetchone()
 checked=[]
 for p in [PRIOR/'selection.json.gz',PRIOR/'neighbour-inputs.json.gz',OLD/'catalogue.json',OLD/'source-forms.json',OLD/'catalogue-index.json']:
  assert ref(p)in prior['evidenceRefs'];checked.append(ref(p))
 for p in [PROPOSAL/'terrain-candidates.json',PROPOSAL/'diagnostic.json.gz']:
  assert ref(p)in proposal['evidenceRefs'];checked.append(ref(p))
 diagnostic=read(PROPOSAL/'diagnostic.json.gz');assert diagnostic['completeActualBasicCovered']and diagnostic['completeGuardFootprintCovered']and diagnostic['completeOuterEnvelopeUpperSeamWithinUnchanged2mm'],'Proposed finite coverage/seam remains failed'
 assert ref(INPUT/'check-selection.json.gz')in inputs['evidenceRefs']and ref(ACTUAL/'complete-actual-render-geometry.json.gz')in actual_receipt['evidenceRefs']and ref(BASIC/'complete-current-basic-geometry.json.gz')in basic_receipt['evidenceRefs']
 assert ref(INTERFACES/'diagnostic.json.gz')in interface_receipt['evidenceRefs']and read(INTERFACES/'diagnostic.json.gz')['allPackedInterfaceUpperSeamsWithinUnchanged2mm']
 assert read(INPUT/'post-mount-exact-regional-rebind.json')['complete80CurrentFormAndExistingNativeTuplesExactlyEqual']
 selected=read(INPUT/'check-selection.json.gz');assert selected['manifestSHA256']==MANIFEST and len(selected['rows'])==1;row=selected['rows'][0];assert row['uid']==UID
 source=ROOT/row['candidate']['path'];assert ref(source)in prior['evidenceRefs']and digest(source.read_bytes())==row['sourceSHA256'];checked.append(ref(source))
 actual=read(ACTUAL/'complete-actual-render-geometry.json.gz');basic=read(BASIC/'complete-current-basic-geometry.json.gz');assert actual['startAndEndInputsVerified']and basic['startAndEndInputsVerified']
 rows=actual['rows'];assert [r['uid']for r in rows]==[UID,'landsd/186864:0']
 historical_actual=read(BASE/'government-xl-vancor-own-retained-actual-render-capture-v1-20261011/complete-actual-render-geometry.json.gz');assert rows==historical_actual['rows'],'Actual source/Pak entire attribute/matrix tuple changed'
 historical_basic=read(BASE/'government-xl-vancor-basic-253697-whole-projection-diagnostic-v1-20261011/complete-current-basic-geometry.json.gz');assert basic['actor']==historical_basic['actor']and basic['actor']['completeFaces']==48
 idx=np.asarray(rows[0]['completeOriginalIndex'],int).reshape(-1,3);streams={'providerOriginal':decode_original_world_triangles(source.read_bytes())}
 for mode,key in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftAssociatedF32ModelMatrix','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32ModelMatrix','completeExplicitBalancedFloat32WorldPosition')]:streams[mode]=np.asarray(rows[0][key],dtype='<f8').reshape(-1,3)[idx]
 assert {k:digest(v.astype('<f8').tobytes())for k,v in streams.items()}==diagnostic['sourceStreamSHA256s'],'Historical numeric terrain proof cannot transfer to changed source arithmetic'
 DOC.mkdir(parents=True);(DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes());raw=source.read_bytes();dest=LOCAL/'assets'/source.name;dest.parent.mkdir(parents=True);dest.write_bytes(raw);row['candidate']['path']=str(dest.relative_to(ROOT));selected['batch']=BATCH;save(DOC/'selection.json.gz',selected)
 for name in ['catalogue.json','catalogue-index.json','source-forms.json']:shutil.copyfile(OLD/name,LOCAL/name)
 deps=from_catalogues(manifest,[LOCAL/'catalogue.json']);save(DOC/'dependency-preflight.json',deps);assert not any(r['blockers']for r in deps['rows'])
 context=read(INPUT/'context.json.gz')['rows'][0];identity=verify_files(row,context,LOCAL/'current-identity-replay');assert identity['passed'];save(DOC/'exact-current-identity.json',identity)
 terrain=read(PROPOSAL/'terrain-candidates.json');assert len(terrain)==1 and terrain[0]['uids']==[UID]and terrain[0]['replaces']['retainedUids']==['landsd/186864:0'];tp=ROOT/terrain[0]['path'];assert ref(tp)in proposal['evidenceRefs']and ref(tp)['sha256']==terrain[0]['sha256'];save(DOC/'terrain-candidates.json',terrain)
 neighbours=read(PRIOR/'neighbour-inputs.json.gz');
 for path,sha in list(neighbours['inputHashes'].items()):
  if path=='3d-viewer/city/data/manifest.json':neighbours['inputHashes'][path]=MANIFEST
  else:assert digest((ROOT/path).read_bytes())==sha,'Changed original neighbour input requires independent new qualification: '+path
 assert len(neighbours['rows'])==80 and len({r['building']['uid']for r in neighbours['rows']})==80;assert neighbours['candidateIds']==[UID];neighbours['patches']=terrain;save(DOC/'neighbour-inputs.json.gz',neighbours)
 pins=[ref(Path(__file__)),ref(manifest),*[ref(ROOT/p)for p in neighbours['inputHashes']],*[ref(ROOT/'3d-viewer'/url)for url in read(manifest)['officialModelCatalogues']],*checked,ref(tp),ref(INPUT/'context.json.gz'),ref(INPUT/'result.json'),ref(PRIOR/'result.json'),ref(PROPOSAL/'result.json')]
 for captured in [actual,basic]:
  for path,sha in captured['inputHashes'].items():
   assert digest((ROOT/path).read_bytes())==sha; pins.append(ref(ROOT/path))
 for directory in [ACTUAL,BASIC,INTERFACES]:
  pins.extend(ref(p)for p in directory.rglob('*')if p.is_file())
 for name in ['acceptance-metrics.mjs','check-neighbours.mjs','check-native-neighbours.mjs','native-neighbour-policy.mjs','acceptance-policy.py','xl-final-script-pass.py','exact_original_georef_cell_identity_20261009.py','dependency_preflight.py']:pins.append(ref(HERE/name))
 def call(args,allowed=(0,)):
  process=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);save(DOC/('command-'+str(len(list(DOC.glob('command-*.json'))))+'.json'),dict(args=args,exitCode=process.returncode,stdout=process.stdout,stderr=process.stderr));assert process.returncode in allowed,process.stderr;assert reservations.owns(lease)and all(ref(ROOT/r['path'])==r for r in pins),'Current input/source/module drift'
 rel=lambda p:str(p.relative_to(ROOT))
 call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
 call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1))
 call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
 runtime=read(LOCAL/'runtime-geometry.json.gz')['rows'][0];tri=np.asarray(runtime['position']).reshape(-1,3)[np.asarray(runtime['index']).reshape(-1,3)];ground=np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3);final=module('vancor_complete_changed_ground_foundation','xl-final-script-pass.py');b=row['source']['building'];f=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));foundation=dict(uid=UID,sourceSHA256=row['sourceSHA256'],foundation=f,strictFoundationAccepted=f['completeTerrainTriangles']==f['triangles']and not f['fullyBuriedUpwardTriangles']and f['fullyBuriedAreaFraction']==0);save(DOC/'foundation.json',foundation)
 metrics=read(DOC/'metrics.json');policy=module('vancor_changed_ground_raw_policy','acceptance-policy.py');reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=row['sourceSHA256'],identityProof=identity['proof']),metrics['rows'][0],metrics['profiles']['mobile']);reasons+=[]if foundation['strictFoundationAccepted']else['whole-source-foundation'];reasons+=read(DOC/'validation.json')['results'][0].get('concerns',[])
 native=read(DOC/'native-neighbour-checks.json');resolved=set(native['resolved']);reasons+=['native-neighbour-regression:'+u for u in set(native['blocked'])-resolved];reasons+=['terrain-regresses-neighbour:'+r['uid']for r in read(DOC/'neighbour-checks.json')['rows']if r['reasons']and r['uid']not in resolved]
 save(DOC/'diagnostic.json',dict(uid=UID,currentManifest=start,rawReasons=sorted(set(reasons)),fullCurrentNeighbourForms=80,completeCurrentNativeCensus=6642,fullFreshActualOwnPakAttributeMatrixAndFourStreamsReplayed=True,completeFresh48BasicAndAll294PackedInterfacesRebound=True,proposedTerrain=ref(tp),sourceGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,terrainRepresentationExplicitlyChanged=True,currentAcceptance=False,installationApproved=False,evidenceRefs=pins))
 assert all(ref(ROOT/r['path'])==r for r in pins)and reservations.owns(lease)
 paths=[ROOT/r['path']for r in pins]+[p for p in DOC.rglob('*')if p.is_file()]+[p for p in LOCAL.rglob('*')if p.is_file()and p!=LEASE];module('vancor_changed_ground_complete_physical_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'changed-terrain-parent-core-apron-complete-current-ordinary-foundation-neighbour-native-runtime-post-mount-diagnostic-v3',paths,dict(uids=[UID],rawReasons=sorted(set(reasons)),sourceGeometryChanges=0,currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(dict(rawReasons=sorted(set(reasons)),strictFoundation=foundation['strictFoundationAccepted'],currentAcceptance=False)))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();forms=read(INPUT/'complete-proposed-region-current-forms.json.gz')['rows'];uids=sorted({r['building']['uid']for r in forms});assert len(uids)==80
 claim=reservations.claim('vancor-changed-core-apron-'+str(uuid.uuid4()),['building:'+u for u in uids]+['terrain-patch:'+UID,'terrain-surface:city/data/government-native-186864-0.json'],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
