"""Nominate complete frozen-sheet originals intersecting missing footprint regions."""
from pathlib import Path
import shapely
from shapely.geometry import shape,box
from run import ROOT,HERE,read,save,digest,connect
from require_remaining_xl import require_remaining
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing26195-missing-sheet-candidates-v2-20261017';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-west-wing26195-missing-coverage-v1-20261017';CAP=BASE/'government-xl-west-wing26195-complete-current-runtime-capture-v2-20261012';UID='landsd/26195:0'
def main():
 assert not DOC.exists();row=next(r for r in read(CAP/'selection.json.gz')['rows']if r['uid']==UID);count=BASE/'government-xl-citic-original-installed-v1-20261017/full-xl-current-count.json';frozen=require_remaining(count,UID,row['sourceSHA256']);cache_key,model_id=frozen['sourceKey'].split('/');assert model_id==row['modelId'];receipt=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  sha,native=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(cache_key,)).fetchone();assert len(sha)==64
 for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 regions=read(PRIOR/'missing-components.geojson')['features'];missing=shapely.union_all([shape(r['geometry'])for r in regions]);models=native['models'];assert models and all(m.get('worldBounds')for m in models)
 target=next(m for m in models if m['modelId']==row['modelId']);assert target['asset']['sha256']==row['sourceSHA256']
 known={r['uid']for r in read(PRIOR/'coverage.json')['sourceAttribution']}|{UID};candidates=[]
 for m in models:
  lo,hi=m['worldBounds'];p=box(lo[0],lo[2],hi[0],hi[2]);area=p.intersection(missing).area
  if area<=0:continue
  matches=[x['uid']for x in m.get('matching',{}).get('viewerMatches',[])]
  candidates.append(dict(model=m,missingBoundingOverlapM2=area,matchingUids=matches,alreadyCompared=bool(matches)and set(matches)<=known,components=[dict(component=r['properties']['component'],boundingOverlapM2=p.intersection(shape(r['geometry'])).area)for r in regions if p.intersection(shape(r['geometry'])).area>0]))
 candidates.sort(key=lambda r:-r['missingBoundingOverlapM2']);summary=dict(uid=UID,sheet=row['candidate']['entry']['sourceTile'],cacheKey=cache_key,resultSHA=sha,completeSheetSources=len(models),allBoundsPresent=True,candidateCount=len(candidates),newCandidateCount=sum(not r['alreadyCompared']for r in candidates),missingAreaM2=missing.area,boundsOnly=True,sourceCoverageAccepted=False,qualification='Complete frozen sheet bounds nomination. Bounds overlap grants no projected geometry or identity credit; adjacent sheets are not ruled out.')
 save(DOC/'candidates.json.gz',dict(summary=summary,rows=candidates));save(DOC/'sheet-result.json.gz',dict(resultSHA=sha,cacheKey=cache_key,result=native))
 refs=[Path(__file__),count,CAP/'selection.json.gz',PRIOR/'result.json',PRIOR/'missing-components.geojson',PRIOR/'coverage.json',HERE/'require_remaining_xl.py']
 out=module('west_missing_sheet_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-sheet-missing-footprint-candidate-scan-v1',refs,dict(uids=[UID],summary=summary,nextStep='Decode nominated original meshes and intersect their actual projected facets with the saved missing polygons.'))
 print(dict(jobId=out['jobId'],summary=summary),flush=True)
 for r in candidates:print(dict(modelId=r['model']['modelId'],uids=r['matchingUids'],boundsOverlap=r['missingBoundingOverlapM2'],alreadyCompared=r['alreadyCompared']),flush=True)
if __name__=='__main__':main()
