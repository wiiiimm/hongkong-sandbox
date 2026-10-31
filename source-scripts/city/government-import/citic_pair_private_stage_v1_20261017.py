"""Qualify unchanged CITIC pair privately; no live catalogues or review state changes."""
from pathlib import Path
import copy,os,subprocess,uuid
import numpy as np
from shapely.geometry import Polygon,MultiPoint
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from citic_reviewed_boundary_identity_v1_20261017 import verify_files as reviewed_identity
from exact_original_georef_cell_identity_20261009 import verify_files as ordinary_identity
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from installed_support_acceptance import resolve_contact
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citic-pair-private-stage-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
P='landsd/232579:0';T='landsd/278303:0';NAMES=['current-pair-v1','current-assembly-v1','current-finite-v1','current-physical-v2','reviewed-boundary-identity-v1']
def folder(name):return BASE/('government-xl-citic-'+name+'-20261017')
def main():
 assert not DOC.exists() and not LOCAL.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=folder(name)/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for q in r['evidenceRefs']:
    assert q['path'] not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(ROOT/p for p in pins)
 claim=reservations.claim('citic-pair-stage-'+str(uuid.uuid4()),['building:'+u for u in [P,T]],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();LOCAL.mkdir();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=digest(manifest.read_bytes());refs.append(manifest)
  sources=copy.deepcopy(read(folder('current-assembly-v1')/'support-inputs.json')['sources']);assembly=read(folder('current-assembly-v1')/'summary.json');finite=read(folder('current-finite-v1')/'summary.json');assert finite['allStrict'] and finite['allFacesCovered']
  assert all(x['strictFoundationAccepted'] for x in assembly['rows'])
  metrics=copy.deepcopy(read(folder('current-pair-v1')/'metrics.json'));policy=module('citic_pair_policy',HERE/'acceptance-policy.py');proofs={};qual=[];entries=[]
  for row in sources:
   u=row['uid'];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);row.update(modelId=row['candidate']['entry']['modelId'],triangles=len(tri));assert row['native']['model']['triangles']==len(tri)
   context=read(folder('current-assembly-v1')/(u.replace('/','-').replace(':','-')+'-context.json'))
   proof=(reviewed_identity if u==P else ordinary_identity)(row,context,LOCAL/'identity'/u.replace('/','-').replace(':','-'));assert proof['passed'];proofs[u]=proof
   m=next(x for x in metrics['rows'] if x['uid']==u)
   if not m['identity']:
    b=row['source']['building'];shape=Polygon(b['rings'][0],b['rings'][1:]);hull=MultiPoint(tri[:,:,[0,2]].reshape(-1,2)).convex_hull;m['identity']=dict(overlap=hull.intersection(shape).area/max(.001,min(hull.area,shape.area)),centroidDistance=hull.centroid.distance(shape.centroid))
   raw_reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=row['sourceSHA256'],identityProof=proof['proof']),m,metrics['profiles']['mobile'])
   foundation=next(x for x in assembly['rows'] if x['uid']==u)
   remaining=resolve_contact(raw_reasons,assembly['interface'],foundation) if u==T else raw_reasons
   assert not remaining,(u,remaining)
   qual.append(dict(uid=u,sourceSHA256=row['sourceSHA256'],rawPolicyReasons=raw_reasons,remainingReasons=remaining,foundationAccepted=True))
   e=copy.deepcopy(row['candidate']['entry']);e.update(rootTranslation=[-834500,0,816500],proceduralWindows=False,sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=False,publicationApproved=False,supportDependencies=[] if u==P else [dict(uid=P,state='candidate',csuid='3526515744P20060312',sha256=next(s['sourceSHA256'] for s in sources if s['uid']==P))]);e['asset']='assets/'+e['sha256']+'.glb.gz';dest=LOCAL/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);entries.append(e)
  cat=dict(rootTranslation=[-834500,0,816500],coordinatePolicy='original-government-fixed-1x',models=entries);save(LOCAL/'catalogue.json',cat);save(LOCAL/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',[r['source']['building'] for r in sources]);save(DOC/'terrain-candidates.json',[]);save(DOC/'identity-proofs.json',proofs);save(DOC/'policy-metrics.json',metrics);save(DOC/'qualification.json',dict(rows=qual,sourceGeometryChanges=0,terrainChanges=0,publication=False))
  replacements=[]
  for url in read(manifest)['officialModelCatalogues']:
   p=ROOT/'3d-viewer'/url;c=read(p)
   if any(m['uid']==P for m in c['models']):
    old=next(m for m in c['models'] if m['uid']==P);assert old['sha256']==next(e['sha256'] for e in entries if e['uid']==P)
    replacement=LOCAL/'replaced-existing-catalogue.json';save(replacement,{**c,'models':[m for m in c['models'] if m['uid']!=P]});replacements.append(dict(url=url,source=str(replacement.relative_to(ROOT)),originalSHA256=digest(p.read_bytes())));refs.append(p)
  assert len(replacements)==1
  bounds=[[min(e['worldBounds'][0][i] for e in entries) for i in range(3)],[max(e['worldBounds'][1][i] for e in entries) for i in range(3)]]
  config=dict(stage=str(LOCAL.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[],catalogueReplacements=replacements,browserUids=[P,T],failureTestUids=[P],dependentFailureUidsByModel={P:[T]},nativeSupportUidsByModel={P:[],T:[]},jointUids=[P,T],fitBox=True,captureDirectionByModel={u:[.75,.55,-.65] for u in [P,T]},captureBoundsByModel={u:bounds for u in [P,T]});save(LOCAL/'browser-config.json',config)
  tool=HERE.parent/'building-batch/validate_candidates.mjs';cmd=['node',str(tool),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'source-forms.json').relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))]
  with (DOC/'loader.log').open('w') as log:completed=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=600)
  validation=read(DOC/'validation.json');save(DOC/'loader-command.json',dict(command=cmd,exitCode=completed.returncode));assert validation['loaderAccepted']==2 and validation['checksPassed']==2 and not validation['exceptions'],validation
  assert digest(manifest.read_bytes())==start
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
  refs.extend([tool,HERE/'citic_reviewed_boundary_identity_v1_20261017.py',HERE/'installed_support_acceptance.py',HERE/'acceptance-policy.py',*[p for p in LOCAL.rglob('*') if p.is_file()]])
  result=module('citic_pair_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'citic-original-pair-private-physical-loader-stage-v1',list(dict.fromkeys(refs)),dict(uids=[P,T],identityAccepted=True,policyChecksPassed=True,loaderChecksPassed=True,sourceGeometryChanges=0,newlyInstalled=0,installationApproved=False));print(dict(jobId=result['jobId'],privatePhysicalPassed=True),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
