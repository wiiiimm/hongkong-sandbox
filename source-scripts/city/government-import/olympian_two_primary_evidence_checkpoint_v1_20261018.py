"""Pin primary architect context and independently verified full-foundation evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-two-primary-architect-v1-20261018';DOC=BASE/BATCH

def main():
 assert DOC.exists()and not(DOC/'result.json').exists();pins={};refs=[Path(__file__),HERE/'olympian-two-incident-face-contacts-v1-20261018.mjs'];verified=[]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in ['government-xl-olympian-two-canonical-contacts-v1-20261018','government-xl-olympian-two-compound-foundations-v4-20261018','government-xl-olympian-two-archive-coverage-v1-20261018']:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
   verified.append(dict(batch=name,jobId=r['jobId'],exactNeonResult=True))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins)
 provenance=read(DOC/'provenance.json');assert digest((DOC/'architect.html').read_bytes())==provenance['sha256']
 images=read(DOC/'image-provenance.json');assert len(images)==7
 for image in images:assert digest((DOC/image['file']).read_bytes())==image['sha256']
 foundations=read(BASE/'government-xl-olympian-two-compound-foundations-v4-20261018/foundations.json')['rows'];assert len(foundations)==4 and all(r['strictFoundationAccepted']and r['foundation']['fullyBuriedTriangles']==0 for r in foundations)
 contacts=read(DOC/'incident-face-contacts.json.gz')['rows'];assert len(contacts)==4
 summary=dict(primaryURL=provenance['url'],primaryImagesInspected=[x['file']for x in images],sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,modelGeometryChanges=0,fullAcceptance=False,identityOnlyApproved=False,sourceSpecificInterfaceInterpretationAccepted=False,foundationFaces=sum(r['foundation']['triangles']for r in foundations),fullyBuriedFaces=0,canonicalFailures=sum(r['canonicalFailures']for r in contacts),sameFaceContactWitnesses=sum(r['sameFaceContactWitnesses']for r in contacts),stillWithoutSameFaceWitness=sum(r['unresolvedWithoutSameFaceContact']for r in contacts),observations=[
 'Architect project material identifies the integrated commercial/residential scheme. Photographs visibly show elevated tower bases, recessed supporting sections and open areas below portions of the residential blocks. This supports investigating source-authored overhangs; it does not metrically register individual failed source faces.',
 'All seven published project images were inspected. Several views show multiple phases; do not assign an individual tower number from appearance alone. No surveyed dimensions or sub-centimetre contact proof can be inferred from these photographs.',
 'The exact original-face diagnostic found contacting vertices on the same finite source triangles for many canonical failed points. The reported along-face spans are source geometry, not new admissible contact distances. Remaining unmatched points require further context.',
 'All four complete original meshes pass strict full-face foundation diagnostics against both unchanged podiums and freshly captured current rendered terrain. This is original-coordinate geometry only; actual rendered tower attributes, four-world interface checks, fresh identity and neighbour qualification remain pending.',
 'The historical terrain candidate cannot route into the current manifest because a replacement parent is absent. Preserve V1 unpinned-capture rejection, V2 stale-parent rejection and V3 asset-directory failure; V4 uses the correct asset root and current terrain. These orchestration failures are not source corruption.',
 'No installation or permanent-uninstallable decision is made. Original podium terrain contacts, current neighbouring actors and full acceptance still require resolution.'])
 save(DOC/'source-review-context.json',summary);save(DOC/'ROOT-VERIFIED.json',dict(stages=verified,verifiedDistinctRefs=len(pins)))
 (DOC/'HANDOFF.md').write_text('\n\n'.join(summary['observations'])+'\n\nNext: account for the remaining424 failed points without a same-face contact witness and the two narrow Tower1 lower slivers, using unchanged source faces and primary context. Then source-specific interpretation and actual four-world checks, not a generic contact threshold change. Rebuild any needed podium terrain route against current parents. Fixed XL260installed/261remaining; all new workers terminal.\n')
 out=module('olympian_primary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-primary-architect-and-complete-foundation-evidence-v1',list(set(refs)),dict(uids=[r['uid']for r in foundations]+['landsd/265851:0','landsd/239351:0'],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],foundationFaces=summary['foundationFaces'],sameFaceWitnesses=summary['sameFaceContactWitnesses'],remaining=summary['stillWithoutSameFaceWitness']),flush=True)
if __name__=='__main__':main()
