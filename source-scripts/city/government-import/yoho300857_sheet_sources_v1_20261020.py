"""Complete cached provider-sheet support discovery, no acceptance or mutation."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho300857-sheet-sources-v1-20261020';DOC=BASE/BATCH
SRC=BASE/'government-xl-two-tower-support-nomination-v1-20261020'
assert not DOC.exists();receipt=read(SRC/'result.json');inp=SRC/'nominations.json';pins={x['path']:x['sha256']for x in receipt['evidenceRefs']};assert digest(inp.read_bytes())==pins[str(inp.relative_to(ROOT))];target=next(r for r in read(inp)['rows']if r['uid']=='landsd/300857:0');box=target['worldBounds'];refs=[Path(__file__),SRC/'result.json',inp];hits=[];registries=[]
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 sheet=c.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s',(target['nativeStageKey'],)).fetchone()[0]
 rows=c.execute('SELECT r.cache_key,r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND i.sheet=%s ORDER BY r.cache_key',(NATIVE_RUN,sheet)).fetchall()
 for key,sha,result in rows:
  save(DOC/('registry-'+key+'.json.gz'),dict(cacheKey=key,resultSHA256=sha,result=result));registries.append(dict(cacheKey=key,resultSHA256=sha,count=len(result['models'])))
  for m in result['models']:
   b=m.get('worldBounds')
   if b and all(b[0][a]<=box[1][a]+2 and box[0][a]-2<=b[1][a]for a in [0,2]):hits.append(dict(cacheKey=key,modelId=m['modelId'],asset=m.get('asset'),triangles=m.get('triangles'),worldBounds=b,verticalGapFromTowerBaseM=box[0][1]-b[1][1],matching=m.get('matching'),isTower=m.get('asset',{}).get('sha256')==target['sourceSHA256']))
final=module('yoho_sheet_forms',HERE/'xl-final-script-pass.py');near=final.load_forms([box[0][0]-2,box[0][2]-2,box[1][0]+2,box[1][2]+2]);forms=[]
for b,polygon,tile in near:
 forms.append(dict(uid=b['uid'],name=b.get('name'),buildingCSUID=b.get('buildingCSUID'),objectId=b.get('objectId'),baseHeightHKPD=b.get('baseHeightHKPD'),topHeightHKPD=b.get('topHeightHKPD'),structureType=b.get('structureType'),rings=b.get('rings'),tile=tile));refs.append(ROOT/'3d-viewer'/tile)
save(DOC/'discovery.json',dict(uid=target['uid'],nativeRun=NATIVE_RUN,sheet=sheet,registries=registries,boundsCandidates=hits,nearbyOfficialForms=forms,scope='All cached results in fixed native run for exact covering sheet; horizontal2m nomination only, no vertical filtering. Neighbour sheets/fresh provider availability not exhausted.',installationApproved=False,sourceGeometryChanges=0))
print(dict(sheet=sheet,registries=len(registries),models=sum(x['count']for x in registries),hits=[(x['modelId'],x['verticalGapFromTowerBaseM'])for x in hits],nearbyForms=[(x['uid'],x['name'])for x in forms]),flush=True)
module('yoho_sheet_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'cached-covering-sheet-source-discovery',list(dict.fromkeys(refs)),dict(uids=[target['uid']],registries=registries,candidates=len(hits),installationApproved=False))
