"""Select two exact adjacent originals; no source or identity approval transfer."""
from pathlib import Path
from copy import deepcopy
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';B='government-xl-nam-cheong-fu-yun-pair-selection-v1-20261023';D=BASE/B
N={'capture':'government-xl-after-fu-wong-nam-cheong-selection-v1-20261023','lookup':'government-xl-nam-cheong-fu-yun-lookup-v1-20261023','acquire':'government-xl-nam-cheong-fu-yun-acquire-v1-20261023'}
assert not D.exists();refs=[Path(__file__)];pins={}
for k,n in N.items():
 _,pins[k]=authenticate(BASE/n);refs.append(BASE/n/'result.json')
def take(k,f):
 p=BASE/N[k]/f;assert digest(p.read_bytes())==pins[k][str(p.relative_to(ROOT))];refs.append(p);return read(p)
s=take('capture','selection.json.gz');assert len(s['rows'])==1;r=s['rows'][0];assert r['uid']=='landsd/268867:0'
lookup=take('lookup','lookup.json');a=take('acquire','summary.json');assert a['sourceRecovered']
other=lookup['currentAdjacentForm'];tile=ROOT/'3d-viewer'/r['source']['tile'];assert [f for f in read(tile)['buildings']if f['uid']==other['uid']]==[other];refs.append(tile)
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');sha,d=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(lookup['nativeCacheKey'],)).fetchone()
 assert sha==lookup['nativeResultSHA256']==r['native']['resultSha'];m=next(m for m in d['models']if m['modelId']=='B340312091301063C0');assert m==lookup['matchedOriginalModels'][0]
entry=deepcopy(m['candidate']);entry.update(proceduralWindows=False,rootTranslation=[-834500,0,816500],sourceBaseHeight=other['baseHeightHKPD'],sourceTopHeight=other['topHeightHKPD'],sourceTile=r['candidate']['entry']['sourceTile'])
assert entry['sha256']==a['sourceSHA256'] and entry['uid']==other['uid']=='landsd/270874:0'
new=dict(uid=other['uid'],modelId=m['modelId'],triangles=m['triangles'],sourceSHA256=entry['sha256'],originalGeometryOnly=True,source=dict(building=other,tile=r['source']['tile'],tileSHA256=digest(tile.read_bytes())),native=dict(cacheKey=lookup['nativeCacheKey'],resultSha=sha,model=m),candidate=dict(path=a['asset']['path'],entry=entry))
rows=[r,new]
for v in rows:
 p=ROOT/v['candidate']['path'];assert digest(p.read_bytes())==v['sourceSHA256'];refs.append(p)
manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==s['manifestSHA256'];refs.append(manifest)
for url in read(manifest)['officialModelCatalogues']:
 p=ROOT/'3d-viewer'/url;assert not {v['uid']for v in rows}&{m['uid']for m in read(p)['models']};refs.append(p)
save(D/'selection.json.gz',dict(rows=rows,manifestSHA256=s['manifestSHA256']))
module('pair_selection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B,'exact-adjacent-original-pair-selection',refs,dict(uids=[v['uid']for v in rows],sourceSHA256ByUid={v['uid']:v['sourceSHA256']for v in rows},installationApproved=False,identityAccepted=False,sourceGeometryChanges=0))
