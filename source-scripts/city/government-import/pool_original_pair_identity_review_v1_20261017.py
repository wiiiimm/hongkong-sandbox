"""Scoped identity relationship for two byte-pinned original swimming-pool components."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sham-shui-po-pool-original-pair-identity-review-v1-20261017';DOC=BASE/BATCH
PODIUM='landsd/265480:0';TOWER='landsd/271043:0'
EXPECTED={PODIUM:'94e8a0199e420baee0673b9c227b1e2411aca086b3459245a7d899bace82a36b',TOWER:'fc1b0d304c3b50903c479cff16789ed94673dbec4ad59b87de8344dbd812991c'}
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};names=['government-xl-sham-shui-po-pool-current-identity-v1-20261017','government-xl-sham-shui-po-pool-four-world-contacts-v2-20261017','government-xl-sham-shui-po-pool-four-world-foundation-v1-20261017']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in names:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for q in r['evidenceRefs']:
    assert q['path'] not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 identities={u:read(BASE/names[0]/(u.replace('/','-').replace(':','-')+'.json')) for u in EXPECTED};assert identities[PODIUM]['proof']['passed']
 raw=identities[TOWER]['proof'];allowed={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'};assert set(raw['reasons'])==allowed
 rows={r['uid']:r for r in read(BASE/'government-xl-sham-shui-po-pool-original-group-v1-20261016/selection.json.gz')['rows']}
 for u,h in EXPECTED.items():
  r=rows[u];assert r['sourceSHA256']==h and digest((ROOT/r['candidate']['path']).read_bytes())==h;assert r['source']['building'] in read(ROOT/'3d-viewer'/r['source']['tile'])['buildings']
 assert rows[PODIUM]['source']['building']['structureType']=='Podium' and rows[TOWER]['source']['building']['structureType']=='Tower'
 contacts=read(BASE/names[1]/'summary.json');assert contacts['allWitnessesVerified'] and len(contacts['rows'])==4
 for r in contacts['rows']:assert r['strictSamples']==58 and r['strictContacts']==40 and r['strictWallContacts']==6 and r['remaining']==r['geometricWitnessesVerified']==12
 foundation=read(BASE/names[2]/'summary.json');assert foundation['allStrictPass'] and len(foundation['rows'])==8
 worlds=read(BASE/names[2]/'world-triangles.json.gz');f=module('pool_pair_current_forms',HERE/'xl-final-script-pass.py');measures=[]
 for mode,world in worlds.items():
  t=np.asarray(world[TOWER]);p=np.asarray(world[PODIUM]);target=Polygon(rows[TOWER]['source']['building']['rings'][0]);parent=Polygon(rows[PODIUM]['source']['building']['rings'][0]);projection=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));parent_projection=shapely.union_all(shapely.polygons(p[:,:,[0,2]]));lo=t.min(axis=(0,1));hi=t.max(axis=(0,1));forms=f.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);other=shapely.union_all([poly for b,poly,_ in forms if b['uid'] not in EXPECTED]);excess=projection.difference(target)
  measure=dict(mode=mode,targetCoverage=projection.intersection(target).area/target.area,maximumTargetDistanceM=float(shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),target).max()),excessAreaM2=excess.area,excessOutsideRecordedPodiumM2=excess.difference(parent).area,excessOutsideOriginalPodiumProjectionM2=excess.difference(parent_projection).area,unrelatedExcessAreaM2=excess.intersection(other).area)
  assert measure['targetCoverage']>=.95 and measure['maximumTargetDistanceM']<=10 and measure['unrelatedExcessAreaM2']<=1 and measure['excessOutsideRecordedPodiumM2']<1e-7 and measure['excessOutsideOriginalPodiumProjectionM2']<=1
  measures.append(measure)
  for _,_,url in forms:refs.append(ROOT/'3d-viewer'/url)
 review=dict(sourceSHA256ByUid=EXPECTED,sourceIdentityRelationshipAccepted=True,relatedOriginalSupportUid=PODIUM,dependentOriginalUid=TOWER,rawTowerIdentity=raw,rawIdentityWarningsRetained=True,scopedResolvedReasons=sorted(allowed),measurements=measures,proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),basis='Each source retains its own exact government ObjectID/CSUID/GeoRef and whole-cell identity. The only unrelated overlap is the independently identified original pool podium. Complete original tower excess lies on that recorded podium and its original geometry; all 58 support samples are accounted for in four worlds with source-bound local wall contact witnesses, and all original facets pass compound foundation. This establishes this exact pair relationship; shared names alone are not used as approval.',scope='Retain both separate source identities and all other buildings. No form-parent rewrite, suppression, coordinate edit, or broader unrelated-overlap exception.',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,fullAcceptance=False,publicationApproved=False)
 DOC.mkdir();save(DOC/'ROOT-SOURCE-REVIEW.json',review);refs += [HERE/'xl-final-script-pass.py']
 out=module('pool_pair_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-pool-pair-identity-relationship-review-v1',list(dict.fromkeys(refs)),dict(uids=list(EXPECTED),sourceIdentityRelationshipAccepted=True,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],relationshipAccepted=True),flush=True)
if __name__=='__main__':main()
