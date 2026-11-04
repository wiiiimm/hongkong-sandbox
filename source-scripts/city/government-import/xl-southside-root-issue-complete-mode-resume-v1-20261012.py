"""UNEXECUTED ROOT-only descriptor issuer; never retires a worker or claims a lease."""
import argparse, importlib.util, json, subprocess, sys
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, digest, reservations
import southside_whole_mode_resume_descriptor_draft_v1_20261012 as guard

BASE=ROOT/'docs/astra-city/government-import'
DRAFT=BASE/'government-xl-southside-unfiltered-original-sheets-comparison-draft-v2-20261012'
CALLER=HERE/'xl-southside-315025-300867-unfiltered-original-sheets-comparison-v2-20261012.py'
PRIOR='government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v1-20261012'
PRIOR_LOCAL=HERE/'local'/PRIOR
ISSUER_LOCAL=HERE/'local/government-xl-southside-root-issued-mode-resume-v1-20261012'
INPUT=BASE/'government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012'
GRADE=BASE/'government-xl-southside-315025-300867-current-grade-source-context-v1-20261012'
CONTRACT=BASE/'government-xl-southside-unfiltered-original-sheets-comparison-draft-v1-20261012/original-sheet-input-contract.json'
CHECKPOINT=PRIOR_LOCAL/'completed-315025-0-providerOriginal.json.gz'
CHECKPOINT_SHA='1323728290de2fea8731df60a8091d9aaa422aa7b8f9bce415bcfe6522389b21'
LOG=DRAFT/'resume-validator-actual-validation-v1/authoritative-log-at-first-whole-mode.txt'
LOG_SHA='feeb2fbe511d6819b40fff79cfc5e5e90316c2ef3e4a1792fbc44b290b3368f8'
COVERAGE=BASE/'government-xl-original-installation-followup-20261011/root-southside-coverage-reuse-tests-20261012.json'
COVERAGE_SHA='6a852a6cce6ba9f9aba10ab5e7351c56902ad3fe1236566568787459da1d02c9'
REAL_VALIDATION=BASE/'government-xl-original-installation-followup-20261011/root-southside-real-whole-mode-resume-tests-verified-20261012.json'
REAL_VALIDATION_SHA='1fb191ab0bee17c09cd8fee5e0dd89b0cb971c79391b568b2f72966886e62f7b'
MANIFEST=guard.MANIFEST

def file_pin(p):
 p=Path(p).resolve();assert ROOT in p.parents and p.is_file()
 return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def check_pin(pin):
 guard.pin(pin);p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];return p

def absent():
 lines=subprocess.check_output(['ps','-eo','args='],text=True).splitlines()
 caller=str(HERE/'xl-southside-315025-300867-unfiltered-original-sheets-comparison-v1-20261012.py')
 supervisor=str(HERE.parent/'shared-modelling/reservations.py');lease=str(PRIOR_LOCAL/'reservation.json')
 return not any((caller in q and '--owned'in q)or(supervisor in q and lease in q)for q in lines)

def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def declared_faces(data):
 seen=set();count=0
 def visit(i):
  nonlocal count
  assert i not in seen;seen.add(i);node=data['nodes'][i]
  if 'mesh'in node:
   for primitive in data['meshes'][node['mesh']]['primitives']:
    assert primitive.get('mode',4)==4
    key=primitive['indices']if 'indices'in primitive else primitive['attributes']['POSITION'];n=data['accessors'][key]['count'];assert n%3==0;count+=n//3
  for child in node.get('children',[]):visit(child)
 for i in data['scenes'][data.get('scene',0)]['nodes']:visit(i)
 return count

def write_exclusive(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(data)

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--root-recipe-path',required=True)
 parser.add_argument('--root-recipe-sha256',required=True)
 parser.add_argument('--root-retirement-path',required=True)
 parser.add_argument('--root-retirement-sha256',required=True)
 parser.add_argument('--reviewed-caller-sha256',required=True)
 args=parser.parse_args()
 # No process stop, lease release, review write, or implicit retirement authority.
 assert not(BASE/PRIOR/'result.json').exists(),'Completed v1 supersedes resume'
 assert absent(),'Prior worker/supervisor must already be absent'
 lease_path=PRIOR_LOCAL/'reservation.json';lease=read(lease_path)
 assert lease['batch']==PRIOR and not reservations.owns(lease),'Prior lease must already be released'
 retirement_path=check_pin(dict(path=args.root_retirement_path,sha256=args.root_retirement_sha256));retirement=read(retirement_path)
 assert retirement['kind']=='root-issued-southside-complete-mode-retirement-v1'and retirement['priorBatch']==PRIOR
 assert retirement['currentManifestSHA256']==MANIFEST and retirement['currentAcceptance']is False
 assert retirement['priorLeaseReleased']is True and retirement['noOwnedOrSupervisorProcessRemaining']is True
 assert retirement['priorLeaseFileSHA256']==digest(lease_path.read_bytes())
 assert digest(CALLER.read_bytes())==args.reviewed_caller_sha256
 recipe_path=check_pin(dict(path=args.root_recipe_path,sha256=args.root_recipe_sha256));recipe=read(recipe_path)
 # Fresh __main__ process exactly matches the eventual caller import context.
 emitted=subprocess.run([sys.executable,str(CALLER),'--resume-recipe-only'],cwd=ROOT,text=True,capture_output=True,check=True)
 assert not emitted.stderr,emitted.stderr
 fresh_recipe=json.loads(emitted.stdout);assert fresh_recipe==recipe
 assert recipe['kind']=='southside-resume-source-recipe-v1'and recipe['callerSHA256']==args.reviewed_caller_sha256
 assert recipe['currentManifestSHA256']==MANIFEST and recipe['completeFourSheetDeclaredFacets']==774477 and len(recipe['resources'])==52
 assert recipe['currentAcceptance']is False and recipe['installationApproved']is False
 pins=recipe['inputPins']+recipe['codePins']
 for key in ['inputPins','codePins']:
  assert recipe[key]and len({q['path']for q in recipe[key]})==len(recipe[key])
 for pin in pins:check_pin(pin)
 for p,sha in [(CHECKPOINT,CHECKPOINT_SHA),(LOG,LOG_SHA),(COVERAGE,COVERAGE_SHA),(REAL_VALIDATION,REAL_VALIDATION_SHA)]:assert digest(p.read_bytes())==sha
 output_paths=[DRAFT/'root-issued-resume-contract.json',DRAFT/'resume-contract.json',DRAFT/'root-descriptor-issuance-report.json']
 assert not any(p.exists()for p in output_paths)and not ISSUER_LOCAL.exists()
 before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes();assert digest(before)==MANIFEST
 contract=read(CONTRACT);decoder=module('southside_root_issuer_decoder',HERE/'xl-second-pass.py');decoder.LOCAL=ISSUER_LOCAL
 fragments=[];inventory=[]
 for sheet in contract['sheets']:
  count=0
  for record in sheet['allOriginalTerrainFiles']:
   path=ROOT/sheet['folder']/'terrain'/record['name'];assert digest(path.read_bytes())==record['sha256']
   if path.suffix!='.gltf':continue
   world=np.asarray(decoder.terrain_triangles(path),dtype='<f8')
   assert world.ndim==3 and world.shape[1:]==(3,3)and np.isfinite(world).all()and len(world)==declared_faces(read(path))
   fragments.append(world);count+=len(world);inventory.append(dict(path=str(path.relative_to(ROOT)),sourceSHA256=record['sha256'],facets=len(world),completeFacetSHA256=digest(world.tobytes())))
  assert count==sheet['declaredCompleteSceneTerrainFacets']
 whole=np.concatenate(fragments);assert len(whole)==774477;whole_sha=digest(whole.tobytes())
 uid=guard.UID;actual=read(INPUT/'complete-current-actual-source-and-ground-315025-0.json.gz')
 bounds=np.asarray([actual['completeOriginalPOSITIONProof']['originalWholeSourceBounds'],*actual['completeWholeUnusedVertexBounds']],dtype='<f8');assert bounds.shape==(4,2,3)and np.isfinite(bounds).all()
 low,high=bounds[:,0].min(0),bounds[:,1].max(0)
 keep=(whole[:,:,0].max(1)>=low[0])&(whole[:,:,0].min(1)<=high[0])&(whole[:,:,2].max(1)>=low[2])&(whole[:,:,2].min(1)<=high[2])
 selected=whole[keep];assert len(selected)==25388;selected_sha=digest(selected.tobytes())
 data=read(INPUT/'complete-two-actor-four-stream-ground-inputs.json.gz')['rows'][uid];assert data['sourceSHA256']==guard.SOURCE
 world=np.asarray(data['completeWorldStreams'][guard.MODE]['completeWorldTriangles'],dtype='<f8');assert world.shape==(11699,3,3)
 oldrows=read(GRADE/'diagnostic.json.gz')['rows'];matches=[q for q in oldrows if q['uid']==uid and q['arithmetic']==guard.MODE];assert len(matches)==1;old=matches[0]
 descriptor=dict(schema=guard.SCHEMA,priorBatch=PRIOR,uid=uid,arithmetic=guard.MODE,sourceSHA256=guard.SOURCE,currentManifestSHA256=MANIFEST,completeOriginalFaces=11699,completeFullOriginalGroundFacets=len(whole),completeFullOriginalGroundSHA256=whole_sha,selectedOriginalGroundFacets=len(selected),selectedOriginalGroundSHA256=selected_sha,completeWorldSHA256=digest(world.tobytes()),checkpointPin=file_pin(CHECKPOINT),completionLogPin=file_pin(LOG),rootRetirementPin=file_pin(retirement_path),rootCoverageValidationPin=file_pin(COVERAGE),inputPins=recipe['inputPins'],codePins=recipe['codePins'],currentAcceptance=False,installationApproved=False)
 blobs={q['path']:(ROOT/q['path']).read_bytes()for q in [descriptor['checkpointPin'],descriptor['completionLogPin'],descriptor['rootRetirementPin'],descriptor['rootCoverageValidationPin'],*pins]}
 assert absent()and not reservations.owns(lease)and not(BASE/PRIOR/'result.json').exists()
 guard.validate_descriptor(descriptor,trusted=descriptor,blobs=blobs,completed_v1_exists=False,prior_processes_absent=True,prior_lease_released=True)
 proof=guard.validate_complete_mode(read(CHECKPOINT),descriptor,world_bytes=world.tobytes(),current_records=old['allCompleteOriginalFiniteRecords'],current_failed_ids=old['allRawFailedFaces'],full_ground_sha256=whole_sha,selected_ground_sha256=selected_sha,completion_log=LOG.read_text())
 assert(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before
 for pin in pins:check_pin(pin)
 for p,sha in [(CHECKPOINT,CHECKPOINT_SHA),(LOG,LOG_SHA),(COVERAGE,COVERAGE_SHA),(REAL_VALIDATION,REAL_VALIDATION_SHA),(CALLER,args.reviewed_caller_sha256),(recipe_path,args.root_recipe_sha256),(retirement_path,args.root_retirement_sha256)]:assert digest(p.read_bytes())==sha
 assert digest(lease_path.read_bytes())==retirement['priorLeaseFileSHA256']and absent()and not reservations.owns(lease)
 serialized=(json.dumps(descriptor,sort_keys=True,indent=2)+'\n').encode()
 refs=[file_pin(recipe_path),file_pin(retirement_path),file_pin(lease_path),file_pin(Path(__file__)),*pins]
 refs.extend(file_pin(p)for p in ISSUER_LOCAL.rglob('*')if p.is_file())
 report=dict(kind='root-issued-southside-resume-descriptor-issuance-v1',rootIssuedContractSHA256=digest(serialized),candidateDescriptorSHA256=digest(serialized),callerSHA256=args.reviewed_caller_sha256,rootRecipePin=file_pin(recipe_path),rootRetirementPin=file_pin(retirement_path),completeFreshGroundFacets=len(whole),completeFreshGroundSHA256=whole_sha,completeFreshSelectedGroundFacets=len(selected),completeFreshSelectedGroundSHA256=selected_sha,completeFreshSourceInventory=inventory,wholeModeValidation=proof,noClearanceRecomputation=True,isolatedCallerRecipe=True,priorLeaseReleased=True,noOwnedOrSupervisorProcessRemaining=True,evidenceRefs=refs,currentAcceptance=False,installationApproved=False)
 write_exclusive(output_paths[0],serialized);write_exclusive(output_paths[1],serialized);write_exclusive(output_paths[2],(json.dumps(report,sort_keys=True,indent=2)+'\n').encode())
 print(json.dumps(dict(rootIssuedContractPath=str(output_paths[0].relative_to(ROOT)),rootIssuedContractSHA256=digest(serialized),completeOrderedOriginalProofRecords=11699,completeFreshGroundFacets=774477,selectedGroundFacets=25388,currentAcceptance=False,installationApproved=False)),flush=True)
if __name__=='__main__':main()
