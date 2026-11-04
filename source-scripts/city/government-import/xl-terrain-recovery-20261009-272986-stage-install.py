"""Stage unchanged West Kowloon Government Offices South Tower with fresh identity and exact wall-role replay.

This adapter performs publication dry runs and desktop/mobile browser acceptance.
It never mutates the live manifest or grants installed credit. A guarded publisher
must replay the same evidence under its publication lease before live integration.
"""
import argparse,importlib.util,json,os,shutil,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect,NATIVE_RUN
from routed_original_cell_identity import verify_files,POLICY
from dependency_preflight import from_catalogues

UID='landsd/272986:0'
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-272986-retained-neighbours-20261009'
BASE=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-272986-current-inputs'
ROLE=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-272986-current-wall-role'
BATCH='government-xl-terrain-recovery-272986-typed-stage-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
STAGE=HERE/'accepted'/BATCH
LEASE=HERE/'local'/BATCH/'install-reservation.json'

def ref(path):
 path=Path(path);return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def recheck(local):
 """No mutations to current assets: fresh identity plus deterministic role replay."""
 physical=read(PHYSICAL/'result.json');role_result=read(ROLE/'result.json')
 for doc,result in [(PHYSICAL,physical),(ROLE,role_result)]:
  assert read(doc/'neon-sync.json')=={'jobId':result['jobId'],'resultVerified':True}
  with connect() as con:
   con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
  for item in result['evidenceRefs']:assert ref(ROOT/item['path'])==item
 assert physical['uid']==UID and physical['publication'] is False and physical['newlyInstalled']==physical['modelGeometryChanges']==physical['scriptExternalAICalls']==0
 rows=read(PHYSICAL/'selection.json.gz')['rows'];assert len(rows)==1;row=rows[0]
 context=next(r for r in read(BASE/'context.json.gz')['rows'] if r['uid']==UID)
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY')
  assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 identity=verify_files(row,context,local)
 assert identity['policy']==POLICY and identity['passed'] and identity==read(PHYSICAL/'owned-source-identity.json')
 kernel=module('west_kowloon_current_wall_role',HERE/'xl-terrain-recovery-20261009-272986-current-wall-role.py')
 role=kernel.recheck();assert json.loads(json.dumps(role))==read(ROLE/'typed-role.json.gz')
 assert role['verifiedWallRole'] and role['independentPhysicalChecksPassed'] and not role['unresolvedIndependentPhysicalReasons']
 assert role['sourceSHA256']==row['sourceSHA256']==physical['sourceSHA256']
 assert role['currentNeighbourFormsAccounted']==10 and role['currentForeignBasicActors']==9
 assert role['originalWallRimAccounting']['ordinaryRimSamples']==309 and role['originalWallRimAccounting']['strictOrdinaryAnchorSamples']==108
 assert set(role['typedWallOnlyResolvedReasons'])==set(physical['reasons'])
 assert role['strictLowRimAndSamplerPass']
 return row,identity,role

def owned():
 def owns():assert reservations.owns(read(LEASE))
 def call(command):
  subprocess.run(command,cwd=ROOT,check=True,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'});owns()
 owns();row,identity,role=recheck(HERE/'local'/BATCH/'identity-recheck')
 save(DOC/'identity-publication-recheck.json',identity);save(DOC/'typed-role-publication-recheck.json.gz',role)
 entry=dict(row['candidate']['entry']);assert not entry.get('suppressesBuildingUids') and not entry.get('supportDependencies')
 entry.update(priority='landmark',proceduralWindows=False,sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,
  placementReview='Complete unchanged original LOD3 south tower. Unique exact provider identity and current complete geographic cell pass. All12314 original faces continuously checked; only original exposed crossing wall10379 receives exact positive-dimensional original-wall-to-clear-roof contact role, with full source graph and no welding. Raw prior no-full-edge roof path retained. All41982 runtime samples and314rim samples replayed and face-attributed;309ordinary samples preserve existing -.5m clearance, <=+.1m minimumcontact and <=1m maximum,108strict ±.1m anchors. Allordinary/upward/degeneratefaces, wholefoundation,10currentneighbours, runtime sampler andcompleteforeign separation pass. Two source-disjoint neighbour footprints retain exact parent terrain; sourceTINundertargetunchanged. Originalmesh/root/elevationunchanged;zeroAI geometry modelling.')
 asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/row['candidate']['path'],asset);assert ref(asset)['sha256']==entry['sha256']
 catalogue=read(HERE/'local'/PHYSICAL.name/'catalogue.json');catalogue.update(models=[entry],counts={'packedModels':1},area='West Kowloon Government Offices South Tower unchanged original provider exterior')
 save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
 forms=read(PHYSICAL/'neighbour-inputs.json.gz')['rows'];source_forms=[r['building'] for r in forms if r['building']['uid']==UID];assert len(source_forms)==1
 save(STAGE/'source-forms.json',source_forms)
 candidates=read(PHYSICAL/'terrain-candidates.json');assert len(candidates)==1;candidate=candidates[0]
 assert candidate['uids']==[UID] and not candidate.get('replaces') and not candidate.get('replacesMany') and ref(ROOT/candidate['path'])['sha256']==candidate['sha256']
 patch=STAGE/Path(candidate['path']).name;shutil.copyfile(ROOT/candidate['path'],patch)
 p=read(patch);assert p.get('nativeMesh') and not p.get('patches')
 assert p['meta']['parentTerrain']=='city/data/terrain.json' and p['meta']['parentSha256']==ref(ROOT/'3d-viewer/city/data/terrain.json')['sha256']
 terrain={'source':ref(patch)['path'],'sha256':ref(patch)['sha256'],'destination':'city/data/'+patch.name,'resolution':p['cell'],'area':catalogue['area']+' indexed government terrain'}
 destination='city/data/official-models/'+BATCH+'/catalogue.json'
 save(STAGE/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':ref(STAGE/'catalogue.json')['path'],'destination':destination}],'topLevelTerrainPatches':[terrain]})
 manifest=ROOT/'3d-viewer/city/data/manifest.json';dependencies=from_catalogues(manifest,[STAGE/'catalogue.json']);assert not any(r['blockers'] for r in dependencies['rows']);save(DOC/'dependencies.json',dependencies)
 save(STAGE/'browser-config.json',{'stage':str(STAGE.relative_to(ROOT))+'/','doc':str(DOC.relative_to(ROOT))+'/','catalogueURL':destination,'terrain':[terrain],'fitBox':True,'captureBoundsByModel':{UID:entry['worldBounds']},'browserUids':[UID],'failureTestUids':[UID],'nativeSupportUidsByModel':{}})
 evidence=[ref(p) for p in [Path(__file__),PHYSICAL/'result.json',ROLE/'result.json',ROLE/'typed-role.json.gz',DOC/'identity-publication-recheck.json',DOC/'typed-role-publication-recheck.json.gz',DOC/'dependencies.json',STAGE/'catalogue.json',STAGE/'plan.json',STAGE/'browser-config.json',HERE/'routed_original_cell_identity.py',HERE/'xl-terrain-recovery-20261009-272986-current-wall-role.py',HERE/'resolution-assembly-browser.mjs']]
 decision={'batch':BATCH,'uids':[UID],'sourceSHA256s':{UID:row['sourceSHA256']},'checksPassed':True,'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,'sourceEvidenceInterpretationUsedAI':True,'aiGeometryModelling':False,'evidenceRefs':evidence}
 save(DOC/'stage.json',decision)
 call([sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),ref(STAGE/'plan.json')['path'],'--receipt',str(LEASE),'--phase',BATCH])
 call(['node',str(HERE/'resolution-assembly-browser.mjs'),'staged',ref(STAGE/'browser-config.json')['path']])
 module('west_kowloon_browser_validator',HERE/'integrate.py').browser_verified(DOC/'staged-browser.json',{UID})
 for item in evidence:assert ref(ROOT/item['path'])==item
 # Replay under the same lease after browser work: no stale approval credit.
 recheck(HERE/'local'/BATCH/'identity-recheck-final')
 decision.update(stagedBrowser=ref(DOC/'staged-browser.json'),passed=True,failures=[],livePublicationRequired=True)
 save(DOC/'acceptance.json',decision);print(json.dumps({'stagedBrowserPassed':True,'uid':UID,'publication':False,'newlyInstalled':0}),flush=True)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--owned',action='store_true');args=parser.parse_args()
 if args.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):return owned()
 assert not DOC.exists(),'Fresh immutable acceptance stage required'
 forms=read(PHYSICAL/'neighbour-inputs.json.gz')['rows'];scope={r['building']['uid'] for r in forms}|{UID}
 claim=reservations.claim('xl-terrain-recovery-272986-stage-'+str(uuid.uuid4()),['building:'+u for u in sorted(scope)]+['terrain-patch:'+UID],batch=BATCH,ttl=3600);assert claim['ok'],claim
 save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)

if __name__=='__main__':main()
