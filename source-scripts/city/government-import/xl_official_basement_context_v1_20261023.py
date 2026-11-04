"""Check official basement metadata against exact cached original source bounds."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';N='government-xl-remaining-official-structure-context-v1-20261022';B='government-xl-official-basement-context-v1-20261023';D=BASE/B
assert not D.exists();_,pins=authenticate(BASE/N);refs=[Path(__file__),BASE/N/'result.json']
def take(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
metadata=take(BASE/N/'summary.json');structures={}
for p in (BASE/N).glob('structures-*.json'):
 if p.name.endswith('-request.json'):continue
 for f in take(p)['features']:
  a=f['attributes'];structures[a['BuildingStructureID']]=a
rows=[]
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY')
 for r in metadata['rows']:
  below=[structures[i]for i in r['officialStructureIDs']if i in structures and (structures[i].get('StoreysInBasement')or 0)>0]
  if not below:continue
  cache,modelid=r['sourceKey'].split('/');found=db.execute("SELECT r.result_sha,m.value FROM astra_modelling.native_stage_results r CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') m WHERE r.cache_key=%s AND m.value->>'modelId'=%s",(cache,modelid)).fetchall();assert len(found)==1
  native_sha,model=found[0];assert model['asset']['sha256']==r['indexedSourceSHA256'];bounds=model['worldBounds'];assert len(bounds)==2 and len(bounds[0])==len(bounds[1])==3
  primary=r['officialPrimaryRecords'];assert len(primary)==1 and r['officialExactActiveRecord'];record=primary[0];base=record.get('BaseHeight');assert base==(r['currentForm']or{}).get('baseHeightHKPD')
  difference=base-bounds[0][1]if base is not None else None
  rows.append(dict(uid=r['uid'],sourceKey=r['sourceKey'],sourceSHA256=r['indexedSourceSHA256'],nativeResultSHA256=native_sha,nativeModel=model,officialPrimaryRecord=record,officialStructureRecords=below,officialBaseHeightHKPD=base,sourceMinimumY=bounds[0][1],sourceMaximumY=bounds[1][1],sourceDepthBelowOfficialBaseM=difference,belowGradeGeometryNominated=difference is not None and difference>.5))
summary=dict(uids=sorted(r['uid']for r in rows),counts=dict(officialBasementMetadata=len(rows),originalBoundsBelowOfficialBaseOverHalfMetre=sum(r['belowGradeGeometryNominated']for r in rows)),rows=rows,installationApproved=False,physicalAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0,qualification='Official basement-storey records plus exact source-version-bound converter AABBs nominate semantic investigation only. Basement metadata does not prove the original mesh contains a valid basement, explain particular buried facets, establish support or approve any physical exception. Retain every raw failure and existing whole-source/four-world/terrain/neighbour/browser obligation.')
save(D/'summary.json',summary);module('basement_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B,'official-basement-source-bound-context',refs,summary)
print(summary['counts'],flush=True)
print([(r['uid'],r['sourceDepthBelowOfficialBaseM'])for r in rows if r['belowGradeGeometryNominated']],flush=True)
