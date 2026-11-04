"""Complete current-bound named136 original school-wing identity, no physics waiver."""
from copy import deepcopy
import importlib.util,json
from run import ROOT,HERE,read,digest,connect,NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files as raw_verify
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from evangel_college_original_wing_extension_identity_20261011 import proposal,UID,CSUID,MODEL,SOURCE_SHA,RAW_REASONS
BASE=ROOT/'docs/astra-city/government-import'
RAW=BASE/'government-xl-evangel-college-91306-current-complete-identity-diagnostic-v1-20261011'
PRIMARY=BASE/'government-xl-evangel-college-91306-primary-relations-v1-20261011'
SOURCE=BASE/'government-xl-evangel-college-91306-western-original-patches-context-v1-20261011'
PROPOSAL=BASE/'government-xl-evangel-college-91306-original-wing-extension-proposal-v1-20261011'
POLICY='evangel-college-exact136-original-school-wing-extension-identity-only-v1'
PRIMARY_PARAMETERS={'f':'json','where':"BuildingCSUID IN ('4507318353T20070410')",'outFields':'*','returnGeometry':'true','outSR':'2326','orderByFields':'OBJECTID','resultRecordCount':'1000'}
def current_binding(captured_row,captured_context,row,context,loaded_forms,captured_forms,manifest_bytes,captured_manifest_bytes,native_results,installed_uids):
 assert row==captured_row and context==captured_context
 assert row['uid']==context['uid']==UID and row['modelId']==MODEL and row['sourceSHA256']==SOURCE_SHA
 assert manifest_bytes==captured_manifest_bytes
 assert len({f['uid']for f in loaded_forms})==len(loaded_forms)and len({f['uid']for f in captured_forms})==len(captured_forms)
 assert {f['uid']:f for f in loaded_forms}=={f['uid']:f for f in captured_forms}
 assert native_results==[(row['native']['resultSha'],)]and UID not in installed_uids
 return True
def named_identity(previous,row,world,forms,provider,source_context,frozen_proposal):
 recomputed=proposal(previous,row,world,forms,provider,source_context);frozen=deepcopy(frozen_proposal);refs=frozen.pop('architecturalInterpretationPrimaryRefs')
 assert len(refs)==4 and all(set(r)=={'path','sha256'}and len(r['sha256'])==64 for r in refs)
 assert frozen==recomputed and recomputed['proposalSpatialGuardsSatisfied']and previous['reasons']==RAW_REASONS
 out=deepcopy(previous);out.update(policy=POLICY,passed=True,reasons=[],rawWingExtentReasonsRetained=previous['reasons'],rawOriginalIdentityRetained=deepcopy(previous),completeWingExtensionInterpretation=recomputed,architecturalPrimaryRefs=refs,allOtherCurrentFormsRetained=forms,proof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,physicalAccepted=False,structuralSupportAccepted=False,physicalSupportExemption=False,runtimeExemption=False,currentActorRemoval=False,installationApproved=False,modelGeometryChanges=0,qualification='Identity only for unchanged Evangel College original. Complete136 western school-wing-extension records are source-bound and corroborated by the unique named school owner campus model; no exact architectural function, plan registration, legal ownership, support or grounding claim. Full13960 source projection/cell/foreign guards and13824 ordinary extent records retained. Every original component, zero primitive, terrain/foundation/foreign collision/runtime/browser gate remains independent.')
 return out
def verify_files(row,context,local):
 receipt=read(PROPOSAL/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  native=c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchall()
 for pin in receipt['evidenceRefs']:assert digest((ROOT/pin['path']).read_bytes())==pin['sha256']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();parsed=json.loads(before)
 catalogues=[(ROOT/'3d-viewer'/url,digest((ROOT/'3d-viewer'/url).read_bytes()))for url in parsed['officialModelCatalogues']];installed=[m['uid']for p,_ in catalogues for m in read(p)['models']]
 asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SOURCE_SHA;triangles=decode_original_world_triangles(raw)
 s=importlib.util.spec_from_file_location('evangel_current_complete_forms',HERE/'xl-final-script-pass.py');final=importlib.util.module_from_spec(s);s.loader.exec_module(final);low,high=triangles.min((0,1)),triangles.max((0,1));forms=final.load_forms([low[0]-2,low[2]-2,high[0]+2,high[2]+2])
 for _,_,tile in forms:assert digest((ROOT/'3d-viewer'/tile).read_bytes())==context['neighbourTileHashes'][tile]
 current_binding(read(RAW/'selection.json.gz')['rows'][0],read(RAW/'context.json.gz')['rows'][0],row,context,[f for f,_,_ in forms],read(RAW/'complete-current-forms.json.gz')['rows'],before,(RAW/'captured-manifest.json').read_bytes(),native,installed)
 request=read(PRIMARY/'exact-current-one-primary.request.json');assert request['url']=='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'and request['parameters']==PRIMARY_PARAMETERS and request['sha256']==digest((PRIMARY/'exact-current-one-primary.json').read_bytes())
 previous=raw_verify(row,context,local/'raw-whole-cell');assert previous==read(RAW/'identity.json')
 result=named_identity(previous,row,triangles,[f for f,_,_ in forms],read(PRIMARY/'exact-current-one-primary.json'),read(SOURCE/'diagnostic.json.gz'),read(PROPOSAL/'diagnostic.json.gz'))
 assert manifest.read_bytes()==before and asset.read_bytes()==raw
 for path,sha in catalogues:assert digest(path.read_bytes())==sha
 for _,_,tile in forms:assert digest((ROOT/'3d-viewer'/tile).read_bytes())==context['neighbourTileHashes'][tile]
 return result
