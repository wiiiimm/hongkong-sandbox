"""Read-only primary packed-source context beyond the cached viewer-match list."""
from pathlib import Path
import re
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying233291-raw-source-context-v1-20261029';LOOKUP='government-xl-fuying233291-current-original-lookup-v1-20261029'
def main():
 out=BASE/BATCH;assert not out.exists();_,pins=authenticate(BASE/LOOKUP);path=BASE/LOOKUP/'lookup.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];prior=read(path);row=prior['rows'][0];assert row['uid']=='landsd/233291:0'and not row['matches'];form=row['source']['building'];points=[p for ring in form['rings']for p in ring];box=[min(p[0]for p in points),min(p[1]for p in points),max(p[0]for p in points),max(p[1]for p in points)];prefix='B'+form['buildingCSUID'][:10];candidates=[];total=0
 with connect()as db:
  db.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
  for record in prior['checkedNativeRecords']:
   sha,result=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(record['cacheKey'],)).fetchone();assert sha==record['resultSHA256']
   for model in result['models']:
    total+=1;bounds=model.get('worldBounds');spatial=bool(bounds and bounds[0][0]<=box[2]and bounds[1][0]>=box[0]and bounds[0][2]<=box[3]and bounds[1][2]>=box[1]);exact=model['modelId'].startswith(prefix)
    if exact or spatial:candidates.append(dict(sheet=record['sheet'],nativeCacheKey=record['cacheKey'],nativeResultSHA256=sha,sourceKey=record['cacheKey']+'/'+model['modelId'],exactCSUIDGeoRefPrefix=exact,closedSourceAABBTouchesForm=spatial,model=model))
 summary=dict(uids=[row['uid']],source=row['source'],expectedGeoRefPrefix=prefix,formBounds=box,searchedSheets=prior['searchedSheets'],checkedNativeRecords=prior['checkedNativeRecords'],completeRawModelsChecked=total,candidates=candidates,exactPrefixModels=sum(r['exactCSUIDGeoRefPrefix']for r in candidates),sourceGeometryChanges=0,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Complete raw packed models on two explicitly pinned sheets, independent of cached matching lists. Prefix and closed actual-source AABB nomination only; no exact component, source ownership, contact or source absence conclusion.')
 save(out/'summary.json',summary);module('fuying_raw_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-local-pinned-raw-source-prefix-and-actual-bounds-nomination', [Path(__file__),BASE/LOOKUP/'result.json',path],summary);print(dict(modelsChecked=total,nominated=len(candidates),exactPrefix=summary['exactPrefixModels']),flush=True)
if __name__=='__main__':main()
