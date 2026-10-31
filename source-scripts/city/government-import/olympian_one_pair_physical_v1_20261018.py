"""Pair validation, full compound foundations, current neighbours; raw failures retained."""
from pathlib import Path
import subprocess,numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-one-pair-physical-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PAIR=BASE/'government-xl-olympian-one-original-assembly-v1-20261018';ATTR=BASE/'government-xl-olympian-one-actual-render-attributes-v1-20261018';NEAR=BASE/'government-xl-olympian-one-neighbours-v1-20261018';IDENTITY=BASE/'government-xl-olympian-one-identity-review-v1-20261018';REVIEW=BASE/'government-xl-olympian-one-source-review-v1-20261018';BIND=BASE/'government-xl-olympian-one-wall-binding-v1-20261018';POD='landsd/72354:0';TOWER='landsd/256927:0'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PAIR,ATTR,NEAR,IDENTITY,REVIEW,BIND]:
   receipt=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(folder/'result.json')
   for e in receipt['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(PAIR/'selection.json.gz')['rows'];assert [r['uid']for r in rows]==[POD,TOWER];worlds={'original':{}};entries=[]
 for r in rows:
  raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];worlds['original'][r['uid']]=decode_original_world_triangles(raw);target=LOCAL/r['candidate']['entry']['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);entries.append(r['candidate']['entry'])
 save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=entries,counts=dict(packedModels=2),area='Private original Olympian City One assembly'))
 save(LOCAL/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{r['uid']:r['source']for r in rows});save(DOC/'terrain-candidates.json',read(PAIR/'terrain-candidates.json'))
 validate=HERE.parent/'building-batch/validate_candidates.mjs';cmd=['node',str(validate),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'source-forms.json').relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))]
 with(DOC/'validation.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 assert p.returncode in[0,1];save(DOC/'validation-command.json',dict(command=cmd,exitCode=p.returncode))
 near=read(NEAR/'neighbour-inputs.json.gz');near['candidateIds']=[POD,TOWER];save(DOC/'neighbour-inputs.json.gz',near)
 for tool in ['check-neighbours.mjs','check-native-neighbours-multi-retained-scoped-v3.mjs']:subprocess.run(['node',str(HERE/tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True);refs.append(HERE/tool)
 capture=read(ATTR/'attributes.json.gz')['rows']
 for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]={r['uid']:np.asarray(r[field],dtype='<f8').reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]for r in capture}
 g=read(HERE/'local'/PAIR.name/'runtime-geometry.json.gz')['rows'];ground=np.unique(np.concatenate([np.asarray(r['drawnGroundGeometry']).reshape(-1,9)for r in g]),axis=0).reshape(-1,3,3);final=module('olympian_pair_foundation',HERE/'xl-final-script-pass.py');foundations=[];bindings=read(BIND/'exact-source-face-bindings.json.gz')['bindings']
 for mode,world in worlds.items():
  for r in rows:
   uid=r['uid'];tri=world[uid];h=digest(tri.astype('<f8').tobytes());assert h==next(b['wholeWorldSHA256']for b in bindings if b['uid']==uid and b['mode']==mode)
   support=ground if uid==POD else np.concatenate([ground,world[POD]]);b=r['source']['building'];f=final.foundation_context(tri,support,Polygon(b['rings'][0],b['rings'][1:]));strict=f['completeTerrainTriangles']==len(tri)and f['fullyBuriedAreaFraction']==0 and f['fullyBuriedUpwardTriangles']==0
   item=dict(uid=uid,mode=mode,worldSHA256=h,foundation=f,strictFoundationAccepted=strict);foundations.append(item);save(DOC/(uid.split('/')[1]+'-'+mode+'-foundation.json'),item);print(uid,mode,'foundation',strict,flush=True)
 metrics=read(PAIR/'metrics.json');identity=read(IDENTITY/'72354:0-review.json');tower=read(PAIR/'256927:0-identity.json');assert identity['identityOnlyApproved']and tower['passed'];policy=module('olympian_pair_policy',HERE/'acceptance-policy.py');raw=[]
 for r in rows:
  proof=identity['identityProof']if r['uid']==POD else tower['proof'];m=next(m for m in metrics['rows']if m['uid']==r['uid']);raw.extend(r['uid']+':'+x for x in policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=r['sourceSHA256'],identityProof=proof),m,metrics['profiles']['mobile']))
 validation=read(DOC/'validation.json');raw.extend('validation:'+r['uid']+':'+x for r in validation['results']for x in r.get('concerns',[]))
 if validation['loaderAccepted']!=2 or validation['checksPassed']!=2 or validation['exceptions']:raw.append('complete-current-loader-validation')
 for r in read(DOC/'neighbour-checks.json')['rows']:raw.extend('neighbour:'+r['uid']+':'+x for x in r['reasons'])
 native=read(DOC/'native-neighbour-checks.json');raw.extend('native:'+uid for uid in set(native['blocked'])-set(native['resolved']))
 raw.extend('foundation:'+r['uid']+':'+r['mode']for r in foundations if not r['strictFoundationAccepted']);raw.append('original-support-interface-unresolved')
 summary=dict(uids=[POD,TOWER],rawReasons=sorted(set(raw)),allCompoundFoundationsPassed=all(r['strictFoundationAccepted']for r in foundations),loaderChecksPassed=validation['checksPassed'],installationApproved=False,sourceGeometryChanges=0);save(DOC/'summary.json',summary);print(summary,flush=True)
 for report in [read(DOC/'neighbour-checks.json'),native,validation]:
  for p,h in report.get('inputHashes',{}).items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([validate,HERE/'xl-final-script-pass.py',HERE/'acceptance-policy.py',HERE/'exact_packed_world_geometry_20261009.py']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file())
 module('olympian_pair_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-pair-loader-neighbour-four-world-foundations',list(dict.fromkeys(refs)),summary)
if __name__=='__main__':main()
