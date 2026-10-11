"""Continue held XL sources with fenced, reproducible compute-only diagnostics."""
import importlib.util,json,sys,uuid,zipfile,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
BASE=ROOT/'docs/astra-city/government-import/government-xl-remaining-20260923'
DOC=BASE/'sol-continuation-20261003'
LOCAL=HERE/'local/sol-continuation-20261003'
LEASE=LOCAL/'reservation.json'
UIDS=read(BASE/'sol-pilot-20261002/packet.json')['uids']
RESOURCES=UIDS+['landsd/175935:0','landsd/233218:0','landsd/254491:0']
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def ref(p):return {'path':str(Path(p).relative_to(ROOT)),'sha256':digest(Path(p).read_bytes())}
def owns():
 r=read(LEASE);assert reservations.owns(r),'Live reservation required';assert reservations.heartbeat(r)['ok']
 if (LOCAL/'job.json').exists():assert jobs.heartbeat(read(LOCAL/'job.json'),lease_seconds=1800),'Job lease lost'
 return r
def start():
 if LEASE.exists() and reservations.owns(read(LEASE)):receipt=owns()
 else:
  claim=reservations.claim('codex-sol-continuation-'+str(uuid.uuid4()),['building:'+u for u in RESOURCES],batch='sol-continuation-20261003');assert claim['ok'],claim
  receipt=json.loads(json.dumps(claim['reservation'],default=str));save(LEASE,receipt)
 if (DOC/'checkpoint.json').exists():return
 stage='sol-compute-continuation-v1'
 payload={'priorReview':ref(BASE/'sol-pilot-20261002/review.json'),'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'uids':UIDS,'geometryChanges':0,'scope':'Scripted source recovery, support and terrain diagnostics; no AI remodelling.'}
 jid=jobs.enqueue('sol-continuation-20261003',stage,payload);job=jobs.claim('sol-continuation-20261003',receipt['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
 save(LOCAL/'job.json',json.loads(json.dumps(job,default=str)))
 save(DOC/'checkpoint.json',{'batch':'sol-continuation-20261003','jobId':jid,'priorReview':payload['priorReview'],'uids':UIDS,'humanStatus':'in-process','scriptAiCalls':0,'modelGeometryChanges':0,'publication':False})
 print({'jobId':jid,'inProcess':len(UIDS)},flush=True)
def recover():
 owns();sys.path.insert(0,str(HERE.parent/'citywide-native'))
 from download import acquire
 from convert import _convert_one
 uid='landsd/175935:0';sheet='6-SE-20D';mid='B293562547102063C0'
 src=HERE/'local/government-xl-remaining-20260923/recovered/sheets'/sheet
 directory=read(src/'directory/result.json');assert directory['directorySHA256']=='7018b6b569a99a511a61f3aa22c31c3857f42da400c45221927697d2e89963ac'
 directory['models']=[m for m in directory['models'] if m['modelId']==mid];assert len(directory['models'])==1
 out=LOCAL/'ocean-pride-support';acquired=acquire(directory,src/'directory/zip-directory.bin',out/'original')
 tile=ROOT/'3d-viewer/city/data/tiles/-3_-5.json';raw=tile.read_bytes();b=next(r for r in json.loads(raw)['buildings'] if r['uid']==uid);assert b['buildingCSUID']=='2935625471P20190531'
 (out/'packed').mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(out/'original'/(sheet+'.zip')) as z:
  name='BUILDING/'+mid+'/'+mid+'.gltf';converted=_convert_one(z,z.getinfo(name),out/'decoded',out/'packed',{}, {'modelId':mid})
 from shapely.geometry import Polygon,MultiPoint
 footprint=Polygon(b['rings'][0],b['rings'][1:]);hull=MultiPoint([(x,z) for x,_,z in converted['terrainSamples']['position']]).convex_hull
 entry={**converted['asset'],'uid':uid,'modelId':mid,'objectId':b['objectId'],'buildingCSUID':b['buildingCSUID'],'label':'Ocean Pride / Tsuen Wan West podium','recordedBaseHeight':b['baseHeightHKPD'],'recordedTopHeight':b['topHeightHKPD'],'worldBounds':converted['worldBounds'],'triangles':converted['triangles'],'footprintCentroidDistanceMetres':hull.centroid.distance(footprint.centroid),'overlapOfSmallerFootprint':hull.intersection(footprint).area/min(hull.area,footprint.area),'placementReviewed':False,'priority':'unreviewed','publicationApproved':False,'rootTranslation':[-834500,0,816500],'sourceTile':sheet}
 asset=out/'packed'/entry['asset'];assert digest(asset.read_bytes())==entry['sha256']
 row={'uid':uid,'source':{'building':b,'tile':str(tile.relative_to(ROOT/'3d-viewer')),'tileSHA256':digest(raw)},'candidate':{'path':str(asset),'entry':entry},'native':{'sheet':sheet,'model':converted,'directPinnedRecovery':True}}
 save(LOCAL/'support-runtime.json.gz',{'rows':[row],'aiCalls':0,'modelGeometryChanges':0})
 report={'uid':uid,'sheet':sheet,'modelId':mid,'sourceSHA256':entry['sha256'],'worldBounds':entry['worldBounds'],'triangles':entry['triangles'],'directorySHA256':directory['directorySHA256'],'sourceETag':directory['etag'],'acquisition':{k:v for k,v in acquired.items() if k!='source'},'runtime':ref(LOCAL/'support-runtime.json.gz'),'aiCalls':0,'modelGeometryChanges':0,'publication':False}
 save(DOC/'ocean-pride-support-recovery.json',report);print({k:report[k] for k in ('uid','triangles','sourceSHA256','worldBounds')},flush=True)

def citywalk_checks():
 owns();checks=module('continuation_citywalk_checks','xl-yoho-mall-ii-acceptance.py');patches=module('continuation_citywalk_patches','native_patch_resolution.py')
 old=BASE/'citywalk-terrain-diagnostic-20260925';doc=DOC/'citywalk';option=read(DOC/'citywalk-terrain-options.json')['diagnosticParentRescue'];source=ROOT/option['candidatePatch']['path'];assert digest(source.read_bytes())==option['candidatePatch']['sha256']
 patch=read(source);bounds=patches._patch_bounds(patch);_,_,missing,excess=patches.projected_context(patch,bounds);original_excess=patch['nativeMesh']['sourceOverlap']['measuredProjectedExcessM2'];assert excess<=original_excess+.25 and missing.area<=.25
 patch['nativeMesh']['source']['numericalCoverageGap']={'policy':'parent-grid-fallback','measuredAreaM2':missing.area,'maximumAreaM2':.25,'maximumFraction':1e-3}
 path=LOCAL/'citywalk/government-native-134332-0.json';evidence=doc/'native-overlap.json';save(path,patch)
 patches.approve_original_overlap(patch,path,evidence,read(old/'native-overlap.json')['source']['files']);patch['nativeMesh']['sourceOverlap']['evidencePath']=str(evidence.relative_to(ROOT));patches.finalize_overlap_evidence(patch,evidence)
 module('continuation_validator','../island-detail-integration/publish.py').validate_patch(patch,read(ROOT/'3d-viewer/city/data/terrain.json'));save(path,patch)
 result={**read(old/'result.json'),'uids':['landsd/134332:0'],'patchPath':str(path.relative_to(ROOT)),'patchSHA256':digest(path.read_bytes())};save(doc/'result.json',result)
 checks.DOC=doc;checks.LOCAL=LOCAL/'citywalk-checks';checks.STAGE=checks.LOCAL/'candidates';sys.argv=[__file__,'prepare'];checks.run()
 # Replace the already installed Citywalk 2 terrain instead of drawing two
 # conflicting versions of the same native TIN; retain and recheck its model.
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');existing=next(p for p in manifest['terrainPatches'] if p['url']=='city/data/government-native-134332-0.json')
 terrain=read(doc/'terrain-candidates.json');terrain[0]['replaces']={'url':existing['url'],'sha256':digest((ROOT/'3d-viewer'/existing['url']).read_bytes()),'retainedUids':['landsd/305615:0']};save(doc/'terrain-candidates.json',terrain)
 inputs=read(doc/'neighbour-inputs.json.gz');inputs['patches']=terrain;save(doc/'neighbour-inputs.json.gz',inputs)
 for command in (
 ['node',str(HERE/'acceptance-metrics.mjs'),'--selection',str((doc/'selection.json.gz').relative_to(ROOT)),'--candidates',str(checks.STAGE.relative_to(ROOT)),'--terrain-candidates',str((doc/'terrain-candidates.json').relative_to(ROOT)),'--out',str((doc/'metrics.json').relative_to(ROOT))],
 ['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',str(checks.STAGE.relative_to(ROOT)),'--source-forms',str((checks.STAGE/'source-forms.json').relative_to(ROOT)),'--terrain-candidates',str((doc/'terrain-candidates.json').relative_to(ROOT)),'--out',str((doc/'validation.json').relative_to(ROOT))],
 ['node',str(HERE/'check-neighbours.mjs'),str(doc.relative_to(ROOT))+'/'],
 ['node',str(HERE/'check-native-neighbours.mjs'),str(doc.relative_to(ROOT))+'/']):
  outcome=subprocess.run(command,cwd=ROOT);assert outcome.returncode in (0,1)

 foundation=module('continuation_citywalk_foundation','xl-phase-one-foundation.py');foundation.DOC=doc;foundation.LOCAL=checks.LOCAL;foundation.UID='landsd/134332:0';foundation.OUTPUT=doc/'foundation.json';foundation.run()


def ocean_checks():
 owns();doc=DOC/'ocean-pride';stage=LOCAL/'ocean-pride-candidates';support=read(LOCAL/'support-runtime.json.gz')['rows'][0]
 old=read(BASE/'citywalk-terrain-diagnostic-20260925/selection.json.gz');tower=next(r for r in old['rows'] if r['uid']=='landsd/273839:0');rows=[support,tower]
 template=read(HERE/'accepted/government-xxl-20260911/catalogue.json');entries=[];forms={}
 for row in rows:
  e=row['candidate']['entry'];source=Path(row['candidate']['path']);assert digest(source.read_bytes())==e['sha256'];target=stage/e['asset'];target.parent.mkdir(parents=True,exist_ok=True)
  import shutil
  shutil.copyfile(source,target);entries.append(e);forms[row['uid']]=row['source']
 template.update(area='Ocean Pride exact original tower and podium diagnostic',models=entries,counts={'packedModels':2});save(stage/'catalogue.json',template);save(stage/'catalogue-index.json',{'models':2,'catalogues':['catalogue.json']});save(stage/'source-forms.json',forms)
 save(doc/'selection.json.gz',{'rows':rows,'manifestSHA256':digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()),'aiCalls':0})
 for command in (
 ['node',str(HERE/'acceptance-metrics.mjs'),'--selection',str((doc/'selection.json.gz').relative_to(ROOT)),'--candidates',str(stage.relative_to(ROOT)),'--out',str((doc/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'ocean-pride-runtime-geometry.json.gz').relative_to(ROOT))],
 ['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',str(stage.relative_to(ROOT)),'--source-forms',str((stage/'source-forms.json').relative_to(ROOT)),'--out',str((doc/'validation.json').relative_to(ROOT))]):
  outcome=subprocess.run(command,cwd=ROOT);assert outcome.returncode in (0,1)


def citywalk_protect():
 owns();mask=module('continuation_citywalk_mask','xl-shared-neighbour-mask-eval.py');doc=DOC/'citywalk';result=read(doc/'result.json');native=read(doc/'native-neighbour-checks.json');resolved=set(native['resolved']);blocked=sorted({u for r in read(doc/'neighbour-checks.json')['patches'] for u in r['blockedBy']}-resolved)
 assert blocked and 'landsd/134332:0' not in blocked
 mask.LOCAL=LOCAL/'citywalk-protected';mask.SOURCE=mask.LOCAL/'input.json';save(mask.SOURCE,{'rows':[{'uid':'landsd/134332:0','site':'citywalk','candidatePatch':{'path':result['patchPath'],'sha256':result['patchSHA256']},'sharedFootprintUids':[{'uid':u} for u in blocked]}]})
 mask.DIAGNOSTIC_DIRS={'citywalk':doc};mask.SOURCE_ASSET_DIRS={'citywalk':LOCAL/'citywalk-checks/candidates'};mask.OUTPUT=DOC/'citywalk-protected-options.json';mask.run()
 masked=read(mask.OUTPUT)['rows'][0];folder=mask.LOCAL/'citywalk';foundation=module('continuation_citywalk_protected_foundation','xl-phase-one-foundation.py');foundation.UID='landsd/134332:0';foundation.LOCAL=LOCAL/'citywalk-checks';foundation.DOC=folder;foundation.SELECTION=doc/'selection.json.gz';foundation.OUTPUT=DOC/'citywalk-protected-foundation.json';save(folder/'result.json',{**result,'patchPath':masked['candidatePatch']['path'],'patchSHA256':masked['candidatePatch']['sha256']});foundation.run()


def festival_checks():
 owns();checks=module('continuation_festival_checks','xl-yoho-mall-ii-acceptance.py');patches=module('continuation_festival_patches','native_patch_resolution.py')
 old=BASE/'festival-pair-rescue-diagnostic-20261002';doc=DOC/'festival';option=read(DOC/'festival-terrain-options.json')['diagnosticParentRescue'];source=ROOT/option['candidatePatch']['path'];assert digest(source.read_bytes())==option['candidatePatch']['sha256']
 patch=read(source);bounds=patches._patch_bounds(patch);_,_,missing,excess=patches.projected_context(patch,bounds);original_excess=patch['nativeMesh']['sourceOverlap']['measuredProjectedExcessM2'];assert excess<=original_excess+.25 and missing.area<=.25
 patch['nativeMesh']['source']['numericalCoverageGap']={'policy':'parent-grid-fallback','measuredAreaM2':missing.area,'maximumAreaM2':.25,'maximumFraction':1e-3}
 path=LOCAL/'festival/government-native-91827-0.json';evidence=doc/'native-overlap.json';save(path,patch)
 patches.approve_original_overlap(patch,path,evidence,read(old/'native-overlap.json')['source']['files']);patch['nativeMesh']['sourceOverlap']['evidencePath']=str(evidence.relative_to(ROOT));patches.finalize_overlap_evidence(patch,evidence)
 module('continuation_festival_validator','../island-detail-integration/publish.py').validate_patch(patch,read(ROOT/'3d-viewer/city/data/terrain.json'));save(path,patch)
 result={**read(old/'result.json'),'uids':['landsd/91827:0'],'patchPath':str(path.relative_to(ROOT)),'patchSHA256':digest(path.read_bytes())};save(doc/'result.json',result)
 checks.DOC=doc;checks.LOCAL=LOCAL/'festival-checks';checks.STAGE=checks.LOCAL/'candidates';sys.argv=[__file__,'prepare'];checks.run()
 foundation=module('continuation_festival_foundation','xl-phase-one-foundation.py');foundation.DOC=doc;foundation.LOCAL=checks.LOCAL;foundation.UID='landsd/91827:0';foundation.OUTPUT=doc/'foundation.json';foundation.run()


def sync():
 receipt=owns();prior=read(BASE/'sol-pilot-20261002/review.json');rows=[dict(r) for r in prior['rows']]
 components={r['uid']:r for r in read(DOC/'source-components.json')['rows']};supports={r['uid']:r for r in read(DOC/'support-contact.json')['rows']}
 updates={
 'landsd/91827:0':('primary-terrain-cleared-upper-neighbour-dependency-unresolved','Exact source-backed lower parent facet selection now passes all 66,130 current terrain samples, 51 low-rim checks, no sampler disagreement and all 18,484 source faces without burial. Standalone neighbour check still flags upper landsd/104302:0; no installation.','Resolve the upper connected low-rim component and paired runtime support, then repeat joint neighbour/browser gates. Do not install the primary alone while the upper fallback hold remains.'),
 'landsd/104302:0':('connected-upper-component-contact-unresolved','The lowest-rim component is connected and has 605/1,224 contacts; 212 samples lack vertical support and 407 have no source layer in the contact interval. Alternate-layer probing does not clear the hold.','Establish the actual support interface of the connected component and distinguish documented overhangs/atrium spans; topology alone is not acceptance.'),
 'landsd/255917:0':('connected-rim-source-support-unresolved','The low-rim component is connected, with 74/144 contacts, 16 missing vertical intersections and 54 points with no contact layer. No hidden alternate support layer clears them.','Use the saved exact component/source-face indices to examine terrain-facing embedded interfaces and the installed podium; recheck full drawn terrain.'),
 'landsd/255647:0':('connected-rim-and-neighbour-terrain-unresolved','The low-rim component is connected, with 101/131 contacts, 13 missing vertical intersections and 17 with no contact layer. The prior four buried upward faces remain unresolved.','Resolve the four exact buried faces and support interfaces while retaining the installed podium and Block 9.'),
 'landsd/255539:0':('connected-rim-and-podium-below-grade-unresolved','The connected low rim has 116/134 contacts, seven missing intersections and 11 points outside all contact layers. The podium remains held by its saved 111 buried upward faces.','Use the component inventory with source/revision evidence to resolve legitimate below-grade intent before joint terrain/browser acceptance.'),
 'landsd/264206:0':('podium-component-and-nested-terrain-unresolved','All 19,551 original faces are inventoried as 144 diagnostic connected components. The existing 102 buried upward faces are not cleared by topology.','Match the saved component indices to exact nested terrain faces and current higher tower forms; do not replace the tower based on its misleading label.'),
 'landsd/336430:0':('component-membership-and-terrain-unresolved','All 21,186 original faces are inventoried as 26 diagnostic connected components. The four unrelated overlapping forms and 36 buried upward faces remain explicit.','Use component face indices to map the unrelated small form and park neighbours against exact source/revision metadata.'),
 'landsd/273672:0':('buried-faces-under-both-available-surfaces','Both buried upward faces remain buried even under the pointwise lower of original parent and native terrain. Whole-source comparison found 45 sampled points buried under both; no fabricated lower surface was generated.','Investigate those two pinned source faces and authoritative revision/component metadata. Repeating parent/native minimum masks cannot resolve this hold.'),
 'landsd/134332:0':('neighbour-protection-and-source-foundation-conflict','A 71-face parent-preservation candidate passes full foundation, but replacing the installed TIN flags 66 neighbours (six installed native forms remain unresolved). Protecting neighbours reduces this to one resolved native neighbour, but buries four upward source faces. Current viewer is unchanged.','Resolve the four source faces in the neighbour-preserving variant and retest installed Citywalk 2/current terrain. Do not publish the unprotected variant.'),
 'landsd/273839:0':('installed-support-resolved-two-embedded-contact-points','Exact support landsd/175935:0 is already installed. Its triangle/winding hash exactly equals the independently recovered original despite different packed asset hashes. There is vertical support at all 76 rim samples; 74 pass, two extend 0.46m below the support and fail the -0.1m contact tolerance. Both original source meshes pass CPU picking/collision; no installation.','Reuse the installed pinned podium. Resolve the two exact embedded source points without changing surveyed coordinates or relaxing the contact rule merely for this model.')}
 for row in rows:
  hold,observation,next_work=updates[row['uid']];row.update(humanStatus='held-unknown',detailedHold=hold,observation=observation,nextWork=next_work,sourceComponents=components[row['uid']],installationApproved=False,installed=False,needsAIModeling=False,needsHumanDecision=False,aiModelingRequiredEstablished=False,nextActionType='compute-investigation')
  if row['uid'] in supports:row['supportDiagnostic']={k:v for k,v in supports[row['uid']].items() if k not in ('failed','layers','components')}
 # Include result.json in nested terrain diagnostics, excluding only final report.
 paths=[p for p in DOC.rglob('*') if p.is_file() and p not in (DOC/'result.json',DOC/'neon-sync.json',DOC/'ledger-sync.json',DOC/'checkpoint.json',DOC/'README.md')]
 paths += [HERE/n for n in ('sol-continuation-20261003.py','sol-terrain-options-20261003.py','sol-source-components-20261003.py','sol-support-contact-20261003.mjs','support-contact.mjs','native_patch_resolution.py')]
 report={'batch':'sol-continuation-20261003','priorReview':ref(BASE/'sol-pilot-20261002/review.json'),'rows':rows,'counts':{'processed':10,'newlyInstalled':0,'heldUnknown':10,'heldAI':0,'heldHuman':0,'inProcess':0},'evidenceRefs':[ref(p) for p in sorted(set(paths))],'scriptExternalAICalls':0,'aiGeometryGeneration':False,'modelGeometryChanges':0,'publication':False,'executor':'Codex root; AI used for code/non-modelling work only','supportEquivalence':read(DOC/'support-contact.json')['supportEquivalence'],'viewerManifest':ref(ROOT/'3d-viewer/city/data/manifest.json'),'localOnlyCandidates':'Derived terrain and acquisition caches in local/ are not R2-published; exact hashes and reproducible commands are retained. Installed support asset is already portable in the viewer.'}
 save(DOC/'result.json',report);job=read(LOCAL/'job.json')
 snapshot=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')['snapshotId']
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');sources=dict(con.execute('SELECT uid,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(snapshot,UIDS)).fetchall())
 by_uid={r['uid']:r for r in rows};assert all(by_uid[uid]['sourceSHA256']==sha for uid,sha in sources.items())
 if sources:
  ledger=module('continuation_ledger','../model-review-ledger/ledger.py');effort={'method':'scripted','ai_model':None,'reasoning_effort':'not-applicable','job_id':job['id'],'issue':'HKS-203','output_ref':str((DOC/'result.json').relative_to(ROOT))}
  recorded=ledger.record_many(snapshot,LEASE,[(uid,'held',DOC/'result.json',by_uid[uid]['observation']+' '+by_uid[uid]['nextWork'],None) for uid in sources],effort=effort,request_id='sol-continuation-20261003-'+job['id']);save(DOC/'ledger-sync.json',{'snapshotId':snapshot,'rows':recorded,'notPlannedHere':sorted(set(UIDS)-set(sources))})
 with connect() as con:
  con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,receipt)
  assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(report),job['id'],job['owner'],job['token'])).rowcount==1
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(job['id'],)).fetchone()[0]==report
 save(DOC/'neon-sync.json',{'jobId':job['id'],'resultVerified':True,'result':ref(DOC/'result.json')});assert reservations.release(receipt)['ok'];print({'jobId':job['id'],'processed':10,'installed':0,'held':10,'inProcess':0},flush=True)

if __name__=='__main__':{'start':start,'recover':recover,'citywalk':citywalk_checks,'ocean':ocean_checks,'protect':citywalk_protect,'festival':festival_checks,'sync':sync}[sys.argv[1]]()
