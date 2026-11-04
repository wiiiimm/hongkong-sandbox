"""Find station source records across the three pinned podium terrain sheets."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-southside-station-original-lookup-v1-20261028';DOC=BASE/BATCH;GROUND='government-xl-la-marina-southside-original-terrain-v1-20261028';UID='landsd/300867:0'
def main():
 assert not DOC.exists();_,pins=authenticate(BASE/GROUND);p=BASE/GROUND/'source-inputs.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];inputs=read(p)['inputs'];manifest=ROOT/'3d-viewer/city/data/manifest.json';m=read(manifest);forms=[];refs=[Path(__file__),BASE/GROUND/'result.json',p,manifest]
 for tile in m['tiles']:
  path=ROOT/'3d-viewer'/tile['url']
  for b in read(path)['buildings']:
   if b['uid']==UID:forms.append(dict(building=b,tile=tile['url'],tileSHA256=digest(path.read_bytes())));refs.append(path)
 assert len(forms)==1;form=forms[0]['building'];rows=[]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for sheet,record in inputs.items():
   sha,native=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(record['cacheKey'],)).fetchone();assert sha==record['resultSHA256'];matches=[]
   for model in native['models']:
    entry=model.get('candidate',{});viewer=[r for r in model.get('matching',{}).get('viewerMatches',[])if r['uid']==UID and r.get('buildingCSUID')==form.get('buildingCSUID')]
    if viewer:matches.append(dict(sourceKey=record['cacheKey']+'/'+model['modelId'],modelId=model['modelId'],triangles=model['triangles'],candidate=entry,matchingCurrentCSUID=True,model=model))
   rows.append(dict(sheet=sheet,nativeCacheKey=record['cacheKey'],nativeResultSHA256=sha,matches=matches))
 installed=[]
 for url in m['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;refs.append(path)
  installed.extend(dict(catalogue=str(path.relative_to(ROOT)),entry=e)for e in read(path)['models']if e['uid']==UID)
 result=dict(uids=['landsd/315025:0'],stationUid=UID,currentStationForm=forms[0],sheetsChecked=rows,stationCurrentlyInstalled=bool(installed),installedEntries=installed,sourceGeometryChanges=0,identityAccepted=False,installationApproved=False,qualification='Exact current UID/CSUID source lookup over all three authenticated adjacent terrain-sheet native records. No inferred model identity, support relationship, footprint exclusion, publication approval or source edit.')
 save(DOC/'lookup.json',result);module('southside_station_lookup_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-station-source-lookup-in-pinned-adjacent-sheets',refs,result);print(dict(stationCurrentlyInstalled=bool(installed),matches=[(r['sheet'],[(x['modelId'],x['triangles'])for x in r['matches']])for r in rows]),flush=True)
if __name__=='__main__':main()
