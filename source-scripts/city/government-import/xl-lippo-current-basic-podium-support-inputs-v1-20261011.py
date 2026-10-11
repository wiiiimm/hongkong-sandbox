"""Bind actual BASIC podium and two original upper sources; diagnostic only."""
from pathlib import Path
import importlib.util,json,subprocess,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from lippo_three_original_current_inventory_20261010 import catalogue_inventory
BATCH='government-xl-lippo-current-basic-podium-support-inputs-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
PHYS=DOC.parent/'government-xl-lippo-two-original-disjoint-current-parent-physical-v3-20261011'
CAPTURE=DOC.parent/'government-xl-lippo-current-bound-six-roof-inputs-v4-20261011'
TOWER=DOC.parent/'government-xl-lippo-tower-current-complete-original-identity-diagnostic-v2-20261011'
LANGHAM=DOC.parent/'government-xl-lippo-langham-current-complete-original-identity-diagnostic-v2-20261011'
EXPORTER=HERE/'xl-lippo-current-basic-podium-support-geometry-v1-20261011.mjs'
def main():
 assert not DOC.exists();claim=reservations.claim('lippo-actual-basic-body-inputs-'+str(uuid.uuid4()),['building:landsd/231645:0','building:landsd/237843:0','building:landsd/239465:0'],batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();inventory=catalogue_inventory(before)
  capture=read(CAPTURE/'current-inputs.json.gz');assert digest(before)==capture['manifestSHA256'] and inventory==capture['catalogueInventory']
  own=[b for b in capture['forms'] if b['uid']=='landsd/231645:0'];assert len(own)==1;building=own[0];tile='city/data/tiles/0_-1.json';tilepath=ROOT/'3d-viewer'/tile
  assert [b for b in read(tilepath)['buildings'] if b['uid']==building['uid']]==[building]
  installed=[e for url in read(manifest)['officialModelCatalogues'] for e in read(ROOT/'3d-viewer'/url)['models']];assert not any(e['uid'] in {'landsd/231645:0','landsd/237843:0','landsd/239465:0'} for e in installed)
  rows=[]
  for d in [TOWER,LANGHAM]:
   receipt=read(d/'result.json');proof=read(d/'identity.json');assert proof['passed'] and proof['reasons']==[]
   for ref in receipt['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
   with connect() as c:
    c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
   selected=read(d/'selection.json.gz');assert selected['manifestSHA256']==digest(before) and len(selected['rows'])==1;r=selected['rows'][0]
   assert digest((ROOT/r['candidate']['path']).read_bytes())==r['sourceSHA256']
   with connect() as c:
    c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,r['native']['cacheKey'])).fetchone()==(r['native']['resultSha'],)
   rows.append(r)
  assert {r['uid'] for r in rows}=={'landsd/237843:0','landsd/239465:0'}
  save(DOC/'input.json.gz',dict(currentBasicUID=building['uid'],currentForm=building,currentTile=tile,currentTileSHA256=digest(tilepath.read_bytes()),manifestSHA256=digest(before),catalogueInventory=inventory,rows=rows,originalGovernmentPodiumUsedAsSupport=False))
  result=subprocess.run(['node',str(EXPORTER)],cwd=ROOT,capture_output=True,text=True);save(DOC/'export-log.json',dict(command=['node',str(EXPORTER.relative_to(ROOT))],exitCode=result.returncode,stdout=result.stdout,stderr=result.stderr));assert result.returncode==0,result.stderr
  body=read(DOC/'complete-current-basic-podium-geometry.json.gz');assert body['startAndEndInputHashesVerified'] and body['currentActorChanges']==0 and not body['originalGovernmentPodiumUsedAsSupport']
  for path,pin in body['inputHashes'].items():assert digest((ROOT/path).read_bytes())==pin
  assert manifest.read_bytes()==before and catalogue_inventory(before)==inventory and reservations.owns(claim['reservation'])
  refs=[Path(__file__),EXPORTER,HERE/'literal_production_module_dependency_closure_20261010.mjs',HERE/'test_literal_production_module_dependency_closure_20261010.mjs',CAPTURE/'result.json',CAPTURE/'current-inputs.json.gz',PHYS/'result.json',HERE/'local'/PHYS.name/'runtime-geometry.json.gz',*[d/'result.json' for d in [TOWER,LANGHAM]],*[d/'selection.json.gz' for d in [TOWER,LANGHAM]],*[ROOT/r['candidate']['path'] for r in rows]]+[ROOT/path for path in body['inputHashes']]
  sp=importlib.util.spec_from_file_location('lippo_basic_input_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
  receipt=m.freeze(BATCH,'complete-actual-current-basic-podium-plus-two-original-support-inputs-v1',refs,dict(uids=['landsd/231645:0','landsd/237843:0','landsd/239465:0'],manifestSHA256=digest(before),completeCurrentBasicFaces=len(body['completeCurrentRendererBody']['index'])//3,completeUpperOriginalFaces=sum(r['triangles'] for r in rows),originalGovernmentPodiumUsedAsSupport=False,groundSupportAccepted=False,physicalAccepted=False,installationApproved=False))
  print(json.dumps(dict(jobId=receipt['jobId'],basicFaces=receipt['completeCurrentBasicFaces'],originalGovernmentPodiumUsedAsSupport=False)),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
