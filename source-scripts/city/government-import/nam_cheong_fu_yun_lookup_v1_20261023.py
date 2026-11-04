"""Bind the exact cached adjacent original for source118003 identity investigation."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
B='government-xl-nam-cheong-fu-yun-lookup-v1-20261023';BASE=ROOT/'docs/astra-city/government-import';D=BASE/B
CAP='government-xl-after-fu-wong-nam-cheong-capture-v1-20261023'
assert not D.exists()
_,pins=authenticate(BASE/CAP);p=BASE/CAP/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
r=next(x for x in read(p)['rows']if x['uid']=='landsd/268867:0');tile=ROOT/'3d-viewer'/r['source']['tile'];other=next(x for x in read(tile)['buildings']if x['uid']=='landsd/270874:0')
assert other['buildingCSUID']=='3403120913T20050430'
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');sha,d=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(r['native']['cacheKey'],)).fetchone()
 assert sha==r['native']['resultSha']
 matches=[m for m in d['models']if m['modelId']=='B340312091301063C0'];assert len(matches)==1
 assert matches[0]['triangles']==6035 and matches[0]['asset']['sha256']=='159453e8bc40543eb211dd9e0e2081e9796651051f430c935359e29b03ea31eb'
 assert any(v['uid']==other['uid'] and v['buildingCSUID']==other['buildingCSUID'] for v in matches[0]['matching']['viewerMatches'])
 lookup=dict(nativeCacheKey=r['native']['cacheKey'],nativeResultSHA256=sha,matchedOriginalModels=matches,currentAdjacentForm=other,currentTileSHA256=digest(tile.read_bytes()),sourceOnly=True,identityAccepted=False,installationApproved=False)
 save(D/'lookup.json',lookup)
 module('adjacent_lookup_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B,'exact-adjacent-original-lookup',[Path(__file__),BASE/CAP/'result.json',p,tile,D/'lookup.json'],dict(uids=['landsd/268867:0'],relatedUID=other['uid'],matchedModels=1,identityAccepted=False,installationApproved=False))
