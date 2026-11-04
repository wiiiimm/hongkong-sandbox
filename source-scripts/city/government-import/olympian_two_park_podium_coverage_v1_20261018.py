"""Account for the podium footprint using exact original assembly projections."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon,mapping
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-olympian-two-park-seven-four-world-v2-20261018';SEL=BASE/'government-xl-olympian-two-park-current-identity-runtime-v1-20261018';BATCH='government-xl-olympian-two-park-podium-coverage-v1-20261018';DOC=BASE/BATCH;UID='landsd/72277:0';TOWERS=['landsd/79627:0','landsd/83600:0','landsd/79657:0','landsd/80122:0','landsd/83837:0']
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,SEL]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 worlds=read(CAP/'world-triangles.json.gz')['original'];row=next(x for x in read(SEL/'selection.json.gz')['rows']if x['uid']==UID);form=row['source']['building'];target=Polygon(form['rings'][0],form['rings'][1:]);projections={u:shapely.union_all(shapely.polygons(np.asarray(worlds[u])[:,:,[0,2]]))for u in [UID]+TOWERS};missing=target.difference(projections[UID]);towerunion=shapely.union_all([projections[u]for u in TOWERS]);assembly=shapely.union_all(list(projections.values()));remaining=target.difference(assembly)
 summary=dict(uids=[UID]+TOWERS,sourceSHA256=row['sourceSHA256'],targetAreaM2=target.area,podiumOnlyCoverage=target.intersection(projections[UID]).area/target.area,missingFromPodiumM2=missing.area,missingCoveredByTowersM2=missing.intersection(towerunion).area,assemblyCoverage=target.intersection(assembly).area/target.area,remainingUncoveredM2=remaining.area,fullAcceptance=False,newlyInstalled=0,qualification='Complete original planar projection accounting only. Identity, vertical relationship, support, terrain and publication decisions remain separate.')
 save(DOC/'coverage.json',summary);save(DOC/'geometry.json.gz',dict(target=mapping(target),podium=mapping(projections[UID]),missingFromPodium=mapping(missing),towerProjections={u:mapping(projections[u])for u in TOWERS},remainingUncovered=mapping(remaining)))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins);out=module('podium_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-park-podium-complete-assembly-coverage-v1',list(set(refs)),summary);print(dict(jobId=out['jobId'],**summary),flush=True)
if __name__=='__main__':main()
