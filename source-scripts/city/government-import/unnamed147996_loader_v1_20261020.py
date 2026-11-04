"""Private original-library loader checks and source identity captures; no approval."""
from pathlib import Path
import json,sys,uuid,copy,subprocess
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-unnamed147996-loader-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-unnamed147996-candidate-runtime-v2-20261020';NEAR=BASE/'government-xl-unnamed147996-neighbours-v2-20261020';FOUND=BASE/'government-xl-unnamed147996-four-mode-foundations-v1-20261020';UID='landsd/147996:0'
def owned():
 assert not DOC.exists();lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);pins={};refs=[Path(__file__)]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,NEAR,FOUND,BASE/'government-xl-unnamed147996-terrain-validation-v1-20261020',BASE/'government-xl-unnamed147996-identity-review-v1-20261020',BASE/'government-xl-unnamed147996-hoi-yu-prior-review-v1-20261020']:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=read(CAP/'selection.json.gz')['rows'][0];assert row['uid']==UID
 e=copy.deepcopy(row['candidate']['entry']);e['proceduralWindows']=False;raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];asset=LOCAL/e['asset'];asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(raw)
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');key=row['native']['cacheKey']
  assert c.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone()[0]==row['native']['resultSha']
  sheet=c.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s',(key,)).fetchone()[0]
 assert not e.get('sourceTile') or e['sourceTile']==sheet;e['sourceTile']=sheet
 save(DOC/'source-tile-binding.json',dict(uid=UID,cacheKey=key,resultSha=row['native']['resultSha'],sourceTile=sheet))
 save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=[e],counts=dict(packedModels=1),area='Private original source'))
 save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{UID:row['source']});patches=read(CAP/'terrain-candidates.json');assert len(patches)==1
 finalpath=HERE/'local/government-xl-unnamed147996-terrain-validation-v1-20261020/candidate-terrain.json'
 oldterrain=read(ROOT/patches[0]['path']);finalterrain=read(finalpath)
 assert oldterrain['nativeMesh']['position']==finalterrain['nativeMesh']['position'] and oldterrain['nativeMesh']['index']==finalterrain['nativeMesh']['index']
 patches[0]['path']=str(finalpath.relative_to(ROOT));patches[0]['sha256']=digest(finalpath.read_bytes());save(DOC/'terrain-candidates.json',patches)
 save(DOC/'runtime-terrain-binding.json',dict(originalRuntimeReceipt=read(CAP/'result.json')['jobId'],validatedTerrainReceipt=read(BASE/'government-xl-unnamed147996-terrain-validation-v1-20261020/result.json')['jobId'],positionsAndIndicesUnchanged=True,change='Only source-overlap audit metadata added',installationApproved=False))
 tool=HERE.parent/'building-batch/validate_candidates.mjs';cmd=['node',str(tool),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'source-forms.json').relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))]
 with (DOC/'validation.log').open('w') as log:proc=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'validation-command.json',dict(command=cmd,exitCode=proc.returncode));assert proc.returncode in [0,1];v=read(DOC/'validation.json');refs.append(tool)
 identity=read(BASE/'government-xl-next-twenty-original-identity-v2-20261020/147996:0/identity.json');policy=module('central_library_policy',HERE/'acceptance-policy.py');metrics=read(CAP/'metrics.json');rawreasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=row['sourceSHA256'],identityProof=read(BASE/'government-xl-unnamed147996-identity-review-v1-20261020/147996:0-review.json')['identityProof']),metrics['rows'][0],metrics['profiles']['mobile'])
 summary=dict(uid=UID,loaderAccepted=v['loaderAccepted'],checksPassed=v['checksPassed'],exceptions=v['exceptions'],ordinaryConcerns=[dict(uid=r['uid'],concerns=r.get('concerns',[]))for r in v['results']],rawPolicyReasons=rawreasons,viewsAlreadyReviewedSeparately=False,identityApprovalPending=False,rawIdentityReasonsRetained=identity['reasons'],installationApproved=False);save(DOC/'summary.json',summary);print(summary,flush=True)
 for report in [v]:
  for p,h in {**report.get('inputHashes',{}),**report.get('hashes',{})}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([HERE/'acceptance-policy.py',BASE/'government-xl-next-twenty-original-identity-v2-20261020/147996:0/identity.json']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');assert reservations.owns(lease)
 module('central_library_loader_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unnamed147996-original-loader-checks',list(dict.fromkeys(refs)),dict(uids=[UID],summary=summary,installationApproved=False))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+UID,'terrain-patch:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
