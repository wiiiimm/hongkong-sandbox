"""Preserve primary architectural context without claiming exact survey or placement approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-murray-primary-plan-context-v1-20261017';DOC=BASE/BATCH

def main():
 assert not (DOC/'result.json').exists()
 for file,request in [('architect-plan-page.html','request.json'),('architect-level-01.jpg','image-request.json')]:assert digest((DOC/file).read_bytes())==read(DOC/request)['sha256']
 paths=[Path(__file__)];proofs=[]
 for name in ['government-xl-murray-original-buried-surface-context-v1-20261017','government-xl-murray-original-terrain-interface-v1-20261017']:
  p=BASE/name/'result.json';r=read(p)
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  pins={}
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
  for f,h in pins.items():assert digest((ROOT/f).read_bytes())==h
  verification=dict(jobId=r['jobId'],exactNeonResultVerified=True,distinctHashesVerified=len(pins));save(p.parent/'ROOT-VERIFIED.json',verification);proofs.append(verification);paths.append(p)
 review=dict(sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,imagesActuallyInspected=['architect-level-01.jpg','../government-xl-murray-original-buried-surface-context-v1-20261017/group-1.png','../government-xl-murray-original-buried-surface-context-v1-20261017/group-2.png'],observations=['Eight flagged source faces form a near-vertical strip; two form a downward-facing narrow underside.','The architect-supplied first-floor plan shows the tower, podium circulation, planted areas and curved approach.','No exact surveyed registration or section elevation establishes the roles of the ten source faces.','All ten fixed-band whole-facet terrain proofs fail; nearest witness distances reach approximately1.105m.'],decision='unresolved-source-terrain-intersection',installationApproved=False,permanentRejection=False,nextStep='Obtain matching ground/section or original source component evidence to distinguish embedded foundation/retaining surfaces from incorrect terrain intrusion. Do not repeat unchanged distance or source-coverage tests. Podium identity extent/coverage and current complete physical acceptance also remain outstanding.',verifiedReceipts=proofs)
 save(DOC/'ROOT-SOURCE-REVIEW.json',review)
 (DOC/'HANDOFF.md').write_text('Murray remains unresolved, not corrupted or permanently rejected. Original two-sheet coverage5496/5496; ten buried faces now exhaustively enumerated into two groups. Eight near-vertical faces535,536,537,538,4550,4551,4552,4553; two downward faces4660,4661. None has complete fixed0.1m original-terrain proximity; do not apply the prior Oi Sin contact-resolution interpretation here. First-floor architect plan reviewed but lacks surveyed mapping and lower-grade sections for exact face functions. All strict failures retained. New receipts and evidence verified in pinnedNeon. No source geometry edits, terrain publication, optimisation or installation credit. No workers remain running. Next action: source component/ground-level section evidence, or continue another actionable remainingXL while this exact unresolved reason remains recorded. Counts253installed/268remaining/521, detailed6678.\n')
 result=module('murray_primary_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'murray-primary-plan-context-unresolved-source-terrain-v1',paths,dict(uids=['landsd/265825:0','landsd/248655:0'],fullAcceptance=False,sourceEvidenceInterpretationUsedAI=True,remainingReason='podium-source-terrain-intersection-and-identity-extent-unresolved',nextStep=review['nextStep']))
 print(dict(jobId=result['jobId'],verifiedReceipts=proofs),flush=True)
if __name__=='__main__':main()
