"""Restore original clubhouse via existing revision-checked government fallback."""
import sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
import shape_prepare
BATCH='government-xl-inone-clubhouse-restore-v2-20261022';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
 assert not DOC.exists()
 prior=BASE/'government-xl-inone-adjoining-sources-v1-20261022';_,pins=authenticate(prior);p=prior/'sources.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 r=next(r for r in read(p)['rows']if r['model']['modelId']=='B369231905501063C0');uid='landsd/277974:0';m=r['model'];assert m['candidate']['uid']==uid
 tile=ROOT/'3d-viewer/city/data/tiles/1_-2.json';b=next(b for b in read(tile)['buildings']if b['uid']==uid);assert b['buildingCSUID']==m['candidate']['buildingCSUID']
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+uid],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  inp=LOCAL/'recovery-inputs.json.gz';save(inp,dict(rows=[uid],sources={uid:dict(building=b)},native=[dict(cacheKey=r['cacheKey'],resultSha=r['resultSha'],sheet='11-NW-25B',model=m)]))
  result=shape_prepare.prepare(inp,LOCAL/'recovered',allow_source=True,workers=1,env_file=ROOT/'.env.modelling',reservation_receipt=lease)
  refs=[Path(__file__),p,prior/'result.json',tile,inp,Path(shape_prepare.__file__)]
  summary=dict(uids=[uid],recovery=result,installationApproved=False,newlyInstalled=0,priorFailure='V1: R2 endpoint configuration unavailable; source lease released, no source corruption implied.')
  if not result['errors']:
   asset=Path(result['rows'][0]['candidate']['path']);assert digest(asset.read_bytes())==m['asset']['sha256'];refs.append(asset);summary['sourceSHA256']=m['asset']['sha256']
  refs.extend(x for x in (LOCAL/'recovered').rglob('*')if x.is_file()and x.name!='reservation.json')
  save(DOC/'recovery.json',summary)
  module('inone_restore2_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-clubhouse-source-recovery',refs,summary)
  print(dict(errors=result['errors'],methods=result['methods']),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
