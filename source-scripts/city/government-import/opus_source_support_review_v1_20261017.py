"""Scoped unchanged Opus wall/ground support review; no general policy changes."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-source-support-review-v1-20261017';DOC=BASE/BATCH
NAMES=['government-xl-opus-stable-assembly-identity-v1-20261017','government-xl-opus-complete-contact-account-v1-20261017','government-xl-opus-original-patch-roles-v1-20261017','government-xl-opus-assembly-original-patch-v1-20261017']
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for x in r['evidenceRefs']:pins.setdefault(x['path'],set()).add(x['sha256'])
 def consume(p):
  assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 identity=consume(BASE/NAMES[0]/'ROOT-SOURCE-REVIEW.json');account=consume(BASE/NAMES[1]/'account.json.gz');role=consume(BASE/NAMES[2]/'ROOT-SOURCE-REVIEW.json');finite=consume(BASE/NAMES[3]/'proofs.json.gz');assert identity['sourceIdentityRelationshipAccepted'] and role['sourceRoleInterpretationAccepted'];assert len(finite['rows'])==13557 and all(r['proof']['groundProjectionCovered'] for r in finite['rows']);assert all(r['proof']['existingOrdinaryClearanceBoundProved'] for r in finite['rows'][967:]);assert role['foundation']['fullyBuriedUpwardTriangles']==0
 summary=[]
 for r in account['rows']:
  expected=(2,0,0,2) if r['uid']=='landsd/322573:0' else (75,4,9,62);assert (r['samples'],r['strictGroundOrPodiumContacts'],r['canonicalSameWallContacts'],r['boundedOriginalWallContacts'])==expected
  assert r['allSamplesAccounted'] and all(m['verifiedOriginalWallContact']['verified'] and all(m['verifiedOriginalWallContact']['checks'].values()) for m in r['mapped']);summary.append({k:v for k,v in r.items() if k!='mapped'})
 assert len(summary)==8;image=BASE/NAMES[1]/'source-junctions.png';assert digest(image.read_bytes()) in pins[str(image.relative_to(ROOT))];refs.append(image)
 review=dict(sourceSHA256ByUid={r['uid']:r['sourceSHA256'] for r in identity['measurements']},sourceSpecificSupportAccepted=True,requiredOriginalPodiumUid='landsd/248432:0',dependentUids=['landsd/322573:0','landsd/319559:0'],groundSHA256=finite['groundSHA256'],worldSHA256=finite['worldSHA256'],sampleAccounts=summary,rawCanonicalWarningsRetained=True,rawClearanceFlagsRetained=role['rawStrictFailuresRetained'],sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,reviewer='Codex ROOT',imagesActuallyViewed=[dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()))],fullAcceptance=False,publicationApproved=False,basis='The exact independently identified originals form the captured assembly. Four companion rim samples meet actual terrain/podium directly, nine meet the canonical original wall intersection rule, and62meet verified intersections on the same original sloped wall within the existing0.5m radius. The tower’s two lowest rim samples likewise intersect the original podium within0.5m; its entire12382face geometry clears terrain, so this is not acceptance of a fully embedded source. All77 samples are accounted in original/literal/left/balanced worlds. Podium130lowerwall and one downwardskin raw flags retain the freshly rebound source-role interpretation; full13557face coverage and zero buriedupward foundation checks pass. Opposite oblique original source views inspected.',scope='Only these exact source hashes and this ground/world binding, with both dependents requiring the original podium. Original geometry,1xscale,poses and canonical interface outputs unchanged. No generic support waiver, no publication permission; final complete-neighbour, runtime, terrain and browser gates remain.')
 DOC.mkdir();save(DOC/'ROOT-SUPPORT-REVIEW.json',review)
 result=module('opus_support_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-source-specific-complete-support-review-v1',refs,dict(uids=sorted(review['sourceSHA256ByUid']),sourceSpecificSupportAccepted=True,fullAcceptance=False,newlyInstalled=0));print(result['jobId'],flush=True)
if __name__=='__main__':main()
