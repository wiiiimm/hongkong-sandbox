"""Look up the exact government podium original for Island Industrial Building."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
def main():
 batch='government-xl-island-industrial-podium-lookup-v1-20261023';doc=BASE/batch;assert not doc.exists();refs=[Path(__file__)]
 source='government-xl-all-200-original-terrain-batch-v2-20261022';_,pins=authenticate(BASE/source);p=BASE/source/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([BASE/source/'result.json',p]);owner=next(r for r in read(p)['rows']if r['uid']=='landsd/20270:0')
 tile=ROOT/'3d-viewer'/owner['source']['tile'];assert digest(tile.read_bytes())==owner['source']['tileSHA256'];refs.append(tile)
 uid='landsd/159422:0';form=next(b for b in read(tile)['buildings']if b['uid']==uid);assert form['buildingCSUID']=='3489620517P20060311'and form['structureType']=='Podium';form={**form,'tile':'0_-3'}
 meta='government-xl-remaining-186-primary-metadata-v1-20261023';_,mp=authenticate(BASE/meta);p=BASE/meta/'metadata.json.gz';assert digest(p.read_bytes())==mp[str(p.relative_to(ROOT))];refs.extend([BASE/meta/'result.json',p]);r=next(r for r in read(p)['rows']if r['uid']==owner['uid']);official=next(f for f in r['footprintMatches']if f['BuildingCSUID']==form['buildingCSUID']);assert official['Status']=='Active'and official['BaseHeight']==form['base']and official['TopHeight']==form['base']+form['height']
 key=owner['native']['cacheKey']
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');sha,native=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert sha==owner['native']['resultSha']
 models=[m for m in native['models']if any(v['uid']==uid and v.get('buildingCSUID')==form['buildingCSUID']for v in m.get('matching',{}).get('viewerMatches',[]))]
 row=dict(uid=uid,currentForm=form,matchedOriginalModels=models,matchCount=len(models),identityAccepted=False)
 result=dict(uids=[owner['uid']],relatedUIDs=[uid],nativeCacheKey=key,nativeResultSHA256=sha,rows=[row],sourceGeometryChanges=0,installationApproved=False,permanentRejection=False,qualification='Exact immutable cached model-to-current UID/CSUID lookup, tied to unchanged current vector tile and fresh official podium record. Shared GeoRef/permit is not support or installation approval. Acquisition remains a separately leased source-only step.')
 save(doc/'lookup.json',result);module('island_podium_lookup_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-island-industrial-podium-original-lookup',refs,result);print(dict(matches=[dict(modelId=m['modelId'],triangles=m['triangles'])for m in models]),flush=True)
if __name__=='__main__':main()
