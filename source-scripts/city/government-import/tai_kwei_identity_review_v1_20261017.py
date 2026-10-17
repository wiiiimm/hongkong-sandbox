"""Bounded complete-original Tai Kwei identity review, no physical/publication approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';PHYSICAL=BASE/'government-xl-tai-kwei-current-physical-v1-20261017';NEIGH=BASE/'government-xl-tai-kwei-neighbour-originals-v1-20261017';CONTACT=BASE/'government-xl-tai-kwei-neighbour-contacts-v2-20261017';BATCH='government-xl-tai-kwei-reviewed-identity-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UID='landsd/106413:0';SHA='797e15e504a549f44c02b55fe11ab769dec45f27f5174c4dc6dc313a7562fe79';EXPECTED={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PHYSICAL,NEIGH,CONTACT]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 row=read(PHYSICAL/'selection.json.gz')['rows'][0];proof=read(PHYSICAL/'identity-proof.json');b=row['source']['building'];assert row['uid']==UID and row['sourceSHA256']==SHA and row['modelId']=='B346442034301063C0' and b['buildingCSUID']=='3464420343T20050430'
 assert proof['originalOwnership']['sourceGraphVerified'] and proof['originalOwnership']['originalRootName']==row['modelId'] and proof['exactCurrentComponentRoute']['qualified'] and set(proof['reasons'])==EXPECTED
 foreign={f['uid']for f in proof['freshCurrentIdentity']['intersectingForms']if f['uid']!=UID};assert foreign=={'landsd/201002:0','landsd/209728:0'}
 contacts=read(CONTACT/'contacts.json');assert contacts['uid']==UID and contacts['sourceSHA256']==SHA and contacts['sourceTriangles']==13114
 final=module('tai_kwei_review_context',HERE/'xl-final-script-pass.py');neighbours=read(NEIGH/'selection.json.gz')['rows'];counterparts=[]
 for r in neighbours:
  raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];t=decode_original_world_triangles(raw);lo=t.min(axis=(0,1));hi=t.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);current=next(b for b,_,_ in forms if b['uid']==r['uid']);assert current==r['source']['building']
  context=dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],identity=final.identity_context(r,t,forms),neighbourTileHashes={tile:digest((ROOT/'3d-viewer'/tile).read_bytes())for _,_,tile in forms})
  other=verify_files(r,context,LOCAL/r['uid'].replace('/','-').replace(':','-'));assert other['originalOwnership']['sourceGraphVerified'] and other['originalOwnership']['originalRootName']==r['modelId'] and other['exactCurrentComponentRoute']['qualified'];save(DOC/(r['uid'].replace('/','-').replace(':','-')+'-identity.json'),other);counterparts.append(dict(uid=r['uid'],modelId=r['modelId'],sourceSHA256=r['sourceSHA256'],originalGraphVerified=True,exactRouteQualified=True))
 for r in contacts['neighbours']:
  assert r['uid']in foreign and r['contacts']['allPairsExamined'] and r['contacts']['sourceFacesOmitted']==0
  assert all(c['bounds'][1][1]<=14.6 for c in r['contacts']['contacts'])
 assert {r['uid']for r in counterparts}==foreign
 decision=dict(uid=UID,sourceSHA256=SHA,modelId=row['modelId'],governmentBuildingCSUID=b['buildingCSUID'],sourceIdentityReviewed=True,sourceIdentityReviewUsedAI=True,identityReviewApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawIdentityProof=proof,rawWarningsRetained=True,scopedResolvedReasons=sorted(EXPECTED),counterpartSources=counterparts,reviewBasis=['Complete original root and exact current government ObjectID/CSUID route identify Tai Kwei Building. Target coverage is 99.2726 percent; all 13,114 source faces remain unchanged.','The only footprint-overlap flags concern the immediately adjoining Tai Fu and Tai Wing. Both exact original roots and current government routes were independently checked.','Root inspected both oblique views of all three complete unchanged originals. They are separate aligned towers with adjoining lower-level bases. The flagged low-level edges belong to Tai Kwei’s own original base, not a misplaced neighbouring tower.','Exact full-source finite-primitive comparison accounts for all source faces, including zero-area facets. Contacts are confined below14.6m HKPD along the adjoining lower-level edges; actual source-projection overlaps are0.1811706753m2 and0.0086265800m2, versus footprint-based4.6624084257m2 and3.9266040173m2. These measurements locate the discrepancy; they do not introduce a new acceptance threshold.','This source-specific identity review resolves only the two neighbour-footprint identity reasons. Raw authored source contacts are retained. No neighbour suppression, collision exemption, support approval, placement approval or publication permission is granted.'],placementReviewed=False,publicationApproved=False,foreignActorSuppressionApproved=False,collisionApproved=False,aiGeometryModelling=False)
 save(DOC/'identity-review.json',decision);(DOC/'ROOT-REVIEW.md').write_text('\n\n'.join(decision['reviewBasis'])+'\n')
 refs +=[PHYSICAL/'identity-proof.json',CONTACT/'contacts.json',NEIGH/'selection.json.gz',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'xl-final-script-pass.py'];refs +=[p for p in LOCAL.rglob('*')if p.is_file()]
 out=module('tai_kwei_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'root-reviewed-exact-original-tai-kwei-identity-v1',list(set(refs)),dict(uids=[UID],sourceSHA256=SHA,identityAccepted=True,sourceIdentityReviewUsedAI=True,identityProof=decision['identityProof'],fullAcceptance=False,nextStep='Finish independent current collision/rendered-world/browser checks and only then publish unchanged Tai Kwei with verified private terrain.'))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()
