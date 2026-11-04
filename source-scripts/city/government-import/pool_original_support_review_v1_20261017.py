"""Source-specific review of unchanged pool wall-to-podium contact; no policy edits."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-sham-shui-po-pool-original-support-review-v1-20261017';DOC=BASE/BATCH
PREFIX='government-xl-sham-shui-po-pool-'
NAMES=['four-world-contacts-v2-20261017','local-wall-paths-v1-20261017','original-pair-identity-review-v1-20261017','four-world-foundation-v2-20261017']
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/(PREFIX+name)/'result.json';r=read(p)
   assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for q in r['evidenceRefs']:
    assert q['path'] not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 contact=read(BASE/(PREFIX+NAMES[0])/'summary.json');strict=read(BASE/(PREFIX+NAMES[0])/'strict-interfaces.json')
 paths=read(BASE/(PREFIX+NAMES[1])/'paths.json');identity=read(BASE/(PREFIX+NAMES[2])/'ROOT-SOURCE-REVIEW.json');foundation=read(BASE/(PREFIX+NAMES[3])/'summary.json')
 assert identity['sourceIdentityRelationshipAccepted'] and foundation['allStrictPass'] and len(foundation['rows'])==8
 assert contact['allWitnessesVerified'] and len(contact['rows'])==4 and len(strict['rows'])==4
 assert len(paths['rows'])==12
 for row in paths['rows']:
  w=row['witness'];assert w and w['continuousOriginalSurface'] and w['maximumPrismRadiusM']==.5
  assert max(abs(v) for v in w['normalY'])<=.1 and len(w['clippedSharedEdges'])==len(w['faces'])-1
 for row in contact['rows']:
  assert row['strictSamples']==58 and row['strictContacts']==40 and row['strictWallContacts']==6 and row['remaining']==row['geometricWitnessesVerified']==12
  assert all(x['geometricWitnessVerified'] and all(x['checks'].values()) for x in row['rows'])
 old=read(BASE/(PREFIX+'four-world-foundation-v1-20261017')/'world-triangles.json.gz');new=read(BASE/(PREFIX+NAMES[3])/'world-triangles.json.gz')
 assert old.keys()==new.keys()
 for mode in old:
  assert old[mode].keys()==new[mode].keys()
  for uid in old[mode]:assert np.array_equal(old[mode][uid],new[mode][uid])
 review=dict(sourceSHA256ByUid=identity['sourceSHA256ByUid'],supportedUid='landsd/271043:0',requiredOriginalSupportUid='landsd/265480:0',sourceSpecificSupportAccepted=True,rawStrictInterfaces=strict['rows'],rawStrictFailuresRetained=True,strictSamplesPerWorld=58,strictContactsPerWorld=40,sameTriangleWallContactsPerWorld=6,localContinuousOriginalWallContactsPerWorld=12,coordinateWorlds=list(new),newTerrainFoundationChecks=8,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,fullAcceptance=False,publicationApproved=False,basis='The twelve remaining rim points connect through their actual original incident wall triangles to the independently identified original podium. Every shared edge is clipped inside a local prism wholly within the existing 0.5m source-clearance radius; contact lies on the original podium within 1mm. The complete paths are verified in original, literal and both Float32 worlds, alongside forty strict contacts and six same-triangle wall contacts. All original faces pass compound foundation against the repaired terrain. This resolves this exact pair support warning without changing any source geometry or the canonical interface result.',scope='Only these exact source SHA256 identities, poses and local contact witnesses. Tower must depend on this podium at runtime. No global support-rule changes, missing support substitution, horizontal buried-floor exception, or publication approval. Full neighbour and browser acceptance remain mandatory.')
 DOC.mkdir();save(DOC/'ROOT-SUPPORT-REVIEW.json',review)
 out=module('pool_support_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-pool-continuous-wall-support-review-v1',list(dict.fromkeys(refs)),dict(uids=list(review['sourceSHA256ByUid']),sourceSpecificSupportAccepted=True,fullAcceptance=False,newlyInstalled=0))
 print(dict(jobId=out['jobId'],sourceSpecificSupportAccepted=True),flush=True)
if __name__=='__main__':main()
