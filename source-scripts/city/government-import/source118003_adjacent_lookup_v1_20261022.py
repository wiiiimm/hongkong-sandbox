"""Bind the exact cached adjacent original for source118003 identity investigation."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
B='government-xl-source118003-adjacent-lookup-v1-20261022';BASE=ROOT/'docs/astra-city/government-import';D=BASE/B
CAP='government-xl-next-seventeen-current-capture-v1-20261022'
assert not D.exists()
_,pins=authenticate(BASE/CAP);p=BASE/CAP/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
r=next(x for x in read(p)['rows']if x['uid']=='landsd/118003:0');tile=ROOT/'3d-viewer'/r['source']['tile'];other=next(x for x in read(tile)['buildings']if x['uid']=='landsd/118128:0')
assert other['buildingCSUID']=='3553718587T20050430'
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');sha,d=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(r['native']['cacheKey'],)).fetchone()
 assert sha==r['native']['resultSha']
 matches=[m for m in d['models']if m['modelId']=='B355371858701063C0'];assert len(matches)==1
 assert matches[0]['triangles']==550 and matches[0]['asset']['sha256']=='e3eee7aecd7157ae547c8a8747ba4e3f6a7f17f5a99ce3a699aecd8089b277b4'
 assert any(v['uid']==other['uid'] and v['buildingCSUID']==other['buildingCSUID'] for v in matches[0]['matching']['viewerMatches'])
 lookup=dict(nativeCacheKey=r['native']['cacheKey'],nativeResultSHA256=sha,matchedOriginalModels=matches,currentAdjacentForm=other,currentTileSHA256=digest(tile.read_bytes()),sourceOnly=True,identityAccepted=False,installationApproved=False)
 save(D/'lookup.json',lookup)
 module('adjacent_lookup_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B,'exact-adjacent-original-lookup',[Path(__file__),BASE/CAP/'result.json',p,tile,D/'lookup.json'],dict(uids=['landsd/118003:0'],relatedUID=other['uid'],matchedModels=1,identityAccepted=False,installationApproved=False))
