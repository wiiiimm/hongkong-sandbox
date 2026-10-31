"""Bind Hoi Yu's existing support interpretation to unchanged current sources."""
from pathlib import Path
import math
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-park-avenue239350-hoi-yu-prior-review-v2-20261018';DOC=BASE/BATCH
OLD=BASE/'government-xl-hoi-fu-yu-typed-original-installed-v3-20261009';CHECK=BASE/'government-xl-park-avenue239350-native-regression-v1-20261018'
def main():
 assert not DOC.exists();refs=[Path(__file__)];records=[]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [OLD,CHECK]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);records.append(r);refs.append(folder/'result.json')
 oldpins={e['path']:e['sha256']for e in records[0]['evidenceRefs']}
 oldpins.update({e['path']:e['sha256']for e in records[0]['evidence'].values()if isinstance(e,dict)and 'path'in e and 'sha256'in e})
 for name in ['typed-roles-publication-recheck.json','installed-acceptance.json','support-recheck/diagnostic.json.gz']:
  p=OLD/name;assert digest(p.read_bytes())==oldpins[str(p.relative_to(ROOT))];refs.append(p)
 decision=read(OLD/'installed-acceptance.json');assert decision['passed']and decision['modelGeometryChanges']==0
 current=read(CHECK/'native-neighbour-checks.json');pins={e['path']:e['sha256']for e in records[1]['evidenceRefs']}
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins)
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');entries={}
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:
   if e['uid']in ['landsd/177604:0','landsd/177605:0']:
    asset=p.parent/e['asset'];assert digest(asset.read_bytes())==e['sha256'];entries[e['uid']]=e;refs.extend([p,asset])
 tower=entries['landsd/177605:0'];support=entries['landsd/177604:0'];assert tower['sha256']==decision['sourceSHA256s']['landsd/177605:0'];dep=next(x for x in tower['supportDependencies']if x['uid']==support['uid']);assert dep['sha256']==support['sha256']and dep['csuid']==support['buildingCSUID'];assert tower['sha256']in records[0]['sourceSHA256s'].values()and support['sha256']in records[0]['sourceSHA256s'].values()
 row=next(x for x in current['rows']if x['uid']==tower['uid']);t=row['terrain'];assert t['newlyWhollyBuried']==t['newlyUpwardWhollyBuried']==0 and abs(t['maximumBurialIncrease'])<1e-10 and abs(t['minimumGapBefore']-t['minimumGapAfter'])<=math.ulp(t['minimumGapBefore'])
 summary=dict(minimumGapDifferenceM=abs(t['minimumGapBefore']-t['minimumGapAfter']),minimumGapOneULPM=math.ulp(t['minimumGapBefore']),uids=[tower['uid'],support['uid']],existingExactSourceSupportReviewVerified=True,currentSourcesAndDependencyUnchanged=True,threePodiumCandidateTerrainRegression=row,rawGenericSupportFailureRetained=True,qualification='Prior exact-source support acceptance is relevant; the 50% generic rim failure is not new source damage. Current corrected three-podium candidate repeats complete terrain regression with no changed clearance or new burial. No new installation or blanket policy exemption.',fullAcceptance=False,newlyInstalled=0)
 save(DOC/'review.json',summary);r=module('hoi_yu_prior_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'park-avenue-hoi-yu-prior-exact-support-review-v1',list(set(refs)),summary);print(r['jobId'],flush=True)
if __name__=='__main__':main()
