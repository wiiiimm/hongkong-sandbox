"""Discover exact government sources for the unmatched POPCORN II neighbour across all registered government sheets."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-popcorn-neighbour-source-v1-20261021';DOC=BASE/BATCH;SRC=BASE/'government-xl-tko-assembly-capture-v1-20261021'
def main():
 assert not DOC.exists();receipt=read(SRC/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};selection=SRC/'selection.json.gz';assert digest(selection.read_bytes())==pins[str(selection.relative_to(ROOT))]
 row=next(r for r in read(selection)['rows']if r['uid']=='landsd/265489:0');refs=[Path(__file__),SRC/'result.json',selection];forms={};manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest)
 for t in read(manifest)['tiles']:
  p=ROOT/'3d-viewer'/t['url'];matches=[b for b in read(p)['buildings']if b['uid'] in {'landsd/81731:0'}]
  if matches:
   refs.append(p)
   for b in matches:forms[b['uid']]=dict(building=b,tile=t['url'])
 assert set(forms)=={'landsd/81731:0'};found=[]
 hashes={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  import json
  pattern=json.dumps(dict(models=[dict(matching=dict(officialCandidates=[dict(objectId=81731,buildingCSUID=forms['landsd/81731:0']['building']['buildingCSUID'])]))]))
  registries=db.execute('SELECT DISTINCT r.cache_key,r.result_sha,r.result,i.sheet FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.result @> %s::jsonb ORDER BY r.cache_key',(NATIVE_RUN,pattern)).fetchall()
  save(DOC/'query.json',dict(runId=NATIVE_RUN,pattern=json.loads(pattern),matchingRegistries=len(registries),scope='all registered sheets in pinned native run'))
  for key,sha,result,sheet in registries:
   hits=[]
   for model in result['models']:
    for c in model.get('matching',{}).get('officialCandidates',[]):
     for uid,source in forms.items():
      b=source['building']
      if c.get('objectId')==b['objectId'] and c.get('buildingCSUID')==b['buildingCSUID']:
       hits.append(dict(uid=uid,source=source,model=model,candidate=c,nativeStageKey=key,nativeStageSHA256=sha,sheet=sheet))
   if hits:save(DOC/('registry-'+key+'.json.gz'),dict(cacheKey=key,resultSHA256=sha,result=result));found.extend(hits)
 for p,h in hashes.items():assert digest((ROOT/p).read_bytes())==h
 save(DOC/'nominations.json',dict(rows=found,forms=forms,missing=sorted(set(forms)-{x['uid']for x in found}),installationApproved=False))
 result=dict(uids=sorted(forms),found=sorted({x['uid']for x in found}),missing=sorted(set(forms)-{x['uid']for x in found}),installationApproved=False,sourceGeometryChanges=0)
 module('tko_neighbour_sources_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-object-and-csuid-neighbour-original-discovery',refs,result)
 print([(r['uid'],r['model']['modelId'],r['model']['triangles'],r['model']['asset']['sha256'])for r in found],flush=True)
if __name__=='__main__':main()
