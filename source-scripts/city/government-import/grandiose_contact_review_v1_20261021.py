"""Bounded interpretation of authored original contacts; no physical acceptance."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grandiose-contact-review-v1-20261021';DOC=BASE/BATCH
folders=[BASE/n for n in ['government-xl-grandiose-clubhouse-contact-view-v1-20261021','government-xl-grandiose-clubhouse-original-contact-v1-20261021','government-xl-grandiose-original-support-v1-20261021','government-xl-grandiose-lower-surface-inset-v1-20261021']]
assert not DOC.exists();refs=[Path(__file__)];pins={}
with connect() as db:
 db.execute('SET TRANSACTION READ ONLY')
 for folder in folders:
  r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
support=read(folders[2]/'support-checks.json.gz');assert sum(len(r['interface']['unresolved']) for r in support['rows'])==31
image=folders[0]/'contact-context.png';assert str(image.relative_to(ROOT)) in pins
policy=ROOT/'.agents/skills/hong-kong-model-improvement/SKILL.md';text=policy.read_text();assert 'Uninterpreted authored components and source crossings alone are not holds.' in text;refs.append(policy)
review=dict(uids=['landsd/246824:0','landsd/27898:0'],reviewer='Codex ROOT',imageActuallyViewed=dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes())),decision='Original source contacts are documented context, not an independent non-installability verdict.',observations=['Plan and elevations show the contacting source facets near the adjoining edge of the two complete originals. The oblique panel displays only contacting faces; omitted context is not evidence of hidden geometry.','Exact complete original-source comparison retains 69 line contacts and zero area contacts. This does not prove absence of solid penetration, physical support or architectural ownership.','The generic contact count is not itself an additional gate in the named acceptance policy. No existing identity, terrain, strict support, picking/collision, neighbour or publication requirement is waived.'],remainingConcreteFailures=dict(podiumBuriedFaces=4,podiumUpwardBuriedFaces=0,podiumMinimumTerrainGapM=-0.7966712169,grandioseBlock3UnresolvedSupportContacts=18,grandioseBlock1UnresolvedSupportContacts=13),nextAction='Resolve the exact remaining source/terrain failures and strict tower/podium interfaces; do not repeat unchanged full source contact counting or require global watertightness.',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,geometryChanges=0,installationApproved=False,publicationApproved=False,newlyInstalled=0)
save(DOC/'ROOT-CONTACT-REVIEW.json',review)
refs.extend(ROOT/p for p in pins)
result=module('contact_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-authored-contact-interpretation',list(dict.fromkeys(refs)),review)
print(result['jobId'])
