"""Unexecuted v2 orchestration: exact actual BASIC extents, unchanged terrain maths."""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
import southside_actual_basic_extent_gate_v2_20261012 as extent
OLD=HERE/'xl-southside-315025-300867-private-authentic-terrain-diagnostic-v1-20261012.py'
assert digest(OLD.read_bytes())=='bdc4e67ad975e4c7464a63539c618fa9dd9d9669c3d52ec80c92b36be41281c8'
spec=importlib.util.spec_from_file_location('southside_unchanged_private_terrain_v1',OLD);base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
BATCH='government-xl-southside-315025-300867-private-authentic-terrain-diagnostic-v3-20261012'
base.BATCH=BATCH;base.DOC=base.BASE/BATCH;base.LOCAL=HERE/'local'/BATCH;base.LEASE=base.LOCAL/'reservation.json'
DRAFT=base.BASE/'government-xl-southside-private-authentic-terrain-draft-v2-20261012'
INPUT=DRAFT/'actual-basic-extent-input.json.gz';PROOF=DRAFT/'actual-basic-extent-proof.json.gz'
FAILURE=base.DRAFT/'immutable-before-claim-failure-v1/failure-and-resource-census.json'
def draft_refs():
 return [Path(__file__),HERE/'southside_actual_basic_extent_gate_v2_20261012.py',HERE/'test_southside_actual_basic_extent_gate_v2_20261012.py',HERE/'xl-southside-315025-300867-current-basic-extent-geometry-v1-20261012.mjs',DRAFT/'METHOD-v2.md',FAILURE,base.DRAFT/'immutable-before-claim-failure-v1/authorised-private-construction-v1.log',base.DRAFT/'immutable-before-claim-failure-v1/xl-southside-315025-300867-private-authentic-terrain-diagnostic-v1-20261012.py',DRAFT/'immutable-extent-schema-failure-v1/failure.json',*[p for p in (DRAFT/'immutable-extent-schema-failure-v1').iterdir()if p.is_file()]]
def prepare_input():
 state=base.preflight();assert not state[11]and not state[12]['nominated'];assert len(state[13])==1238
 refs=draft_refs();pins=dict(state[2]);pins.update({str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs})
 assert not INPUT.exists()and not PROOF.exists()
 save(INPUT,dict(schema='southside-complete-basic-extent-input-v1',forms=list(state[13].values()),domainBounds=state[10],inputHashes=pins,originalCompleteResources=state[-2],all46ProtectiveFormsVerbatim=state[4]['completeCurrentForms'],complete6649NativeNomination=state[12],sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False))
 print(json.dumps(dict(input=str(INPUT.relative_to(ROOT)),sha256=digest(INPUT.read_bytes()),forms=1238,oldProvisionalResources=len(state[-2]),noLease=True,noDB=True,noOriginalTerrainDecode=True)),flush=True)
def checked_state():
 state=list(base.preflight());assert INPUT.exists()and PROOF.exists();assert not state[11]
 source=read(INPUT);proof=read(PROOF);assert source['forms']==list(state[13].values())and source['domainBounds']==state[10]and source['originalCompleteResources']==state[-2]
 assert source['complete6649NativeNomination']==state[12]and source['all46ProtectiveFormsVerbatim']==state[4]['completeCurrentForms']
 for path,sha in source['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 for path,sha in proof['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 assert all(proof['inputHashes'].get(path)==sha for path,sha in source['inputHashes'].items())
 producer=HERE/'xl-southside-315025-300867-current-basic-extent-geometry-v1-20261012.mjs';assert proof['inputHashes'][str(producer.relative_to(ROOT))]==digest(producer.read_bytes())
 assert proof['inputHashes'][str(INPUT.relative_to(ROOT))]==digest(INPUT.read_bytes())
 for closure in [proof['recursiveProductionModuleClosure'],*proof['recursiveHelperModuleClosures']]:
  assert closure['schema']=='exact-literal-static-dynamic-resource-closure-v1'and closure['completeAuditedLiteralImportClosure']is True and closure['unsupportedDynamicImports']==0 and closure['computedImportsRejected']is True and closure['opaqueResourcesAreNotParsedModules']is True
  assert set(closure['inputHashes'])==set(closure['modules'])|set(closure['resources'])and not set(closure['modules'])&set(closure['resources'])
  assert all(proof['inputHashes'].get(path)==sha for path,sha in closure['inputHashes'].items())
 assert proof['recursiveProductionModuleClosure']['entryPath']=='3d-viewer/city/building-geometry.js'
 assert proof['recursiveProductionModuleClosure']['schema']=='exact-literal-static-dynamic-resource-closure-v1'
 account=extent.validate(proof,state[13],state[12],state[10],digest(INPUT.read_bytes()))
 state[-2]=extent.resources(state[-2],state[13],state[4]['canonicalResources'],account)
 refs=draft_refs()+[INPUT,PROOF,DRAFT/'actual-basic-extent-account.json.gz'];save_account=DRAFT/'actual-basic-extent-account.json.gz'
 value=dict(account=account,all1238FormsRetained=True,all46OriginalProtectiveResourcesRetained=True,oldResourceCount=len(source['originalCompleteResources']),actualAffectedResourceCount=len(state[-2]),actualResources=state[-2],physicalAccepted=False,installationApproved=False)
 if save_account.exists():assert read(save_account)==value
 else:save(save_account,value)
 validation=DRAFT/'immutable-extent-test-validation-v2/validation.json';log=validation.parent/'tests.log';v=read(validation)
 assert v['tests']==8 and v['passed']is True and v['exitCode']==0 and digest(log.read_bytes())==v['testLogSHA256']
 required=[HERE/'southside_actual_basic_extent_gate_v2_20261012.py',HERE/'test_southside_actual_basic_extent_gate_v2_20261012.py']
 assert v['codePins']==[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in required]
 refs.extend([validation,log]);state[1].extend(refs);state[2].update({str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs})
 return tuple(state)
def main():
 if '--prepare-basic-extent-input-only'in sys.argv:return prepare_input()
 state=checked_state()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(noLease=True,noDB=True,noOriginalTerrainDecode=True,completeScannedForms=1238,actualAffectedResources=state[-2],all46OriginalProtectiveResourcesRetained=True,currentAcceptance=False)),flush=True);return
 if '--owned'in sys.argv:return base.owned(state)
 assert not base.LOCAL.exists();claim=reservations.claim('southside-private-authentic-terrain-v2-'+str(uuid.uuid4()),state[-2],batch=BATCH,ttl=3600);assert claim['ok'];save(base.LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(base.LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
