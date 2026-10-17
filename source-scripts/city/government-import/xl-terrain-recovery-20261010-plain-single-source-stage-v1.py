"""Guarded staging for one unchanged source and one new, nonreplacement terrain.

A pinned JSON configuration selects a separately reviewed source-specific current
acceptance adapter. This module never creates acceptance or live publication.
"""
import argparse,importlib.util,json,os,shutil,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect
from dependency_preflight import from_catalogues

def ref(p):
 p=Path(p).resolve();assert p.is_relative_to(ROOT.resolve());return dict(path=str(p.relative_to(ROOT.resolve())),sha256=digest(p.read_bytes()))
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def configuration(path):
 path=Path(path).resolve();assert path.is_relative_to(ROOT.resolve());cfg=read(path);assert cfg['schema']=='plain-single-source-original-stage-v1';assert Path(cfg['batch']).name==cfg['batch'] and cfg['batch'].startswith('government-xl-')
 assert cfg['plainNewTerrain'] is True and cfg['retainedNativeUIDs']==[] and cfg['supportDependencies']==[]
 assert len(cfg['sources'])==1;uid,sha=next(iter(cfg['sources'].items()));assert uid.startswith('landsd/') and len(sha)==64 and all(c in '0123456789abcdef' for c in sha)
 assert type(cfg['completeOriginalFaces']) is int and cfg['completeOriginalFaces']>0 and type(cfg['completeOriginalComponents']) is int and cfg['completeOriginalComponents']>0
 for key in ['physicalReceipt','currentRoleReceipt','currentTypedRole','currentRoleRunner']:assert ref(ROOT/cfg[key]['path'])==cfg[key]
 assert (ROOT/cfg['currentRoleRunner']['path']).resolve().is_relative_to(HERE.resolve())
 return cfg

def recheck(cfg):
 for key in ['physicalReceipt','currentRoleReceipt','currentTypedRole','currentRoleRunner']:assert ref(ROOT/cfg[key]['path'])==cfg[key]
 adapter=module('single_source_current_acceptance',ROOT/cfg['currentRoleRunner']['path']);typed=adapter.recheck();assert typed==read(ROOT/cfg['currentTypedRole']['path'])
 assert typed['independentPhysicalChecksPassed'] is True and typed['unresolvedIndependentPhysicalReasons']==[] and set(typed['uids'])==set(cfg['sources']) and typed['completeOriginalFaces']==cfg['completeOriginalFaces'] and typed['completeOriginalComponents']==cfg['completeOriginalComponents']
 assert typed['manifestSHA256']==digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()) and typed['sourceGeometryChanges']==0 and typed['installationApproved'] is False and typed['publication'] is False
 identities=typed['completeCurrentIdentities'];assert len(identities)==1 and identities[0]['uid'] in cfg['sources'] and identities[0]['passed'] is True
 for key in ['physicalReceipt','currentRoleReceipt']:
  r=read(ROOT/cfg[key]['path']);doc=(ROOT/cfg[key]['path']).parent;assert read(doc/'neon-sync.json')==dict(jobId=r['jobId'],resultVerified=True)
  with connect() as con:con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 physical=(ROOT/cfg['physicalReceipt']['path']).parent;selected=read(physical/'selection.json.gz');assert len(selected['rows'])==1 and selected['manifestSHA256']==typed['manifestSHA256'];row=selected['rows'][0];assert row['uid'] in cfg['sources'] and row['sourceSHA256']==cfg['sources'][row['uid']] and row['triangles']==cfg['completeOriginalFaces']
 assert ref(ROOT/row['candidate']['path'])['sha256']==row['sourceSHA256'] and row['candidate']['entry']['sha256']==row['sourceSHA256'] and row['candidate']['entry']['uid']==row['uid']
 return row,identities,typed

def paths(cfg):
 batch=cfg['batch'];return (ROOT/'docs/astra-city/government-import'/batch,HERE/'accepted'/batch,HERE/'local'/batch/'install-reservation.json')
def owned(config_path):
 cfg=configuration(config_path);doc,stage,leasepath=paths(cfg);lease=read(leasepath)
 def owns():assert reservations.owns(lease)
 def call(cmd):subprocess.run(cmd,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();row,identities,typed=recheck(cfg);save(doc/'identity-publication-recheck.json',identities);save(doc/'typed-role-publication-recheck.json.gz',typed)
 physical=(ROOT/cfg['physicalReceipt']['path']).parent;entry=dict(row['candidate']['entry']);assert not entry.get('suppressesBuildingUids') and not entry.get('supportDependencies') and not entry.get('footprintScope')
 entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,supportDependencies=[],placementReview=cfg['placementReview'])
 asset=stage/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],asset);assert ref(asset)['sha256']==entry['sha256']
 catalogue=read(HERE/'local'/physical.name/'catalogue.json');catalogue.update(models=[entry],counts={'packedModels':1},area=cfg['area']);save(stage/'catalogue.json',catalogue);save(stage/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(stage/'source-forms.json',[row['source']['building']])
 candidates=read(physical/'terrain-candidates.json');assert len(candidates)==1;c=candidates[0];assert c['uids']==[row['uid']] and not c.get('replaces') and not c.get('replacesMany') and ref(ROOT/c['path'])['sha256']==c['sha256'];patch=stage/Path(c['path']).name;shutil.copyfile(ROOT/c['path'],patch);p=read(patch);assert p.get('nativeMesh') and not p.get('patches') and p['meta']['parentTerrain']=='city/data/terrain.json' and p['meta']['parentSha256']==ref(ROOT/'3d-viewer/city/data/terrain.json')['sha256']
 terrain=dict(source=ref(patch)['path'],sha256=ref(patch)['sha256'],destination='city/data/'+patch.name,resolution=p['cell'],area=cfg['area']+' indexed original terrain')
 destination='city/data/official-models/'+cfg['batch']+'/catalogue.json';save(stage/'plan.json',dict(areas=[dict(area=cfg['area'],catalogue=ref(stage/'catalogue.json')['path'],destination=destination)],topLevelTerrainPatches=[terrain]))
 dependencies=from_catalogues(ROOT/'3d-viewer/city/data/manifest.json',[stage/'catalogue.json']);assert not any(r['blockers'] for r in dependencies['rows']);save(doc/'dependencies.json',dependencies)
 uid=row['uid'];direction=cfg['captureDirection'];assert len(direction)==3 and any(v!=0 for v in direction)
 browser=dict(captureDirectionByModel={uid:direction},stage=str(stage.relative_to(ROOT))+'/',doc=str(doc.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[terrain],fitBox=True,captureBoundsByModel={uid:entry['worldBounds']},browserUids=[uid],failureTestUids=[uid],nativeSupportUidsByModel={uid:[]});save(stage/'browser-config.json',browser)
 evidence=[ref(q) for q in [Path(__file__),config_path,ROOT/cfg['physicalReceipt']['path'],ROOT/cfg['currentRoleReceipt']['path'],ROOT/cfg['currentTypedRole']['path'],ROOT/cfg['currentRoleRunner']['path'],doc/'identity-publication-recheck.json',doc/'typed-role-publication-recheck.json.gz',doc/'dependencies.json',stage/'catalogue.json',stage/'plan.json',stage/'browser-config.json',asset,patch,HERE/'xl-terrain-recovery-20261009-multi-native-solid-browser-v4.mjs']]
 decision=dict(batch=cfg['batch'],uids=[uid],sourceSHA256s=cfg['sources'],manifestSHA256=typed['manifestSHA256'],checksPassed=True,publication=False,newlyInstalled=0,modelGeometryChanges=0,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,evidenceRefs=evidence);save(doc/'stage.json',decision)
 call([sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(stage/'plan.json')['path'],'--receipt',str(leasepath),'--phase',cfg['batch']]);call(['node',str(HERE/'xl-terrain-recovery-20261009-multi-native-solid-browser-v4.mjs'),'staged',ref(stage/'browser-config.json')['path']])
 report=module('plain_single_source_browser_verification',HERE/'integrate.py').browser_verified(doc/'staged-browser.json',{uid});assert not report.get('retainedNativeOwnViews',[])
 for r in evidence:assert ref(ROOT/r['path'])==r
 recheck(cfg);decision.update(stagedBrowser=ref(doc/'staged-browser.json'),passed=True,failures=[],livePublicationRequired=True);save(doc/'acceptance.json',decision);print(json.dumps(dict(stagedBrowserPassed=True,uids=[uid],publication=False,newlyInstalled=0)),flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();path=ROOT/a.config;cfg=configuration(path);doc,stage,lease=paths(cfg)
 if a.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):owned(path)
  return
 assert not doc.exists() and not stage.exists();physical=(ROOT/cfg['physicalReceipt']['path']).parent;forms=read(physical/'neighbour-inputs.json.gz')['rows'];resources={('building:' if r['building']['uid'].startswith('landsd/') else 'foreign-form:')+r['building']['uid'] for r in forms}|{'building:'+u for u in cfg['sources']}|{'terrain-patch:'+u for u in cfg['sources']}
 claim=reservations.claim('plain-single-source-stage-'+str(uuid.uuid4()),sorted(resources),batch=cfg['batch'],ttl=3600);assert claim['ok'],claim;save(lease,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(lease),'--',sys.executable,__file__,'--config',a.config,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
