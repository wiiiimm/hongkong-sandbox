"""Read-only saved complete Murray source inventory; no contact/root rerun."""
from pathlib import Path
import sys,json
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2];sys.path.insert(0,str(BASE))
from run import read,save,connect
DOC=ROOT/'docs/astra-city/government-import/government-xl-murray-bounded-original-support-inventory-v1-20261011'
def collect():
 row=next(r for r in read(ROOT/'docs/astra-city/government-import/government-xl-murray-original-support-20261006/selection.json.gz')['rows']if r['uid']=='landsd/265825:0');lo,hi=row['candidate']['entry']['worldBounds']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');sha,result=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone()
 assert sha==row['native']['resultSha'];rows=[]
 for m in result['models']:
  b=m.get('worldBounds')
  assert b is not None,'Inventory cannot omit source lacking bounds'
  if all(b[1][i]>=lo[i]and b[0][i]<=hi[i]for i in [0,2]):rows.append({'modelId':m['modelId'],'bounds':b,'asset':m.get('asset'),'sourceEntry':m['sourceEntry'],'viewerMatches':m.get('matching',{}).get('viewerMatches'),'nativeState':m.get('state')})
 return {'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'sheet':row['native']['sheet'],'cacheKey':row['native']['cacheKey'],'nativeResultSHA256':sha,'completeSheetModels':len(result['models']),'inventoryMethod':'Complete saved native-stage result; every original model whose source bounds overlap Murray tower bounds in XY. Inventory only, not contact/support.','rows':rows,'sourceOnly':True,'installationApproved':False}
if __name__=='__main__':
 assert not (DOC/'original-source-inventory.json').exists(),'Saved completed inventory must not be rerun unchanged'
 save(DOC/'original-source-inventory.json',collect())
